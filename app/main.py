import sys
import asyncio

# Windows Proactor Event Loop Policy Fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import engine, Base, get_db
from app.models import User, Job, Bookmark
from app.schemas import (
    RegisterRequest, VerifyOTPRequest, LoginRequest, TokenResponse,
    UserProfileResponse, PreferenceUpdateRequest, BookmarkToggleRequest
)
from app.security import (
    hash_password, verify_password, create_access_token,
    generate_otp, get_current_user
)
from app.email_service import send_otp_email, send_job_alert
from app.scheduler import start_scheduler, scrape_and_notify

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    yield

app = FastAPI(title="BDJobs Notice Mailer", version="2.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- SMART INSTANT ALERT LOGIC -----------------

async def send_smart_instant_alert(user_email: str, categories: List[str], keywords: List[str], limit: int = 25):
    """Category ba keywords match kore database theke instant notice dispatch kore"""
    async for db in get_db():
        query = select(Job).where(Job.is_expired == False)
        clean_keywords = [k.strip().lower() for k in keywords if k.strip()]

        cat_condition = Job.category.in_(categories) if categories else None
        kw_conditions = []
        for kw in clean_keywords:
            kw_conditions.append(Job.title.ilike(f"%{kw}%"))
            kw_conditions.append(Job.company_name.ilike(f"%{kw}%"))

        if cat_condition is not None and kw_conditions:
            query = query.where(or_(cat_condition, or_(*kw_conditions)))
        elif cat_condition is not None:
            query = query.where(cat_condition)
        elif kw_conditions:
            query = query.where(or_(*kw_conditions))

        query = query.order_by(Job.id.desc()).limit(limit)
        res = await db.execute(query)
        matching_jobs = res.scalars().all()

        if not matching_jobs:
            print(f"--> [INSTANT ALERT] No matching jobs found for {user_email}")
            return

        jobs_data = [
            {
                "title": j.title,
                "company_name": j.company_name,
                "category": j.category,
                "deadline": j.deadline,
                "job_url": j.job_url,
            }
            for j in matching_jobs
        ]

        try:
            await send_job_alert(user_email, jobs_data)
            print(f"--> [INSTANT ALERT SUCCESS] Sent {len(jobs_data)} jobs to {user_email}")
        except Exception as e:
            print(f"--> [INSTANT ALERT ERROR] Failed sending to {user_email}: {e}")
        break

# ----------------- USER PREFERENCES API -----------------

@app.post("/api/v1/users/preferences/update", tags=["User"])
async def update_preferences(
    payload: PreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.subscribed_categories = payload.categories
    current_user.alert_keywords = payload.keywords
    await db.commit()
    await db.refresh(current_user)

    if not current_user.is_paused:
        asyncio.create_task(
            send_smart_instant_alert(
                current_user.email,
                current_user.subscribed_categories or [],
                current_user.alert_keywords or []
            )
        )

    return {
        "message": "Preferences updated",
        "categories": current_user.subscribed_categories,
        "keywords": current_user.alert_keywords
    }

# ----------------- BOOKMARKS APIS -----------------

@app.post("/api/v1/jobs/bookmark/toggle", tags=["Bookmarks"])
async def toggle_bookmark(
    payload: BookmarkToggleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Bookmark).where(Bookmark.user_id == current_user.id, Bookmark.job_id == payload.job_id)
    )
    bookmark = res.scalar_one_or_none()

    if bookmark:
        await db.delete(bookmark)
        await db.commit()
        return {"bookmarked": False, "message": "Removed from bookmarks"}
    else:
        new_bm = Bookmark(user_id=current_user.id, job_id=payload.job_id)
        db.add(new_bm)
        await db.commit()
        return {"bookmarked": True, "message": "Saved to bookmarks"}

@app.get("/api/v1/users/bookmarks", tags=["Bookmarks"])
async def get_my_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Job).join(Bookmark, Bookmark.job_id == Job.id)
        .where(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.id.desc())
    )
    jobs = res.scalars().all()
    items = [
        {
            "id": j.id,
            "job_id": j.job_id,
            "title": j.title,
            "company_name": j.company_name,
            "category": j.category,
            "deadline": j.deadline,
            "location": getattr(j, "location", "Not Specified"),
            "experience_level": getattr(j, "experience_level", "Any"),
            "is_expired": getattr(j, "is_expired", False),
            "job_url": j.job_url,
            "is_bookmarked": True
        }
        for j in jobs
    ]
    return {"bookmarks": items}

# ----------------- AUTH APIS -----------------

@app.post("/api/v1/auth/register", tags=["Auth"])
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    otp = generate_otp()
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_verified=False,
        subscribed_categories=[],
        alert_keywords=[],
        otp_code=otp,
        otp_expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(user)
    await db.commit()
    try:
        await send_otp_email(user.email, otp, "Account Registration")
    except Exception as e:
        print(f"--> [OTP EMAIL FAILED]: {e}")
    return {"message": "OTP sent to your email", "email": user.email}

@app.post("/api/v1/auth/verify-email", tags=["Auth"])
async def verify_email(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or user.otp_code != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    if user.otp_expires_at and user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")

    user.is_verified = True
    user.otp_code = None
    await db.commit()
    await db.refresh(user)

    asyncio.create_task(
        send_smart_instant_alert(
            user.email,
            user.subscribed_categories or [],
            user.alert_keywords or []
        )
    )

    token = create_access_token({"sub": user.email})
    return {"message": "Verified successfully", "access_token": token, "token_type": "bearer"}

@app.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please submit OTP.")

    return {"access_token": create_access_token({"sub": user.email}), "token_type": "bearer"}

@app.get("/api/v1/users/me", response_model=UserProfileResponse, tags=["User"])
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/v1/users/toggle-notifications", tags=["User"])
async def toggle_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.is_paused = not current_user.is_paused
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return {
        "message": "Notification status updated",
        "is_paused": current_user.is_paused
    }

# ----------------- ANALYTICS & MARKET TRENDS -----------------

@app.get("/api/v1/analytics/trends", tags=["Analytics"])
async def get_job_trends(db: AsyncSession = Depends(get_db)):
    """গত ৭ দিনে কোন ক্যাটাগরিতে কতটি সার্কুলার এসেছে তার ডাটা (Chart.js এর জন্য)"""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    query = (
        select(Job.category, func.count(Job.id).label("count"))
        .where(Job.created_at >= seven_days_ago)
        .group_by(Job.category)
        .order_by(func.count(Job.id).desc())
        .limit(6)
    )
    res = await db.execute(query)
    rows = res.fetchall()

    return {
        "labels": [r[0] for r in rows if r[0]],
        "counts": [r[1] for r in rows if r[0]]
    }

# ----------------- JOB CIRCULARS & ADVANCED FILTERS -----------------

@app.get("/api/v1/jobs/categories", tags=["Jobs"])
async def get_all_active_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job.category).distinct())
    categories = [r[0] for r in result.fetchall() if r[0]]
    categories.sort()
    return {"categories": categories}

@app.get("/api/v1/jobs/locations", tags=["Jobs"])
async def get_all_active_locations(db: AsyncSession = Depends(get_db)):
    """Active সব লোকেশন এবং প্রতিটিতে কয়টি জব আছে তা রিটার্ন করে"""
    query = (
        select(Job.location, func.count(Job.id).label("job_count"))
        .where(Job.location.isnot(None), Job.location != "", Job.location != "Not Specified")
        .group_by(Job.location)
        .order_by(func.count(Job.id).desc())
    )
    result = await db.execute(query)
    rows = result.fetchall()

    locations = [{"name": r[0], "count": r[1]} for r in rows if r[0]]
    return {"locations": locations}

@app.get("/api/v1/jobs", tags=["Jobs"])
async def get_jobs(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    categories: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    include_expired: bool = Query(True),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1),
    db: AsyncSession = Depends(get_db)
):
    query = select(Job)

    # 1. Expired filter
    if not include_expired:
        query = query.where(Job.is_expired == False)

    # 2. Text Search (Title ba Company)
    if q and q.strip():
        search_term = f"%{q.strip().lower()}%"
        query = query.where(
            or_(
                func.lower(Job.title).ilike(search_term),
                func.lower(Job.company_name).ilike(search_term)
            )
        )

    # 3. Category Filter (Case-insensitive & Trimmed)
    if category and category.strip():
        cat_clean = category.strip()
        query = query.where(func.lower(func.trim(Job.category)) == cat_clean.lower())
    elif categories and categories.strip():
        cat_list = [c.strip().lower() for c in categories.split(",") if c.strip()]
        if cat_list:
            query = query.where(func.lower(func.trim(Job.category)).in_(cat_list))

    # 4. Location Filter (Smart Substring + Title Fallback)
    if location and location.strip():
        loc_clean = location.strip().lower()
        if loc_clean == "remote":
            query = query.where(
                or_(
                    func.lower(Job.location).ilike("%remote%"),
                    func.lower(Job.title).ilike("%remote%"),
                    func.lower(Job.title).ilike("%work from home%")
                )
            )
        else:
            query = query.where(
                or_(
                    func.lower(Job.location).ilike(f"%{loc_clean}%"),
                    func.lower(Job.title).ilike(f"%{loc_clean}%")
                )
            )

    # 5. Experience Filter (Realistic BDJobs Matching)
    if experience and experience.strip():
        exp_clean = experience.strip().lower()
        if "fresher" in exp_clean or "entry" in exp_clean:
            query = query.where(
                or_(
                    func.lower(Job.experience_level).ilike("%fresher%"),
                    func.lower(Job.experience_level).ilike("%entry%"),
                    func.lower(Job.title).ilike("%fresher%"),
                    func.lower(Job.title).ilike("%junior%"),
                    func.lower(Job.title).ilike("%trainee%"),
                    func.lower(Job.title).ilike("%associate%"),
                    func.lower(Job.title).ilike("%assistant%"),
                    func.lower(Job.title).ilike("%officer%")
                )
            )
        elif "intern" in exp_clean:
            query = query.where(
                or_(
                    func.lower(Job.experience_level).ilike("%intern%"),
                    func.lower(Job.title).ilike("%intern%")
                )
            )
        elif "3+" in exp_clean or "senior" in exp_clean:
            query = query.where(
                or_(
                    func.lower(Job.experience_level).ilike("%3+%"),
                    func.lower(Job.title).ilike("%senior%"),
                    func.lower(Job.title).ilike("%lead%"),
                    func.lower(Job.title).ilike("%manager%"),
                    func.lower(Job.title).ilike("%head%")
                )
            )
        else:
            # 1-3 Years
            query = query.where(
                or_(
                    func.lower(Job.experience_level).ilike("%1-3%"),
                    func.lower(Job.experience_level).ilike("%mid%"),
                    func.not_(
                        or_(
                            func.lower(Job.title).ilike("%senior%"),
                            func.lower(Job.title).ilike("%lead%"),
                            func.lower(Job.title).ilike("%manager%"),
                            func.lower(Job.title).ilike("%intern%")
                        )
                    )
                )
            )

    # Total Count
    count_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_res.scalar() or 0

    # Pagination fetch
    query = query.order_by(Job.id.desc()).offset((page - 1) * size).limit(size)
    res = await db.execute(query)
    jobs = res.scalars().all()

    items = []
    for j in jobs:
        items.append({
            "id": j.id,
            "job_id": j.job_id,
            "title": j.title,
            "company_name": j.company_name,
            "category": j.category or "General",
            "deadline": j.deadline or "N/A",
            "location": getattr(j, "location", None) or "Dhaka",
            "experience_level": getattr(j, "experience_level", None) or "1-3 Years",
            "is_expired": getattr(j, "is_expired", False),
            "job_url": j.job_url,
            "created_at": j.created_at.strftime("%b %d, %Y") if j.created_at else "N/A"
        })
    return {"total": total, "page": page, "size": size, "items": items}

@app.post("/api/v1/trigger-scrape", tags=["Scraper"])
async def trigger_scrape():
    await scrape_and_notify()
    return {"message": "Scrape executed successfully"}

# ----------------- WEB FRONTEND -----------------

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def serve_homepage():
    with open("app/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
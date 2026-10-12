from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select
from sqlalchemy import update, func, and_
from app.database import AsyncSessionLocal
from app.models import Job, User, Bookmark
from app.scraper import BDJobsScraper
from app.email_service import send_email
from app.utils import parse_deadline_date, extract_job_metadata
from datetime import datetime, date, timedelta

scheduler = AsyncIOScheduler()
scraper = BDJobsScraper()

async def auto_cleanup_expired_jobs():
    """ডেডলাইন পার হয়ে যাওয়া সার্কুলারগুলোকে is_expired = True মার্ক করে"""
    today = date.today()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            update(Job)
            .where(Job.deadline_date < today, Job.is_expired == False)
            .values(is_expired=True)
        )
        await session.commit()
        if result.rowcount > 0:
            print(f"--> [CLEANUP] Marked {result.rowcount} expired jobs as is_expired=True")

async def send_urgent_deadline_reminders():
    """বুকমার্ক করা জবের ডেডলাইন ১-২ দিন বাকি থাকলে ইউজারকে সতর্কতা মেইল পাঠানো"""
    today = date.today()
    expiring_soon_min = today + timedelta(days=1)
    expiring_soon_max = today + timedelta(days=2)

    async with AsyncSessionLocal() as session:
        # ইউজার এবং তাদের বুকমার্ক করা যে সার্কুলারগুলোর মেয়াদ ২৪-৪৮ ঘণ্টার মধ্যে শেষ হবে
        query = (
            select(User.email, Job)
            .join(Bookmark, Bookmark.user_id == User.id)
            .join(Job, Job.id == Bookmark.job_id)
            .where(
                User.is_verified == True,
                User.is_paused == False,
                Job.is_expired == False,
                Job.deadline_date >= expiring_soon_min,
                Job.deadline_date <= expiring_soon_max
            )
        )
        res = await session.execute(query)
        rows = res.all()

        user_expiring_map = {}
        for email, job in rows:
            user_expiring_map.setdefault(email, []).append(job)

        for email, jobs in user_expiring_map.items():
            cards = "".join([
                f"""
                <li style="margin-bottom: 10px;">
                    <strong>{j.title}</strong> at {j.company_name}<br/>
                    <span style="color: #dc2626; font-size: 13px;">Deadline: {j.deadline} (Expiring Soon!)</span><br/>
                    <a href="{j.job_url}" style="color: #0284c7; font-size: 12px;">Apply Before Deadline &rarr;</a>
                </li>
                """
                for j in jobs
            ])
            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 500px; padding: 20px; border: 1px solid #fca5a5; border-radius: 8px;">
                <h3 style="color: #dc2626; margin-top: 0;">⏳ Urgent: Your Saved Jobs Are Expiring Soon!</h3>
                <p>The deadline for the following saved job(s) will pass within 24-48 hours:</p>
                <ul>{cards}</ul>
            </div>
            """
            try:
                await send_email(email, "⏳ Urgent: Application Deadline Expiring Soon", html)
                print(f"--> [REMINDER] Sent deadline alert to {email}")
            except Exception as e:
                print(f"--> [REMINDER ERROR] {email}: {e}")

async def scrape_and_notify():
    async with AsyncSessionLocal() as session:
        scraped_jobs = await scraper.get_latest_jobs()
        new_jobs = []

        for item in scraped_jobs:
            query = await session.execute(select(Job).where(Job.job_id == item["job_id"]))
            if not query.scalars().first():
                deadline_dt = parse_deadline_date(item.get("deadline", ""))
                loc, exp = extract_job_metadata(item.get("title", ""), item.get("location"))

                job_data = {
                    **item,
                    "deadline_date": deadline_dt,
                    "location": loc,
                    "experience_level": exp,
                    "is_expired": False
                }
                job = Job(**job_data)
                session.add(job)
                new_jobs.append(job_data)

        if new_jobs:
            await session.commit()
            print(f"--> [DB] Added {len(new_jobs)} new intelligent jobs.")

def start_scheduler():
    # নিয়মিত স্ক্র্যাপিং (প্রতি ৩০ মিনিট)
    scheduler.add_job(scrape_and_notify, "interval", minutes=30)
    # প্রতিদিন রাত ১২:০১ এ মেয়াদোত্তীর্ণ জব অটো-ক্লিনআপ
    scheduler.add_job(auto_cleanup_expired_jobs, "cron", hour=0, minute=1)
    # প্রতিদিন সকাল ৯:০০ টায় ডেডলাইন রিমাইন্ডার পাঠানো
    scheduler.add_job(send_urgent_deadline_reminders, "cron", hour=9, minute=0)
    scheduler.start()
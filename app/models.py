from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    subscribed_categories = Column(JSONB, default=list)
    alert_keywords = Column(JSONB, default=list)
    is_paused = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    category = Column(String, index=True)
    deadline = Column(String)
    job_url = Column(String, nullable=False)
    
    # নতুন ইন্টেলিজেন্ট ফিল্ডস:
    location = Column(String, default="Not Specified", index=True)
    experience_level = Column(String, default="Any", index=True) # Fresher, 1-3 Years, 3+ Years
    deadline_date = Column(Date, nullable=True, index=True)
    is_expired = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
    job = relationship("Job")
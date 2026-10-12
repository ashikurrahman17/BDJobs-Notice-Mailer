from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime



# Auth Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

# User & Preference Schemas
class UserProfileResponse(BaseModel):
    id: int
    email: str
    is_verified: bool
    subscribed_categories: List[str] = []
    alert_keywords: List[str] = []  # <-- Eita thaka must
    is_paused: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryPreferenceRequest(BaseModel):
    categories: List[str]

# Job & Search Schemas
class JobResponse(BaseModel):
    id: int
    job_id: str
    title: str
    company_name: str
    category: str
    deadline: Optional[str]
    job_url: str
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedJobsResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[JobResponse]

class PreferenceUpdateRequest(BaseModel):
    categories: List[str] = []
    keywords: List[str] = []

class BookmarkToggleRequest(BaseModel):
    job_id: int
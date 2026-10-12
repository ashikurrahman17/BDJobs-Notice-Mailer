import re
from datetime import datetime
from typing import Optional, Tuple

def parse_deadline_date(deadline_str: str) -> Optional[datetime.date]:
    """বিভিন্ন ফরম্যাটের ডেডলাইন স্ট্রিং থেকে date অবজেক্ট তৈরি করে"""
    if not deadline_str:
        return None
    patterns = ["%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%b %d, %Y"]
    clean_str = deadline_str.strip()
    for fmt in patterns:
        try:
            return datetime.strptime(clean_str, fmt).date()
        except ValueError:
            continue
    return None

def extract_job_metadata(title: str, raw_location: str = None) -> Tuple[str, str]:
    """টাইটেল ও লোকেশন স্ট্রিং থেকে এক্সপেরিয়েন্স লেভেল এবং লোকেশন নির্ধারণ করে"""
    title_lower = title.lower()
    
    # Experience Level Extraction
    if any(k in title_lower for k in ["intern", "internship"]):
        exp = "Internship"
    elif any(k in title_lower for k in ["fresher", "freshers", "entry", "trainee", "junior", "apprentice"]):
        exp = "Fresher / Entry"
    elif any(k in title_lower for k in ["senior", "lead", "principal", "manager", "head"]):
        exp = "3+ Years"
    else:
        exp = "1-3 Years"

    # Location normalization
    loc = raw_location.strip() if raw_location else "Dhaka"
    if any(k in title_lower for k in ["remote", "work from home"]):
        loc = "Remote"

    return loc, exp
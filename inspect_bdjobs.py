import httpx
from bs4 import BeautifulSoup
import re

url = "https://jobs.bdjobs.com/jobsearch.asp?fcatId=8"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

with httpx.Client(headers=headers, follow_redirects=True, timeout=15.0) as client:
    res = client.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    
    # jobdetails লিংকগুলো খোঁজা
    links = [a.get("href") for a in soup.find_all("a") if a.get("href") and "jobdetails" in a.get("href").lower()]
    print(f"Total 'jobdetails' links found: {len(links)}")
    if links:
        print("Sample links:", links[:3])
    else:
        # পেজে কোনো জব টাইটেল বা কার্ডের নমুনা ক্লাস প্রিন্ট করা
        divs = [d.get("class") for d in soup.find_all("div") if d.get("class")]
        print(f"Sample classes in page (first 10): {divs[:10]}")
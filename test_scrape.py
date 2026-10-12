import httpx
from bs4 import BeautifulSoup

url = "https://jobs.bdjobs.com/jobsearch.asp?fcatId=8"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

with httpx.Client(headers=headers, follow_redirects=True, timeout=15.0) as client:
    res = client.get(url)
    print("Status Code:", res.status_code)
    print("Response Length:", len(res.text))
    # পেজের টাইটেল দেখে বুঝা যাবে আমরা ব্লকড কি না
    soup = BeautifulSoup(res.text, "html.parser")
    print("Page Title:", soup.title.string if soup.title else "No Title")
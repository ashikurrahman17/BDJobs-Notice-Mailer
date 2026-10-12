import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        captured_jobs = []

        # বিডিজবস ব্যাকগ্রাউন্ডে যেসব JSON রেসপন্স পাঠায় তা সরাসরি ক্যাচ করা
        async def handle_response(response):
            if "job" in response.url.lower() and "json" in response.headers.get("content-type", "").lower():
                try:
                    data = await response.json()
                    # যদি ডেটায় লিস্ট বা জব অ্যারে থাকে
                    items = data.get("data") or data.get("jobs") or data.get("d") or data
                    if isinstance(items, str):
                        items = json.loads(items)
                    if isinstance(items, list) and len(items) > 0:
                        print(f"--> [INTERCEPTED] Found {len(items)} items from URL: {response.url[:60]}")
                        captured_jobs.extend(items)
                except Exception:
                    pass

        page.on("response", handle_response)

        print("Navigating to BDJobs...")
        await page.goto("https://jobs.bdjobs.com/jobsearch.asp?fcatId=8", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        print(f"Total raw items intercepted: {len(captured_jobs)}")
        if captured_jobs:
            print("First item sample:", captured_jobs[0])

        await browser.close()

asyncio.run(run())
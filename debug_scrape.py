import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # headless=False দিলে আপনার সামনে ক্রোম ব্রাউজার ওপেন হবে এবং দেখতে পাবেন বিডিজবস কী দেখাচ্ছে
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        print("Navigating to BDJobs...")
        await page.goto("https://jobs.bdjobs.com/jobsearch.asp?fcatId=8", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # পেজের আসল স্ক্রিনশট সেভ করা
        await page.screenshot(path="bdjobs_debug.png")
        print("Screenshot saved to bdjobs_debug.png")
        await browser.close()

asyncio.run(run())
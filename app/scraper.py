import asyncio
from typing import List, Dict
from playwright.sync_api import sync_playwright

# BDJobs-er shob verified live categories ebong tader URL
ALL_BDJOBS_CATEGORIES = {
    "Accounting & Finance": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=1",
    "Bank & Non-Bank Fin.": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=2",
    "Supply Chain & Procurement": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=3",
    "Education & Training": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=4",
    "Engineer & Architects": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=5",
    "Garments & Textile": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=6",
    "HR & Org. Development": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=7",
    "IT & Telecommunication": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=8",
    "Marketing & Sales": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=9",
    "Media & Journalism": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=11",
    "Medical & Pharma": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=12",
    "NGO & Development": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=13",
    "Research & Consultancy": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=14",
    "Secretary & Receptionist": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=15",
    "Data Entry & Operator": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=16",
    "Customer Service & Call Centre": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=17",
    "Design & Creative": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=19",
    "Hospitality & Tourism": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=25",
    "Beauty Care & Health": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=26",
    "Security & Support Service": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=27",
    "Law & Legal": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=28",
    "Govt & Public Service": "https://jobs.bdjobs.com/jobsearch.asp?fcatId=36",
}

def _scrape_all_categories_sync() -> List[Dict]:
    all_jobs = []
    seen_ids = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        for cat_name, url in ALL_BDJOBS_CATEGORIES.items():
            category_items = []

            def on_response(response):
                if "GetJobSearch" in response.url and response.status == 200:
                    try:
                        data = response.json()
                        items = data.get("data") if isinstance(data, dict) and "data" in data else data
                        if isinstance(items, list):
                            category_items.extend(items)
                    except Exception:
                        pass

            page.on("response", on_response)

            try:
                print(f"--> [BROWSER] Intercepting live circulars for {cat_name}...")
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)

                cat_count = 0
                for itm in category_items:
                    if not isinstance(itm, dict):
                        continue

                    job_id = str(itm.get("Jobid") or itm.get("jobid") or "")
                    title = str(itm.get("jobTitle") or itm.get("JobTitle") or "").strip()
                    company = str(itm.get("companyName") or itm.get("CompanyName") or "Confidential").strip()
                    deadline = str(itm.get("deadline") or "Check Circular").strip()

                    if job_id and title and job_id not in seen_ids:
                        seen_ids.add(job_id)
                        all_jobs.append({
                            "job_id": job_id,
                            "title": title,
                            "company_name": company,
                            "deadline": deadline,
                            "job_url": f"https://bdjobs.com/h/details/{job_id}?ln=1",
                            "category": cat_name
                        })
                        cat_count += 1

                print(f"--> [CAPTURED] {cat_count} jobs from {cat_name}")

            except Exception as err:
                print(f"--> [ERROR] {cat_name}: {err}")

        browser.close()

    return all_jobs


class BDJobsScraper:
    async def get_latest_jobs(self) -> List[Dict]:
        print("--> [SCRAPER] Starting multi-category sync worker...")
        return await asyncio.to_thread(_scrape_all_categories_sync)
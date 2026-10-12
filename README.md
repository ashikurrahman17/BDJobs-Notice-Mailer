# **BDJobs Notice Mailer & Real-time Alert System**

An automated background scraping, filtering, and notification engine designed to keep job seekers informed about the latest circulars on BDJobs without the manual hassle of daily browsing.

---

## **Project Overview**

The BDJobs Notice Mailer & Real-time Alert System continuously monitors BDJobs—Bangladesh's largest job portal—for new job listings. It automatically scrapes newly posted circulars, categorizes them according to specialized criteria (such as Experience Level, Industry, and Location), matches them against active user subscriptions, and dispatches instant, personalized email notifications.

By shifting from manual search to an event-driven alert model, the system ensures candidates never miss urgent opportunities or tight application windows.

---

## **Problem & Use Case**

### **The Problem**

- **Tight Application Windows**: Popular job circulars often have short application lifespans, causing candidates to miss deadlines due to infrequent manual portal checks.
- **Information Overload**: BDJobs hosts thousands of listings across disparate categories. Browsing through irrelevant postings to find entry-level or specific niche roles is time-consuming and inefficient.
- **Lack of Granular Alerts**: Built-in portal notifications are often generic, delayed, or fail to filter precisely for specific criteria like "Fresher / Entry Level" or localized region preferences.

### **The Solution**

- **Automated Scraper**: Runs scheduled background tasks to ingest new job postings within minutes of publication.
- **Targeted Keyword & Category Subscriptions**: Users receive alerts *only* for the specific job titles, experience levels, or departments they care about.
- **Real-time Delivery**: Direct HTML-formatted email digests straight to the user's inbox with direct application links.

---

## **Key Features**

- **Secure OTP Authentication**: Account registration and email verification utilizing time-based One-Time Passwords (OTP) to prevent fake subscriptions.
- **Personalized Preference Engine**: Users can curate custom subscription criteria based on keywords (e.g., "Software Engineer", "Marketing"), job type ("Entry Level", "Mid Level"), and location constraints.
- **Instant Email Alerts**: Rich HTML emails containing key details: job title, company name, experience requirement, location, posting date, and direct application link.
- **Advanced Query Filtering**: Built-in REST API parameters to slice listings by dynamic criteria including deadlines, required skill sets, and company type.
- **Automated Background Scheduler**: Powered by APScheduler to handle task execution for routine scraping, data parsing, and bulk mail queue processing without blocking API threads.

---

## **Technical Challenges & Web Scraping Observations**

Scraping BDJobs presents several structural and anti-scraping challenges. The table below outlines these obstacles and the technical mitigations implemented within this architecture:

| Challenge / Observation | Technical Impact | Engineering Solution |
| :---- | :---- | :---- |
| **Dynamic DOM Classes** | CSS class names and layout wrappers change periodically or vary across different job categories. | Implemented resilient fallback parsing strategies relying on structural DOM relationships, relative XPath, and normalized text attributes rather than volatile class names. |
| **Anti-Bot & Rate Limiting** | Rapid repetitive requests trigger HTTP 429/403 responses or IP throttling. | Configured user-agent rotation, randomized delay intervals between pagination requests, and session pooling using `httpx`. |
| **Inconsistent HTML Structure** | Hot Jobs, Featured Listings, and Standard Listings render completely different markup structures. | Created polymorphic parser engines that detect listing types via content signatures and apply tailored parsing pipelines per listing wrapper. |
| **Complex Pagination Handling** | Deep pagination uses asynchronous JS calls and dynamic URL parameters. | Intercepted underlying XHR/JSON API endpoints where accessible; implemented headless browser execution (Playwright/Selenium fallback) for JavaScript-heavy rendering. |
| **Unstructured Deadline Text** | Deadline formats vary across listings (e.g., "30 Nov 2024", "Apply within 5 days", "Extended"). | Developed custom regex patterns and date-parsing modules to standardize all deadlines into UTC ISO timestamps for unified database filtering. |

---

## **Technology Stack**

- **Backend Framework**: FastAPI (Python 3.10+)
- **Database & ORM**: PostgreSQL (hosted on Neon) with SQLAlchemy ORM
- **Task Scheduling**: APScheduler (Advanced Python Scheduler)
- **Web Scraping**: BeautifulSoup4, `httpx`, and Playwright (for dynamic rendering)
- **Frontend Templates**: HTML5, Tailwind CSS, Chart.js (for user dashboard metrics)
- **Authentication**: JWT (JSON Web Tokens) & Passlib (Bcrypt hashing)
- **Email Infrastructure**: SMTP with Jinja2 HTML email templating

---

## **System Architecture**

```
                                  +-----------------------+
                                  |     BDJobs Portal     |
                                  +-----------+-----------+
                                              |
                                      [ Scheduled Scrape ]
                                              v
+-------------------+             +-----------+-----------+
|   APScheduler     |------------>|   Scraper Pipeline    |
| (Background Task) |             | (BS4 / Playwright)    |
+-------------------+             +-----------+-----------+
                                              |
                                     [ Parsed Job Items ]
                                              v
+-------------------+             +-----------+-----------+             +-------------------+
|  PostgreSQL/Neon  |<----------->|  FastAPI Service Layer |<----------->| User Dashboard UI |
|    (Database)     |             +-----------+-----------+             +-------------------+
+-------------------+                         |
                                      [ Subscription Match ]
                                              v
                                  +-----------+-----------+
                                  |    SMTP Mail Queue    |
                                  +-----------+-----------+
                                              |
                                      [ HTML Email Alert ]
                                              v
                                  +-----------+-----------+
                                  |     End User Inbox    |
                                  +-----------------------+
```

---

## **Project Structure**

```
bdjobs-notice-mailer/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── jobs.py
│   │       │   ├── subscriptions.py
│   │       │   └── scraper.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── job.py
│   │   └── subscription.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── job.py
│   │   └── email.py
│   ├── services/
│   │   ├── scraper_engine.py
│   │   ├── mailer.py
│   │   └── matcher.py
│   ├── static/
│   ├── templates/
│   │   ├── dashboard.html
│   │   └── email_alert.html
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## **Environment Variables Setup**

Create a `.env` file in the root directory by copying `.env.example`:

```env
# Server Configuration
PROJECT_NAME="BDJobs Notice Mailer"
API_V1_STR="/api/v1"
SECRET_KEY="your-super-secret-key-change-this-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Database Settings (PostgreSQL/Neon)
DATABASE_URL="postgresql://user:password@ep-cool-service-123456.eastus2.azure.neon.tech/bdjobs_db?sslmode=require"

# SMTP Email Configuration
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-specific-password"
EMAILS_FROM_EMAIL="your-email@gmail.com"
EMAILS_FROM_NAME="BDJobs Alert System"

# Scheduler Settings
SCRAPER_INTERVAL_HOURS=2
```

---

## **Running Locally**

Follow these step-by-step commands to set up and run the application on a new machine.

### **Prerequisites**

- Python 3.10 or higher
- Git
- PostgreSQL Database (or Neon DB URI)

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/your-username/bdjobs-notice-mailer.git
cd bdjobs-notice-mailer
```

### **Step 2: Set Up Virtual Environment**

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### **Step 3: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

### **Step 4: Configure Environment Variables**

```bash
cp .env.example .env
# Edit .env file with your database URI and SMTP credentials
```

### **Step 5: Initialize Database & Run Server**

```bash
# Start the FastAPI application with Uvicorn
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### **Step 6: Access the webpage in the browswer**

```bash
http://127.0.0.1:8000
```

Access the interactive API documentation at `http://127.0.0.1:8000/docs`.

---

## **REST API Endpoints**

| Method | Endpoint | Description | Access Level |
| :---- | :---- | :---- | :---- |
| `POST` | `/api/v1/auth/register` | Register new user & send OTP verification email | Public |
| `POST` | `/api/v1/auth/verify-otp` | Validate registration OTP code | Public |
| `POST` | `/api/v1/auth/login` | Authenticate user & return JWT token | Public |
| `GET` | `/api/v1/jobs` | Retrieve paginated job listings with keyword/location filters | Authenticated |
| `GET` | `/api/v1/jobs/{id}` | Get detailed information for a specific job circular | Authenticated |
| `POST` | `/api/v1/subscriptions` | Create or update user job alert preferences | Authenticated |
| `GET` | `/api/v1/subscriptions/me` | Fetch active subscriptions for current user | Authenticated |
| `POST` | `/api/v1/trigger-scrape` | Manually invoke scraping engine (Admins only) | Admin |
| `GET` | `/api/v1/health` | System diagnostics and database connection health check | Public |

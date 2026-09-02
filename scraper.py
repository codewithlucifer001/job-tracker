import os
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# 50 Globally Trending Job & Tech Platforms (RSS / Public Endpoints)
PLATFORMS_FEED_URLS = [
    "https://weworkremotely.com/remote-jobs.rss",
    "https://remote.co/remote-jobs/feed/",
    "https://jobicy.com/feed/",
    "https://himalayas.com/jobs.rss",
    "https://4dayweek.io/remote-engineering-jobs.rss",
    "https://www.flexjobs.com/rss",
    "https://justremote.co/remote-jobs.rss",
    "https://nodesk.co/remote-jobs/feed/",
    "https://www.workingnomads.com/jobs/rss",
    "https://www.remotively.com/feed",
    "https://stackoverflow.com/jobs/feed",
    "https://news.ycombinator.com/rss",
    "https://builtins.com/rss/jobs",
    "https://www.dice.com/jobs/feed",
    "https://www.builtinnyc.com/jobs/rss",
    "https://www.builtinseattle.com/jobs/rss",
    "https://www.builtinla.com/jobs/rss",
    "https://www.builtinboston.com/jobs/rss",
    "https://www.builtincolorado.com/jobs/rss",
    "https://www.builtinaustin.com/jobs/rss",
    "https://wellfound.com/jobs.rss",
    "https://angel.co/jobs.rss",
    "https://startup.jobs/feed",
    "https://remoteok.com/api",
    "https://www.workatastartup.com/jobs.rss",
    "https://ycombinator.com/jobs/rss",
    "https://www.techstars.com/jobs.rss",
    "https://www.adzuna.com/land/a/rss",
    "https://www.glassdoor.com/feed/jobs.rss",
    "https://www.ziprecruiter.com/jobs/rss",
    "https://arc.dev/remote-jobs/rss",
    "https://turing.com/jobs/rss",
    "https://braintrust.dev/jobs/rss",
    "https://gun.io/jobs/rss",
    "https://www.topcoder.com/feed",
    "https://freelancermap.com/feed/jobs.rss",
    "https://www.upwork.com/ab/feed/jobs/rss",
    "https://www.guru.com/g/jobs/rss",
    "https://www.peopleperhour.com/feed/jobs.rss",
    "https://www.SimplyHired.com/rss",
    "https://www.monster.com/jobs/rss",
    "https://www.careerbuilder.com/jobs/rss",
    "https://www.themuse.com/api/v2/jobs?page=1",
    "https://www.simplyhired.com/search?q=software+engineer&rss=true",
    "https://www.dice.com/jobs?q=developer&rss=true",
    "https://www.getonbrd.com/feed.rss",
    "https://www.workingnomads.com/api/exposed_jobs/",
    "https://www.idealist.org/en/jobs.rss",
    "https://www.AuthenticJobs.com/rss",
    "https://www.crunchboard.com/jobs.rss"
]

def send_discord_alert(job_title, job_url):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Discord webhook URL missing.")
        return
    
    payload = {
        "content": f"🚨 **New Remote Job Alert!**\n**Title:** {job_title}\n**Link:** {job_url}"
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print(f"Discord alert sent successfully for: {job_title}")
        else:
            print(f"Failed to send Discord alert: {response.text}")
    except Exception as e:
        print(f"Error sending Discord message: {e}")

def run_pipeline():
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI is not set.")
        return

    client = MongoClient(mongo_uri)
    db = client["job_tracker_db"]
    jobs_collection = db["listings"]
    jobs_collection.create_index("url", unique=True)

    new_jobs_found = 0
    print("Checking 50 global platforms for new remote job opportunities...")
    
    for url in PLATFORMS_FEED_URLS:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            for item in items[:5]:
                title = item.title.text if item.title else "Software Role"
                link = item.link.text if item.link else url
                
                job_doc = {
                    "title": title,
                    "url": link,
                    "source": url
                }
                
                try:
                    jobs_collection.insert_one(job_doc)
                    new_jobs_found += 1
                    print(f"New Job Added: {title}")
                    send_discord_alert(title, link)
                except Exception:
                    pass
        except Exception:
            continue

    print(f"Job scanning complete. Total new listings added: {new_jobs_found}")

if __name__ == "__main__":
    run_pipeline()
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import db
import site_finder
import email_sender


def send_daily():
    liked = db.get_liked_sites()
    disliked = db.get_disliked_sites()
    sent = db.get_all_urls()

    try:
        site = site_finder.find_new_site(liked, disliked, sent)
    except Exception as e:
        print(f"[parrticles] site_finder error: {e}", flush=True)
        return

    site_id = db.record_sent(site["url"], site["title"], site["description"])

    try:
        email_sender.send_daily_email(
            to=os.environ["TO_EMAIL"],
            site_id=site_id,
            url=site["url"],
            title=site["title"],
            description=site["description"],
        )
        print(f"[parrticles] sent site #{site_id}: {site['url']}", flush=True)
    except Exception as e:
        print(f"[parrticles] email error: {e}", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()

    hour = int(os.environ.get("SEND_HOUR_UTC", "9"))
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily, CronTrigger(hour=hour, minute=0, timezone="UTC"))
    scheduler.start()
    print(f"[parrticles] scheduler running — daily at {hour:02d}:00 UTC", flush=True)

    yield

    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/feedback", response_class=HTMLResponse)
def feedback(id: int = Query(...), response: str = Query(...)):
    if response not in ("yes", "no"):
        raise HTTPException(status_code=400, detail="Invalid response")

    db.record_feedback(id, response)

    if response == "yes":
        message = "Glad you liked it. Tomorrow will bring something similar."
        symbol = "&#10003;"
    else:
        message = "Noted. Tomorrow will be something completely different."
        symbol = "&#10007;"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>parrticles</title>
  <style>
    body {{
      font-family: 'Courier New', Courier, monospace;
      background: #080808;
      color: #d8d8d8;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }}
    .inner {{ text-align: center; }}
    .sym {{ font-size: 40px; color: #fff; margin-bottom: 20px; }}
    p {{ font-size: 13px; color: #666; letter-spacing: 0.04em; }}
  </style>
</head>
<body>
  <div class="inner">
    <div class="sym">{symbol}</div>
    <p>{message}</p>
  </div>
</body>
</html>"""


@app.get("/history", response_class=HTMLResponse)
def history():
    sites = db.get_history()
    rows = ""
    for s in sites:
        fb = s.get("feedback") or "<span style='color:#444'>pending</span>"
        rows += (
            f"<tr>"
            f"<td>{s['sent_at'][:10]}</td>"
            f"<td><a href='{s['url']}'>{s['title']}</a></td>"
            f"<td>{fb}</td>"
            f"</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>parrticles / history</title>
  <style>
    body {{ font-family: 'Courier New', Courier, monospace; background: #080808; color: #d8d8d8; padding: 40px 32px; }}
    h1 {{ font-size: 16px; font-weight: normal; color: #fff; margin-bottom: 32px; letter-spacing: 0.05em; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 700px; }}
    th {{ text-align: left; font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: #555; padding: 0 20px 10px 0; border-bottom: 1px solid #1e1e1e; }}
    td {{ padding: 10px 20px 10px 0; border-bottom: 1px solid #111; font-size: 13px; }}
    a {{ color: #aaa; text-decoration: none; }}
    a:hover {{ color: #fff; }}
  </style>
</head>
<body>
  <h1>parrticles / history</h1>
  <table>
    <thead><tr><th>Date</th><th>Site</th><th>Feedback</th></tr></thead>
    <tbody>{rows or '<tr><td colspan="3" style="color:#333; padding-top:20px">nothing sent yet</td></tr>'}</tbody>
  </table>
</body>
</html>"""


@app.get("/send-now")
def send_now():
    """Manual trigger — useful for testing deployment."""
    send_daily()
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

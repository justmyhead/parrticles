import os
import resend


def send_daily_email(to: str, site_id: int, url: str, title: str, description: str):
    app_url = os.environ["APP_URL"].rstrip("/")
    yes_link = f"{app_url}/feedback?id={site_id}&response=yes"
    no_link = f"{app_url}/feedback?id={site_id}&response=no"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Today's site</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Courier New', Courier, monospace;
      background: #080808;
      color: #d8d8d8;
      padding: 48px 24px;
    }}
    .wrap {{ max-width: 520px; margin: 0 auto; }}
    .eyebrow {{
      font-size: 10px;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      color: #555;
      margin-bottom: 12px;
    }}
    h1 {{
      font-size: 30px;
      font-weight: normal;
      color: #ffffff;
      line-height: 1.2;
      margin-bottom: 6px;
    }}
    .url {{
      font-size: 12px;
      color: #555;
      margin-bottom: 28px;
      word-break: break-all;
    }}
    .url a {{ color: #555; text-decoration: none; }}
    .desc {{
      font-size: 14px;
      line-height: 1.7;
      color: #aaa;
      margin-bottom: 36px;
    }}
    .open {{
      display: inline-block;
      background: #ffffff;
      color: #000000;
      padding: 13px 26px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 12px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      text-decoration: none;
      margin-bottom: 52px;
    }}
    .feedback-label {{
      font-size: 10px;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: #444;
      margin-bottom: 14px;
    }}
    .btns {{ display: flex; gap: 10px; }}
    .btn {{
      padding: 11px 20px;
      border: 1px solid #333;
      background: #111;
      color: #ccc;
      font-family: 'Courier New', Courier, monospace;
      font-size: 12px;
      letter-spacing: 0.06em;
      text-decoration: none;
    }}
    .foot {{
      margin-top: 64px;
      font-size: 10px;
      color: #333;
      letter-spacing: 0.1em;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="eyebrow">Today's site</div>
    <h1>{title}</h1>
    <div class="url"><a href="{url}">{url}</a></div>
    <div class="desc">{description}</div>
    <a class="open" href="{url}" target="_blank">Open it &rarr;</a>

    <div class="feedback-label">Was it good?</div>
    <div class="btns">
      <a class="btn" href="{yes_link}">Yes, more like this</a>
      <a class="btn" href="{no_link}">No, try again</a>
    </div>

    <div class="foot">parrticles &middot; daily design</div>
  </div>
</body>
</html>"""

    resend.api_key = os.environ["RESEND_API_KEY"]
    resend.Emails.send({
        "from": os.environ.get("FROM_EMAIL", "parrticles <daily@parrticles.com>"),
        "to": [to],
        "subject": f"Today's site: {title}",
        "html": html,
    })

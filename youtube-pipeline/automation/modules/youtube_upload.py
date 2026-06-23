"""
Module 7 — YouTube Upload
YouTube Data API v3 → upload video + schedule publication
"""

import os, json, datetime, pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "youtube_token.pickle")

def get_youtube_client():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secrets_file = os.environ.get("YOUTUBE_CLIENT_SECRETS", "client_secrets.json")
            flow = InstalledAppFlow.from_client_secrets_file(secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(video: dict, seo: dict, thumbnail: dict, config: dict) -> dict:
    youtube   = get_youtube_client()
    ycfg      = config["youtube"]
    sched_cfg = config["channel"]["publish_schedule"]

    # Schedule: next Tuesday or Friday at 14h EST
    publish_at = _next_publish_time(sched_cfg["days"], sched_cfg["hour_est"])

    title       = seo.get("optimized_title", "BodyTruth Video")[:100]
    description = seo.get("description", "")[:5000]
    tags        = seo.get("tags", [])[:25]

    body = {
        "snippet": {
            "title":       title,
            "description": description,
            "tags":        tags,
            "categoryId":  ycfg["category_id"],
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus":           "private" if ycfg["privacy"] == "private" else "public",
            "publishAt":               publish_at.isoformat() + "Z",
            "selfDeclaredMadeForKids": ycfg["made_for_kids"],
            "madeForKids":             ycfg["made_for_kids"],
        }
    }

    if ycfg.get("ai_disclosure"):
        body["status"]["containsSyntheticMedia"] = True

    print(f"[youtube_upload] Uploading: {title}")
    print(f"[youtube_upload] Scheduled for: {publish_at}")

    media = MediaFileUpload(
        video["filepath"],
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 10  # 10MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"[youtube_upload] Uploading... {pct}%")

    video_id = response["id"]
    print(f"[youtube_upload] Uploaded → https://youtu.be/{video_id}")

    # Upload thumbnail
    if thumbnail and os.path.exists(thumbnail.get("filepath", "")):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail["filepath"], mimetype="image/jpeg")
        ).execute()
        print(f"[youtube_upload] Thumbnail set")

    return {
        "video_id":  video_id,
        "url":       f"https://youtu.be/{video_id}",
        "title":     title,
        "scheduled": publish_at.isoformat()
    }


def _next_publish_time(days: list, hour_est: int) -> datetime.datetime:
    day_map = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,
               "friday":4,"saturday":5,"sunday":6}
    target_days = [day_map[d] for d in days]

    # EST = UTC-5
    now_utc = datetime.datetime.utcnow()
    now_est = now_utc - datetime.timedelta(hours=5)

    for offset in range(1, 8):
        candidate = now_est + datetime.timedelta(days=offset)
        if candidate.weekday() in target_days:
            publish_est = candidate.replace(hour=hour_est, minute=0, second=0, microsecond=0)
            publish_utc = publish_est + datetime.timedelta(hours=5)
            return publish_utc

    return now_utc + datetime.timedelta(days=3)

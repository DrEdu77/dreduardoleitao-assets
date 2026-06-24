"""
Module 3b — Video Clip Fetching
Pexels Videos API → download MP4 clips per chapter keyword (replaces image fetch)
"""

import os, requests, time
from modules.image_fetch import KEYWORDS_BY_CHANNEL, KEYWORDS_FALLBACK

PEXELS_VIDEO_API = "https://api.pexels.com/videos/search"

CLIPS_PER_CHAPTER = 15   # ~15 clips × 9 chapters = 135 clips total
MAX_CLIP_SECONDS  = 20   # cap each clip at 20s (avoid very long clips)
MIN_CLIP_SECONDS  = 3    # skip clips shorter than 3s


def fetch_video_clips(script: dict, config: dict) -> dict:
    api_key     = os.environ["PEXELS_API_KEY"]
    slug        = script["slug"]
    channel_key = config["channel"]["name"].lower().replace(" ", "")

    keywords_map = KEYWORDS_BY_CHANNEL.get(channel_key, KEYWORDS_FALLBACK)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "clips", slug)
    os.makedirs(out_dir, exist_ok=True)

    downloaded  = []
    clip_index  = 0
    headers     = {"Authorization": api_key}

    for chapter_num, keywords in keywords_map.items():
        chapter_clips = 0

        for keyword in keywords:
            if chapter_clips >= CLIPS_PER_CHAPTER:
                break

            print(f"[clip_fetch] Chapter {chapter_num} — '{keyword}'...")
            params = {"query": keyword, "per_page": 10, "orientation": "landscape"}

            try:
                resp = requests.get(PEXELS_VIDEO_API, headers=headers,
                                    params=params, timeout=15)
                resp.raise_for_status()
                videos = resp.json().get("videos", [])
            except Exception as e:
                print(f"[clip_fetch] Warning: {e}")
                continue

            for video in videos:
                if chapter_clips >= CLIPS_PER_CHAPTER:
                    break

                duration = video.get("duration", 0)
                if duration < MIN_CLIP_SECONDS or duration > 60:
                    continue

                # Prefer HD (≥1280px wide), fall back to SD
                files = video.get("video_files", [])
                hd = [f for f in files
                      if f.get("quality") == "hd" and (f.get("width") or 0) >= 1280]
                sd = [f for f in files
                      if f.get("quality") == "sd" and (f.get("width") or 0) >= 640]
                best = (hd or sd or [None])[0]
                if not best:
                    continue

                filename = f"{clip_index:04d}-ch{chapter_num:02d}-{video['id']}.mp4"
                filepath = os.path.join(out_dir, filename)

                if not os.path.exists(filepath):
                    try:
                        r = requests.get(best["link"], timeout=90, stream=True)
                        r.raise_for_status()
                        with open(filepath, "wb") as f:
                            for chunk in r.iter_content(chunk_size=65536):
                                f.write(chunk)
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"[clip_fetch] Download failed: {e}")
                        continue

                downloaded.append({
                    "path":     filepath,
                    "chapter":  chapter_num,
                    "index":    clip_index,
                    "duration": min(duration, MAX_CLIP_SECONDS),
                    "width":    best.get("width", 1280),
                    "height":   best.get("height", 720),
                })
                clip_index    += 1
                chapter_clips += 1
                print(f"[clip_fetch]   {filename} ({duration}s)")

    total_secs = sum(c["duration"] for c in downloaded)
    print(f"[clip_fetch] Done — {len(downloaded)} clips, "
          f"~{total_secs/60:.1f} min raw footage → {out_dir}")
    return {
        "clips":          downloaded,
        "directory":      out_dir,
        "count":          len(downloaded),
        "total_duration": total_secs,
    }

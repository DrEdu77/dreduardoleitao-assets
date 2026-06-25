"""
Module 3c — Pixabay Video Clip Fetching
Pixabay Videos API → download MP4 clips with REAL soccer gameplay footage
Much better than Pexels for sports-specific content.

API docs: https://pixabay.com/api/docs/#api_videos
Free tier: 100 requests/hour, up to 200 results per page
"""

import os, requests, time

PIXABAY_VIDEO_API = "https://pixabay.com/api/videos/"

CLIPS_PER_CHAPTER = 12
MAX_CLIP_SECONDS  = 30
MIN_CLIP_SECONDS  = 4

# Soccer-specific keywords per chapter — guaranteed soccer content
# Uses Pixabay's sports category for extra precision
SOCCER_KEYWORDS = {
    # Hook — Copa do Mundo, estádio lotado, troféu FIFA
    0: ["soccer world cup stadium", "soccer trophy cup", "soccer fans celebration"],
    # GOAT debate / Messi — jogadas, Argentina, drible
    1: ["soccer player dribbling", "soccer argentina", "soccer goal kick"],
    # Pelé / Brasil — futebol clássico, jogador brasileiro, campo verde
    2: ["soccer brazil", "soccer player running ball", "soccer match play"],
    # Copa do Mundo — finais, gols históricos, comemorações épicas
    3: ["soccer world cup", "soccer goal celebration", "soccer championship"],
    # Gols e recordes — jogadas espetaculares, chutes, defesas
    4: ["soccer goal score", "soccer penalty kick", "soccer goalkeeper save"],
    # Pelé no Cosmos / USA — soccer americano, estádio EUA, torcida americana
    5: ["soccer USA", "soccer stadium crowd", "soccer match game"],
    # Debate GOAT — troféus, comparativo, análise, estatísticas
    6: ["soccer trophy award", "soccer player celebration", "soccer win champion"],
    # Torcida / emoção — fãs apaixonados, bandeiras, festa nas arquibancadas
    7: ["soccer fans cheering", "soccer crowd stadium", "soccer supporters flags"],
    # Conclusão / próxima geração — crianças, futuro, sonho
    8: ["children playing soccer", "kids soccer field", "youth soccer training"],
}


def fetch_pixabay_clips(script: dict, config: dict) -> dict:
    api_key     = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        raise RuntimeError("PIXABAY_API_KEY not set in .env")

    slug        = script["slug"]
    channel_key = config["channel"]["name"].lower().replace(" ", "")

    # Use channel-specific keywords if defined, else soccer defaults
    from modules.image_fetch import KEYWORDS_BY_CHANNEL
    channel_kw = KEYWORDS_BY_CHANNEL.get(channel_key, {})

    # Build keyword map — prefer SOCCER_KEYWORDS for soccertruth
    if channel_key == "soccertruth":
        keywords_map = SOCCER_KEYWORDS
    else:
        # Convert image_fetch keywords to Pixabay-friendly terms
        keywords_map = channel_kw if channel_kw else SOCCER_KEYWORDS

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "clips", slug)
    os.makedirs(out_dir, exist_ok=True)

    downloaded = []
    clip_index = 0

    for chapter_num, keywords in keywords_map.items():
        chapter_clips = 0

        for keyword in keywords:
            if chapter_clips >= CLIPS_PER_CHAPTER:
                break

            print(f"[pixabay_fetch] Chapter {chapter_num} — '{keyword}'...")

            params = {
                "key":       api_key,
                "q":         keyword,
                "video_type":"film",       # real footage, not animation
                "category":  "sports",     # sports category for soccer precision
                "per_page":  15,
                "safesearch":"true",
                "order":     "popular",
            }

            try:
                resp = requests.get(PIXABAY_VIDEO_API, params=params, timeout=15)
                resp.raise_for_status()
                hits = resp.json().get("hits", [])
            except Exception as e:
                print(f"[pixabay_fetch] Warning: {e}")
                # Retry without category filter
                try:
                    params.pop("category", None)
                    resp = requests.get(PIXABAY_VIDEO_API, params=params, timeout=15)
                    resp.raise_for_status()
                    hits = resp.json().get("hits", [])
                except Exception as e2:
                    print(f"[pixabay_fetch] Retry failed: {e2}")
                    continue

            for hit in hits:
                if chapter_clips >= CLIPS_PER_CHAPTER:
                    break

                duration = hit.get("duration", 0)
                if duration < MIN_CLIP_SECONDS or duration > 90:
                    continue

                # Prefer large (HD), fall back to medium
                videos = hit.get("videos", {})
                large  = videos.get("large", {})
                medium = videos.get("medium", {})
                small  = videos.get("small", {})

                best = None
                for quality in [large, medium, small]:
                    if quality.get("url") and quality.get("width", 0) >= 640:
                        best = quality
                        break

                if not best:
                    continue

                use_secs = min(duration, MAX_CLIP_SECONDS)
                filename = f"{clip_index:04d}-ch{chapter_num:02d}-pb{hit['id']}.mp4"
                filepath = os.path.join(out_dir, filename)

                if not os.path.exists(filepath):
                    try:
                        r = requests.get(best["url"], timeout=90, stream=True)
                        r.raise_for_status()
                        with open(filepath, "wb") as f:
                            for chunk in r.iter_content(chunk_size=65536):
                                f.write(chunk)
                        time.sleep(0.4)
                    except Exception as e:
                        print(f"[pixabay_fetch] Download failed: {e}")
                        continue

                downloaded.append({
                    "path":     filepath,
                    "chapter":  chapter_num,
                    "index":    clip_index,
                    "duration": use_secs,
                    "width":    best.get("width", 1280),
                    "height":   best.get("height", 720),
                    "source":   "pixabay",
                })
                clip_index    += 1
                chapter_clips += 1
                print(f"[pixabay_fetch]   {filename} ({duration}s)")

    total_secs = sum(c["duration"] for c in downloaded)
    print(f"[pixabay_fetch] Done — {len(downloaded)} clips, "
          f"~{total_secs/60:.1f} min raw → {out_dir}")

    return {
        "clips":          downloaded,
        "directory":      out_dir,
        "count":          len(downloaded),
        "total_duration": total_secs,
    }

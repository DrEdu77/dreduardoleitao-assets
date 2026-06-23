"""
Module 3 — Image Fetching
Pexels API → download images per chapter keyword
"""

import os, requests, json, time

PEXELS_API = "https://api.pexels.com/v1/search"

CHAPTER_KEYWORDS = {
    0: ["spine xray", "human skeleton", "anatomy medical"],
    1: ["vertebrae anatomy", "spinal cord", "spine structure"],
    2: ["brain neurons", "nervous system", "nerve signals"],
    3: ["mri scan", "disc herniation", "spinal disc"],
    4: ["sitting desk posture", "back pain office", "sedentary lifestyle"],
    5: ["chronic pain", "doctor hospital", "back surgery"],
    6: ["phone neck pain", "screen time posture", "office ergonomics"],
    7: ["yoga movement", "exercise spine", "healthy posture"],
    8: ["nature peaceful", "body movement", "wellness health"]
}

def fetch_images(script: dict, config: dict) -> dict:
    api_key    = os.environ["PEXELS_API_KEY"]
    slug       = script["slug"]
    chapters   = script.get("chapters", [])
    per_page   = config["pexels"]["per_page"]
    total_imgs = config["video"]["images_per_video"]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "images", slug)
    os.makedirs(out_dir, exist_ok=True)

    per_chapter = max(per_page, total_imgs // max(len(CHAPTER_KEYWORDS), 1))
    downloaded  = []
    img_index   = 0

    headers = {"Authorization": api_key}

    for chapter_num, keywords in CHAPTER_KEYWORDS.items():
        for keyword in keywords:
            print(f"[image_fetch] Chapter {chapter_num} — '{keyword}'...")
            params = {
                "query":       keyword,
                "per_page":    per_page,
                "orientation": config["pexels"]["orientation"],
                "size":        config["pexels"]["size"]
            }
            try:
                resp = requests.get(PEXELS_API, headers=headers, params=params, timeout=15)
                resp.raise_for_status()
                photos = resp.json().get("photos", [])
            except Exception as e:
                print(f"[image_fetch] Warning: {e}")
                continue

            for photo in photos:
                url = photo["src"].get("large2x") or photo["src"]["large"]
                ext = ".jpg"
                filename = f"{img_index:04d}-ch{chapter_num:02d}-{photo['id']}{ext}"
                filepath = os.path.join(out_dir, filename)

                if not os.path.exists(filepath):
                    try:
                        img_data = requests.get(url, timeout=20).content
                        with open(filepath, "wb") as f:
                            f.write(img_data)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"[image_fetch] Download failed: {e}")
                        continue

                downloaded.append({"path": filepath, "chapter": chapter_num, "index": img_index})
                img_index += 1

            if img_index >= total_imgs:
                break
        if img_index >= total_imgs:
            break

    print(f"[image_fetch] Done — {len(downloaded)} images → {out_dir}")
    return {"images": downloaded, "directory": out_dir, "count": len(downloaded)}

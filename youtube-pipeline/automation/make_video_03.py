"""
make_video_03.py — SoccerTruth Draft 03
Mescla:
  1. Fotos CC-licensed de Pelé e Messi (Wikimedia Commons)
  2. Clips Pexels de "jogadas parecidas" e "sosias"
  3. Clips Pexels existentes do draft 02

Resultado: CapCut draft "03 SoccerTruth — Messi vs Pele..."
"""

import os, sys, requests, subprocess, time, shutil
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Config ──────────────────────────────────────────────────────────────────
BASE        = Path(__file__).parent
load_dotenv(BASE / ".env")

sys.path.insert(0, str(BASE))
from modules.capcut_gen import generate_capcut_project

CLIPS_02_DIR = BASE / "output" / "clips" / "messi-vs-pele-30-facts-nobody-tells-you-who-really-is-the-goat"
IMAGES_DIR   = BASE / "output" / "player_images"
CLIPS_03_DIR = BASE / "output" / "clips_03"
AUDIO_PATH   = str(next(
    (BASE / "output" / "audio" / "messi-vs-pele-30-facts-nobody-tells-you-who-really-is-the-goat").glob("*-full.mp3"),
    ""
))
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(CLIPS_03_DIR, exist_ok=True)

# ── 1. Wikimedia Commons — imagens CC de Pelé e Messi ──────────────────────

WIKIMEDIA_QUERIES = [
    ("pele",  "Pelé+footballer+Santos+Brazil",        8),
    ("messi", "Lionel+Messi+Argentina+footballer",    8),
]

WIKI_API     = "https://commons.wikimedia.org/w/api.php"
WIKI_HEADERS = {
    "User-Agent": "SoccerTruth/1.0 (YouTube faceless channel; ducoluna@gmail.com) python-requests/2.x"
}

# Categorias do Wikimedia Commons para busca por era/período
WIKIMEDIA_CATEGORIES = {
    "pele": [
        "Pelé",
        "Pelé at Santos FC",
        "Pelé at New York Cosmos",
        "Brazil at the 1970 FIFA World Cup",
        "Brazil at the 1966 FIFA World Cup",
        "Brazil at the 1958 FIFA World Cup",
    ],
    "messi": [
        "Lionel Messi",
        "Argentina at the 2022 FIFA World Cup",
        "Lionel Messi at the 2022 FIFA World Cup",
        "Argentina at the 2014 FIFA World Cup",
    ],
}

# Títulos de arquivo conhecidos (fallback extra) — URLs resolvidas via API
FALLBACK_FILE_TITLES = {
    "pele": [
        "File:Pelé (1958).jpg",
        "File:Pele 1977.jpg",
        "File:Pele with trophy.jpg",
        "File:Pelé no Santos.jpg",
        "File:Pele Brazil World Cup.jpg",
        "File:Edson Arantes do Nascimento - Pelé cropped.jpg",
        "File:Pele Cosmos.jpg",
        "File:New York Cosmos 1977.jpg",
    ],
    "messi": [],  # API já retorna bastante para Messi
}

def fetch_wikimedia_by_category(category: str, limit: int = 6) -> list[dict]:
    """Busca imagens de uma categoria Wikimedia Commons via API."""
    try:
        resp = requests.get(WIKI_API, params={
            "action":    "query",
            "generator": "categorymembers",
            "gcmtitle":  f"Category:{category}",
            "gcmtype":   "file",
            "gcmlimit":  limit * 3,
            "prop":      "imageinfo",
            "iiprop":    "url|extmetadata|size",
            "format":    "json",
        }, headers=WIKI_HEADERS, timeout=15)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
    except Exception as e:
        print(f"  [WARN] Categoria '{category}': {e}")
        return []

    images = []
    for page in pages.values():
        info_list = page.get("imageinfo", [])
        if not info_list:
            continue
        info      = info_list[0]
        url       = info.get("url", "")
        width     = info.get("width",  0)
        height    = info.get("height", 0)
        meta_data = info.get("extmetadata", {})
        license_s = meta_data.get("LicenseShortName", {}).get("value", "")

        if not any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
            continue

        ok_licenses = ["CC0", "CC BY", "CC-BY", "Public Domain", "PD"]
        is_free     = any(lic in license_s for lic in ok_licenses)

        if is_free and url and width >= 500:
            images.append({"url": url, "license": license_s, "width": width, "height": height})
        if len(images) >= limit:
            break

    return images

def resolve_file_url(file_title: str) -> str | None:
    """Resolve URL direta de um arquivo Wikimedia via API."""
    try:
        resp = requests.get(WIKI_API, params={
            "action":  "query",
            "titles":  file_title,
            "prop":    "imageinfo",
            "iiprop":  "url|size|extmetadata",
            "format":  "json",
        }, headers=WIKI_HEADERS, timeout=10)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info_list = page.get("imageinfo", [])
            if info_list:
                info  = info_list[0]
                url   = info.get("url", "")
                width = info.get("width", 0)
                if url and width >= 400:
                    return url
    except Exception:
        pass
    return None

def search_wikimedia_images(query: str, limit: int = 10) -> list[dict]:
    """Busca imagens CC-licensed no Wikimedia Commons."""
    # Step 1: busca títulos de arquivos
    try:
        resp = requests.get(WIKI_API, params={
            "action": "query",
            "list": "search",
            "srsearch": query.replace("+", " "),
            "srnamespace": "6",   # File namespace
            "srlimit": limit * 3,
            "format": "json",
        }, headers=WIKI_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [WARN] Wikimedia API erro: {e} — usando fallback hardcoded")
        return []
    results = resp.json().get("query", {}).get("search", [])

    images = []
    for r in results:
        title = r["title"]
        if not any(ext in title.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            continue

        # Step 2: busca URL e metadados de licença
        meta = requests.get(WIKI_API, params={
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size",
            "format": "json",
        }, headers=WIKI_HEADERS, timeout=15)
        meta.raise_for_status()
        pages = meta.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info_list = page.get("imageinfo", [])
            if not info_list:
                continue
            info = info_list[0]
            url  = info.get("url", "")
            meta_data = info.get("extmetadata", {})
            license_short = meta_data.get("LicenseShortName", {}).get("value", "")
            width  = info.get("width",  0)
            height = info.get("height", 0)

            # Aceita CC0, CC-BY, CC-BY-SA, Public Domain
            ok_licenses = ["CC0", "CC BY", "CC-BY", "Public Domain", "PD"]
            is_free = any(lic in license_short for lic in ok_licenses)
            is_big  = width >= 640 and height >= 400

            if is_free and is_big and url:
                images.append({
                    "title":   title,
                    "url":     url,
                    "license": license_short,
                    "width":   width,
                    "height":  height,
                })
                if len(images) >= limit:
                    break

        if len(images) >= limit:
            break
        time.sleep(0.3)

    return images


def download_image(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    try:
        r = requests.get(url, timeout=30, headers=WIKI_HEADERS)
        r.raise_for_status()
        # Verifica se é imagem válida
        if len(r.content) < 5000:
            print(f"  [WARN] Arquivo muito pequeno ({len(r.content)}b) — pulando")
            return False
        dest.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"  [WARN] Download falhou: {e}")
        return False


def image_to_video(img_path: Path, out_path: Path, duration: int = 4) -> bool:
    """Converte imagem em clip MP4 de N segundos com Ken Burns zoom-in."""
    if out_path.exists():
        return True
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(img_path),
        "-vf", (
            "scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,"
            f"zoompan=z='min(zoom+0.001,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={duration*25}:s=1920x1080,"
            "fps=25"
        ),
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    if result.returncode != 0:
        print(f"  [WARN] ffmpeg falhou: {result.stderr.decode('utf-8', errors='replace')[-200:]}")
        return False
    return True


# ── 2. Pexels — clips de "jogadas parecidas" e "sosias" ───────────────────

SIMILAR_PLAYS_KEYWORDS = [
    "soccer dribble skills close up",
    "soccer overhead bicycle kick",
    "soccer street football skills",
    "soccer freestyle football tricks",
    "soccer amazing goal celebration",
    "soccer penalty shootout dramatic",
    "soccer children prodigy skills",
    "soccer one man dribble",
]

PEXELS_VIDEO_API = "https://api.pexels.com/videos/search"

def fetch_pexels_similar(keywords: list[str], out_dir: Path, max_per_kw: int = 3) -> list[Path]:
    """Baixa clips Pexels de jogadas parecidas."""
    downloaded = []
    headers = {"Authorization": PEXELS_KEY}
    seen_ids = set()

    for kw in keywords:
        print(f"  [pexels] '{kw}'...")
        try:
            resp = requests.get(PEXELS_VIDEO_API, headers=headers, params={
                "query": kw,
                "per_page": 10,
                "orientation": "landscape",
            }, timeout=15)
            resp.raise_for_status()
            videos = resp.json().get("videos", [])
        except Exception as e:
            print(f"  [WARN] {e}")
            continue

        count = 0
        for v in videos:
            vid_id = v["id"]
            if vid_id in seen_ids:
                continue
            seen_ids.add(vid_id)

            # Pega melhor arquivo <= 1080p
            files = sorted(v.get("video_files", []),
                           key=lambda f: f.get("height", 0), reverse=True)
            best = next((f for f in files if f.get("height", 0) <= 1080
                         and f.get("file_type") == "video/mp4"), None)
            if not best:
                continue

            fname  = out_dir / f"similar-{vid_id}.mp4"
            if fname.exists():
                downloaded.append(fname)
                count += 1
            else:
                try:
                    r = requests.get(best["link"], timeout=60, stream=True)
                    r.raise_for_status()
                    with open(fname, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            f.write(chunk)
                    downloaded.append(fname)
                    count += 1
                    print(f"    → {fname.name}")
                except Exception as e:
                    print(f"  [WARN] {e}")

            if count >= max_per_kw:
                break
        time.sleep(0.5)

    return downloaded


# ── 3. Coleta clips 02 existentes (Pexels genéricos) ──────────────────────

def collect_02_clips() -> list[Path]:
    """Coleta clips MP4 do draft 02 (Pexels), excluindo yt-dlp e finale."""
    clips = sorted([
        p for p in CLIPS_02_DIR.glob("*.mp4")
        if "-yt" not in p.name and "FINALE" not in p.name.upper()
    ])
    print(f"  [02-clips] {len(clips)} clips Pexels encontrados")
    return clips


# ── 4. Monta lista intercalada ─────────────────────────────────────────────

def build_interleaved(player_clips: list[Path], similar_clips: list[Path],
                      base_clips: list[Path]) -> list[dict]:
    """
    Ordem: 2 base → 1 player → 1 similar → 2 base → 1 player → 1 similar → ...
    """
    result      = []
    p_idx       = 0
    s_idx       = 0
    b_idx       = 0
    base_total  = len(base_clips)
    cycle       = 0

    while b_idx < base_total or p_idx < len(player_clips):
        # 2 clips base
        for _ in range(2):
            if b_idx < base_total:
                p = base_clips[b_idx]
                result.append({"path": str(p), "duration": _probe_duration(p)})
                b_idx += 1

        # 1 clip de jogador real
        if p_idx < len(player_clips):
            p = player_clips[p_idx]
            result.append({"path": str(p), "duration": _probe_duration(p)})
            p_idx += 1

        # 1 clip jogada parecida
        if similar_clips:
            p = similar_clips[s_idx % len(similar_clips)]
            result.append({"path": str(p), "duration": _probe_duration(p)})
            s_idx += 1

        cycle += 1

    return result


def _probe_duration(p: Path) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
            capture_output=True, text=True, timeout=10
        )
        return float(r.stdout.strip()) if r.stdout.strip() else 5.0
    except Exception:
        return 5.0


# ── 5. Main ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print(" SOCCERTRUTH — Draft 03 (Wikimedia + Similar Plays + Pexels)")
    print("="*60 + "\n")

    # ── 1. Wikimedia images → video clips ──────────────────────────────────
    print("[STEP 1] Buscando fotos CC de Pelé e Messi no Wikimedia Commons...")
    player_clips = []

    for label, query, limit in WIKIMEDIA_QUERIES:
        print(f"\n  [busca texto] {label} — '{query}'")
        text_images = search_wikimedia_images(query, limit)
        print(f"  Encontradas via busca texto: {len(text_images)}")

        # Busca por categorias específicas (Santos, Cosmos, 1970, Argentina...)
        cat_images = []
        for cat in WIKIMEDIA_CATEGORIES.get(label, []):
            print(f"  [categoria] '{cat}'...")
            found = fetch_wikimedia_by_category(cat, limit=4)
            cat_images.extend(found)
            time.sleep(0.4)

        # Resolve file titles de fallback via API
        extra_urls = []
        for ftitle in FALLBACK_FILE_TITLES.get(label, []):
            url = resolve_file_url(ftitle)
            if url:
                extra_urls.append({"url": url, "license": "CC-resolved"})
            time.sleep(0.2)

        # Deduplica por URL
        seen_urls = set()
        all_images = []
        for img in (text_images + cat_images + extra_urls):
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                all_images.append(img)

        print(f"  Total único após dedup: {len(all_images)} imagens")

        for i, img in enumerate(all_images[:limit]):
            img_file = IMAGES_DIR / f"{label}-{i+1:02d}.jpg"
            vid_file = CLIPS_03_DIR / f"player-{label}-{i+1:02d}.mp4"

            lic = img.get("license", "?")
            print(f"  [{label}] {lic} — {img['url'].split('/')[-1][:55]}")
            if download_image(img["url"], img_file):
                if image_to_video(img_file, vid_file, duration=4):
                    player_clips.append(vid_file)
                    print(f"    ✅ {vid_file.name}")

    print(f"\n  Total clips de jogadores: {len(player_clips)}")

    # ── 2. Pexels — jogadas parecidas ──────────────────────────────────────
    print("\n[STEP 2] Baixando clips de jogadas parecidas (Pexels)...")
    similar_dir = CLIPS_03_DIR / "similar"
    os.makedirs(similar_dir, exist_ok=True)
    similar_clips = fetch_pexels_similar(SIMILAR_PLAYS_KEYWORDS, similar_dir, max_per_kw=3)
    print(f"  Total clips similares: {len(similar_clips)}")

    # ── 3. Clips 02 existentes ─────────────────────────────────────────────
    print("\n[STEP 3] Coletando clips Pexels do draft 02...")
    base_clips = collect_02_clips()

    # ── 4. Montar lista intercalada ────────────────────────────────────────
    print("\n[STEP 4] Montando lista intercalada...")
    all_clips = build_interleaved(player_clips, similar_clips, base_clips)
    total_dur = sum(c["duration"] for c in all_clips)
    print(f"  Total clips: {len(all_clips)} | Duração total: {total_dur/60:.1f} min")

    # ── 5. Gerar CapCut draft 03 ───────────────────────────────────────────
    print("\n[STEP 5] Gerando CapCut draft 03...")

    import subprocess as sp
    probe = sp.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", AUDIO_PATH],
        capture_output=True, text=True
    )
    audio_duration = float(probe.stdout.strip()) if probe.stdout.strip() else 1130.0

    script_obj = {
        "title": "Messi vs Pele: 30 Facts Nobody Tells You - Who Really Is The GOAT?",
        "slug":  "messi-vs-pele-30-facts-nobody-tells-you-who-really-is-the-goat",
        "text":  "", "word_count": 2785, "chapters": [], "timestamp": "20260629"
    }
    audio_obj = {
        "filepath": AUDIO_PATH,
        "duration": audio_duration,
        "chunks": []
    }
    clips_obj = {
        "clips":          all_clips,
        "count":          len(all_clips),
        "total_duration": total_dur,
        "directory":      str(CLIPS_03_DIR),
    }

    # Config soccertruth
    import json as _json
    with open(BASE / "config-soccertruth.json", encoding="utf-8") as f:
        config = _json.load(f)

    # Sobrescreve nome do draft para "03 SoccerTruth..."
    config["channel"]["name"] = "03 SoccerTruth"

    result = generate_capcut_project(script_obj, audio_obj, clips_obj, config)

    print("\n" + "="*60)
    print(f" DRAFT 03 PRONTO — '{result['draft_name']}'")
    print(f" Clips: {result['segments']} segmentos")
    print(" Abra o CapCut → draft '03 SoccerTruth' → Exportar")
    print("="*60 + "\n")


if __name__ == "__main__":
    if not AUDIO_PATH or not Path(AUDIO_PATH).exists():
        print("❌ Áudio não encontrado em output/audio/...")
        sys.exit(1)
    if not PEXELS_KEY:
        print("❌ PEXELS_API_KEY não encontrada no .env")
        sys.exit(1)
    main()

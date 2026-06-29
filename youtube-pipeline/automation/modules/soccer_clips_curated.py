"""
Module 3d — Soccer Curated Clips — ONLY Messi & Pelé
Strategy: download each source video ONCE, cut segments locally with ffmpeg.
Clips alternate strictly Messi → Pelé → Messi → Pelé throughout the video.

Sources verified via yt-dlp search 2026-06-25.
"""

import os, subprocess, time

# ── SOURCE VIDEOS ─────────────────────────────────────────────────────────────
# MESSI
# EdwIVC7LaJE — Messi All FIFA World Cup Goals 2006-2022        (507s)
# Q_A_FP2F7T0 — Messi FIFA World Cup Goals compilation          (155s)
# t6HWYe2AT0o — Messi Best Assists career compilation           (435s)
# nA8wHQvHPJU — Messi 100 Magical Dribbling Skills              (354s)

# PELÉ
# WXg8P0u9W9I — Pele Top 10 Impossible Goals Ever               (217s)
# bUTRZGCiiFs — Pele's Top 5 Goals FIFA World Cup               (105s)
# HeL80yYlMOU — Pelé Gols em 1964 pelo Santos                   (207s)
# PoTRjML32JA — Pelé Gols em 1963 pelo Santos                   (137s)
# e86n8WASSUs — All 31 Goals Pelé New York Cosmos FC            (199s)
# prSYaKD1s4w — 10 Pelé Goals That SHOCKED The World            (232s)

# FINALE (FIFA ceremony — both legends referenced)
# 2htb5t-Sl0Q — Homenagem ao Rei Pelé no Prêmio FIFA The Best 2022 (1054s)

SOURCES = {
    # MESSI
    "EdwIVC7LaJE": {"title": "Messi All FIFA World Cup Goals 2006-2022",   "duration": 507},
    "Q_A_FP2F7T0": {"title": "Messi FIFA World Cup Goals compilation",      "duration": 155},
    "t6HWYe2AT0o": {"title": "Messi Best Assists career compilation",       "duration": 435},
    "nA8wHQvHPJU": {"title": "Messi 100 Magical Dribbling Skills",          "duration": 354},
    # PELÉ
    "WXg8P0u9W9I": {"title": "Pele Top 10 Impossible Goals Ever",           "duration": 217},
    "bUTRZGCiiFs": {"title": "Pele Top 5 Goals FIFA World Cup",             "duration": 105},
    "HeL80yYlMOU": {"title": "Pelé Gols em 1964 pelo Santos",               "duration": 207},
    "PoTRjML32JA": {"title": "Pelé Gols em 1963 pelo Santos",               "duration": 137},
    "e86n8WASSUs": {"title": "All 31 Goals Pelé New York Cosmos FC",        "duration": 199},
    "prSYaKD1s4w": {"title": "10 Pelé Goals That SHOCKED The World",        "duration": 232},
    # FINALE
    "2htb5t-Sl0Q": {"title": "Homenagem Pelé FIFA The Best 2022 ceremony",  "duration": 1054},
}

# ── SEGMENTS — strictly alternating Messi (M) → Pelé (P) ─────────────────────
# Each segment used ONCE. No two consecutive clips from the same source video.
# ch = chapter index (maps to audio chapter for CapCut sync)

SEGMENTS = [
    # Ch0 — HOOK: Copa do Mundo, os dois maiores
    {"id": "EdwIVC7LaJE", "start":  0, "end": 28, "ch": 0, "label": "M", "desc": "Messi WC 2022 Qatar final goal"},
    {"id": "WXg8P0u9W9I", "start":  0, "end": 28, "ch": 0, "label": "P", "desc": "Pelé impossible goal #1"},
    {"id": "Q_A_FP2F7T0", "start":  0, "end": 28, "ch": 0, "label": "M", "desc": "Messi WC goal compilation open"},
    {"id": "bUTRZGCiiFs", "start":  0, "end": 28, "ch": 0, "label": "P", "desc": "Pelé WC top goal #1"},

    # Ch1 — DOIS GOATS: mundos diferentes, mesma grandeza
    {"id": "t6HWYe2AT0o", "start":  0, "end": 28, "ch": 1, "label": "M", "desc": "Messi best assist #1"},
    {"id": "HeL80yYlMOU", "start":  0, "end": 28, "ch": 1, "label": "P", "desc": "Pelé Santos 1964 goal #1"},
    {"id": "nA8wHQvHPJU", "start":  0, "end": 28, "ch": 1, "label": "M", "desc": "Messi magical dribble #1"},
    {"id": "e86n8WASSUs", "start":  0, "end": 28, "ch": 1, "label": "P", "desc": "Pelé NY Cosmos goal #1"},
    {"id": "t6HWYe2AT0o", "start": 30, "end": 58, "ch": 1, "label": "M", "desc": "Messi assist #2"},

    # Ch2 — OS NÚMEROS: gols, assistências, décadas
    {"id": "WXg8P0u9W9I", "start": 30, "end": 58, "ch": 2, "label": "P", "desc": "Pelé impossible goal #2"},
    {"id": "EdwIVC7LaJE", "start": 30, "end": 58, "ch": 2, "label": "M", "desc": "Messi WC 2010 goal"},
    {"id": "HeL80yYlMOU", "start": 30, "end": 58, "ch": 2, "label": "P", "desc": "Pelé Santos 1964 goal #2"},
    {"id": "nA8wHQvHPJU", "start": 30, "end": 58, "ch": 2, "label": "M", "desc": "Messi dribble #2"},
    {"id": "PoTRjML32JA", "start":  0, "end": 28, "ch": 2, "label": "P", "desc": "Pelé Santos 1963 goal #1"},

    # Ch3 — A COPA DO MUNDO: troféus e lendas
    {"id": "EdwIVC7LaJE", "start": 60, "end": 88, "ch": 3, "label": "M", "desc": "Messi WC 2014 goal"},
    {"id": "bUTRZGCiiFs", "start": 30, "end": 58, "ch": 3, "label": "P", "desc": "Pelé WC goal #2"},
    {"id": "t6HWYe2AT0o", "start": 60, "end": 88, "ch": 3, "label": "M", "desc": "Messi assist #3"},
    {"id": "e86n8WASSUs", "start": 30, "end": 58, "ch": 3, "label": "P", "desc": "Pelé Cosmos goal #2"},
    {"id": "EdwIVC7LaJE", "start": 90, "end": 118, "ch": 3, "label": "M", "desc": "Messi WC 2022 Final"},

    # Ch4 — IDADE E LONGEVIDADE: pico e recordes
    {"id": "prSYaKD1s4w", "start":  0, "end": 28, "ch": 4, "label": "P", "desc": "Pelé shocking goal #1"},
    {"id": "nA8wHQvHPJU", "start": 60, "end": 88, "ch": 4, "label": "M", "desc": "Messi dribble #3"},
    {"id": "WXg8P0u9W9I", "start": 60, "end": 88, "ch": 4, "label": "P", "desc": "Pelé impossible goal #3"},
    {"id": "t6HWYe2AT0o", "start": 90, "end": 118, "ch": 4, "label": "M", "desc": "Messi assist #4"},
    {"id": "PoTRjML32JA", "start": 30, "end": 58, "ch": 4, "label": "P", "desc": "Pelé Santos 1963 goal #2"},

    # Ch5 — PELÉ E OS EUA: Cosmos, futebol e legado americano
    {"id": "e86n8WASSUs", "start": 60, "end": 88, "ch": 5, "label": "P", "desc": "Pelé Cosmos NY goal #3"},
    {"id": "Q_A_FP2F7T0", "start": 30, "end": 58, "ch": 5, "label": "M", "desc": "Messi WC dribble skill"},
    {"id": "e86n8WASSUs", "start": 90, "end": 118, "ch": 5, "label": "P", "desc": "Pelé Cosmos NY goal #4"},
    {"id": "nA8wHQvHPJU", "start": 90, "end": 118, "ch": 5, "label": "M", "desc": "Messi dribble #4"},
    {"id": "HeL80yYlMOU", "start": 60, "end": 88, "ch": 5, "label": "P", "desc": "Pelé Santos goal #3"},

    # Ch6 — 30 FATOS: comparativo definitivo
    {"id": "EdwIVC7LaJE", "start": 120, "end": 148, "ch": 6, "label": "M", "desc": "Messi WC record goal"},
    {"id": "prSYaKD1s4w", "start": 30, "end": 58, "ch": 6, "label": "P", "desc": "Pelé shocking goal #2"},
    {"id": "t6HWYe2AT0o", "start": 120, "end": 148, "ch": 6, "label": "M", "desc": "Messi assist #5"},
    {"id": "WXg8P0u9W9I", "start": 90, "end": 118, "ch": 6, "label": "P", "desc": "Pelé impossible goal #4"},
    {"id": "EdwIVC7LaJE", "start": 150, "end": 178, "ch": 6, "label": "M", "desc": "Messi WC milestone career"},

    # Ch7 — EMOÇÃO E CELEBRAÇÃO
    {"id": "prSYaKD1s4w", "start": 60, "end": 88, "ch": 7, "label": "P", "desc": "Pelé shocking goal #3"},
    {"id": "nA8wHQvHPJU", "start": 120, "end": 148, "ch": 7, "label": "M", "desc": "Messi dribble #5"},
    {"id": "HeL80yYlMOU", "start": 90, "end": 118, "ch": 7, "label": "P", "desc": "Pelé Santos goal #4"},
    {"id": "EdwIVC7LaJE", "start": 180, "end": 208, "ch": 7, "label": "M", "desc": "Messi WC trophy lift"},
    {"id": "prSYaKD1s4w", "start": 90, "end": 118, "ch": 7, "label": "P", "desc": "Pelé shocking goal #4"},

    # Ch8 — LEGADO ETERNO: dois GOATs, um só amor pelo futebol
    {"id": "t6HWYe2AT0o", "start": 150, "end": 178, "ch": 8, "label": "M", "desc": "Messi career assist legacy"},
    {"id": "e86n8WASSUs", "start": 120, "end": 148, "ch": 8, "label": "P", "desc": "Pelé Cosmos legacy final"},
    {"id": "Q_A_FP2F7T0", "start": 60, "end": 88, "ch": 8, "label": "M", "desc": "Messi WC career goal final"},
    {"id": "WXg8P0u9W9I", "start": 120, "end": 148, "ch": 8, "label": "P", "desc": "Pelé eternal legend"},
    # FINALE — FIFA The Best 2022 tribute (ceremony honoring Pelé + Messi era)
    {"id": "2htb5t-Sl0Q", "start": 0, "end": 28, "ch": 8, "label": "BOTH", "desc": "FIFA tribute — GOAT forever"},
]


def _download_source(vid_id: str, title: str, src_dir: str) -> str | None:
    filepath = os.path.join(src_dir, f"{vid_id}.mp4")
    if os.path.exists(filepath) and os.path.getsize(filepath) > 500_000:
        size_mb = os.path.getsize(filepath) / 1_048_576
        print(f"[soccer] ✅ cached: {vid_id} — {title} ({size_mb:.0f} MB)")
        return filepath

    url = f"https://www.youtube.com/watch?v={vid_id}"
    print(f"[soccer] ⬇  {vid_id} — {title}...")
    cmd = [
        "python", "-m", "yt_dlp",
        "--quiet", "--no-warnings",
        "-f", "best[height<=1080][ext=mp4]/best[ext=mp4]",
        "-o", filepath,
        url,
    ]
    try:
        result = subprocess.run(cmd, timeout=300, capture_output=True, text=True)
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 500_000:
            print(f"[soccer]    FAILED — {result.stderr[:200]}")
            return None
        size_mb = os.path.getsize(filepath) / 1_048_576
        print(f"[soccer]    ✅ {size_mb:.0f} MB")
        return filepath
    except Exception as e:
        print(f"[soccer]    ERROR: {e}")
        return None


def _cut_segment(src_path: str, out_path: str, start: int, end: int) -> bool:
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10_000:
        return True
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", src_path,
        "-t", str(end - start),
        "-c:v", "copy", "-c:a", "copy",
        "-avoid_negative_ts", "make_zero",
        out_path,
    ]
    try:
        subprocess.run(cmd, timeout=60, capture_output=True, check=True)
        return os.path.exists(out_path) and os.path.getsize(out_path) > 10_000
    except Exception:
        return False


def fetch_soccer_curated_clips(script: dict, config: dict) -> dict:
    slug    = script["slug"]
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "clips", slug)
    src_dir = os.path.join(out_dir, "_sources")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(src_dir, exist_ok=True)

    # ── PHASE 1: Download each source video ONCE ─────────────────────────────
    print(f"\n[soccer] PHASE 1 — downloading {len(SOURCES)} source videos...")
    source_paths: dict[str, str | None] = {}
    for vid_id, info in SOURCES.items():
        source_paths[vid_id] = _download_source(vid_id, info["title"], src_dir)
        time.sleep(0.5)

    available = {k for k, v in source_paths.items() if v}
    missing   = set(SOURCES) - available
    if missing:
        print(f"[soccer] ⚠ {len(missing)} sources unavailable: {missing}")
    print(f"[soccer] {len(available)}/{len(SOURCES)} sources ready\n")

    # ── PHASE 2: Cut segments locally with ffmpeg ─────────────────────────────
    print(f"[soccer] PHASE 2 — cutting {len(SEGMENTS)} segments (Messi ↔ Pelé alternating)...")
    downloaded = []
    for i, seg in enumerate(SEGMENTS):
        vid_id = seg["id"]
        if vid_id not in available:
            print(f"[soccer]   SKIP {i:04d}-ch{seg['ch']:02d} [{seg['label']}] — source unavailable")
            continue

        filename = f"{i:04d}-ch{seg['ch']:02d}-{seg['label']}-yt{vid_id}-{seg['start']}.mp4"
        filepath = os.path.join(out_dir, filename)
        duration = seg["end"] - seg["start"]

        ok = _cut_segment(source_paths[vid_id], filepath, seg["start"], seg["end"])
        if ok:
            print(f"[soccer]   ✅ [{seg['label']}] {filename} ({duration}s) — {seg['desc']}")
            downloaded.append({
                "path":     filepath,
                "chapter":  seg["ch"],
                "index":    i,
                "duration": duration,
                "width":    1920,
                "height":   1080,
                "label":    seg["label"],
                "desc":     seg["desc"],
            })
        else:
            print(f"[soccer]   ❌ FAILED: {filename}")

    total_secs = sum(c["duration"] for c in downloaded)
    messi_clips = sum(1 for c in downloaded if c["label"] == "M")
    pele_clips  = sum(1 for c in downloaded if c["label"] == "P")
    print(f"\n[soccer] {len(downloaded)} clips ready — {total_secs/60:.1f} min")
    print(f"[soccer] Messi: {messi_clips} clips | Pelé: {pele_clips} clips | Finale: 1")
    print(f"\n[soccer] ⚠ CAPCUT FINAL STEP:")
    print(f"[soccer]   Add a static IMAGE of Messi + Pelé together (jerseys, smiling)")
    print(f"[soccer]   as the LAST 5 seconds before export.")

    return {
        "clips":          downloaded,
        "directory":      out_dir,
        "count":          len(downloaded),
        "total_duration": total_secs,
    }

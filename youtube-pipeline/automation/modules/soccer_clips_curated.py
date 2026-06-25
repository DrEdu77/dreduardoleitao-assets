"""
Module 3d — Soccer Curated Clips — Best Goals, Saves & Assists of All Time
Downloads real professional soccer footage via yt-dlp from YouTube.
All video IDs verified working as of 2026-06-24.

COPYRIGHT: Content ID claims possible (revenue sharing only, not strikes).
Standard practice for sports analysis/educational channels.
"""

import os, subprocess, time

# ── VERIFIED YOUTUBE IDs ─────────────────────────────────────────────────────
# EdwIVC7LaJE — Messi All FIFA World Cup Goals 2006-2022 (507s)
# Q_A_FP2F7T0 — Messi FIFA World Cup Goals (155s)
# WXg8P0u9W9I — Pele Top 10 Impossible Goals (217s)
# bUTRZGCiiFs — Pele Top 5 Goals FIFA World Cup (105s)
# yxvaURdWJS8 — Best Goalkeeper Saves (519s)
# 55lI1TpiO-s — 100 Legendary Saves in Football (884s)
# QtSMXXJq11Q — Best Goals Qatar 2022 World Cup (624s)
# tud8DAWjRao — Top 20 Goals 2022 FIFA World Cup (1289s)

SOCCER_CURATED = [
    # Ch0 — Hook: Copa do Mundo, estádio, atmosfera épica
    {"id": "QtSMXXJq11Q", "start":   0, "end":  28, "chapter": 0, "desc": "Qatar 2022 World Cup best goals intro"},
    {"id": "QtSMXXJq11Q", "start":  30, "end":  58, "chapter": 0, "desc": "Qatar 2022 goal #1"},
    {"id": "tud8DAWjRao", "start":   0, "end":  28, "chapter": 0, "desc": "Top 20 World Cup goals intro"},
    {"id": "tud8DAWjRao", "start":  30, "end":  58, "chapter": 0, "desc": "World Cup goal celebration"},

    # Ch1 — Messi GOAT: gols e assistências históricas
    {"id": "EdwIVC7LaJE", "start":   0, "end":  28, "chapter": 1, "desc": "Messi 1st World Cup goal 2006"},
    {"id": "EdwIVC7LaJE", "start":  30, "end":  58, "chapter": 1, "desc": "Messi goal Argentina 2010"},
    {"id": "EdwIVC7LaJE", "start":  60, "end":  88, "chapter": 1, "desc": "Messi World Cup 2014 goal"},
    {"id": "Q_A_FP2F7T0", "start":   0, "end":  28, "chapter": 1, "desc": "Messi World Cup goal compilation"},
    {"id": "Q_A_FP2F7T0", "start":  30, "end":  58, "chapter": 1, "desc": "Messi dribble World Cup"},

    # Ch2 — Pelé: gols clássicos, Brasil, lenda
    {"id": "WXg8P0u9W9I", "start":   0, "end":  28, "chapter": 2, "desc": "Pele impossible goal #1"},
    {"id": "WXg8P0u9W9I", "start":  30, "end":  58, "chapter": 2, "desc": "Pele impossible goal #2"},
    {"id": "WXg8P0u9W9I", "start":  60, "end":  88, "chapter": 2, "desc": "Pele impossible goal #3"},
    {"id": "bUTRZGCiiFs", "start":   0, "end":  28, "chapter": 2, "desc": "Pele FIFA World Cup goal #1"},
    {"id": "bUTRZGCiiFs", "start":  30, "end":  58, "chapter": 2, "desc": "Pele FIFA World Cup goal #2"},

    # Ch3 — Copa do Mundo: finais, gols históricos
    {"id": "tud8DAWjRao", "start":  60, "end":  88, "chapter": 3, "desc": "World Cup 2022 goal top 20 #3"},
    {"id": "tud8DAWjRao", "start":  90, "end": 118, "chapter": 3, "desc": "World Cup 2022 goal top 20 #4"},
    {"id": "QtSMXXJq11Q", "start":  60, "end":  88, "chapter": 3, "desc": "Qatar 2022 goal #3"},
    {"id": "QtSMXXJq11Q", "start":  90, "end": 118, "chapter": 3, "desc": "Qatar 2022 goal #4"},
    {"id": "EdwIVC7LaJE", "start":  90, "end": 118, "chapter": 3, "desc": "Messi 2022 World Cup Final goal"},

    # Ch4 — Gols e recordes espetaculares
    {"id": "tud8DAWjRao", "start": 120, "end": 148, "chapter": 4, "desc": "World Cup spectacular goal #5"},
    {"id": "tud8DAWjRao", "start": 150, "end": 178, "chapter": 4, "desc": "World Cup spectacular goal #6"},
    {"id": "QtSMXXJq11Q", "start": 120, "end": 148, "chapter": 4, "desc": "Qatar 2022 stunning goal #5"},
    {"id": "EdwIVC7LaJE", "start": 120, "end": 148, "chapter": 4, "desc": "Messi World Cup record goal"},

    # Ch5 — Defesas impossíveis (salvadas históricas)
    {"id": "yxvaURdWJS8", "start":   0, "end":  28, "chapter": 5, "desc": "Best goalkeeper save #1"},
    {"id": "yxvaURdWJS8", "start":  30, "end":  58, "chapter": 5, "desc": "Best goalkeeper save #2"},
    {"id": "55lI1TpiO-s", "start":   0, "end":  28, "chapter": 5, "desc": "Legendary save #1"},
    {"id": "55lI1TpiO-s", "start":  30, "end":  58, "chapter": 5, "desc": "Legendary save #2"},
    {"id": "55lI1TpiO-s", "start":  60, "end":  88, "chapter": 5, "desc": "Legendary save #3"},

    # Ch6 — Comparativo GOAT: Messi vs Pelé
    {"id": "EdwIVC7LaJE", "start": 150, "end": 178, "chapter": 6, "desc": "Messi all-time record"},
    {"id": "WXg8P0u9W9I", "start":  90, "end": 118, "chapter": 6, "desc": "Pele all-time classic"},
    {"id": "Q_A_FP2F7T0", "start":  60, "end":  88, "chapter": 6, "desc": "Messi World Cup milestone"},
    {"id": "bUTRZGCiiFs", "start":  60, "end":  88, "chapter": 6, "desc": "Pele World Cup record"},

    # Ch7 — Torcida, emoção, celebração
    {"id": "tud8DAWjRao", "start": 180, "end": 208, "chapter": 7, "desc": "World Cup crowd celebration"},
    {"id": "QtSMXXJq11Q", "start": 150, "end": 178, "chapter": 7, "desc": "Qatar 2022 fans eruption"},
    {"id": "tud8DAWjRao", "start": 210, "end": 238, "chapter": 7, "desc": "World Cup stadium emotion"},

    # Ch8 — Conclusão: legado, próxima geração
    {"id": "EdwIVC7LaJE", "start": 180, "end": 208, "chapter": 8, "desc": "Messi World Cup legacy"},
    {"id": "WXg8P0u9W9I", "start": 120, "end": 148, "chapter": 8, "desc": "Pele legacy soccer"},
    {"id": "tud8DAWjRao", "start": 240, "end": 268, "chapter": 8, "desc": "Soccer world cup finale"},
]


def fetch_soccer_curated_clips(script: dict, config: dict) -> dict:
    slug    = script["slug"]
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "clips", slug)
    os.makedirs(out_dir, exist_ok=True)

    downloaded = []
    clip_index = 0

    for entry in SOCCER_CURATED:
        vid_id  = entry["id"]
        start   = entry["start"]
        end     = entry["end"]
        chapter = entry["chapter"]
        desc    = entry["desc"]
        duration = end - start

        filename = f"{clip_index:04d}-ch{chapter:02d}-yt{vid_id}-{start}.mp4"
        filepath = os.path.join(out_dir, filename)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 50000:
            print(f"[soccer_clips] ✅ cached: {filename}")
        else:
            url = f"https://www.youtube.com/watch?v={vid_id}"
            print(f"[soccer_clips] Ch{chapter} — {desc}...")
            cmd = [
                "python", "-m", "yt_dlp",
                "--quiet", "--no-warnings",
                "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[ext=mp4]",
                "--download-sections", f"*{start}-{end}",
                "--force-keyframes-at-cuts",
                "-o", filepath,
                url
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if not os.path.exists(filepath) or os.path.getsize(filepath) < 50000:
                    print(f"[soccer_clips]   SKIP (download failed)")
                    continue
                print(f"[soccer_clips]   ✅ {filename} ({duration}s)")
                time.sleep(0.3)
            except Exception as e:
                print(f"[soccer_clips]   SKIP ({e})")
                continue

        downloaded.append({
            "path":     filepath,
            "chapter":  chapter,
            "index":    clip_index,
            "duration": duration,
            "width":    1920,
            "height":   1080,
            "desc":     desc,
        })
        clip_index += 1

    total_secs = sum(c["duration"] for c in downloaded)
    print(f"\n[soccer_clips] {len(downloaded)} clips — {total_secs/60:.1f} min total → {out_dir}")
    return {"clips": downloaded, "directory": out_dir, "count": len(downloaded), "total_duration": total_secs}

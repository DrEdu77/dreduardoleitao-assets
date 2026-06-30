#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
queue-approval.py — Registra assets do Studio na fila de aprovacao do GrowthOS

Uso:
  python3 -X utf8 queue-approval.py --folder C:/Users/User/growthOS/output/studio/hernia-de-disco/
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

GROWTHOS_DIR  = Path("C:/Users/User/growthOS")
CAROUSELS_DIR = GROWTHOS_DIR / "output" / "carousels"


def slugify(text: str) -> str:
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Fila de aprovacao")
    parser.add_argument("--folder", required=True, help="Pasta com assets do Studio gerados")
    parser.add_argument("--title",  help="Titulo do post (opcional — detectado automaticamente)")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Erro: pasta nao encontrada: {folder}")
        exit(1)

    title = args.title or folder.name.replace("-", " ").title()

    # Detecta videos disponiveis
    videos = list(folder.glob("*.mp4"))
    audio  = folder / "audio.mp3"
    cover  = next(iter(folder.glob("*.png")), None)

    # Cria pasta na estrutura do GrowthOS (carousels-studio-YYYYMMDD)
    today   = datetime.now().strftime("%Y%m%d")
    version = f"carousels-studio-{today}"
    slug    = slugify(title)
    dest    = CAROUSELS_DIR / version / slug
    dest.mkdir(parents=True, exist_ok=True)

    # Copia ou cria symlinks dos videos para a pasta dest
    import shutil
    for v in videos:
        shutil.copy2(v, dest / v.name)
    if cover:
        # Cria pasta slides/ com a capa para preview no email
        slides_dir = dest / "slides"
        slides_dir.mkdir(exist_ok=True)
        shutil.copy2(cover, slides_dir / "cover.png")
    if audio.exists():
        shutil.copy2(audio, dest / "audio.mp3")

    # Copia legendas
    for caption_file in folder.glob("caption_*.md"):
        shutil.copy2(caption_file, dest / caption_file.name)

    # Gera caption.md principal (Instagram) para o sistema de aprovacao
    ig_caption = folder / "caption_instagram.md"
    if ig_caption.exists():
        (dest / "caption.md").write_text(ig_caption.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        (dest / "caption.md").write_text(f"# {title}\n\nDor ninguem merece. Agende: (11) 3042-1334", encoding="utf-8")

    # Cria post-status.json no formato GrowthOS
    status = {
        "status":        "draft",
        "published":     False,
        "title":         title,
        "caption_written": True,
        "slides_exported": bool(cover),
        "slides_count":  1,
        "videos":        [v.name for v in videos],
        "created_at":    datetime.now().isoformat(),
        "source":        "corpo-vivo-studio",
        "studio_folder": str(folder),
        "username":      "corpovivomed",
        "post_url":      None,
    }
    (dest / "post-status.json").write_text(
        json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nRegistrado na fila: {dest}")
    print(f"Videos: {[v.name for v in videos]}")
    print(f"Proximo passo: python3 -X utf8 C:/Users/User/growthOS/publisher/notify-approval.py --force")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch-produce.py — Producao em lote de conteudo para multiplos temas

Uso:
  python3 -X utf8 batch-produce.py \
    --topics "hernia de disco,dor lombar,pilates para coluna" \
    --formats reel,story,feed,facebook,linkedin
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR   = Path(__file__).parent
STUDIO_OUTPUT = Path("C:/Users/User/growthOS/output/studio")
NOTIFY_SCRIPT = Path("C:/Users/User/growthOS/publisher/notify-approval.py")


def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def run_script(args: list[str]) -> bool:
    result = subprocess.run([sys.executable, "-X", "utf8"] + args,
                            capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0 and result.stderr:
        print(f"ERRO: {result.stderr.rstrip()}")
    return result.returncode == 0


def produce_topic(topic: str, formats: str, roteiro: str | None = None) -> bool:
    slug       = slugify(topic)
    output_dir = STUDIO_OUTPUT / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / "audio.mp3"

    print(f"\n{'='*60}")
    print(f"Produzindo: {topic}")
    print(f"{'='*60}")

    # Fase 2: Audio
    if roteiro:
        text_arg = ["--text", roteiro]
    else:
        # Roteiro minimo automatico (Claude deve passar --text com roteiro real)
        text_arg = ["--text", f"Olá, eu sou o Dr. Eduardo Leitão da Clínica Corpo Vivo Alpha. "
                               f"Hoje vou falar sobre {topic}. Dor ninguém merece. "
                               f"Agende sua avaliação: 11 3042-1334."]

    print("\n[Fase 2] Gerando audio (ElevenLabs)...")
    ok = run_script([str(SCRIPTS_DIR / "generate-voice.py")] + text_arg +
                    ["--output", str(audio_path)])
    if not ok:
        print(f"  Falhou gerar audio para: {topic}")
        return False

    # Fase 3: Video
    print("\n[Fase 3] Gerando video (HeyGen)...")
    ok = run_script([str(SCRIPTS_DIR / "generate-video.py"),
                     "--audio", str(audio_path),
                     "--output-dir", str(output_dir),
                     "--formats", formats])
    if not ok:
        print(f"  Falhou gerar video para: {topic}")
        return False

    # Gera legendas minimas
    for plat, desc in [("instagram", "#corpovivo #osteopatia #dornascoluna"),
                       ("facebook",  "Marque alguem que precisa ver isso!"),
                       ("linkedin",  f"Reflexao clinica sobre {topic}. #saude #osteopatia")]:
        caption = (output_dir / f"caption_{plat}.md")
        if not caption.exists():
            caption.write_text(f"# {topic.title()}\n\n{desc}\n\n"
                                f"Agende: (11) 3042-1334 | @corpovivomed", encoding="utf-8")

    # Fase 5 prep: Registra na fila
    print("\n[Fase 5] Registrando na fila de aprovacao...")
    run_script([str(SCRIPTS_DIR / "queue-approval.py"),
                "--folder", str(output_dir),
                "--title", topic.title()])

    return True


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Producao em lote")
    parser.add_argument("--topics",  required=True, help="Temas separados por virgula")
    parser.add_argument("--formats", default="reel,story,feed,facebook,linkedin",
                        help="Formatos de video")
    args = parser.parse_args()

    topics  = [t.strip() for t in args.topics.split(",") if t.strip()]
    success = []
    failed  = []

    print(f"\nBatch Studio — {len(topics)} temas | {datetime.now().strftime('%d/%m %H:%M')}")

    for topic in topics:
        ok = produce_topic(topic, args.formats)
        (success if ok else failed).append(topic)

    print(f"\n{'='*60}")
    print(f"Concluido: {len(success)}/{len(topics)} temas")
    if failed:
        print(f"Falhas: {', '.join(failed)}")

    if success:
        print("\nDisparando email de aprovacao com todos os assets...")
        subprocess.run([sys.executable, "-X", "utf8", str(NOTIFY_SCRIPT), "--force"],
                       encoding="utf-8")

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()

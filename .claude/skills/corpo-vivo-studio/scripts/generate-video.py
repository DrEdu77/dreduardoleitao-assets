#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-video.py — Gera videos com avatar Dr. Eduardo via HeyGen API v2

Modos de voz:
  --text roteiro.txt   Usa TTS nativo HeyGen (voz PT-BR configurada)
  --audio audio.mp3    Usa audio pre-gerado do ElevenLabs via URL publica

Uso:
  python3 -X utf8 generate-video.py --text roteiro.txt --formats reel,feed,facebook,linkedin \
    --output-dir C:/Users/User/growthOS/output/studio/tema/video/

  python3 -X utf8 generate-video.py --audio audio.mp3 --audio-url https://cdn.../audio.mp3 \
    --formats reel --output-dir ./video/
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_FILE = Path.home() / ".growthos" / "studio-config.json"
BASE_URL    = "https://api.heygen.com"

# Avatar Eduardo: ea3bcd5f3b704bb78e62c7880a7395fd
# Voz PT-BR HeyGen: 804aabbf954e45dc87f98b13910abf2a

FORMATS = {
    "reel":     {"width": 1080, "height": 1920, "filename": "reel_9x16.mp4",      "desc": "Instagram Reel / TikTok"},
    "story":    {"width": 1080, "height": 1920, "filename": "story_9x16_15s.mp4", "desc": "Instagram Story"},
    "feed":     {"width": 1080, "height": 1080, "filename": "feed_1x1.mp4",       "desc": "Instagram Feed"},
    "facebook": {"width": 1920, "height": 1080, "filename": "facebook_16x9.mp4",  "desc": "Facebook / YouTube"},
    "linkedin": {"width": 1920, "height": 1080, "filename": "linkedin_16x9.mp4",  "desc": "LinkedIn"},
    "youtube":  {"width": 1920, "height": 1080, "filename": "youtube_16x9.mp4",   "desc": "YouTube"},
}

BACKGROUND_COLOR = "#1A4A40"  # verde-musgo Corpo Vivo


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        print("Erro: studio-config.json nao encontrado. Execute: python3 -X utf8 setup-credentials.py")
        sys.exit(1)
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def build_voice_block(cfg: dict, text: str = "", audio_url: str = "") -> dict:
    """Monta o bloco 'voice' do payload HeyGen."""
    if audio_url:
        return {"type": "audio", "audio_url": audio_url}
    voice_id = cfg.get("heygen_voice_id_pt", "804aabbf954e45dc87f98b13910abf2a")
    return {
        "type":       "text",
        "input_text": text,
        "voice_id":   voice_id,
        "speed":      1.0,
    }


def create_video(api_key: str, avatar_id: str, voice_block: dict,
                 width: int, height: int, test: bool = False) -> str | None:
    """Cria video no HeyGen e retorna o video_id."""
    payload = json.dumps({
        "video_inputs": [{
            "character": {
                "type":         "avatar",
                "avatar_id":    avatar_id,
                "avatar_style": "normal",
            },
            "voice":      voice_block,
            "background": {"type": "color", "value": BACKGROUND_COLOR},
        }],
        "dimension": {"width": width, "height": height},
        "test": test,
    }).encode("utf-8")

    req = urllib.request.Request(f"{BASE_URL}/v2/video/generate", data=payload, method="POST")
    req.add_header("X-Api-Key",     api_key)
    req.add_header("Content-Type",  "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            video_id = data.get("data", {}).get("video_id")
            print(f"  Video criado — ID: {video_id}")
            return video_id
    except urllib.error.HTTPError as e:
        print(f"  Erro criar video HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}")
        return None


def wait_for_video(api_key: str, video_id: str, timeout_min: int = 15) -> str | None:
    """Aguarda processamento e retorna a URL do video."""
    url = f"{BASE_URL}/v1/video_status.get?video_id={video_id}"
    req = urllib.request.Request(url)
    req.add_header("X-Api-Key", api_key)

    deadline = time.time() + timeout_min * 60
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data  = json.loads(resp.read()).get("data", {})
                status = data.get("status", "pending")
                print(f"  Status: {status}          ", end="\r")
                if status == "completed":
                    print()
                    return data.get("video_url")
                elif status == "failed":
                    print(f"\n  Falha: {data.get('error', 'desconhecido')}")
                    return None
        except Exception as e:
            print(f"\n  Erro status: {e}")
        time.sleep(20)

    print(f"\n  Timeout ({timeout_min} min) atingido.")
    return None


def download_video(video_url: str, output_path: Path) -> bool:
    req = urllib.request.Request(video_url)
    req.add_header("User-Agent", "CorpoVivoStudio/1.0")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(resp.read())
        size_mb = round(output_path.stat().st_size / (1024 * 1024), 1)
        print(f"  Salvo: {output_path.name} ({size_mb} MB)")
        return True
    except Exception as e:
        print(f"  Erro download: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — HeyGen Video Generator")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--text",      help="Arquivo TXT com roteiro (usa TTS HeyGen PT-BR)")
    grp.add_argument("--audio-url", help="URL publica do MP3 (ElevenLabs pre-gerado)")
    parser.add_argument("--output-dir", required=True, help="Pasta de saida dos videos")
    parser.add_argument("--formats", default="reel,feed,facebook,linkedin",
                        help="Formatos: reel,story,feed,facebook,linkedin,youtube")
    parser.add_argument("--test",   action="store_true",
                        help="Modo teste HeyGen (watermark, sem debitar creditos)")
    args = parser.parse_args()

    cfg       = load_config()
    api_key   = cfg.get("heygen_api_key", "")
    avatar_id = cfg.get("heygen_avatar_id", "ea3bcd5f3b704bb78e62c7880a7395fd")

    if not api_key:
        print("Erro: heygen_api_key nao configurado. Execute: python3 -X utf8 setup-credentials.py")
        sys.exit(1)

    # Prepara bloco de voz
    if args.text:
        text_content = Path(args.text).read_text(encoding="utf-8")
        # Limpa placeholders do roteiro (seccoes de formatacao)
        linhas = [l for l in text_content.splitlines()
                  if not l.startswith("---") and not l.startswith("#")]
        texto_limpo = " ".join(l.strip() for l in linhas if l.strip())[:4000]
        voice_block = build_voice_block(cfg, text=texto_limpo)
        print(f"Modo: TTS HeyGen | {len(texto_limpo)} chars")
    else:
        voice_block = build_voice_block(cfg, audio_url=args.audio_url)
        print(f"Modo: Audio URL | {args.audio_url[:60]}...")

    output_dir = Path(args.output_dir)
    formats    = [f.strip() for f in args.formats.split(",")]
    unknown    = [f for f in formats if f not in FORMATS]
    if unknown:
        print(f"Formatos invalidos: {unknown}. Disponiveis: {list(FORMATS.keys())}")
        sys.exit(1)

    print(f"Avatar: {avatar_id}")
    print(f"Formatos: {', '.join(formats)}\n")

    success = 0
    for fmt in formats:
        spec = FORMATS[fmt]
        print(f"[{fmt}] {spec['desc']} ({spec['width']}x{spec['height']})")

        video_id = create_video(api_key, avatar_id, voice_block,
                                spec["width"], spec["height"], test=args.test)
        if not video_id:
            continue

        video_url = wait_for_video(api_key, video_id)
        if not video_url:
            continue

        if download_video(video_url, output_dir / spec["filename"]):
            success += 1

    print(f"\n{success}/{len(formats)} videos gerados com sucesso.")
    sys.exit(0 if success == len(formats) else 1)


if __name__ == "__main__":
    main()

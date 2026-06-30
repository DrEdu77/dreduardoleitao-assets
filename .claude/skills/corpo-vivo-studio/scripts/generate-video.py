#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-video.py — Gera videos com avatar via HeyGen API

Uso:
  python3 -X utf8 generate-video.py \
    --audio audio.mp3 \
    --output-dir C:/Users/User/growthOS/output/studio/tema/ \
    --formats reel,story,feed,facebook,linkedin
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
        print("Erro: studio-config.json nao encontrado.")
        print("Execute: python3 -X utf8 setup-credentials.py")
        sys.exit(1)
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def upload_audio(api_key: str, audio_path: Path) -> str | None:
    """Faz upload do MP3 para o HeyGen e retorna a URL publica."""
    url = f"{BASE_URL}/v1/asset"
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    boundary = "----HeyGenBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{audio_path.name}"\r\n'
        f"Content-Type: audio/mpeg\r\n\r\n"
    ).encode("utf-8") + audio_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(f"{url}", data=body, method="POST")
    req.add_header("X-Api-Key", api_key)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            audio_url = data.get("data", {}).get("url")
            print(f"Audio enviado: {audio_url}")
            return audio_url
    except urllib.error.HTTPError as e:
        print(f"Erro upload audio HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        return None


def create_video(api_key: str, avatar_id: str, audio_url: str,
                 width: int, height: int) -> str | None:
    """Cria video no HeyGen e retorna o video_id."""
    payload = json.dumps({
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal",
            },
            "voice": {
                "type": "audio",
                "audio_url": audio_url,
            },
            "background": {
                "type": "color",
                "value": BACKGROUND_COLOR,
            },
        }],
        "dimension": {"width": width, "height": height},
        "test": False,
    }).encode("utf-8")

    req = urllib.request.Request(f"{BASE_URL}/v2/video/generate", data=payload, method="POST")
    req.add_header("X-Api-Key", api_key)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            video_id = data.get("data", {}).get("video_id")
            print(f"Video criado — ID: {video_id}")
            return video_id
    except urllib.error.HTTPError as e:
        print(f"Erro criar video HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        return None


def wait_for_video(api_key: str, video_id: str, timeout_min: int = 15) -> str | None:
    """Aguarda processamento e retorna a URL do video."""
    url = f"{BASE_URL}/v1/video_status.get?video_id={video_id}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("X-Api-Key", api_key)

    deadline = time.time() + timeout_min * 60
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read()).get("data", {})
                status = data.get("status")
                print(f"  Status: {status}", end="\r")
                if status == "completed":
                    print()
                    return data.get("video_url")
                elif status == "failed":
                    print(f"\nFalha no video: {data.get('error', 'desconhecido')}")
                    return None
        except Exception as e:
            print(f"\nErro ao verificar status: {e}")
        time.sleep(30)

    print(f"\nTimeout ({timeout_min} min) atingido.")
    return None


def download_video(video_url: str, output_path: Path) -> bool:
    req = urllib.request.Request(video_url)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(resp.read())
        size_mb = output_path.stat().st_size // (1024 * 1024)
        print(f"Video salvo: {output_path} ({size_mb} MB)")
        return True
    except Exception as e:
        print(f"Erro download: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — HeyGen Video Generator")
    parser.add_argument("--audio",      required=True, help="Arquivo MP3 de narração")
    parser.add_argument("--output-dir", required=True, help="Pasta de saida dos videos")
    parser.add_argument("--formats",    default="reel,story,feed,facebook,linkedin",
                        help="Formatos separados por virgula: reel,story,feed,facebook,linkedin,youtube")
    args = parser.parse_args()

    cfg       = load_config()
    api_key   = cfg.get("heygen_api_key", "")
    avatar_id = cfg.get("heygen_avatar_id", "")

    if not api_key or not avatar_id:
        print("Erro: heygen_api_key ou heygen_avatar_id nao configurados.")
        print("Execute: python3 -X utf8 setup-credentials.py")
        sys.exit(1)

    audio_path = Path(args.audio)
    output_dir = Path(args.output_dir)
    formats    = [f.strip() for f in args.formats.split(",")]

    unknown = [f for f in formats if f not in FORMATS]
    if unknown:
        print(f"Formatos desconhecidos: {unknown}. Disponiveis: {list(FORMATS.keys())}")
        sys.exit(1)

    print(f"\nUpload do audio: {audio_path}")
    audio_url = upload_audio(api_key, audio_path)
    if not audio_url:
        sys.exit(1)

    success_count = 0
    for fmt in formats:
        spec = FORMATS[fmt]
        print(f"\nGerando {spec['desc']} ({spec['width']}x{spec['height']})...")

        video_id = create_video(api_key, avatar_id, audio_url, spec["width"], spec["height"])
        if not video_id:
            print(f"  Falhou criar video para {fmt}")
            continue

        print(f"  Aguardando processamento (ate 15 min)...")
        video_url = wait_for_video(api_key, video_id)
        if not video_url:
            print(f"  Falhou obter URL para {fmt}")
            continue

        output_path = output_dir / spec["filename"]
        if download_video(video_url, output_path):
            success_count += 1

    print(f"\n{success_count}/{len(formats)} videos gerados com sucesso.")
    sys.exit(0 if success_count == len(formats) else 1)


if __name__ == "__main__":
    main()

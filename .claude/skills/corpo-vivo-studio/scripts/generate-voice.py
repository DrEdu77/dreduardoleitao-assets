#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-voice.py — Gera narração via ElevenLabs API

Uso:
  python3 -X utf8 generate-voice.py --text "roteiro aqui" --output audio.mp3
  python3 -X utf8 generate-voice.py --text-file roteiro.txt --output audio.mp3 --model turbo
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_FILE = Path.home() / ".growthos" / "studio-config.json"
BASE_URL    = "https://api.elevenlabs.io/v1"

MODELS = {
    "multilingual": "eleven_multilingual_v2",   # producao final
    "turbo":        "eleven_turbo_v2_5",         # testes rapidos
    "flash":        "eleven_flash_v2_5",         # ultra rapido
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        print("Erro: studio-config.json nao encontrado.")
        print("Execute: python3 -X utf8 setup-credentials.py")
        sys.exit(1)
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def generate_voice(text: str, output_path: Path, model: str = "multilingual", cfg: dict = None) -> bool:
    api_key  = cfg.get("elevenlabs_api_key", "")
    voice_id = cfg.get("elevenlabs_voice_id", "")

    if not api_key or not voice_id:
        print("Erro: elevenlabs_api_key ou elevenlabs_voice_id nao configurados.")
        print("Execute: python3 -X utf8 setup-credentials.py")
        return False

    model_id = MODELS.get(model, MODELS["multilingual"])

    # Dividir em blocos se necessario (limite ElevenLabs: 5000 chars)
    if len(text) > 4800:
        blocks = split_text(text, 4800)
        print(f"Texto longo — dividido em {len(blocks)} blocos")
        mp3_parts = []
        for i, block in enumerate(blocks, 1):
            print(f"  Gerando bloco {i}/{len(blocks)}...")
            part_path = output_path.parent / f"_part_{i:02d}.mp3"
            if not _call_api(api_key, voice_id, model_id, block, part_path, cfg):
                return False
            mp3_parts.append(part_path)
        concatenate_mp3s(mp3_parts, output_path)
        for p in mp3_parts:
            p.unlink(missing_ok=True)
        return True
    else:
        return _call_api(api_key, voice_id, model_id, text, output_path, cfg)


def _call_api(api_key: str, voice_id: str, model_id: str, text: str,
              output_path: Path, cfg: dict) -> bool:
    url = f"{BASE_URL}/text-to-speech/{voice_id}"
    payload = json.dumps({
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability":         cfg.get("elevenlabs_stability", 0.65),
            "similarity_boost":  cfg.get("elevenlabs_similarity", 0.80),
            "style":             cfg.get("elevenlabs_style", 0.20),
            "use_speaker_boost": True,
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("xi-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "audio/mpeg")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(resp.read())
        size_kb = output_path.stat().st_size // 1024
        print(f"Audio gerado: {output_path} ({size_kb} KB)")
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Erro ElevenLabs HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"Erro: {e}")
        return False


def split_text(text: str, max_chars: int) -> list[str]:
    sentences = text.replace(". ", ".|").replace("! ", "!|").replace("? ", "?|").split("|")
    blocks, current = [], ""
    for s in sentences:
        if len(current) + len(s) > max_chars:
            if current:
                blocks.append(current.strip())
            current = s
        else:
            current += " " + s
    if current.strip():
        blocks.append(current.strip())
    return blocks


def concatenate_mp3s(parts: list[Path], output: Path):
    combined = b""
    for p in parts:
        combined += p.read_bytes()
    output.write_bytes(combined)
    print(f"MP3 concatenado: {output}")


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — ElevenLabs TTS")
    parser.add_argument("--text",      help="Texto do roteiro direto na linha de comando")
    parser.add_argument("--text-file", help="Arquivo .txt ou .md com o roteiro")
    parser.add_argument("--output",    required=True, help="Caminho de saida .mp3")
    parser.add_argument("--model",     default="multilingual",
                        choices=["multilingual", "turbo", "flash"], help="Modelo ElevenLabs")
    args = parser.parse_args()

    cfg = load_config()
    output_path = Path(args.output)

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        parser.error("Informe --text ou --text-file")
        return

    print(f"\nGerando audio: {len(text)} chars | modelo={args.model}")
    ok = generate_voice(text, output_path, model=args.model, cfg=cfg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

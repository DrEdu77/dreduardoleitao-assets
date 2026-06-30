#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcribe-audio.py — [Prioridade 6] Transcreve audio MP3/WAV para SRT (legendas)

Fontes em ordem de prioridade:
  1. OpenAI Whisper API (online, alta precisao, key opcional)
  2. Whisper local via whisper Python package (gratuito, offline)
  3. SRT placeholder com timestamps (fallback — sem transcricao real)

Uso:
  python3 -X utf8 transcribe-audio.py --audio roteiro.mp3 --output ./legendas/
  python3 -X utf8 transcribe-audio.py --audio roteiro.mp3 --mode local --output ./legendas/
  python3 -X utf8 transcribe-audio.py --audio roteiro.mp3 --mode api --output ./legendas/
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_FILE = Path.home() / ".growthos" / "studio-config.json"

# Whisper API endpoint
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def segundos_para_srt_time(segundos: float) -> str:
    h    = int(segundos // 3600)
    m    = int((segundos % 3600) // 60)
    s    = int(segundos % 60)
    ms   = int((segundos - int(segundos)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def texto_para_srt(segmentos: list) -> str:
    """Converte lista de segmentos [{start, end, text}] para formato SRT."""
    linhas = []
    for i, seg in enumerate(segmentos, 1):
        start = segundos_para_srt_time(seg.get("start", 0))
        end   = segundos_para_srt_time(seg.get("end",   0))
        texto = seg.get("text", "").strip()
        linhas.append(f"{i}\n{start} --> {end}\n{texto}\n")
    return "\n".join(linhas)


def transcrever_whisper_api(audio_path: Path, cfg: dict) -> list:
    """Transcricao via OpenAI Whisper API (requer openai_api_key)."""
    api_key = cfg.get("openai_api_key", "")
    if not api_key:
        print("  openai_api_key nao configurado — pulando Whisper API")
        return []

    print("  Transcrevendo via Whisper API (OpenAI)...")

    boundary = "----CorpoVivoStudio"
    audio_bytes = audio_path.read_bytes()
    ext = audio_path.suffix.lower().lstrip(".")
    mime_map = {"mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4",
                "ogg": "audio/ogg", "flac": "audio/flac", "webm": "audio/webm"}
    mime = mime_map.get(ext, "audio/mpeg")

    body_parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-1\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\npt\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"response_format\"\r\n\r\nverbose_json\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"timestamp_granularities[]\"\r\n\r\nsegment\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{audio_path.name}\"\r\nContent-Type: {mime}\r\n\r\n",
    ]

    body_bytes = b"".join(p.encode("utf-8") for p in body_parts)
    body_bytes += audio_bytes
    body_bytes += f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(WHISPER_URL, data=body_bytes, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type",  f"multipart/form-data; boundary={boundary}")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            segs = data.get("segments", [])
            print(f"  Whisper API: {len(segs)} segmentos transcritos")
            return segs
    except urllib.error.HTTPError as e:
        print(f"  Whisper API erro {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}")
        return []
    except Exception as e:
        print(f"  Whisper API falhou: {e}")
        return []


def transcrever_whisper_local(audio_path: Path) -> list:
    """Transcricao via Whisper local (pip install openai-whisper)."""
    try:
        import whisper
    except ImportError:
        print("  Whisper local nao instalado. Execute: pip install openai-whisper")
        return []

    print("  Transcrevendo via Whisper local (modelo: small)...")
    try:
        model  = whisper.load_model("small")
        result = model.transcribe(str(audio_path), language="pt", verbose=False)
        segs   = result.get("segments", [])
        print(f"  Whisper local: {len(segs)} segmentos")
        return segs
    except Exception as e:
        print(f"  Whisper local falhou: {e}")
        return []


def gerar_srt_placeholder(audio_path: Path, duracao_estimada: float = 60.0) -> list:
    """Gera SRT placeholder quando nenhuma transcricao esta disponivel."""
    print("  Gerando SRT placeholder (sem transcricao real)")
    intervalo = 5.0
    segmentos = []
    t = 0.0
    i = 1
    while t < duracao_estimada:
        segmentos.append({
            "start": t,
            "end":   min(t + intervalo, duracao_estimada),
            "text":  f"[Legenda {i:02d} — substituir por transcricao real]",
        })
        t += intervalo
        i += 1
    return segmentos


def obter_duracao_audio(audio_path: Path) -> float:
    """Tenta obter duracao do audio em segundos."""
    try:
        import wave
        if audio_path.suffix.lower() == ".wav":
            with wave.open(str(audio_path), "r") as wf:
                return wf.getnframes() / wf.getframerate()
    except Exception:
        pass

    try:
        from mutagen.mp3 import MP3
        audio = MP3(str(audio_path))
        return audio.info.length
    except Exception:
        pass

    # Estimativa: 150 palavras/min com locucao medica, ~30s por slide
    return 60.0


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Audio Transcriber")
    parser.add_argument("--audio",  required=True, help="Arquivo de audio (.mp3, .wav, .m4a)")
    parser.add_argument("--output", required=True, help="Pasta de saida das legendas")
    parser.add_argument("--mode",   default="auto",
                        choices=["auto", "api", "local", "placeholder"],
                        help="Modo de transcricao (padrao: auto)")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Arquivo de audio nao encontrado: {args.audio}")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    cfg  = load_config()
    stem = audio_path.stem
    segmentos = []

    print(f"\nTranscricao: {audio_path.name}")
    print(f"Modo: {args.mode}\n")

    if args.mode in ("auto", "api"):
        segmentos = transcrever_whisper_api(audio_path, cfg)

    if not segmentos and args.mode in ("auto", "local"):
        segmentos = transcrever_whisper_local(audio_path)

    if not segmentos:
        duracao = obter_duracao_audio(audio_path)
        segmentos = gerar_srt_placeholder(audio_path, duracao)

    # Gera SRT
    srt_content = texto_para_srt(segmentos)
    srt_path = output_dir / f"{stem}.srt"
    srt_path.write_text(srt_content, encoding="utf-8")
    print(f"\nSRT salvo: {srt_path} ({len(segmentos)} legendas)")

    # Gera TXT puro (para review de copy)
    txt_content = "\n".join(seg.get("text", "").strip() for seg in segmentos)
    txt_path = output_dir / f"{stem}_transcricao.txt"
    txt_path.write_text(txt_content, encoding="utf-8")
    print(f"TXT salvo: {txt_path}")

    # Gera JSON com dados completos
    json_path = output_dir / f"{stem}_segments.json"
    json_path.write_text(json.dumps(segmentos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON salvo: {json_path}")


if __name__ == "__main__":
    main()

"""
Module 2 — Audio Generation
ElevenLabs API → MP3 per chapter chunk → concatenate via FFmpeg
"""

import os, re, subprocess
from elevenlabs.client import ElevenLabs

CHUNK_SIZE = 2400  # chars per API call (safe limit)

def generate_audio(script: dict, config: dict) -> dict:
    api_key  = os.environ["ELEVENLABS_API_KEY"]
    voice_id = os.environ["ELEVENLABS_VOICE_ID"]
    client   = ElevenLabs(api_key=api_key)

    audio_cfg = config["audio"]
    slug      = script["slug"]
    timestamp = script["timestamp"]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "audio", slug)
    os.makedirs(out_dir, exist_ok=True)

    chunks = _split_into_chunks(script["text"], CHUNK_SIZE)
    chunk_files = []

    print(f"[audio_gen] Generating {len(chunks)} audio chunks...")
    for i, chunk in enumerate(chunks):
        chunk_path = os.path.join(out_dir, f"chunk-{i:03d}.mp3")
        print(f"[audio_gen] Chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")

        audio_bytes = client.text_to_speech.convert(
            voice_id=voice_id,
            text=chunk,
            model_id="eleven_multilingual_v2",
            output_format=audio_cfg["output_format"],
            voice_settings={
                "stability":        audio_cfg["stability"],
                "similarity_boost": audio_cfg["similarity_boost"],
                "style":            audio_cfg["style"],
                "use_speaker_boost": audio_cfg["use_speaker_boost"]
            }
        )
        with open(chunk_path, "wb") as f:
            for audio_chunk in audio_bytes:
                f.write(audio_chunk)
        chunk_files.append(chunk_path)

    final_path = os.path.join(out_dir, f"{slug}-{timestamp}-full.mp3")
    _concat_audio(chunk_files, final_path)

    duration = _get_duration(final_path)
    print(f"[audio_gen] Done — {duration:.1f}s → {os.path.basename(final_path)}")

    return {
        "filepath": final_path,
        "chunks":   chunk_files,
        "duration": duration,
        "slug":     slug
    }


def _split_into_chunks(text: str, size: int) -> list:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 > size and current:
            chunks.append(current.strip())
            current = s
        else:
            current += (" " if current else "") + s
    if current:
        chunks.append(current.strip())
    return chunks


def _concat_audio(files: list, output: str):
    list_file = output.replace(".mp3", "_list.txt")
    with open(list_file, "w") as f:
        for fp in files:
            f.write(f"file '{fp}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output
    ], check=True, capture_output=True)
    os.remove(list_file)


def _get_duration(filepath: str) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries",
        "format=duration", "-of", "csv=p=0", filepath
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

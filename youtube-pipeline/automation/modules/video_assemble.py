"""
Module 4 — Video Assembly
FFmpeg → Ken Burns slideshow + audio + subtitles + chapter overlays → MP4
"""

import os, subprocess, glob, math, json

def assemble_video(script: dict, audio: dict, images: dict, srt_path: str, config: dict) -> dict:
    slug        = script["slug"]
    timestamp   = script["timestamp"]
    audio_path  = audio["filepath"]
    duration    = audio["duration"]
    img_dir     = images["directory"]
    img_count   = images["count"]

    vcfg = config["video"]
    secs_per_img = duration / max(img_count, 1)
    fps = vcfg["fps"]
    music_vol = vcfg["background_music_volume"]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "videos")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f"{slug}-{timestamp}.mp4")

    img_list_path = os.path.join(out_dir, f"{slug}-imglist.txt")
    img_files = sorted(glob.glob(os.path.join(img_dir, "*.jpg")))

    if not img_files:
        raise RuntimeError(f"No images found in {img_dir}")

    # Write image list with duration per image
    with open(img_list_path, "w") as f:
        for img in img_files:
            f.write(f"file '{img}'\n")
            f.write(f"duration {secs_per_img:.3f}\n")
        f.write(f"file '{img_files[-1]}'\n")  # last frame hold

    print(f"[video_assemble] Building video: {len(img_files)} images @ {secs_per_img:.1f}s each...")

    # Check for background music — prefer channel-specific full track, then any mp3
    music_dir_out = os.path.join(os.path.dirname(__file__), "..", "output", "music")
    music_dir_assets = os.path.join(os.path.dirname(__file__), "..", "assets", "music")
    music_files = (
        glob.glob(os.path.join(music_dir_out, "*-full.mp3")) or
        glob.glob(os.path.join(music_dir_out, "*.mp3")) or
        glob.glob(os.path.join(music_dir_assets, "*.mp3"))
    )

    if music_files:
        # With background music
        music_path = music_files[0]
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", img_list_path,
            "-i", audio_path,
            "-stream_loop", "-1", "-i", music_path,
            "-filter_complex",
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            f"zoompan=z='min(zoom+0.0008,1.3)':d={int(fps*secs_per_img)}:s=1920x1080,"
            f"fps={fps}[vid];"
            f"[2:a]volume={music_vol}[music];"
            f"[1:a][music]amix=inputs=2:duration=first[audio]",
            "-map", "[vid]", "-map", "[audio]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration), output_path
        ]
    else:
        # Without background music
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", img_list_path,
            "-i", audio_path,
            "-filter_complex",
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            f"fps={fps}[vid]",
            "-map", "[vid]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration), output_path
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr[-2000:]}")

    # Burn subtitles if SRT exists
    if srt_path and os.path.exists(srt_path):
        subtitled_path = output_path.replace(".mp4", "-sub.mp4")
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        sub_cmd = [
            "ffmpeg", "-y", "-i", output_path,
            "-vf", f"subtitles='{srt_escaped}':force_style='FontSize=36,FontName=Arial,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Alignment=2'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy", subtitled_path
        ]
        sub_result = subprocess.run(sub_cmd, capture_output=True, text=True)
        if sub_result.returncode == 0:
            os.replace(subtitled_path, output_path)

    os.remove(img_list_path)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[video_assemble] Done — {size_mb:.1f}MB → {os.path.basename(output_path)}")

    return {"filepath": output_path, "size_mb": size_mb, "duration": duration}


def assemble_from_clips(script: dict, audio: dict, clips: dict, config: dict) -> dict:
    """Assemble final video from MP4 clips (Pexels Videos) + voice + music."""
    slug       = script["slug"]
    timestamp  = script["timestamp"]
    audio_path = audio["filepath"]
    duration   = audio["duration"]
    clip_list  = clips["clips"]

    vcfg      = config["video"]
    fps       = vcfg["fps"]
    music_vol = vcfg["background_music_volume"]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "videos")
    os.makedirs(out_dir, exist_ok=True)
    output_path     = os.path.join(out_dir, f"{slug}-{timestamp}-clips.mp4")
    clips_list_path = os.path.join(out_dir, f"{slug}-clipslist.txt")

    # Loop clips until we fill the full audio duration
    entries        = []
    total_covered  = 0.0
    idx            = 0
    while total_covered < duration:
        clip     = clip_list[idx % len(clip_list)]
        use_secs = min(clip["duration"], duration - total_covered)
        entries.append((clip["path"], use_secs))
        total_covered += use_secs
        idx += 1

    with open(clips_list_path, "w", encoding="utf-8") as f:
        for path, secs in entries:
            safe = path.replace("\\", "/")
            f.write(f"file '{safe}'\n")
            f.write(f"inpoint 0\n")
            f.write(f"outpoint {secs:.3f}\n")

    print(f"[video_assemble] Building from {len(entries)} clip segments "
          f"({len(clip_list)} unique clips)...")

    music_dir_out    = os.path.join(os.path.dirname(__file__), "..", "output", "music")
    music_dir_assets = os.path.join(os.path.dirname(__file__), "..", "assets", "music")
    music_files = (
        glob.glob(os.path.join(music_dir_out, "*-full.mp3")) or
        glob.glob(os.path.join(music_dir_out, "*.mp3")) or
        glob.glob(os.path.join(music_dir_assets, "*.mp3"))
    )

    scale_filter = (
        f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
        f"crop=1920:1080,fps={fps}[vid]"
    )

    if music_files:
        music_path = music_files[0]
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", clips_list_path,
            "-i", audio_path,
            "-stream_loop", "-1", "-i", music_path,
            "-filter_complex",
            f"{scale_filter};"
            f"[2:a]volume={music_vol}[music];"
            f"[1:a][music]amix=inputs=2:duration=first[audio]",
            "-map", "[vid]", "-map", "[audio]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration), output_path,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", clips_list_path,
            "-i", audio_path,
            "-filter_complex", scale_filter,
            "-map", "[vid]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration), output_path,
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error:\n{result.stderr[-3000:]}")

    os.remove(clips_list_path)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[video_assemble] Done — {size_mb:.1f}MB → {os.path.basename(output_path)}")
    return {"filepath": output_path, "size_mb": size_mb, "duration": duration}

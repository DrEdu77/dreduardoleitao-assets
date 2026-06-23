"""
YouTube Faceless Pipeline — Main Orchestrator
Multi-Channel | Dr. Eduardo Leitão

Usage:
  python pipeline.py --title "50 Shocking Facts About Your Spine"
  python pipeline.py --title "..." --channel cryptotruth
  python pipeline.py --title "..." --skip-script
  python pipeline.py --title "..." --dry-run
  python pipeline.py --list-channels

Channels:
  bodytruth    (default) — Health/spine, CPM $10-15
  cryptotruth            — Cryptocurrency, CPM $30-60
"""

import os, sys, json, argparse, time
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Import modules
sys.path.insert(0, str(Path(__file__).parent))
from modules.script_gen    import generate_script
from modules.audio_gen     import generate_audio
from modules.image_fetch   import fetch_images
from modules.video_assemble import assemble_video
from modules.thumbnail_gen import generate_thumbnail
from modules.seo_gen       import generate_seo
from modules.youtube_upload import upload_video

CHANNEL_CONFIGS = {
    "bodytruth":    "config.json",
    "cryptotruth":  "config-cryptotruth.json",
    "wealthcodes":  "config-wealthcodes.json",
    "catfacts":     "config-catfacts.json",
    "luxurydogs":   "config-luxurydogs.json",
    "soccertruth":  "config-soccertruth.json",
}

def load_config(channel: str = "bodytruth") -> dict:
    filename = CHANNEL_CONFIGS.get(channel.lower())
    if not filename:
        raise ValueError(f"Unknown channel: '{channel}'. Available: {list(CHANNEL_CONFIGS.keys())}")
    config_path = Path(__file__).parent / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_pipeline(title: str, channel: str = "bodytruth",
                 skip_script: bool = False,
                 skip_audio: bool = False, dry_run: bool = False,
                 existing_script_path: str = None):

    config = load_config(channel)
    channel_name = config["channel"]["name"]
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f" {channel_name.upper()} PIPELINE — {title[:50]}")
    print(f"{'='*60}\n")

    # ── STEP 1: Script ──────────────────────────────────────────
    if existing_script_path:
        print("[STEP 1] Loading existing script...")
        with open(existing_script_path, "r", encoding="utf-8") as f:
            text = f.read()
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d-%H%M")
        script = {"title": title, "slug": slug, "text": text,
                  "word_count": len(text.split()), "chapters": [],
                  "filepath": existing_script_path, "timestamp": ts}
    elif not skip_script:
        print("[STEP 1] Generating script...")
        script = generate_script(title, config)
    else:
        raise ValueError("Must provide --title and either generate or --script path")

    print(f"         ✅ Script ready — {script['word_count']} words\n")

    # ── STEP 2: Audio ───────────────────────────────────────────
    if not skip_audio:
        print("[STEP 2] Generating audio (ElevenLabs)...")
        audio = generate_audio(script, config)
        print(f"         ✅ Audio ready — {audio['duration']:.0f}s\n")
    else:
        print("[STEP 2] Audio generation skipped\n")
        audio = {"filepath": None, "duration": 2700, "chunks": []}

    # ── STEP 3: Images ──────────────────────────────────────────
    print("[STEP 3] Fetching images (Pexels)...")
    images = fetch_images(script, config)
    print(f"         ✅ {images['count']} images ready\n")

    # ── STEP 4: Video Assembly ──────────────────────────────────
    if audio["filepath"]:
        print("[STEP 4] Assembling video (FFmpeg)...")
        srt_path = None  # SRT generation optional
        video = assemble_video(script, audio, images, srt_path, config)
        print(f"         ✅ Video ready — {video['size_mb']:.1f}MB\n")
    else:
        print("[STEP 4] Skipped (no audio)\n")
        video = {"filepath": None, "size_mb": 0, "duration": 0}

    # ── STEP 5: Thumbnail ───────────────────────────────────────
    print("[STEP 5] Generating thumbnail...")
    thumbnail = generate_thumbnail(title, script, config)
    print(f"         ✅ Thumbnail ready\n")

    # ── STEP 6: SEO ─────────────────────────────────────────────
    print("[STEP 6] Generating SEO...")
    seo = generate_seo(script, config)
    print(f"         ✅ SEO ready — {len(seo.get('tags',[]))} tags\n")

    # ── STEP 7: YouTube Upload ──────────────────────────────────
    if not dry_run and video["filepath"]:
        print("[STEP 7] Uploading to YouTube...")
        result = upload_video(video, seo, thumbnail, config)
        print(f"         ✅ Published → {result['url']}")
        print(f"         📅 Scheduled: {result['scheduled']}\n")
    else:
        result = {"video_id": None, "url": None, "dry_run": True}
        print("[STEP 7] Dry run — YouTube upload skipped\n")

    elapsed = time.time() - t0
    print(f"{'='*60}")
    print(f" PIPELINE COMPLETE in {elapsed/60:.1f} minutes")
    if result.get("url"):
        print(f" YouTube URL: {result['url']}")
    print(f"{'='*60}\n")

    return {
        "script":    script,
        "audio":     audio,
        "images":    images,
        "video":     video,
        "thumbnail": thumbnail,
        "seo":       seo,
        "upload":    result
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Faceless Multi-Channel Pipeline")
    parser.add_argument("--title",          required=False, default=None, help="Video title")
    parser.add_argument("--channel",        default="bodytruth",
                        choices=list(CHANNEL_CONFIGS.keys()),
                        help="Channel to produce for (default: bodytruth)")
    parser.add_argument("--script",         default=None,  help="Path to existing script file")
    parser.add_argument("--skip-script",    action="store_true")
    parser.add_argument("--skip-audio",     action="store_true")
    parser.add_argument("--dry-run",        action="store_true", help="Skip YouTube upload")
    parser.add_argument("--list-channels",  action="store_true", help="List available channels")
    args = parser.parse_args()

    if args.list_channels:
        print("\nAvailable channels:")
        for key, cfg_file in CHANNEL_CONFIGS.items():
            cfg_path = Path(__file__).parent / cfg_file
            exists = "OK" if cfg_path.exists() else "MISSING CONFIG"
            print(f"  --channel {key:<14} ({cfg_file}) [{exists}]")
        print()
        sys.exit(0)

    if not args.title:
        parser.error("--title is required unless --list-channels is used")

    run_pipeline(
        title=args.title,
        channel=args.channel,
        skip_script=args.skip_script,
        skip_audio=args.skip_audio,
        dry_run=args.dry_run,
        existing_script_path=args.script
    )

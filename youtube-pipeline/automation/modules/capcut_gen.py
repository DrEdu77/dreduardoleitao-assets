"""
Module 7 — CapCut Project Generator
pycapcut → builds a CapCut draft with voice + B-roll clips, ready to Export.

User workflow after this runs:
  1. Open CapCut on Windows
  2. Find the draft (name shown in terminal)
  3. Add music from CapCut music library (recommended: cinematic/documentary)
  4. Click Export → 4K / 60fps
  5. Run youtube_upload separately with the exported file
"""

import os

CAPCUT_DRAFT_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", "C:/Users/User/AppData/Local"),
    "CapCut", "User Data", "Projects", "com.lveditor.draft"
)


def generate_capcut_project(script: dict, audio: dict, clips: dict, config: dict) -> dict:
    try:
        import pycapcut
    except ImportError:
        raise RuntimeError("pycapcut not installed — run: python -m pip install pyCapCut")

    if not os.path.isdir(CAPCUT_DRAFT_DIR):
        raise RuntimeError(f"CapCut draft folder not found:\n  {CAPCUT_DRAFT_DIR}\nIs CapCut installed?")

    title       = script["title"]
    voice_path  = os.path.abspath(audio["filepath"])
    voice_secs  = audio["duration"]
    clip_list   = clips["clips"]
    channel     = config["channel"]["name"]

    draft_name = f"{channel} — {title[:45]}"
    SEC        = pycapcut.SEC  # 1_000_000 microseconds

    print(f"[capcut_gen] Creating draft: '{draft_name}'")
    print(f"[capcut_gen] Voice: {voice_secs/60:.1f} min | Clips: {len(clip_list)}")

    draft_folder = pycapcut.DraftFolder(CAPCUT_DRAFT_DIR)
    sf           = draft_folder.create_draft(draft_name, 1920, 1080, fps=30,
                                             allow_replace=True)

    # ── Voice audio track ────────────────────────────────────────────────────
    voice_mat = pycapcut.AudioMaterial(voice_path, "Voice — " + channel)
    sf.add_material(voice_mat)
    sf.add_track(pycapcut.TrackType.audio, "voice")
    sf.add_segment(
        pycapcut.AudioSegment(
            voice_mat,
            pycapcut.Timerange(0, int(voice_secs * SEC)),
            volume=1.0,
        ),
        track_name="voice",
    )

    # ── B-roll video track ───────────────────────────────────────────────────
    sf.add_track(pycapcut.TrackType.video, "broll")

    # Pre-register all unique materials to avoid duplicates in the project
    materials_by_path: dict[str, pycapcut.VideoMaterial] = {}
    for clip in clip_list:
        p = clip["path"]
        if p not in materials_by_path:
            mat = pycapcut.VideoMaterial(p)
            sf.add_material(mat)
            materials_by_path[p] = mat

    # Fill the entire voice duration with looping clips
    current_us = 0
    end_us     = int(voice_secs * SEC)
    idx        = 0

    while current_us < end_us:
        clip   = clip_list[idx % len(clip_list)]
        mat    = materials_by_path[clip["path"]]
        use_s  = min(clip["duration"], (end_us - current_us) / SEC)
        use_us = int(use_s * SEC)
        if use_us <= 0:
            break

        sf.add_segment(
            pycapcut.VideoSegment(
                mat,
                pycapcut.Timerange(current_us, use_us),
                source_timerange=pycapcut.Timerange(0, use_us),
                volume=0.0,  # mute clip's original audio
            ),
            track_name="broll",
        )

        current_us += use_us
        idx        += 1

    # ── Save ─────────────────────────────────────────────────────────────────
    sf.save()

    print(f"\n[capcut_gen] Draft saved successfully!")
    print(f"  Draft name : {draft_name}")
    print(f"  Location   : {CAPCUT_DRAFT_DIR}")
    print(f"  Clips used : {idx} segments ({len(clip_list)} unique)")
    print(f"\n  NEXT STEPS:")
    print(f"  1. Open CapCut")
    print(f"  2. Find draft: '{draft_name}'")
    print(f"  3. Add music: Music > CapCut Audio > Documentary / Cinematic")
    print(f"  4. Click Export > 1080p or 4K > Export")
    print(f"  5. Upload the exported file to YouTube")

    return {
        "draft_name":   draft_name,
        "draft_folder": CAPCUT_DRAFT_DIR,
        "segments":     idx,
        "clip_count":   len(clip_list),
    }

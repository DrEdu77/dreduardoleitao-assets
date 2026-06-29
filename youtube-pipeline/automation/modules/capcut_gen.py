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

    if not clip_list:
        raise RuntimeError("No clips available — check that clip download succeeded (0 clips found)")

    import re
    draft_name = re.sub(r'[\\/:*?"<>|]', '-', f"{channel} — {title[:45]}").strip()
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

    # Pre-register materials and read ACTUAL file durations (pyCapCut probes the file)
    materials_by_path:  dict[str, pycapcut.VideoMaterial] = {}
    actual_duration_us: dict[str, int]                    = {}
    for clip in clip_list:
        p = clip["path"]
        if p not in materials_by_path:
            mat = pycapcut.VideoMaterial(p)
            sf.add_material(mat)
            materials_by_path[p]  = mat
            actual_duration_us[p] = mat.duration   # microseconds from file metadata

    # Use each clip ONCE — no repeats — in chapter order
    current_us = 0
    end_us     = int(voice_secs * SEC)
    idx        = 0

    for clip in clip_list:
        if current_us >= end_us:
            break

        mat       = materials_by_path[clip["path"]]
        real_us   = actual_duration_us[clip["path"]]
        remaining = end_us - current_us
        use_us    = min(int(clip["duration"] * SEC), real_us, remaining)
        if use_us <= 0:
            continue

        sf.add_segment(
            pycapcut.VideoSegment(
                mat,
                pycapcut.Timerange(current_us, use_us),
                source_timerange=pycapcut.Timerange(0, use_us),
                volume=0.0,
            ),
            track_name="broll",
        )

        current_us += use_us
        idx        += 1

    # If clips ran out before voice ended, fill remainder looping from start
    if current_us < end_us:
        print(f"[capcut_gen] Clips ended at {current_us/SEC:.0f}s — looping to fill {end_us/SEC:.0f}s")
        loop_idx = 0
        while current_us < end_us:
            clip      = clip_list[loop_idx % len(clip_list)]
            mat       = materials_by_path[clip["path"]]
            real_us   = actual_duration_us[clip["path"]]
            remaining = end_us - current_us
            use_us    = min(int(clip["duration"] * SEC), real_us, remaining)
            if use_us <= 0:
                break
            sf.add_segment(
                pycapcut.VideoSegment(
                    mat,
                    pycapcut.Timerange(current_us, use_us),
                    source_timerange=pycapcut.Timerange(0, use_us),
                    volume=0.0,
                ),
                track_name="broll",
            )
            current_us += use_us
            loop_idx   += 1

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

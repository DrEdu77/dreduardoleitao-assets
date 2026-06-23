"""
Module 1 — Script Generation
Claude API → 7,500-word YouTube script in English
"""

import os, json, re
from datetime import datetime
import anthropic

def generate_script(title: str, config: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    facts   = config["script"]["facts_count"]
    words   = config["script"]["word_count_target"]
    niche   = config["channel"]["niche"]
    audience = config["channel"]["target_audience"]

    prompt = f"""You are a professional YouTube scriptwriter for educational documentary content targeting {audience}.

Write a complete 45-minute YouTube script for a video titled: "{title}"

--- CONTENT RULES ---
- {words} words total
- Hook (30 sec): Start with a shocking, visceral statement. NO greetings, NO "welcome back". Start mid-action.
- Intro (90 sec): Tease 3 of the most surprising facts. Create urgency to watch to the end.
- {facts} facts organized in 8 chapters (6-7 facts each)
- Each fact: 3-4 sentences (state the fact → explain WHY it's surprising → real implication for the viewer)
- Chapter markers: [CHAPTER X: CHAPTER TITLE]
- Mid-roll markers: [MID-ROLL] — place at facts 7, 14, 21, 28, 35, 42, 48
- CTA (60 sec): Ask viewers what surprised them most. Tell them to subscribe. Tease the next video.

--- TONE ---
Like a brilliant, calm expert friend who respects your intelligence.
No sensationalism. No empty hype. Just powerful, true, useful information.
Speak directly to the viewer: "you", "your", "you'll discover".

--- AUDIENCE ---
{audience} who care about their health, body, and longevity.
Connect facts to their daily life, work, mobility, and aging.

--- FORMAT OUTPUT ---
Return ONLY the script text. No meta-commentary. Start directly with the hook sentence.
Include [CHAPTER X: TITLE] and [MID-ROLL] markers exactly as specified.
"""

    print(f"[script_gen] Generating script for: {title}")
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}]
    )
    script_text = response.content[0].text

    chapters = _parse_chapters(script_text)
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{slug}-{timestamp}.txt"

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "scripts")
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(script_text)

    word_count = len(script_text.split())
    print(f"[script_gen] Done — {word_count} words, {len(chapters)} chapters → {filename}")

    return {
        "title": title,
        "slug": slug,
        "text": script_text,
        "word_count": word_count,
        "chapters": chapters,
        "filepath": filepath,
        "timestamp": timestamp
    }


def _parse_chapters(text: str) -> list:
    chapters = []
    lines = text.split('\n')
    current = None
    for i, line in enumerate(lines):
        m = re.match(r'\[CHAPTER\s+(\d+):\s*(.+?)\]', line, re.IGNORECASE)
        if m:
            if current:
                current["end_line"] = i - 1
                chapters.append(current)
            current = {
                "number": int(m.group(1)),
                "title": m.group(2).strip(),
                "start_line": i,
                "end_line": None
            }
    if current:
        current["end_line"] = len(lines) - 1
        chapters.append(current)
    return chapters

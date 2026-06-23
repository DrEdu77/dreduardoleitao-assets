"""
Module 6 — SEO Generation
Claude API → title + description + 25 tags + hashtags
"""

import os, json, re
import anthropic

def generate_seo(script: dict, config: dict) -> dict:
    client   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    title    = script["title"]
    chapters = script.get("chapters", [])
    slug     = script["slug"]
    timestamp = script["timestamp"]

    chapter_list = "\n".join(
        [f"Chapter {c['number']}: {c['title']}" for c in chapters]
    ) if chapters else "N/A"

    prompt = f"""You are a YouTube SEO expert specializing in educational health content for Americans 50+.

Video title: "{title}"
Chapters: {chapter_list}
Channel: BodyTruth (faceless educational channel, health/body facts)

Generate the following and return as valid JSON:

{{
  "optimized_title": "final title max 70 chars with number + power word",
  "description": "complete 400-word description with natural keywords, chapter timestamps (use approximate times), call to subscribe, 3 Amazon book recommendations (no actual links, just titles), and end with 5 hashtags",
  "tags": ["list of exactly 25 tags mixing broad and long-tail"],
  "hashtags": ["5 hashtags for description"],
  "end_screen_script": "20-second spoken script for end screen — tease next video, ask to subscribe",
  "thumbnail_text": {{
    "main": "max 3 words in CAPS",
    "sub": "4-6 words"
  }}
}}

IMPORTANT: Return only valid JSON, no markdown, no explanation."""

    print(f"[seo_gen] Generating SEO for: {title}")
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # Clean up markdown code blocks if present
    raw = re.sub(r'^```(?:json)?\n?', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'\n?```$', '', raw, flags=re.MULTILINE)

    seo = json.loads(raw)

    # Add default tags from config
    default_tags = config["youtube"]["default_tags"]
    all_tags = list(dict.fromkeys(seo.get("tags", []) + default_tags))[:25]
    seo["tags"] = all_tags

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "seo")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{slug}-{timestamp}-seo.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(seo, f, ensure_ascii=False, indent=2)

    print(f"[seo_gen] Done → {os.path.basename(out_path)}")
    return seo

"""
Module 5 — Thumbnail Generation
Pillow → 1280x720 YouTube thumbnail automatically
"""

import os, textwrap
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(title: str, script: dict, config: dict, bg_image_url: str = None) -> dict:
    slug         = script["slug"]
    timestamp    = script["timestamp"]
    tcfg         = config["thumbnail"]
    channel_name = config["channel"]["name"]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "thumbnails")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f"{slug}-{timestamp}.jpg")

    W, H = tcfg["width"], tcfg["height"]

    # Colors — support both key naming conventions
    bg_color      = tcfg.get("background_color", "#080808")
    primary_color = tcfg.get("text_primary_color", tcfg.get("title_color", "#FFD700"))
    second_color  = tcfg.get("text_secondary_color", tcfg.get("subtitle_color", "#FFFFFF"))
    electric      = tcfg.get("electric_color", primary_color)
    premium       = tcfg.get("premium_color", second_color)

    # Base gradient from background_color
    img  = _make_gradient(W, H, bg_color)
    draw = ImageDraw.Draw(img)

    # Accent lines top/bottom
    draw.rectangle([0, 0, W, 8], fill=premium)
    draw.rectangle([0, H-8, W, H], fill=premium)

    # Parse title into main + sub lines
    main_text, sub_text = _parse_title(title)

    # Fonts
    font_main = _get_font(100)
    font_sub  = _get_font(52)
    font_tag  = _get_font(36)

    # Main text (electric color, large)
    _draw_text_centered(draw, main_text, font_main, W, H * 0.37, electric, stroke=5)

    # Divider line
    draw.rectangle([W//2 - 200, int(H*0.58)-4, W//2 + 200, int(H*0.58)+4], fill=premium)

    # Sub text (premium/gold color)
    _draw_text_centered(draw, sub_text, font_sub, W, H * 0.70, premium, stroke=3)

    # Channel tag bottom right
    _draw_text_centered(draw, channel_name.upper(), font_tag, W, H * 0.90, "#888888", stroke=1)

    img.save(output_path, "JPEG", quality=95)
    print(f"[thumbnail_gen] Done -> {os.path.basename(output_path)}")
    return {"filepath": output_path}


def _parse_title(title: str):
    import re
    # Priority 1: if there's a number anywhere in title, use "NUMBER KEYWORD" as main
    m = re.search(r'(\d+)\s+([\w\s]{3,25}?)(?:\s+(?:Nobody|That|You|About|For|In|The|Of))', title, re.IGNORECASE)
    if m:
        number = m.group(1)
        keyword = m.group(2).strip()
        # Build short main: "50 WEALTH CODES"
        main = f"{number} {keyword}".upper()
        # Sub: everything after the number phrase, shortened
        rest = title[m.start():].split(None, len(keyword.split()) + 1)
        after = " ".join(rest[len(keyword.split()) + 1:]) if len(rest) > len(keyword.split()) + 1 else ""
        if not after:
            after = title.split("—")[-1].strip() if "—" in title else title.split()[-4:]
        return main, (after[:45] + "...") if len(after) > 45 else after

    # Priority 2: split at em-dash, use SHORTER part as main
    if "—" in title:
        parts = title.split("—", 1)
        p0, p1 = parts[0].strip(), parts[1].strip()
        # Use whichever part is shorter as main text (more thumbnail-friendly)
        main = (p0 if len(p0) <= len(p1) else p1).upper()
        sub  = p1 if len(p0) <= len(p1) else p0
        # Cap main at 30 chars
        if len(main) > 30:
            words = main.split()
            main = " ".join(words[:4])
        return main, (sub[:50] + "...") if len(sub) > 50 else sub

    # Fallback: first 4 words as main
    words = title.split()
    return " ".join(words[:4]).upper(), " ".join(words[4:15])


def _make_gradient(W: int, H: int, bg_hex: str = "#080808") -> Image.Image:
    # Parse hex color
    bg_hex = bg_hex.lstrip("#")
    r0 = int(bg_hex[0:2], 16)
    g0 = int(bg_hex[2:4], 16)
    b0 = int(bg_hex[4:6], 16)

    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        factor = y / H
        r = min(255, int(r0 + factor * 20))
        g = min(255, int(g0 + factor * 15))
        b = min(255, int(b0 + factor * 10))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img


def _get_font(size: int) -> ImageFont.ImageFont:
    font_paths = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()


def _draw_text_centered(draw, text: str, font, canvas_w: int, y_center: float,
                         color: str, stroke: int = 2):
    lines = textwrap.wrap(text, width=24)
    line_h = font.size + 10
    total_h = len(lines) * line_h
    y = y_center - total_h / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (canvas_w - w) / 2
        draw.text((x, y), line, font=font, fill=color,
                  stroke_width=stroke, stroke_fill="#000000")
        y += line_h

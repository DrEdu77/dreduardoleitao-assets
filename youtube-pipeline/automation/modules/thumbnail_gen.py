"""
Module 5 — Thumbnail Generation
Pillow → 1280x720 YouTube thumbnail automatically
"""

import os, requests, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_thumbnail(title: str, script: dict, config: dict, bg_image_url: str = None) -> dict:
    slug      = script["slug"]
    timestamp = script["timestamp"]
    tcfg      = config["thumbnail"]

    out_dir = os.path.join(os.path.dirname(__file__), "..", "output", "thumbnails")
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f"{slug}-{timestamp}.jpg")

    W, H = tcfg["width"], tcfg["height"]

    # Base image: download from Pexels or use gradient
    if bg_image_url:
        try:
            img_data = requests.get(bg_image_url, timeout=15).content
            img = Image.open(__import__('io').BytesIO(img_data)).convert("RGB")
            img = img.resize((W, H), Image.LANCZOS)
        except:
            img = _make_gradient(W, H)
    else:
        img = _make_gradient(W, H)

    # Dark overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * tcfg["overlay_opacity"])))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Parse title: extract number + main text
    main_text, sub_text = _parse_title(title)

    # Main text (large, yellow)
    font_main = _get_font(110)
    font_sub  = _get_font(56)
    font_tag  = _get_font(38)

    # Draw main text centered
    _draw_text_centered(draw, main_text, font_main, W, H * 0.38, tcfg["title_color"], stroke=4)

    # Draw subtitle
    _draw_text_centered(draw, sub_text, font_sub, W, H * 0.62, tcfg["subtitle_color"], stroke=2)

    # Channel tag bottom right
    _draw_text_centered(draw, "BodyTruth", font_tag, W, H * 0.88, "#AAAAAA", stroke=1)

    img.save(output_path, "JPEG", quality=95)
    print(f"[thumbnail_gen] Done → {os.path.basename(output_path)}")
    return {"filepath": output_path}


def _parse_title(title: str):
    import re
    m = re.match(r'^(\d+\s+\w+)\s+(.+)$', title)
    if m:
        return m.group(1).upper(), m.group(2)
    words = title.split()
    half = len(words) // 2
    return " ".join(words[:half]).upper(), " ".join(words[half:])


def _make_gradient(W: int, H: int) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(10 + (y / H) * 30)
        g = int(5  + (y / H) * 10)
        b = int(20 + (y / H) * 60)
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
    lines = textwrap.wrap(text, width=22)
    line_h = font.size + 8
    total_h = len(lines) * line_h
    y = y_center - total_h / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (canvas_w - w) / 2
        draw.text((x, y), line, font=font, fill=color,
                  stroke_width=stroke, stroke_fill="#000000")
        y += line_h

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create-carousel.py — [Prioridade 3] Cria carrossel PNG com design Corpo Vivo

Gera slides 1080x1080 com paleta verde-musgo, tipografia profissional e layout estrategico.
Nao requer API externa — usa Pillow.

Uso:
  python3 -X utf8 create-carousel.py --tema "hernia de disco" --slides 6 --output ./images/
  python3 -X utf8 create-carousel.py --content slides.json --output ./images/
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_OK = True
except ImportError:
    PIL_OK = False

# Paleta Corpo Vivo Alpha
VERDE_MUSGO   = (26,  74,  64)   # #1A4A40
VERDE_CLARO   = (74, 155, 143)   # #4A9B8F
BRANCO        = (255, 255, 255)
CINZA_CLARO   = (248, 249, 250)  # #F8F9FA
DOURADO       = (201, 168,  76)  # #C9A84C — acento premium
PRETO_SUAVE   = ( 30,  30,  30)

SIZE = (1080, 1080)

# Templates de slides por tipo
SLIDE_TEMPLATES = {
    "cover": {
        "bg_color":   VERDE_MUSGO,
        "layout":     "centered_big_text",
        "text_color": BRANCO,
        "accent":     DOURADO,
    },
    "problem": {
        "bg_color":   CINZA_CLARO,
        "layout":     "split_left",
        "text_color": PRETO_SUAVE,
        "accent":     VERDE_MUSGO,
    },
    "tip": {
        "bg_color":   BRANCO,
        "layout":     "numbered_list",
        "text_color": PRETO_SUAVE,
        "accent":     VERDE_CLARO,
    },
    "quote": {
        "bg_color":   VERDE_CLARO,
        "layout":     "centered_quote",
        "text_color": BRANCO,
        "accent":     BRANCO,
    },
    "cta": {
        "bg_color":   VERDE_MUSGO,
        "layout":     "cta_final",
        "text_color": BRANCO,
        "accent":     DOURADO,
    },
}

# Estrutura padrao de carrossel clinico (6 slides)
DEFAULT_STRUCTURE = [
    {"type": "cover",   "tag": "VOCE SABIA?",     "title": "{hook}",     "subtitle": "@corpovivomed"},
    {"type": "problem", "tag": "O PROBLEMA",       "title": "Por que a dor persiste?", "body": "{problema}"},
    {"type": "tip",     "tag": "A SOLUCAO",        "title": "Como tratamos na Corpo Vivo", "items": ["{s1}", "{s2}", "{s3}"]},
    {"type": "tip",     "tag": "NOSSO DIFERENCIAL","title": "Por que somos diferentes",   "items": ["{d1}", "{d2}", "{d3}"]},
    {"type": "quote",   "tag": "RESULTADO",        "title": '"{resultado}"',              "subtitle": "— Dr. Eduardo Leitao"},
    {"type": "cta",     "tag": "AGENDE AGORA",     "title": "Dor ninguem merece",         "contact": "(11) 3042-1334\n@corpovivomed"},
]


def draw_slide_cover(draw, img, slide: dict, fonts: dict):
    w, h = SIZE
    tmpl = SLIDE_TEMPLATES["cover"]

    # Barra superior
    draw.rectangle([(0, 0), (w, 8)], fill=DOURADO)

    # Tag
    tag = slide.get("tag", "CORPO VIVO")
    draw.text((w // 2, 120), tag, fill=DOURADO, font=fonts["tag"], anchor="mm")

    # Titulo grande
    title = slide.get("title", "Titulo")
    _draw_wrapped_text(draw, title, (w // 2, h // 2 - 40), fonts["title_big"],
                       BRANCO, max_width=900, align="center")

    # Logo / handle
    subtitle = slide.get("subtitle", "@corpovivomed")
    draw.text((w // 2, h - 100), subtitle, fill=VERDE_CLARO, font=fonts["small"], anchor="mm")

    # Barra inferior
    draw.rectangle([(0, h - 8), (w, h)], fill=DOURADO)


def draw_slide_problem(draw, img, slide: dict, fonts: dict):
    w, h = SIZE
    # Fundo com retangulo esquerdo colorido
    draw.rectangle([(0, 0), (12, h)], fill=VERDE_MUSGO)

    tag = slide.get("tag", "")
    draw.text((60, 80), tag, fill=VERDE_MUSGO, font=fonts["tag"], anchor="lm")

    title = slide.get("title", "")
    _draw_wrapped_text(draw, title, (60, 220), fonts["title"],
                       PRETO_SUAVE, max_width=940, align="left")

    body = slide.get("body", "")
    if body:
        _draw_wrapped_text(draw, body, (60, 420), fonts["body"],
                           (80, 80, 80), max_width=940, align="left")


def draw_slide_tip(draw, img, slide: dict, fonts: dict):
    w, h = SIZE
    tmpl = SLIDE_TEMPLATES["tip"]

    tag = slide.get("tag", "")
    draw.text((w // 2, 90), tag, fill=VERDE_CLARO, font=fonts["tag"], anchor="mm")

    title = slide.get("title", "")
    _draw_wrapped_text(draw, title, (w // 2, 200), fonts["title"],
                       PRETO_SUAVE, max_width=900, align="center")

    # Linha separadora
    draw.rectangle([(80, 280), (w - 80, 284)], fill=VERDE_CLARO)

    items = slide.get("items", [])
    y = 340
    for i, item in enumerate(items[:5], 1):
        # Numero circulado
        cx, cy = 110, y + 28
        draw.ellipse([(cx - 28, cy - 28), (cx + 28, cy + 28)], fill=VERDE_MUSGO)
        draw.text((cx, cy), str(i), fill=BRANCO, font=fonts["number"], anchor="mm")

        # Texto do item
        _draw_wrapped_text(draw, item, (160, y + 4), fonts["body"],
                           PRETO_SUAVE, max_width=860, align="left")
        y += 160


def draw_slide_quote(draw, img, slide: dict, fonts: dict):
    w, h = SIZE
    # Aspas decorativas grandes
    draw.text((80, 60), "“", fill=(255, 255, 255, 80), font=fonts["title_big"], anchor="lt")

    title = slide.get("title", "")
    _draw_wrapped_text(draw, title, (w // 2, h // 2 - 60), fonts["quote"],
                       BRANCO, max_width=880, align="center")

    subtitle = slide.get("subtitle", "")
    if subtitle:
        draw.text((w // 2, h - 180), subtitle, fill=DOURADO, font=fonts["body"], anchor="mm")


def draw_slide_cta(draw, img, slide: dict, fonts: dict):
    w, h = SIZE

    # Barra decorativa topo
    draw.rectangle([(0, 0), (w, 6)], fill=DOURADO)

    tag = slide.get("tag", "AGENDE AGORA")
    draw.text((w // 2, 100), tag, fill=DOURADO, font=fonts["tag"], anchor="mm")

    title = slide.get("title", "")
    _draw_wrapped_text(draw, title, (w // 2, h // 2 - 80), fonts["title_big"],
                       BRANCO, max_width=900, align="center")

    contact = slide.get("contact", "(11) 3042-1334")
    for i, line in enumerate(contact.split("\n")):
        draw.text((w // 2, h - 260 + i * 70), line,
                  fill=VERDE_CLARO, font=fonts["subtitle"], anchor="mm")

    # Barra inferior
    draw.rectangle([(0, h - 6), (w, h)], fill=DOURADO)


def _draw_wrapped_text(draw, text, pos, font, color, max_width=900, align="left"):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        try:
            bbox = font.getbbox(test)
            w    = bbox[2] - bbox[0]
        except Exception:
            w = len(test) * 20
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    x, y = pos
    line_h = 80
    total_h = len(lines) * line_h
    if align == "center":
        y -= total_h // 2

    for line in lines:
        if align == "center":
            draw.text((x, y), line, fill=color, font=font, anchor="mm")
        else:
            draw.text((x, y), line, fill=color, font=font, anchor="lm")
        y += line_h


def load_fonts():
    """Tenta carregar fontes do sistema. Fallback para default do Pillow."""
    from PIL import ImageFont

    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    def try_font(size):
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    return {
        "title_big": try_font(72),
        "title":     try_font(56),
        "subtitle":  try_font(44),
        "body":      try_font(36),
        "tag":       try_font(28),
        "small":     try_font(24),
        "quote":     try_font(48),
        "number":    try_font(32),
    }


def create_slide(slide: dict, index: int, output_dir: Path, fonts: dict) -> Path:
    slide_type = slide.get("type", "tip")
    tmpl       = SLIDE_TEMPLATES.get(slide_type, SLIDE_TEMPLATES["tip"])
    bg_color   = tmpl["bg_color"]

    img  = Image.new("RGB", SIZE, bg_color)
    draw = ImageDraw.Draw(img)

    dispatch = {
        "cover":   draw_slide_cover,
        "problem": draw_slide_problem,
        "tip":     draw_slide_tip,
        "quote":   draw_slide_quote,
        "cta":     draw_slide_cta,
    }
    draw_fn = dispatch.get(slide_type, draw_slide_tip)
    draw_fn(draw, img, slide, fonts)

    out_path = output_dir / f"carousel_slide_{index:02d}.png"
    img.save(str(out_path), "PNG", optimize=True)
    print(f"  Slide {index:02d} [{slide_type}]: {out_path.name}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Criador de Carrossel")
    parser.add_argument("--tema",    help="Tema clinico para gerar estrutura automatica")
    parser.add_argument("--content", help="Arquivo JSON com conteudo dos slides")
    parser.add_argument("--slides",  type=int, default=6, help="Numero de slides (3-10)")
    parser.add_argument("--output",  required=True, help="Pasta de saida")
    args = parser.parse_args()

    if not PIL_OK:
        print("Erro: Pillow nao instalado. Execute: pip install Pillow")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.content:
        slides_data = json.loads(Path(args.content).read_text(encoding="utf-8-sig"))
    else:
        tema = args.tema or "Saude e Qualidade de Vida"
        slides_data = DEFAULT_STRUCTURE[:args.slides]
        # Substitui placeholders pelo tema
        slides_str = json.dumps(slides_data)
        for key in ["{hook}", "{problema}", "{s1}", "{s2}", "{s3}",
                    "{d1}", "{d2}", "{d3}", "{resultado}"]:
            slides_str = slides_str.replace(key, f"[{tema}]")
        slides_data = json.loads(slides_str)

    print(f"\nCriando carrossel: {len(slides_data)} slides → {output_dir}")
    fonts  = load_fonts()
    paths  = [create_slide(s, i + 1, output_dir, fonts) for i, s in enumerate(slides_data)]
    print(f"\n{len(paths)} slides criados em {output_dir}")


if __name__ == "__main__":
    main()

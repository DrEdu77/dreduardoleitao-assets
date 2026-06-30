"""
make_thumbnails.py — SoccerTruth Thumbnails
Cria miniaturas profissionais 1280x720 para V01 e V02

V01: Messi vs Pelé  — split esquerda/direita + texto dourado
V02: World Cup Secrets — troféu + texto impactante
"""

import os, sys, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Fix Windows encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE         = Path(__file__).parent
IMAGES_DIR   = BASE / "output" / "player_images"
THUMB_DIR    = BASE / "output" / "thumbnails"
os.makedirs(THUMB_DIR, exist_ok=True)

# Cores SoccerTruth
BG_DARK   = (10, 15, 46)      # #0A0F2E azul marinho
GOLD      = (255, 215, 0)     # #FFD700 dourado
RED       = (220, 30, 30)     # vermelho
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
GOLD_GLOW = (255, 200, 0, 80)

W, H = 1280, 720

# ── Font loader ────────────────────────────────────────────────────────────

def load_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/Impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── Text helpers ────────────────────────────────────────────────────────────

def draw_text_shadow(draw, text, pos, font, color, shadow_color=(0,0,0), offset=4):
    x, y = pos
    for dx, dy in [(-offset, offset), (offset, offset), (-offset, -offset), (offset, -offset)]:
        draw.text((x+dx, y+dy), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=color)

def draw_text_centered(draw, text, y, font, color, shadow=True, img_w=W):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (img_w - tw) // 2
    if shadow:
        draw_text_shadow(draw, text, (x, y), font, color)
    else:
        draw.text((x, y), text, font=font, fill=color)
    return tw

def draw_glow_text(draw, text, pos, font, color, glow_color, glow_radius=8):
    """Efeito glow em texto via offsets múltiplos."""
    x, y = pos
    r, g, b = glow_color[:3]
    for spread in range(glow_radius, 0, -2):
        alpha = max(30, 120 - spread * 12)
        glc = (r, g, b)
        for dx in range(-spread, spread+1, 2):
            for dy in range(-spread, spread+1, 2):
                draw.text((x+dx, y+dy), text, font=font, fill=glc)
    draw.text((x, y), text, font=font, fill=color)


# ── Image helpers ───────────────────────────────────────────────────────────

def load_and_crop(path: Path, target_w: int, target_h: int,
                  grayscale: bool = False) -> Image.Image:
    img = Image.open(path).convert("RGB")
    # Resize mantendo aspecto, depois crop central
    ratio = max(target_w / img.width, target_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top  = max(0, (new_h - target_h) // 3)   # foca no topo (rosto)
    img = img.crop((left, top, left + target_w, top + target_h))
    if grayscale:
        img = ImageEnhance.Color(img).enhance(0.0)
        img = ImageEnhance.Contrast(img).enhance(1.3)
    return img

def add_gradient_overlay(img: Image.Image, direction="left",
                          color=(10, 15, 46), strength=200) -> Image.Image:
    """Overlay gradiente para fundir a foto com o fundo."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    w, h    = img.size
    for i in range(w if direction in ("left", "right") else h):
        if direction == "left":
            alpha = int(strength * (1 - i / w) ** 2)
            draw.line([(i, 0), (i, h)], fill=(*color, alpha))
        elif direction == "right":
            alpha = int(strength * (i / w) ** 2)
            draw.line([(i, 0), (i, h)], fill=(*color, alpha))
        elif direction == "bottom":
            alpha = int(strength * (i / h) ** 1.5)
            draw.line([(0, i), (w, i)], fill=(*color, alpha))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")

def pexels_image(keyword: str, dest: Path, api_key: str) -> Path | None:
    if dest.exists() and dest.stat().st_size > 10000:
        return dest
    try:
        resp = requests.get("https://api.pexels.com/v1/search",
                            headers={"Authorization": api_key},
                            params={"query": keyword, "per_page": 5,
                                    "orientation": "landscape"}, timeout=10)
        photos = resp.json().get("photos", [])
        if not photos:
            return None
        url = photos[0]["src"]["large2x"]
        r = requests.get(url, timeout=20)
        dest.write_bytes(r.content)
        return dest
    except Exception as e:
        print(f"  [WARN] Pexels download: {e}")
        return None


# ── V01: MESSI vs PELÉ ─────────────────────────────────────────────────────

def make_v01():
    print("\n[V01] Messi vs Pele thumbnail...")

    canvas = Image.new("RGB", (W, H), BG_DARK)

    # Carrega fotos — maior qualidade
    messi_path = IMAGES_DIR / "messi-01.jpg"   # 6.8 MB — melhor
    pele_path  = IMAGES_DIR / "pele-03.jpg"    # 3.8 MB — melhor
    alt_pele   = IMAGES_DIR / "pele-01.jpg"

    if not pele_path.exists():
        pele_path = alt_pele

    HALF = W // 2

    if messi_path.exists():
        messi_img = load_and_crop(messi_path, HALF + 80, H, grayscale=False)
        messi_img = add_gradient_overlay(messi_img, "right", BG_DARK, 220)
        canvas.paste(messi_img, (-40, 0))
        print("  Messi OK")

    if pele_path.exists():
        pele_img = load_and_crop(pele_path, HALF + 80, H, grayscale=True)
        pele_img = add_gradient_overlay(pele_img, "left", BG_DARK, 220)
        canvas.paste(pele_img, (HALF - 40, 0))
        print("  Pelé OK")

    # Linha divisória dourada no centro
    draw = ImageDraw.Draw(canvas)
    for x in range(HALF - 2, HALF + 3):
        draw.line([(x, 0), (x, H)], fill=GOLD)

    # Faixa preta semitransparente no topo para o texto
    top_band = Image.new("RGBA", (W, 120), (0, 0, 0, 180))
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.alpha_composite(top_band, (0, 0))
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # ── Textos ────────────────────────────────────────────────────────────
    f_huge  = load_font(140)
    f_big   = load_font(80)
    f_med   = load_font(56)
    f_small = load_font(42)
    f_label = load_font(50)

    # Topo: "WHO IS THE REAL GOAT?"
    draw_text_centered(draw, "WHO IS THE REAL GOAT?", 18, f_small, RED)

    # Centro: "VS" dourado gigante
    bbox = draw.textbbox((0,0), "VS", font=f_huge)
    vs_w = bbox[2] - bbox[0]
    vs_x = (W - vs_w) // 2
    vs_y = H // 2 - 80
    draw_glow_text(draw, "VS", (vs_x, vs_y), f_huge, GOLD, (255, 200, 0), glow_radius=10)

    # "30 FACTS" acima do VS
    draw_text_centered(draw, "30 FACTS", vs_y - 85, f_med, WHITE)

    # Nome MESSI (lado esquerdo)
    draw_text_shadow(draw, "MESSI", (60, H - 110), f_big, GOLD)

    # Nome PELÉ (lado direito)
    bbox_p = draw.textbbox((0,0), "PELÉ", font=f_big)
    pw = bbox_p[2] - bbox_p[0]
    draw_text_shadow(draw, "PELÉ", (W - pw - 60, H - 110), f_big, WHITE)

    # "NOBODY TELLS YOU" na base central
    draw_text_centered(draw, "NOBODY TELLS YOU", H - 55, f_label, (200, 200, 200))

    # Bordas douradas (frames premium)
    for thickness, alpha in [(4, 255), (8, 80)]:
        ov = Image.new("RGBA", (W, H), (0,0,0,0))
        d2 = ImageDraw.Draw(ov)
        d2.rectangle([(thickness//2, thickness//2),
                       (W - thickness//2, H - thickness//2)],
                      outline=(*GOLD, alpha), width=thickness)
        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba.alpha_composite(ov)
        canvas = canvas_rgba.convert("RGB")

    out = THUMB_DIR / "THUMB-V01-messi-vs-pele-FINAL.png"
    canvas.save(out, "PNG", quality=95)
    print(f"  Salva: {out.name}")
    return out


# ── V02: WORLD CUP SECRETS ────────────────────────────────────────────────

def make_v02(pexels_key: str):
    print("\n[V02] World Cup Secrets thumbnail...")

    canvas = Image.new("RGB", (W, H), BG_DARK)

    # Tenta baixar imagem de troféu do Pexels
    trophy_path = THUMB_DIR / "_wc_trophy_bg.jpg"
    trophy_img  = pexels_image("world cup soccer trophy stadium", trophy_path, pexels_key)

    if trophy_img and trophy_img.exists():
        bg = load_and_crop(trophy_img, W, H, grayscale=False)
        # Escurece e satura para dar foco ao texto
        bg = ImageEnhance.Brightness(bg).enhance(0.35)
        bg = ImageEnhance.Color(bg).enhance(1.8)
        canvas.paste(bg, (0, 0))
        # Overlay azul escuro gradiente
        bg = add_gradient_overlay(canvas.copy(), "bottom", BG_DARK, 240)
        canvas.paste(bg, (0, 0))
        print("  Background troféu OK")
    else:
        # Fallback: background gradiente puro
        draw_bg = ImageDraw.Draw(canvas)
        for y in range(H):
            t = y / H
            r = int(BG_DARK[0] + (20 - BG_DARK[0]) * t)
            g = int(BG_DARK[1] + (5  - BG_DARK[1]) * t)
            b = int(BG_DARK[2] + (80 - BG_DARK[2]) * t * 0.3)
            draw_bg.line([(0, y), (W, y)], fill=(r, g, b))
        print("  Background gradiente (fallback)")

    draw = ImageDraw.Draw(canvas)

    f_giant  = load_font(200)
    f_huge   = load_font(100)
    f_big    = load_font(68)
    f_med    = load_font(50)
    f_small  = load_font(38)

    # "50" gigante dourado com glow
    bbox = draw.textbbox((0,0), "50", font=f_giant)
    num_w = bbox[2] - bbox[0]
    num_x = (W - num_w) // 2
    num_y = 60
    draw_glow_text(draw, "50", (num_x, num_y), f_giant, GOLD, (255, 180, 0), glow_radius=14)

    # "WORLD CUP" em branco grande
    draw_text_centered(draw, "WORLD CUP", 300, f_huge, WHITE)

    # "SECRETS" dourado
    draw_text_centered(draw, "SECRETS", 400, f_big, GOLD)

    # Linha separadora vermelha
    sep_y = 490
    draw.rectangle([(100, sep_y), (W - 100, sep_y + 4)], fill=RED)

    # "FIFA DOESN'T WANT YOU TO KNOW" vermelho
    draw_text_centered(draw, "FIFA DOESN'T WANT", sep_y + 18, f_med, RED)
    draw_text_centered(draw, "YOU TO KNOW", sep_y + 72, f_med, RED)

    # Estrelas decorativas
    for x_pos in [60, 200, W - 200, W - 60]:
        draw.text((x_pos - 15, 310), "★", font=load_font(36), fill=GOLD)

    # Borda dourada premium
    for thickness, alpha in [(4, 255), (10, 60)]:
        ov = Image.new("RGBA", (W, H), (0,0,0,0))
        d2 = ImageDraw.Draw(ov)
        d2.rectangle([(thickness//2, thickness//2),
                       (W - thickness//2, H - thickness//2)],
                      outline=(*GOLD, alpha), width=thickness)
        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba.alpha_composite(ov)
        canvas = canvas_rgba.convert("RGB")

    out = THUMB_DIR / "THUMB-V02-world-cup-secrets-FINAL.png"
    canvas.save(out, "PNG", quality=95)
    print(f"  Salva: {out.name}")
    return out


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(BASE / ".env")
    pexels_key = os.environ.get("PEXELS_API_KEY", "")

    v01 = make_v01()
    v02 = make_v02(pexels_key)

    print("\n" + "="*55)
    print(" THUMBNAILS PRONTAS")
    print("="*55)
    print(f" V01: {v01}")
    print(f" V02: {v02}")
    print("\n Abra a pasta e use no YouTube Studio:")
    print(f" {THUMB_DIR}")
    print("="*55)

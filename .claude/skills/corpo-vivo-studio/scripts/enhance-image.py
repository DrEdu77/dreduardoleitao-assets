#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhance-image.py — [Prioridade 2] Melhora qualidade de imagens antes de postar

Aplica: sharpness, clarity, color grading, upscale, marca d'agua sutil.
Nao requer API externa — usa Pillow (instalado localmente).

Uso:
  python3 -X utf8 enhance-image.py --input foto.jpg --output foto_enhanced.jpg
  python3 -X utf8 enhance-image.py --input ./images/ --output ./enhanced/ --batch
"""

import argparse
import sys
from pathlib import Path


def enhance(input_path: Path, output_path: Path, level: str = "standard") -> bool:
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
    except ImportError:
        print("Pillow nao instalado. Execute: pip install Pillow")
        return False

    try:
        img = Image.open(input_path).convert("RGB")
        original_size = img.size

        # --- Upscale se menor que 1080px ---
        min_dim = min(img.width, img.height)
        if min_dim < 1080:
            scale = 1080 / min_dim
            new_w  = int(img.width  * scale)
            new_h  = int(img.height * scale)
            img    = img.resize((new_w, new_h), Image.LANCZOS)
            print(f"  Upscale: {original_size} -> {img.size}")

        # --- Sharpness ---
        sharp_factor = {"light": 1.3, "standard": 1.6, "strong": 2.0}.get(level, 1.6)
        img = ImageEnhance.Sharpness(img).enhance(sharp_factor)

        # --- Contraste sutil ---
        contrast_factor = {"light": 1.05, "standard": 1.10, "strong": 1.18}.get(level, 1.10)
        img = ImageEnhance.Contrast(img).enhance(contrast_factor)

        # --- Saturacao de cor (levemente mais vibrante) ---
        color_factor = {"light": 1.05, "standard": 1.12, "strong": 1.20}.get(level, 1.12)
        img = ImageEnhance.Color(img).enhance(color_factor)

        # --- Brilho levemente aumentado ---
        brightness_factor = {"light": 1.02, "standard": 1.05, "strong": 1.08}.get(level, 1.05)
        img = ImageEnhance.Brightness(img).enhance(brightness_factor)

        # --- Unsharp mask para clareza ---
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))

        # --- Marca d'agua sutil "@corpovivomed" ---
        draw     = ImageDraw.Draw(img)
        wm_text  = "@corpovivomed"
        wm_x     = img.width  - 200
        wm_y     = img.height - 30
        draw.text((wm_x + 1, wm_y + 1), wm_text, fill=(0, 0, 0, 80))
        draw.text((wm_x,     wm_y),     wm_text, fill=(255, 255, 255, 120))

        # --- Salvar ---
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "JPEG", quality=95, optimize=True)
        size_kb = output_path.stat().st_size // 1024
        print(f"  Enhanced: {output_path.name} ({size_kb} KB) [{level}]")
        return True

    except Exception as e:
        print(f"Erro ao processar {input_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Image Enhancer")
    parser.add_argument("--input",   required=True,  help="Arquivo ou pasta de entrada")
    parser.add_argument("--output",  required=True,  help="Arquivo ou pasta de saida")
    parser.add_argument("--level",   default="standard",
                        choices=["light", "standard", "strong"],
                        help="Nivel de enhancement (padrao: standard)")
    parser.add_argument("--batch",   action="store_true", help="Processa toda a pasta")
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_path = Path(args.output)

    if args.batch or input_path.is_dir():
        exts   = {".jpg", ".jpeg", ".png", ".webp"}
        images = [f for f in input_path.iterdir() if f.suffix.lower() in exts]
        if not images:
            print(f"Nenhuma imagem encontrada em {input_path}")
            sys.exit(1)
        print(f"\nEnhancement batch: {len(images)} imagens | level={args.level}")
        ok = sum(
            enhance(img, output_path / img.name, args.level)
            for img in images
        )
        print(f"\n{ok}/{len(images)} imagens processadas.")
    else:
        print(f"\nEnhancement: {input_path.name} | level={args.level}")
        ok = enhance(input_path, output_path, args.level)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

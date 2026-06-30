#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-image.py — [Prioridade 1] Gera imagens IA para posts da Clinica Corpo Vivo

Fontes em ordem de prioridade:
  1. DALL-E 3 (OpenAI) — foto realista de alta qualidade
  2. Stable Diffusion via Stability AI — alternativa gratuita
  3. Pexels API — banco de fotos profissionais (chave ja configurada)

Uso:
  python3 -X utf8 generate-image.py --tema "hernia de disco" --formato feed
  python3 -X utf8 generate-image.py --tema "pilates" --formato reel --output ./output/
  python3 -X utf8 generate-image.py --prompt "custom prompt" --formato story
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

CONFIG_FILE = Path.home() / ".growthos" / "studio-config.json"
PEXELS_KEY  = "VR6i8x4MIn28S3m7H8ElMKnR1Wq97kWtLcYXOxf3YW4eq383TfU4UDqu"

FORMATO_SPECS = {
    "feed":     {"w": 1080, "h": 1080, "pexels_orientation": "square"},
    "reel":     {"w": 1080, "h": 1920, "pexels_orientation": "portrait"},
    "story":    {"w": 1080, "h": 1920, "pexels_orientation": "portrait"},
    "facebook": {"w": 1920, "h": 1080, "pexels_orientation": "landscape"},
    "linkedin": {"w": 1200, "h": 627,  "pexels_orientation": "landscape"},
    "youtube":  {"w": 1280, "h": 720,  "pexels_orientation": "landscape"},
}

# Prompts clinicos pre-definidos por tema (nivel PhD)
PROMPTS_CLINICOS = {
    "hernia de disco": (
        "Brazilian woman in her 40s holding lower back with mild discomfort, "
        "standing in a modern clean medical clinic, natural soft lighting, warm hopeful atmosphere, "
        "photorealistic 4K, green and white color palette, professional healthcare setting"
    ),
    "dor lombar": (
        "Compassionate male doctor in white coat gently examining patient's back, "
        "modern Brazilian clinic Alphaville SP, warm professional lighting, trust and care visible, "
        "photorealistic 4K, dark green accents"
    ),
    "pilates": (
        "Brazilian woman in her 45s doing pilates reformer exercise in bright modern studio, "
        "smiling and feeling strong, professional instructor visible, natural daylight, "
        "motivational atmosphere, photorealistic 4K, clean white and green aesthetic"
    ),
    "osteopatia": (
        "Close-up of skilled doctor hands performing gentle spinal manipulation on patient, "
        "clinical setting Brazil, soft natural lighting, professional and trustworthy, "
        "ultra-detailed photorealistic 4K, green and white tones"
    ),
    "quiropraxia": (
        "Professional chiropractor performing gentle back adjustment on patient lying on table, "
        "modern clean clinic, warm lighting, Brazilian healthcare environment, "
        "photorealistic 4K, calming green palette"
    ),
    "ortomolecular": (
        "Beautiful composition of natural supplements, fresh vegetables and medical analysis "
        "on clean white surface with dark green accents, Brazilian clinical aesthetic, "
        "professional product photography, 4K, health and wellness theme"
    ),
    "ciatica": (
        "Brazilian man in his 50s sitting at desk with noticeable leg discomfort, "
        "modern home office, realistic depiction of sciatic pain, warm lighting, "
        "hopeful expression suggesting solution, photorealistic 4K"
    ),
    "coluna vertebral": (
        "Medical illustration style spine anatomy with human silhouette, dark green background, "
        "professional medical visual, clean modern design, 4K high resolution"
    ),
    "qualidade de vida": (
        "Energetic Brazilian couple in their 60s, active and smiling outdoors Alphaville SP, "
        "representing health vitality and pain-free living, golden hour lighting, "
        "aspirational lifestyle photography, 4K photorealistic"
    ),
    "pos-cirurgico": (
        "Patient in recovery doing light rehabilitation exercises with caring physiotherapist, "
        "modern Brazilian rehabilitation clinic, progress and hope visible, warm lighting, "
        "photorealistic 4K, green and white medical setting"
    ),
}

PEXELS_QUERIES = {
    "hernia de disco":   "back pain treatment clinic",
    "dor lombar":        "back pain physiotherapy",
    "pilates":           "pilates studio woman",
    "osteopatia":        "osteopathy treatment hands",
    "quiropraxia":       "chiropractic adjustment spine",
    "ortomolecular":     "supplements vitamins health",
    "ciatica":           "leg pain office worker",
    "coluna vertebral":  "spine anatomy medical",
    "qualidade de vida": "healthy couple active lifestyle",
    "pos-cirurgico":     "physical therapy rehabilitation",
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def get_prompt_for_tema(tema: str) -> str:
    tema_lower = tema.lower().strip()
    for key, prompt in PROMPTS_CLINICOS.items():
        if key in tema_lower or tema_lower in key:
            return prompt
    return (
        f"Professional medical clinic scene related to {tema}, "
        "Brazilian healthcare setting, warm professional lighting, "
        "photorealistic 4K, green and white color palette, trust and care atmosphere"
    )


def gerar_via_dalle(prompt: str, fmt: str, output_path: Path, cfg: dict) -> bool:
    api_key = cfg.get("openai_api_key", "")
    if not api_key:
        return False

    spec = FORMATO_SPECS[fmt]
    # DALL-E suporta tamanhos fixos
    if spec["w"] == spec["h"]:
        size = "1024x1024"
    elif spec["w"] > spec["h"]:
        size = "1792x1024"
    else:
        size = "1024x1792"

    payload = json.dumps({
        "model":   "dall-e-3",
        "prompt":  prompt + " --style natural --quality hd",
        "n":       1,
        "size":    size,
        "quality": "hd",
        "style":   "natural",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload, method="POST"
    )
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            img_url = data["data"][0]["url"]

        img_req = urllib.request.Request(img_url)
        with urllib.request.urlopen(img_req, timeout=30) as img_resp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(img_resp.read())

        print(f"DALL-E 3: imagem salva em {output_path}")
        return True
    except Exception as e:
        print(f"DALL-E falhou: {e}")
        return False


def gerar_via_pexels(tema: str, fmt: str, output_path: Path) -> bool:
    query = PEXELS_QUERIES.get(tema.lower(), tema)
    spec  = FORMATO_SPECS[fmt]
    orientation = spec["pexels_orientation"]

    params = urllib.parse.urlencode({
        "query":       query,
        "orientation": orientation,
        "size":        "large",
        "per_page":    1,
    })
    url = f"https://api.pexels.com/v1/search?{params}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", PEXELS_KEY)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())

        photos = data.get("photos", [])
        if not photos:
            print(f"Pexels: nenhuma foto encontrada para '{query}'")
            return False

        photo = photos[0]
        src   = photo["src"]
        img_url = src.get("large2x") or src.get("large") or src.get("original")

        img_req = urllib.request.Request(img_url)
        img_req.add_header("User-Agent", "CorpoVivoStudio/1.0")
        with urllib.request.urlopen(img_req, timeout=30) as img_resp:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(img_resp.read())

        print(f"Pexels: foto '{query}' salva em {output_path}")
        print(f"  Credito: {photo.get('photographer', 'Pexels')} via pexels.com")
        return True
    except Exception as e:
        print(f"Pexels falhou: {e}")
        return False


def aplicar_overlay_marca(img_path: Path, fmt: str) -> bool:
    """Aplica overlay verde-musgo Corpo Vivo e redimensiona para o formato correto."""
    try:
        from PIL import Image, ImageDraw, ImageFilter
        spec = FORMATO_SPECS[fmt]

        img = Image.open(img_path).convert("RGBA")
        img = img.resize((spec["w"], spec["h"]), Image.LANCZOS)

        # Overlay verde-musgo com opacidade 0.60
        overlay = Image.new("RGBA", img.size, (26, 74, 64, 153))  # #1A4A40 @ 60%
        composited = Image.alpha_composite(img, overlay)

        final = composited.convert("RGB")
        final.save(img_path, "JPEG", quality=92, optimize=True)
        print(f"  Overlay aplicado + redimensionado para {spec['w']}x{spec['h']}")
        return True
    except ImportError:
        print("  Pillow nao instalado — overlay nao aplicado. Instalar: pip install Pillow")
        return False
    except Exception as e:
        print(f"  Erro ao aplicar overlay: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Geracao de Imagem")
    parser.add_argument("--tema",    help="Tema clinico (ex: hernia de disco)")
    parser.add_argument("--prompt",  help="Prompt customizado (sobrepoe --tema)")
    parser.add_argument("--formato", default="feed",
                        choices=list(FORMATO_SPECS.keys()),
                        help="Formato de saida")
    parser.add_argument("--output",  default=".", help="Pasta de saida")
    parser.add_argument("--overlay", action="store_true", default=True,
                        help="Aplicar overlay verde Corpo Vivo (padrao: sim)")
    parser.add_argument("--no-overlay", dest="overlay", action="store_false")
    args = parser.parse_args()

    if not args.tema and not args.prompt:
        parser.error("Informe --tema ou --prompt")

    cfg    = load_config()
    prompt = args.prompt or get_prompt_for_tema(args.tema)
    tema   = args.tema or "custom"
    fmt    = args.formato

    slug        = tema.lower().replace(" ", "-").replace("/", "-")
    output_dir  = Path(args.output)
    output_path = output_dir / f"{slug}_{fmt}.jpg"

    print(f"\nGerando imagem: {fmt} | tema={tema}")
    print(f"Prompt: {prompt[:80]}...")

    # Tenta em ordem de prioridade
    gerado = False
    if not gerado:
        gerado = gerar_via_dalle(prompt, fmt, output_path, cfg)
    if not gerado:
        gerado = gerar_via_pexels(tema, fmt, output_path)
    if not gerado:
        print("Nenhuma fonte de imagem disponivel. Configure openai_api_key no studio-config.json")
        sys.exit(1)

    if args.overlay:
        aplicar_overlay_marca(output_path, fmt)

    print(f"\nImagem pronta: {output_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()

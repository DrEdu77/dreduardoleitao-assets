#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seo-optimize.py — [Prioridade 5] Otimiza SEO de todas as captions por plataforma

Usa Claude API para enriquecer hashtags, palavras-chave, CTA e metadata SEO
adaptados para clinica de saude em Alphaville SP.

Uso:
  python3 -X utf8 seo-optimize.py --caption caption_instagram.md --output ./captions/
  python3 -X utf8 seo-optimize.py --folder ./captions/ --output ./captions_seo/
"""

import argparse
import json
import urllib.request
import urllib.error
from pathlib import Path

ANTHROPIC_KEY = "sk-ant-api03-ju76kpY0qDbWdDEfTFtUluzhOqExw4iMf6o6BV5xerZPjAJsrf_p_XitllRsEFFVTsictpov4IHnZnHQx4ESBg-qLWHmwAA"

# Hashtags base por tema clinico (researched, alto engajamento BR)
HASHTAGS_BASE = {
    "instagram": [
        "#osteopatia", "#osteopatiasp", "#dornascoluna", "#colunavertebral",
        "#fisioterapia", "#fisioterapiasp", "#quiropraxia", "#saude", "#saudeebemestar",
        "#qualidadedevida", "#pilates", "#pilatessp", "#hernia", "#herniadedisco",
        "#dorcostal", "#ciatica", "#postura", "#tratamentonaturaldador",
        "#clinicaalphaville", "#alphaville", "#barueri", "#dreduardoleitao",
        "#corpovivo", "#corpovivomed", "#osteopataalpha",
    ],
    "linkedin": [
        "#osteopatia", "#saude", "#qualidadedevida", "#colunavertebral",
        "#medicina", "#fisioterapia", "#bemestar", "#performance",
        "#saudeocupacional", "#ergonomia",
    ],
    "youtube": [
        "#osteopatia", "#dornascoluna", "#hernia", "#fisioterapia",
        "#pilates", "#saude", "#coluna", "#quiropraxia",
    ],
    "tiktok": [
        "#fyp", "#saude", "#dornascoluna", "#osteopatia", "#dicadesaude",
        "#coluna", "#fisioterapia", "#corpovivo",
    ],
}

KEYWORDS_SEO = [
    "osteopatia alphaville", "quiropraxia barueri", "dor nas costas alphaville",
    "fisioterapia alphaville sp", "clinica ortomolecular alphaville",
    "hernia de disco tratamento", "dor lombar cronica tratamento",
    "pilates alphaville sp", "dr eduardo leitao", "coluna vertebral tratamento",
    "sciática tratamento", "osteopatia sp zona oeste",
]


def chamar_claude(prompt: str, max_tokens: int = 1200) -> str:
    payload = json.dumps({
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": max_tokens,
        "messages":   [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload, method="POST"
    )
    req.add_header("x-api-key",         ANTHROPIC_KEY)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("Content-Type",      "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"Claude API erro: {e}")
        return ""


def detectar_plataforma(filename: str) -> str:
    name = Path(filename).stem.lower()
    for plat in ["instagram", "facebook", "linkedin", "youtube", "whatsapp", "tiktok"]:
        if plat in name:
            return plat
    return "instagram"


def otimizar_instagram(caption: str) -> str:
    hashtags_str = " ".join(HASHTAGS_BASE["instagram"])
    prompt = f"""Voce e especialista em SEO para Instagram de clinica medica no Brasil.

CAPTION ATUAL:
{caption}

HASHTAGS BASE: {hashtags_str}

TAREFA: Otimize este caption para maxima visibilidade no Instagram seguindo estas regras:
1. Mantenha o texto original intacto (apenas corrija erros se houver)
2. Certifique-se que o hook na 1a linha para o scroll (max 125 chars)
3. Adicione 3-5 emojis relevantes se nao houver
4. Adicione ao final um bloco de hashtags otimizado (25-30 tags, mix de grande+nicho)
5. CTA claro antes das hashtags: "Agende: (11) 3042-1334 | Link na bio"
6. Inclua pelo menos 3 hashtags locais: #alphaville #barueri #saopaulo

Responda APENAS com o caption otimizado, sem explicacoes.
"""
    return chamar_claude(prompt) or caption


def otimizar_linkedin(caption: str) -> str:
    prompt = f"""Voce e especialista em SEO e autoridade para LinkedIn B2B saude.

CAPTION ATUAL:
{caption}

TAREFA: Otimize para maxima visibilidade e autoridade no LinkedIn:
1. 1a linha: insight forte ou estatistica (hook profissional)
2. Paragrafos curtos (max 3 linhas cada)
3. Use "→" ou "•" para listas em vez de bullets complexos
4. CTA no final: convite para agendar ou conectar
5. 5-10 hashtags profissionais ao final
6. Tom: autoridade medica + empatia

Responda APENAS com o texto otimizado.
"""
    return chamar_claude(prompt) or caption


def otimizar_youtube(caption: str) -> str:
    prompt = f"""Voce e especialista em SEO para YouTube de saude no Brasil.

CAPTION ATUAL:
{caption}

KEYWORDS LOCAIS: {', '.join(KEYWORDS_SEO[:6])}

TAREFA: Se o caption nao tiver titulo e descricao separados, estruture assim:
1. TITULO: [titulo SEO-otimizado com keyword principal nos primeiros 3 words, max 60 chars]
2. DESCRICAO:
   - Paragrafos descritivos (300-500 palavras, inclui keywords naturalmente)
   - Timestamps se aplicavel (00:00 Intro, etc)
   - Links: "Agende: (11) 3042-1334"
   - Inscricao CTA: "Se inscreva para dicas semanais de saude"
3. HASHTAGS: 5-8 hashtags YouTube
4. TAGS: 15 tags separadas por virgula

Responda APENAS com a estrutura otimizada.
"""
    return chamar_claude(prompt) or caption


def gerar_metadata_json(caption: str, plataforma: str, tema: str = "") -> dict:
    return {
        "plataforma": plataforma,
        "tema":       tema,
        "keywords":   KEYWORDS_SEO[:5],
        "hashtags_count": caption.count("#"),
        "char_count":  len(caption),
        "cta_presente": any(kw in caption.lower() for kw in ["agende", "ligue", "link", "whatsapp", "3042"]),
        "emojis_presentes": any(ord(c) > 127 for c in caption),
    }


def otimizar_caption(texto: str, plataforma: str) -> str:
    print(f"  Otimizando SEO para {plataforma}...")
    dispatch = {
        "instagram": otimizar_instagram,
        "linkedin":  otimizar_linkedin,
        "youtube":   otimizar_youtube,
    }
    fn = dispatch.get(plataforma)
    if fn:
        return fn(texto)

    # Fallback generico para facebook, whatsapp, tiktok
    hashtags = " ".join(HASHTAGS_BASE.get(plataforma, HASHTAGS_BASE["instagram"])[:10])
    if "#" not in texto:
        texto += f"\n\n{hashtags}"
    if "3042" not in texto and "link" not in texto.lower():
        texto += "\n\nAgende: (11) 3042-1334 | @corpovivomed"
    return texto


def processar_arquivo(input_file: Path, output_dir: Path) -> bool:
    try:
        conteudo_original = input_file.read_text(encoding="utf-8")
        plataforma = detectar_plataforma(input_file.name)

        # Extrai so o texto da caption (remove header markdown se houver)
        linhas = conteudo_original.splitlines()
        header = ""
        caption = conteudo_original
        if linhas and linhas[0].startswith("#"):
            header  = linhas[0] + "\n\n"
            caption = "\n".join(linhas[2:]) if len(linhas) > 2 else conteudo_original

        otimizado = otimizar_caption(caption.strip(), plataforma)
        meta      = gerar_metadata_json(otimizado, plataforma)

        # Salva caption SEO
        out_caption = output_dir / f"seo_{input_file.name}"
        out_caption.write_text(
            f"{header}{otimizado}\n",
            encoding="utf-8"
        )

        # Salva metadata JSON
        out_meta = output_dir / f"meta_{input_file.stem}.json"
        out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        chars = len(otimizado)
        tags  = otimizado.count("#")
        print(f"  [{plataforma}] {out_caption.name} — {chars} chars, {tags} hashtags")
        return True

    except Exception as e:
        print(f"  Erro em {input_file.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — SEO Optimizer")
    parser.add_argument("--caption", help="Arquivo de caption individual (.md)")
    parser.add_argument("--folder",  help="Pasta com multiplos arquivos de caption")
    parser.add_argument("--output",  required=True, help="Pasta de saida")
    parser.add_argument("--tema",    default="", help="Tema do conteudo (para metadata)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.caption:
        input_file = Path(args.caption)
        if not input_file.exists():
            print(f"Arquivo nao encontrado: {args.caption}")
            return
        print(f"\nOtimizando SEO: {input_file.name}")
        processar_arquivo(input_file, output_dir)

    elif args.folder:
        folder = Path(args.folder)
        arquivos = [f for f in folder.glob("caption_*.md")]
        if not arquivos:
            arquivos = [f for f in folder.glob("*.md")]
        if not arquivos:
            print(f"Nenhum arquivo .md encontrado em {args.folder}")
            return
        print(f"\nOtimizando SEO: {len(arquivos)} arquivos")
        ok = sum(processar_arquivo(f, output_dir) for f in arquivos)
        print(f"\n{ok}/{len(arquivos)} arquivos otimizados em {output_dir}")

    else:
        parser.error("Informe --caption ou --folder")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
write-captions.py — [Prioridade 4] Gera legendas SEO-otimizadas por plataforma

Usa Claude API (Anthropic) para gerar copy especifica por plataforma com tom Dr. Eduardo.

Uso:
  python3 -X utf8 write-captions.py --tema "hernia de disco" --roteiro roteiro.txt --output ./captions/
  python3 -X utf8 write-captions.py --tema "pilates" --output ./captions/
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_FILE  = Path.home() / ".growthos" / "studio-config.json"
ANTHROPIC_KEY = "sk-ant-api03-ju76kpY0qDbWdDEfTFtUluzhOqExw4iMf6o6BV5xerZPjAJsrf_p_XitllRsEFFVTsictpov4IHnZnHQx4ESBg-qLWHmwAA"

BRAND_VOICE = """
CLINICA: Clinica Corpo Vivo Alpha — Osteopatia, Quiropraxia, Ortomolecular, Pilates
MEDICO: Dr. Eduardo Leitao — 25 anos de experiencia, especialista em coluna e dor
PUBLICO: Mulheres (80%) e homens, 30-65 anos, classe A/A+, Alphaville SP
TOM: Empatico, motivacional, profissional, acolhedor — como Silvio Santos: caloroso e conectivo
FRASES-CHAVE: "Dor ninguem merece", "Deixe que eu cuido de voce", "faz sentido para voce?"
PROIBIDO: game-changer, revolucionario, milagroso, resultado garantido, cutting-edge
CONTATO: (11) 3042-1334 | @corpovivomed | @dreduardoleitao
"""

PLATAFORMA_SPECS = {
    "instagram": {
        "max_chars": 2200,
        "hashtags":  True,
        "instrucao": (
            "Legenda para Instagram Feed/Reel. "
            "Hook forte na 1a linha (para o scroll). "
            "Emojis estrategicos (3-5 por texto). "
            "Hashtags ao final: #osteopatia #dornascoluna #corpovivo #saude #fisioterapia "
            "#hernia #qualidadedevida #dreduardoleitao #alphaville #colunavertebral. "
            "CTA no final: 'Agende: (11) 3042-1334 | Link na bio'. Max 2200 chars."
        ),
    },
    "facebook": {
        "max_chars": 5000,
        "hashtags":  False,
        "instrucao": (
            "Post para Facebook. Tom de comunidade acolhedora. "
            "Mais texto, mais contexto, historia mais completa. "
            "Estimular comentarios: 'Marque alguem que precisa ver isso!'. "
            "Sem hashtags em excesso (max 3). CTA claro no final. Max 5000 chars."
        ),
    },
    "linkedin": {
        "max_chars": 3000,
        "hashtags":  True,
        "instrucao": (
            "Post para LinkedIn. Tom de autoridade profissional. "
            "Dados clinicos, experiencia de 25 anos, resultados mensurados. "
            "Estrutura: insight + contexto + solucao + CTA. "
            "Hashtags profissionais: #osteopatia #saude #colunavertebral #qualidadedevida #medicina. "
            "Max 3000 chars."
        ),
    },
    "youtube": {
        "max_chars": 5000,
        "hashtags":  True,
        "instrucao": (
            "Titulo SEO para YouTube (<60 chars, keyword no inicio) + "
            "Descricao com: paragrafos com timestamps, links, hashtags no final. "
            "Formato:\n"
            "TITULO: [titulo otimizado]\n\n"
            "DESCRICAO:\n[descricao completa com capitulos]\n\n"
            "HASHTAGS: #tag1 #tag2...\n"
            "TAGS: [10-15 tags separadas por virgula]"
        ),
    },
    "whatsapp": {
        "max_chars": 1000,
        "hashtags":  False,
        "instrucao": (
            "Mensagem direta para broadcast WhatsApp. "
            "Proxima, direta, como conversa entre amigos. "
            "Sem formatacao markdown. "
            "CTA claro: agendar consulta ou responder a mensagem. Max 1000 chars."
        ),
    },
    "tiktok": {
        "max_chars": 2200,
        "hashtags":  True,
        "instrucao": (
            "Legenda para TikTok. Muito curta e impactante (max 150 chars no corpo). "
            "Hook visual descrito em texto. "
            "Hashtags: #fyp #saude #dornascoluna #osteopatia #dica #corpovivo. "
            "Tom leve e educativo."
        ),
    },
}


def chamar_claude(prompt: str) -> str:
    payload = json.dumps({
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": 1500,
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
    except urllib.error.HTTPError as e:
        print(f"Claude API erro {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}")
        return ""
    except Exception as e:
        print(f"Erro Claude API: {e}")
        return ""


def gerar_caption(tema: str, plataforma: str, roteiro: str = "") -> str:
    spec   = PLATAFORMA_SPECS.get(plataforma, PLATAFORMA_SPECS["instagram"])
    prompt = f"""Voce e o copywriter senior da Clinica Corpo Vivo Alpha.

PERFIL DA MARCA:
{BRAND_VOICE}

TEMA DO CONTEUDO: {tema}

{f'ROTEIRO BASE: {roteiro[:800]}' if roteiro else ''}

INSTRUCOES PARA {plataforma.upper()}:
{spec['instrucao']}

Escreva APENAS a legenda/caption (sem explicacoes extras, sem "aqui esta a legenda:").
Seja autentico, empatico e motivacional. Linguagem acessivel, nao tecnica.
"""
    print(f"  Gerando caption para {plataforma}...")
    texto = chamar_claude(prompt)
    if not texto:
        # Fallback minimo se API falhar
        texto = (
            f"Voce sabia que {tema} tem solucao?\n\n"
            f"Na Clinica Corpo Vivo Alpha, tratamos a causa — nao o sintoma.\n\n"
            f"Dor ninguem merece. Agende sua avaliacao: (11) 3042-1334\n"
            f"@corpovivomed | Alphaville SP"
        )
    return texto


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Caption Writer")
    parser.add_argument("--tema",       required=True, help="Tema clinico do conteudo")
    parser.add_argument("--roteiro",    help="Arquivo com roteiro base (.txt ou .md)")
    parser.add_argument("--output",     required=True, help="Pasta de saida das legendas")
    parser.add_argument("--plataformas", default="instagram,facebook,linkedin,whatsapp",
                        help="Plataformas separadas por virgula")
    args = parser.parse_args()

    roteiro = ""
    if args.roteiro and Path(args.roteiro).exists():
        roteiro = Path(args.roteiro).read_text(encoding="utf-8")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    plataformas = [p.strip() for p in args.plataformas.split(",")]

    print(f"\nGerando captions: {args.tema}")
    print(f"Plataformas: {', '.join(plataformas)}\n")

    for plat in plataformas:
        if plat not in PLATAFORMA_SPECS:
            print(f"  Plataforma desconhecida: {plat} — pulando")
            continue

        caption    = gerar_caption(args.tema, plat, roteiro)
        out_file   = output_dir / f"caption_{plat}.md"
        out_file.write_text(
            f"# Caption {plat.title()} — {args.tema.title()}\n\n{caption}\n",
            encoding="utf-8"
        )
        chars = len(caption)
        limit = PLATAFORMA_SPECS[plat]["max_chars"]
        status = "OK" if chars <= limit else f"LONGO ({chars}/{limit})"
        print(f"  [{status}] {out_file.name} ({chars} chars)")

    print(f"\nCaptions salvas em {output_dir}")


if __name__ == "__main__":
    main()

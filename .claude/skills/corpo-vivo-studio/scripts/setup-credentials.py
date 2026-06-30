#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup-credentials.py — Configura API keys para o Corpo Vivo Studio

Uso:
  python3 -X utf8 setup-credentials.py          # configuracao interativa
  python3 -X utf8 setup-credentials.py --check  # apenas verifica o que falta
"""

import argparse
import json
import sys
from pathlib import Path

CONFIG_DIR  = Path.home() / ".growthos"
CONFIG_FILE = CONFIG_DIR / "studio-config.json"

REQUIRED_KEYS = {
    "elevenlabs_api_key":  "ElevenLabs API Key (em elevenlabs.io > Profile > API Keys)",
    "elevenlabs_voice_id": "ElevenLabs Voice ID do Dr. Eduardo (em Voices > My Voices > copiar ID)",
    "heygen_api_key":      "HeyGen API Key (em app.heygen.com > Settings > API)",
    "heygen_avatar_id":    "HeyGen Avatar ID do Dr. Eduardo (em Studio > Avatars > My Avatars)",
}

OPTIONAL_KEYS = {
    "midjourney_api_key":  "Midjourney API Key (opcional — para capas com foto)",
    "runwayml_api_key":    "Runway ML API Key (opcional — para animacao de imagens)",
    "kling_api_key":       "Kling AI API Key (opcional — para videos realistas)",
    "pika_api_key":        "Pika Labs API Key (opcional — para animacao de fotos)",
    "canva_api_key":       "Canva API Key (opcional — para export de carrosseis)",
    "adobe_firefly_key":   "Adobe Firefly API Key (opcional — para imagens IA premium)",
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def check_config(cfg: dict) -> tuple[list, list]:
    missing_required = [k for k in REQUIRED_KEYS if not cfg.get(k)]
    missing_optional = [k for k in OPTIONAL_KEYS if not cfg.get(k)]
    return missing_required, missing_optional


def run_check(cfg: dict):
    missing_req, missing_opt = check_config(cfg)

    print("\n=== Corpo Vivo Studio — Status de Credenciais ===\n")
    print("OBRIGATORIAS:")
    for k, desc in REQUIRED_KEYS.items():
        status = "OK" if cfg.get(k) else "FALTANDO"
        val = f" ({cfg[k][:8]}...)" if cfg.get(k) else ""
        print(f"  [{status}] {k}{val}")

    print("\nPLATAFORMAS OPCIONAIS:")
    for k, desc in OPTIONAL_KEYS.items():
        status = "CONFIGURADO" if cfg.get(k) else "nao configurado"
        print(f"  [{status}] {k}")

    if missing_req:
        print(f"\n  {len(missing_req)} credencial(is) obrigatoria(s) faltando.")
        print("  Execute sem --check para configurar.")
        sys.exit(1)
    else:
        print("\n  Todas as credenciais obrigatorias estao configuradas.")
        if missing_opt:
            print(f"  {len(missing_opt)} plataforma(s) opcional(is) nao configurada(s).")
        sys.exit(0)


def run_interactive(cfg: dict):
    print("\n=== Corpo Vivo Studio — Configuracao de Credenciais ===\n")
    print("Pressione Enter para manter o valor atual.\n")

    changed = False

    print("--- CREDENCIAIS OBRIGATORIAS ---")
    for k, desc in REQUIRED_KEYS.items():
        current = cfg.get(k, "")
        display = f" [{current[:8]}...]" if current else " [nao configurado]"
        val = input(f"{desc}{display}: ").strip()
        if val:
            cfg[k] = val
            changed = True

    print("\n--- PLATAFORMAS OPCIONAIS (Enter para pular) ---")
    for k, desc in OPTIONAL_KEYS.items():
        current = cfg.get(k, "")
        display = f" [{current[:8]}...]" if current else ""
        val = input(f"{desc}{display}: ").strip()
        if val:
            cfg[k] = val
            changed = True

    if changed:
        save_config(cfg)
        print(f"\n  Credenciais salvas em: {CONFIG_FILE}")
    else:
        print("\n  Nenhuma alteracao feita.")

    missing_req, _ = check_config(cfg)
    if missing_req:
        print(f"\n  ATENCAO: {len(missing_req)} credencial(is) obrigatoria(s) ainda faltando:")
        for k in missing_req:
            print(f"    - {k}: {REQUIRED_KEYS[k]}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Corpo Vivo Studio — Configuracao de credenciais")
    parser.add_argument("--check", action="store_true", help="Apenas verifica, nao edita")
    args = parser.parse_args()

    cfg = load_config()

    if args.check:
        run_check(cfg)
    else:
        run_interactive(cfg)


if __name__ == "__main__":
    main()

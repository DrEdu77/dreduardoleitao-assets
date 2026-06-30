# HeyGen Best Practices — Avatar Video Senior

Fonte: aitmpl.com/skills/heygen-best-practices + documentacao oficial HeyGen API v2

## Qualidade de Avatar — configuracoes otimas

### Avatar Style
- `"avatar_style": "normal"` → rosto natural, movimentos fluidos
- `"avatar_style": "closeup"` → rosto em close para maior impacto emocional (Stories)
- `"avatar_style": "circle"` → avatar em circulo com fundo transparente (sobrepor em imagem)

### Background — melhores praticas para clinica medica
```json
{
  "background": {
    "type": "color",
    "value": "#1A4A40"
  }
}
```
Alternativas:
- `"type": "image", "url": "https://..."` → imagem da clinica como fundo
- `"type": "transparent"` → fundo transparente para composicao (requer plano Pro)

### Fundo recomendado para Corpo Vivo
- Verde-musgo `#1A4A40` para Reel e Story (branded)
- Branco `#FFFFFF` para LinkedIn (profissional)
- Imagem da clinica para Feed Instagram (mais humano)

## Audio — melhores praticas

### Qualidade do audio ElevenLabs para HeyGen
- Frequencia: 44.1kHz ou 48kHz (nao usar 22kHz — labios ficam dessincronizados)
- Formato: MP3 320kbps ou WAV (MP3 128kbps pode causar sync issues)
- Silencio no inicio: adicionar 0.3s de silencio antes da fala evita corte do inicio

### Verificar sincronizacao labial
- Pausas naturais no roteiro ajudam o HeyGen a sincronizar melhor
- Evitar frases muito longas sem pausa (>15 palavras seguidas)
- Pontuacao no texto ElevenLabs = pausas naturais = melhor sincronia

## Dimensoes e formatos por caso de uso

| Plataforma | Dimensao | Avatar Position | Recomendacao |
|-----------|---------|----------------|-------------|
| Instagram Reel | 1080x1920 | Centro ou inferior | closeup style |
| Instagram Story | 1080x1920 | Centro | closeup + CTA overlay |
| Instagram Feed | 1080x1080 | Centro-esquerda | normal style |
| Facebook Video | 1920x1080 | Centro | normal style |
| LinkedIn | 1920x1080 | Esquerda | normal, fundo branco |
| YouTube Shorts | 1080x1920 | Centro | circle style sobre B-roll |

## Rate limits e custos (plano Pro HeyGen)

- 5 videos simultaneos maximos
- Tempo de processamento: ~1-3 min por minuto de video
- Creditos: verificar saldo antes de batch production
- Retry automatico: se falhar, aguardar 60s antes de novo request

## Erros comuns e solucoes

| Erro | Causa | Solucao |
|------|-------|---------|
| `audio_too_long` | Audio > 15min | Dividir em partes de max 10min |
| `avatar_not_found` | Avatar ID errado | Verificar ID em Studio > Avatars |
| `processing_failed` | Audio corrompido | Re-gerar MP3 com ElevenLabs |
| Labios dessincronizados | Audio baixa qualidade | Usar WAV ou MP3 320kbps |
| Video cortado no inicio | Sem silencio inicial | Adicionar 0.3s de padding |

## Webhook para notificacao (evitar polling)

Em vez de polling a cada 30s, configurar webhook:
```json
{
  "callback_id": "corpo-vivo-[video_id]",
  "callback_url": "https://[sua-url]/heygen-webhook"
}
```
Quando pronto, HeyGen envia POST com `video_url` diretamente.

## Composicao avancada — texto sobre video

Para adicionar textos/CTAs sobre o video do avatar (plano Business):
```json
{
  "elements": [{
    "type": "text",
    "content": "Agende: (11) 3042-1334",
    "position": {"x": 0.5, "y": 0.85},
    "style": {"font_size": 32, "color": "#FFFFFF", "bold": true}
  }]
}
```

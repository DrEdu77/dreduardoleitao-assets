---
name: corpo-vivo-studio
description: >
  Estudio de producao de conteudo PhD Master Senior para a Clinica Corpo Vivo Alpha
  (@corpovivomed / @dreduardoleitao). Pipeline completo: roteiro estrategico → imagem IA (FLUX/DALL-E/Canvas)
  → audio via ElevenLabs → video avatar via HeyGen → legenda SEO-otimizada por plataforma →
  aprovacao por email (ducoluna@gmail.com) → publicacao automatica.
  Plataformas: Instagram Feed/Reel/Story, Facebook, LinkedIn, YouTube, TikTok, WhatsApp.
  Usar quando o Dr. Eduardo pedir: "cria conteudo sobre X", "faz um reel sobre X", "produz posts sobre X",
  "gera imagem para X", "cria carrossel sobre X", "/corpo-vivo-studio X", ou qualquer producao de midia
  para a Clinica Corpo Vivo. Integra skills: generate-image, image-enhancer, canvas-design,
  heygen-best-practices, sora, transcribe, social-media-copywriter, seo-optimizer.
---

# Corpo Vivo Studio — PhD Master Senior

Voce e o Diretor Criativo Senior do Corpo Vivo Studio. Dado um tema clinico, produz conteudo
de nivel profissional para todas as plataformas, combinando:
- **Imagem IA** (FLUX / DALL-E / Canvas Design) — fotos e artes realistas
- **Audio** (ElevenLabs) — voz do Dr. Eduardo com timbre natural
- **Video Avatar** (HeyGen) — Dr. Eduardo falando nas cameras
- **Copy otimizada** — roteiro + legendas por plataforma com SEO
- **Aprovacao** — sempre via email antes de publicar

**Regra absoluta:** NUNCA publicar sem aprovacao previa de ducoluna@gmail.com.

## Configuracao inicial

```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/setup-credentials.py --check
```

Credenciais em `C:/Users/User/.growthos/studio-config.json`.
Para adicionar nova ferramenta: rodar sem `--check`.

## Pipeline de Producao (7 fases)

### Fase 1 — Roteiro estrategico

Ler `C:/Users/User/growthOS/brand-voice.yaml` (tom, restricoes, plataformas ativas).
Ver templates prontos em `references/roteiro-templates.md`.

Estrutura hook-first obrigatoria:
- **Hook** (0-3s): para o scroll. Ex: "80% da dor lombar some sem cirurgia."
- **Corpo** (3-55s): educacao pratica, linguagem acessivel, dados reais
- **CTA** (ultimos 5s): "Dor ninguem merece. Agende: (11) 3042-1334"

Tom: empatico + motivacional. Frases-chave: "Dor ninguem merece", "Deixe que eu cuido de voce".
Proibido: `anti_slop.banned_phrases` do brand-voice.yaml.

Gerar versoes separadas por plataforma — ver specs em `references/platform-formats.md`.

### Fase 2 — Imagem de capa e artes [Scripts nativos — Prioridades 1-3]

**[P1] Gerar imagem IA** (DALL-E 3 → Pexels fallback automatico):
```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/generate-image.py \
  --tema "hernia de disco" --formato feed \
  --output "C:/Users/User/growthOS/output/studio/[tema-slug]/images/"
# --overlay aplicado automaticamente (#1A4A40 @ 60%)
```
Temas pre-configurados: hernia de disco, dor lombar, pilates, osteopatia, quiropraxia,
ortomolecular, ciatica, coluna vertebral, qualidade de vida, pos-cirurgico.
Formatos: feed (1080x1080) | reel/story (1080x1920) | facebook (1920x1080) | linkedin (1200x627)
Prompts completos em `references/image-prompts.md`.

**[P2] Melhorar qualidade da imagem** (sharpness + color + watermark):
```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/enhance-image.py \
  --input "C:/Users/User/growthOS/output/studio/[tema-slug]/images/" \
  --output "C:/Users/User/growthOS/output/studio/[tema-slug]/images/enhanced/" \
  --level standard --batch
# Niveis: light | standard | strong
```

**[P3] Criar carrossel PNG** (Pillow — sem API externa):
```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/create-carousel.py \
  --tema "hernia de disco" --slides 6 \
  --output "C:/Users/User/growthOS/output/studio/[tema-slug]/images/"
# Ou com JSON personalizado:
# --content slides.json
```
Tipos de slide: cover, problem, tip, quote, cta.
Paleta automatica: VERDE_MUSGO #1A4A40, VERDE_CLARO #4A9B8F, DOURADO #C9A84C.

Saidas salvar em: `C:/Users/User/growthOS/output/studio/[tema-slug]/images/`

### Fase 3 — Audio via ElevenLabs

```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/generate-voice.py \
  --text "roteiro_aqui" \
  --output "C:/Users/User/growthOS/output/studio/[tema-slug]/audio.mp3"
```

Modelo: `eleven_multilingual_v2` | Voice ID: `L90xzM9HKL8PEJUBcsGt` (Dr. Eduardo Premium PT-BR+EN)
Duracao alvo: Reel=30-60s | Story=15s | Feed/LinkedIn/Facebook=60-90s
Ver parametros em `references/elevenlabs-api.md`.

### Fase 4 — Video Avatar via HeyGen

```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/generate-video.py \
  --audio "C:/Users/User/growthOS/output/studio/[tema-slug]/audio.mp3" \
  --output-dir "C:/Users/User/growthOS/output/studio/[tema-slug]/" \
  --formats reel,story,feed,facebook,linkedin
```

Avatar ID: `c78845d3b71e4be69c10ee26664b7c84` (Dr. Eduardo HeyGen)
Ver boas praticas avancadas em `references/heygen-best-practices.md`.
Ver parametros completos em `references/heygen-api.md`.

**Fallback se HeyGen falhar:** usar skill `sora` com OPENAI_API_KEY para gerar video alternativo.

### Fase 5 — Legendas e SEO [Scripts nativos — Prioridades 4-6]

**[P4] Gerar captions por plataforma** (Claude API — tom Dr. Eduardo):
```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/write-captions.py \
  --tema "hernia de disco" \
  --roteiro "C:/Users/User/growthOS/output/studio/[tema-slug]/roteiro.txt" \
  --plataformas "instagram,facebook,linkedin,youtube,whatsapp" \
  --output "C:/Users/User/growthOS/output/studio/[tema-slug]/captions/"
```
Plataformas: instagram (2200 chars) | facebook (5000) | linkedin (3000) | youtube (titulo+descricao+tags) | whatsapp (1000) | tiktok (150 corpo)
Fallback automatico se API falhar (texto basico com CTA).

**[P5] Otimizar SEO de todas as captions** (hashtags + keywords locais + metadata):
```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/seo-optimize.py \
  --folder "C:/Users/User/growthOS/output/studio/[tema-slug]/captions/" \
  --output "C:/Users/User/growthOS/output/studio/[tema-slug]/captions/" \
  --tema "hernia de disco"
# Gera: seo_caption_instagram.md + meta_caption_instagram.json para cada plataforma
```
Keywords locais configuradas: osteopatia alphaville, dor nas costas alphaville, fisioterapia barueri...

**[P6] Transcrever audio para legendas automaticas (.srt)**:
```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/transcribe-audio.py \
  --audio "C:/Users/User/growthOS/output/studio/[tema-slug]/audio/audio.mp3" \
  --output "C:/Users/User/growthOS/output/studio/[tema-slug]/audio/" \
  --mode auto
# Modos: auto (API → local → placeholder) | api (Whisper API) | local (pip install openai-whisper)
# Saidas: .srt + _transcricao.txt + _segments.json
```

### Fase 6 — Assets exportados por plataforma

Estrutura completa em `C:/Users/User/growthOS/output/studio/[tema-slug]/`:

```
images/
  cover_1080x1080.png         # Instagram Feed / LinkedIn capa
  cover_1080x1920.png         # Reel / Story background
  carousel_slide_01.png       # Carrossel slide 1
  carousel_slide_0N.png       # Carrossel slide N
  linkedin_banner_1200x627.png
audio/
  audio.mp3                   # naracao ElevenLabs
  audio.srt                   # legenda automatica (transcribe)
video/
  reel_9x16.mp4               # Instagram Reel + TikTok  (1080x1920)
  story_9x16_15s.mp4          # Instagram Story (1080x1920, max 15s)
  feed_1x1.mp4                # Instagram Feed video     (1080x1080)
  facebook_16x9.mp4           # Facebook + YouTube       (1920x1080)
  linkedin_16x9.mp4           # LinkedIn video
captions/
  caption_instagram.md        # legenda IG + hashtags
  caption_facebook.md         # legenda Facebook
  caption_linkedin.md         # legenda LinkedIn (autoridade)
  caption_youtube.md          # titulo + descricao SEO + capitulos
  caption_whatsapp.md         # mensagem direta para broadcast
post-status.json              # controle GrowthOS
```

### Fase 7 — Aprovacao e Publicacao

```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/queue-approval.py \
  --folder "C:/Users/User/growthOS/output/studio/[tema-slug]/"

python3 -X utf8 C:/Users/User/growthOS/publisher/notify-approval.py --force
```

Email para `ducoluna@gmail.com` com:
- Thumbnails de todos os videos e imagens
- Legendas completas de cada plataforma
- Lista de hashtags prontas
- Instrucao: responder **APROVAR** para publicacao automatica

## Producao em Lote

```bash
python3 -X utf8 C:/Users/User/.claude/skills/corpo-vivo-studio/scripts/batch-produce.py \
  --topics "hernia de disco,dor lombar,pilates para coluna,osteopatia,ortomolecular"
```

## Adicionando nova ferramenta (design extensivel)

Quando o Dr. Eduardo assinar Midjourney, Runway, Kling, Canva, Adobe Firefly:

1. Rodar `setup-credentials.py` — ja tem slots preparados para todas
2. Adicionar formato em `generate-video.py` → dict `FORMATS` (video) ou novo script (imagem)
3. Adicionar spec em `references/platform-formats.md`
4. Atualizar este SKILL.md na secao relevante

Regra imutavel: SEMPRE aprovar por email antes de publicar em qualquer plataforma nova.

## Scripts nativos implementados (nivel PhD — todos prontos)

| Script | Funcao | Prioridade | Fase |
|--------|--------|-----------|------|
| `scripts/generate-image.py` | Gera foto IA realista (DALL-E → Pexels fallback) + overlay Corpo Vivo | P1 | Fase 2 |
| `scripts/enhance-image.py` | Melhora qualidade: sharpness/contraste/cor + watermark | P2 | Fase 2 |
| `scripts/create-carousel.py` | Carrossel PNG 1080x1080 com design Corpo Vivo (5 tipos de slide) | P3 | Fase 2 |
| `scripts/write-captions.py` | Captions por plataforma usando Claude API com voz Dr. Eduardo | P4 | Fase 5 |
| `scripts/seo-optimize.py` | SEO das captions: hashtags, keywords locais, metadata JSON | P5 | Fase 5 |
| `scripts/transcribe-audio.py` | Transcreve MP3 para .srt (Whisper API → local → placeholder) | P6 | Fase 5 |
| `scripts/generate-voice.py` | Audio ElevenLabs com voz Dr. Eduardo (PT-BR, multilingual) | — | Fase 3 |
| `scripts/generate-video.py` | Video HeyGen avatar 5 formatos (reel/story/feed/facebook/linkedin) | — | Fase 4 |
| `scripts/queue-approval.py` | Registra assets no GrowthOS + cria post-status.json | — | Fase 7 |
| `scripts/batch-produce.py` | Producao em lote de multiplos temas com 1 email de aprovacao | — | Lote |
| `scripts/setup-credentials.py` | Configura API keys ElevenLabs, HeyGen, OpenAI, etc | — | Setup |

## Tabela de referencias

| Arquivo | Quando carregar |
|---------|----------------|
| `references/platform-formats.md` | Specs tecnicas por plataforma (tamanho, duracao, fps) |
| `references/heygen-api.md` | Endpoints, parametros e status HeyGen |
| `references/heygen-best-practices.md` | Boas praticas avancadas de avatar e video |
| `references/elevenlabs-api.md` | Parametros, modelos e voice settings ElevenLabs |
| `references/roteiro-templates.md` | Templates de roteiro por tipo e tema clinico |
| `references/image-prompts.md` | Prompts prontos de imagem IA para temas da clinica |

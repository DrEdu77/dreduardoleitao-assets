# Guia Completo de Producao — YouTube Faceless Pipeline

> Referencia definitiva para produzir e publicar videos nos 6 canais.
> Atualizado apos publicacao do 1 video do WealthCodes (25/06/2026).

---

## ESTRUTURA DE PASTAS

```
C:\Users\User\dreduardoleitao-assets\youtube-pipeline\
l-- automation\
    |-- pipeline.py                  <- Orquestrador principal
    |-- .env                         <- API keys
    |-- config.json                  <- BodyTruth
    |-- config-wealthcodes.json      <- WealthCodes
    |-- config-cryptotruth.json      <- CryptoTruth
    |-- config-catfacts.json         <- CatFacts
    |-- config-luxurydogs.json       <- LuxuryDogs
    |-- config-soccertruth.json      <- SoccerTruth
    l-- modules\
        |-- script_gen.py            <- Gera roteiro (Claude API)
        |-- audio_gen.py             <- Gera audio (ElevenLabs)
        |-- image_fetch.py           <- Busca imagens (Pexels Photos)
        |-- video_clip_fetch.py      <- Busca video clips (Pexels Videos)
        |-- video_assemble.py        <- Monta video (FFmpeg)
        |-- capcut_gen.py            <- Cria draft CapCut
        |-- thumbnail_gen.py         <- Gera thumbnail (Pillow)
        |-- seo_gen.py               <- Gera SEO (Claude API)
        l-- youtube_upload.py        <- Upload YouTube
```

---

## ETAPA 1 — ESCOLHER TITULO E CANAL

**Regra de ouro:** Definir titulo E thumbnail ANTES de produzir.

**Formula de titulo:** `[Numero] + [Tema impactante] + [Angulo surpreendente]`
Exemplos:
- "50 Wealth Codes Nobody Teaches You..."
- "47 Spine Facts Doctors Don't Tell You"
- "33 Bitcoin Secrets The Rich Already Know"

**Limite do YouTube:** maximo 100 caracteres no titulo.

---

## ETAPA 2 — RODAR O PIPELINE

```powershell
cd C:\Users\User\dreduardoleitao-assets\youtube-pipeline\automation
```

### Modo 1 — FFmpeg (rapido, ~6 min, ~70MB)
```powershell
python pipeline.py `
  --title "TITULO DO VIDEO AQUI" `
  --channel wealthcodes `
  --clips `
  --dry-run
```

### Modo 2 — CapCut (cinema, recomendado, ~3.7GB apos export)
```powershell
python pipeline.py `
  --title "TITULO DO VIDEO AQUI" `
  --channel wealthcodes `
  --capcut `
  --dry-run
```

### Modo com audio ja existente (economiza creditos ElevenLabs)
```powershell
python pipeline.py `
  --title "TITULO DO VIDEO AQUI" `
  --channel wealthcodes `
  --audio "CAMINHO_COMPLETO_DO_MP3" `
  --capcut `
  --dry-run
```

**Flags disponiveis:**
- `--clips` = usa Pexels Video (MP4) em vez de fotos
- `--capcut` = gera draft CapCut (implica --clips)
- `--dry-run` = nao faz upload, so gera arquivos locais
- `--audio` = usa MP3 ja existente (pula ElevenLabs)

### Outputs gerados
- Script: `output\scripts\<slug>-<timestamp>.txt`
- Audio: `output\audio\<slug>\<slug>-<timestamp>-full.mp3`
- Clips: `output\clips\<slug>\` (135 arquivos .mp4)
- Thumbnail: `output\thumbnails\<slug>-<timestamp>.jpg`
- SEO: `output\thumbnails\<slug>-<timestamp>-seo.json`
- Draft CapCut: `AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\<nome>`

---

## ETAPA 3 — WORKFLOW CAPCUT

### 3.1 — Abrir CapCut Desktop
- Abrir o app CapCut Desktop (NAO o site capcut.com)
- Fazer login na conta CapCut Pro
- Na tela inicial: ver aba "Projetos" ou "Drafts"
- O projeto criado pelo pipeline aparece com nome: `WealthCodes - [Titulo[:45]]`

### 3.2 — Vincular midia (se necessario)
Se aparecer mensagem "Vincular midia" nos clips:
- Clicar em "Vincular midia"
- Navegar ate a pasta `output\clips\<slug>\`
- CapCut encontra e vincula automaticamente todos os 135 clips

**PROBLEMA FREQUENTE: Windows MAX_PATH (260 chars)**
Se o audio nao vincular (caminho longo demais):
1. Copiar MP3 para local curto: `C:\Users\User\OneDrive\Desktop\wc-voice.mp3`
2. Editar `draft_content.json` na pasta do draft:
   - Buscar o caminho longo do audio
   - Substituir pelo caminho curto
3. Reabrir o projeto no CapCut

### 3.3 — Deletar trilha de audio existente
- Se houver trilha de audio no timeline que nao vinculou: deletar essa trilha

### 3.4 — Arrastar audio para timeline
- No painel esquerdo: clicar em "Midias" (ou "Midia Local")
- Localizar o arquivo MP3 do audio (voz)
- Arrastar para a timeline na posicao correta

### 3.5 — Adicionar musica de fundo
- No painel esquerdo: clicar em "Audio" -> "CapCut Audio" (ou "Musica")
- Filtrar por: Cinematic ou Documentary
- Escolher musica de 4+ minutos (evitar musicas curtas)
- Arrastar para a timeline
- Ajustar volume da musica: clicar na trilha -> painel direito -> "Volume" -> 5 a 10%

### 3.6 — Exportar video
- Clicar em "Exportar" (botao direito superior)
- Configuracoes recomendadas:
  - Resolucao: 1080p
  - FPS: 30
  - Codec: H.264 / MP4
- Arquivo salvo em: `C:\Users\User\AppData\Local\CapCut\Videos\`

**AVISO: Music Copyright**
Musicas da biblioteca CapCut geram Content ID Claim no YouTube.
NAO e strike, mas pode afetar monetizacao.
Solucao para proximos videos: usar Pixabay Music API (royalty-free)

---

## ETAPA 4 — UPLOAD YOUTUBE

### 4.1 — Acesso
- studio.youtube.com com a conta correta
- Criar -> Fazer upload de videos
- Selecionar o arquivo MP4

### 4.2 — Detalhes do video

**Titulo:** (max 100 chars — CONTAR antes de colar!)

**Descricao:** (max 5000 chars)
- Usar descricao do SEO gerado

**Tags/Etiquetas:**
- Clicar em "Mostrar mais"
- Colar as 25 tags do SEO separadas por virgula
- Max: 500 chars no total

**Thumbnail:**
- Fazer upload do arquivo JPG gerado

**Playlist:**
- Criar playlist se for o primeiro video do canal
- Max: 150 chars no titulo da playlist

### 4.3 — Elementos do video
- Legendas automaticas: ativadas (YouTube gera automaticamente)

### 4.4 — Verificacoes
- Direitos de autor: aguardar resultado (~1-2 min)
  - "Nenhum problema" = OK
  - "Conteudo protegido" por musica CapCut = Content ID claim (NAO e strike)
- Disclosure IA: NAO (conteudo educativo factual)

### 4.5 — Visibilidade e Agendamento
- Selecionar "Agendar"
- Horario recomendado: 14:00 ET = 17:00 Brasilia (GMT-03:00)
- Melhor dia: quarta-feira para educacao/financas
- Fuso horario no YouTube: "GMT-03:00" Brasilia/Bogota/Lima

### 4.6 — Configuracoes adicionais (apos agendar)
- Comentarios: Ativar, moderacao Basica (NAO Rigorosa)
- Conceitos automaticos: Permitir
- Data de gravacao: deixar em branco

---

## PROBLEMAS CONHECIDOS E SOLUCOES

| Problema | Causa | Solucao |
|---|---|---|
| CapCut nao vincula midia | Windows MAX_PATH 260 chars | Copiar MP3 para Desktop + editar draft_content.json |
| ValueError source_timerange | Pexels reporta duracao arredondada | Corrigido em capcut_gen.py com mat.duration |
| FileNotFoundError no draft | Titulo termina com espaco | Corrigido com .strip() em capcut_gen.py |
| SEO com 15 tags basicas | Anthropic API key expirada (401) | Renovar ANTHROPIC_API_KEY em .env |
| Content ID Claim | Musica CapCut com copyright | Usar Pixabay Music API nos proximos videos |
| Titulo longo > 100 chars | Limite do YouTube | Contar caracteres antes de colar |
| Titulo do CapCut chars invalidos | Caracteres / : * ? < > | Corrigido com re.sub() em capcut_gen.py |

---

## CANAIS

| Canal | Config | Email | CPM | Status |
|---|---|---|---|---|
| WealthCodes | config-wealthcodes.json | blogdudu77@gmail.com | $15-25 | 1 video agendado 25/06/2026 |
| BodyTruth | config.json | bodytruthechannel@gmail.com | $10-15 | Proximo |
| CryptoTruth | config-cryptotruth.json | cryptotruthchannel@gmail.com | $30-60 | Mes 2 |
| CatFacts | config-catfacts.json | catfactsdailyyoutube@gmail.com | $5-10 | Mes 4 |
| LuxuryDogs | config-luxurydogs.json | luxurydogsworldyt@gmail.com | $5-10 | Mes 5 |
| SoccerTruth | config-soccertruth.json | a criar | $8-15 | Mes 3 |

---

## VIDEOS PUBLICADOS

| Canal | Titulo | URL | Data |
|---|---|---|---|
| WealthCodes | 50 Wealth Codes Nobody Teaches You | https://youtu.be/OO9OGjya7Vc | 25/06/2026 |

---

## ROADMAP

- [ ] Pixabay Music API para evitar copyright
- [ ] Renovar Anthropic API key
- [ ] Text overlays (estilo James Jani)
- [ ] Higgsfield API como fonte alternativa de video
- [ ] YouTube OAuth2 para upload automatizado
- [ ] Cache de clips (evitar re-download)
- [ ] Legendas automaticas via Whisper (SRT)
- [ ] 2 video WealthCodes
- [ ] Primeiro video BodyTruth (prioridade)

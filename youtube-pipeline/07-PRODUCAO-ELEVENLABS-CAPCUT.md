# Guia de Produção — ElevenLabs + CapCut Pro

## O QUE A IA FAZ (tudo):
- Script completo ✅
- Texto dos capítulos, títulos, transições ✅
- SEO: título, descrição, tags ✅
- Thumbnails: copy + layout description para Canva ✅
- Pesquisa de tópicos ✅
- Playlist de stock footage por capítulo ✅

## O QUE VOCÊ FAZ (mínimo):
1. Gerar áudio no ElevenLabs (colar script, clicar Generate)
2. Abrir CapCut Pro e montar usando o template (uma vez configurado, é só substituir)
3. Upload no YouTube (preencher campos que a IA já preparou)

---

## ETAPA 1 — ElevenLabs (sua voz clonada)

### Configuração da voz:
1. Acesse elevenlabs.io → My Voices
2. Selecione sua voz clonada (Dr. Eduardo)
3. Vá em Voice Settings:
   - Stability: **55%** (dá naturalidade sem instabilidade)
   - Similarity: **80%** (mais fiel à sua voz)
   - Style: **30%** (adiciona leve entonação)
   - Speaker Boost: **ON**
4. Language: **English** (ElevenLabs suporta multilingual)

### Gerar o áudio em blocos:

O script tem ~7.600 palavras. Divida em **8 blocos** (um por capítulo):

| Bloco | Conteúdo | Onde começa | Onde termina |
|---|---|---|---|
| 01 | Hook + Intro | "Your spine makes decisions..." | "...let's start" |
| 02 | Capítulo 1 (fatos 1–6) | "You were born with 33..." | "...its current form" |
| 03 | Capítulo 2 (fatos 7–13) | "You are taller in the morning..." | "...during wakefulness" |
| 04 | Capítulo 3 (fatos 14–20) | "The nucleus pulposus..." | "...lower back pain" |
| 05 | Capítulo 4 (fatos 21–27) | "Right now, your spinal cord..." | "...awake" |
| 06 | Capítulo 5 (fatos 28–34) | "Back pain is the leading..." | "...functional limitation" |
| 07 | Capítulo 6 (fatos 35–41) | "Looking down at a phone..." | "...back pain protocols" |
| 08 | Capítulo 7+8 + CTA | "The vagus nerve..." | "...I will see you there" |

### Exportar:
- Formato: MP3
- Qualidade: 192kbps
- Nomear: `v01-bloco-01.mp3`, `v01-bloco-02.mp3`, etc.

---

## ETAPA 2 — Stock Footage (Pexels — grátis, sem copyright)

Pesquisar no pexels.com/videos e baixar antes de editar:

| Capítulo | Termos de busca no Pexels |
|---|---|
| Hook/Intro | "spine xray", "human skeleton", "anatomy" |
| Cap 1 (estrutura) | "vertebrae", "medical scan", "spine anatomy" |
| Cap 2 (inteligência) | "neuron", "brain signals", "nerve" |
| Cap 3 (vértebras) | "mri scan", "disc", "spinal cord" |
| Cap 4 (agora) | "sitting desk", "posture", "back pain" |
| Cap 5 (doenças) | "doctor", "hospital", "pain relief" |
| Cap 6 (vida moderna) | "phone neck", "office sitting", "screen time" |
| Cap 7 (conexões) | "nervous system", "breathing", "sleep" |
| Cap 8 + CTA | "exercise", "yoga", "movement", "nature" |

**Dica:** baixe 3–5 clips por capítulo. No CapCut, você vai alternar entre eles durante a narração.

---

## ETAPA 3 — CapCut Pro: Template Permanente

### Configuração ÚNICA (faça uma vez, salva para todos os vídeos):

**1. Novo projeto:**
- Resolução: 1920 × 1080 (16:9)
- Frame rate: 30fps

**2. Configurações de texto padrão (salvar como preset):**

Texto de capítulo (aparece no início de cada chapter):
- Fonte: **Impact** ou **Bebas Neue**
- Tamanho: 90pt
- Cor: BRANCO com sombra preta (2px)
- Posição: centro superior (y: 10%)
- Duração: 3 segundos
- Animação de entrada: Fade In (0.3s)

Texto de número do fato (aparece em cada fato):
- Fonte: **Roboto Bold**
- Tamanho: 60pt
- Cor: AMARELO (#FFD700) com outline preto
- Posição: canto inferior esquerdo
- Ex: "FACT #7"
- Duração: enquanto o fato é narrado
- Animação: Pop (0.2s)

Texto de fato em destaque (frase principal do fato):
- Fonte: **Roboto Bold**
- Tamanho: 48pt
- Cor: BRANCO
- Background: caixa preta semi-transparente (70% opacidade)
- Posição: centro inferior
- Duração: 4–5 segundos (aparece 1s após o início da narração do fato)

**3. Música de fundo:**
- YouTube Audio Library → buscar "mysterious", "educational", "lo-fi calm"
- Volume: **12–15%** (não deve competir com a voz)
- Recomendar: "Sapphire" ou "Gravity" do YouTube Audio Library (royalty-free)

**4. Transição entre fatos:**
- Tipo: **Cross Dissolve** (Fade)
- Duração: 0.3 segundos
- Aplicar a TODAS as transições de clip

**5. Legendas automáticas:**
- Captions → Auto Captions → Language: English
- Estilo: Branco com sombra, fonte Roboto Medium, tamanho 38pt
- Posição: centro inferior (acima do "FACT #X")

---

## ESTRUTURA DO PROJETO CAPCUT (por vídeo)

```
TRILHA 1 (vídeo): clips de stock footage em sequência
TRILHA 2 (áudio): v01-bloco-01.mp3 ... v01-bloco-08.mp3
TRILHA 3 (música): música de fundo loop
TRILHA 4 (texto): títulos de capítulo + "FACT #X"
TRILHA 5 (texto): frase em destaque do fato
TRILHA 6 (legendas): auto-captions
```

**Tempo de edição estimado após template configurado: 30–45 min por vídeo**

---

## ETAPA 4 — SEO Gerado pela IA

Para cada vídeo, peça ao Claude:

```
Gere para um vídeo do YouTube chamado "[TÍTULO]":
1. Título final otimizado (máx 70 caracteres, inclui número + palavra forte)
2. Descrição completa (400 palavras, timestamps, keywords naturais, call to subscribe)
3. 25 tags (mix de broad e long-tail)
4. 5 hashtags para a descrição
5. Texto do card final (last 20 seconds): o que dizer para promover o próximo vídeo
```

---

## CHECKLIST DE PRODUÇÃO — cada vídeo

**IA faz (antes de você abrir o CapCut):**
- [ ] Script gerado e revisado
- [ ] Áudio gerado no ElevenLabs (8 blocos)
- [ ] Stock footage baixado do Pexels (30–40 clips)
- [ ] Título, descrição, tags gerados pelo Claude
- [ ] Thumbnail copy gerado pelo Claude

**Você faz:**
- [ ] Montar o vídeo no CapCut usando o template
- [ ] Verificar que os clips estão sincronizados com o áudio
- [ ] Revisar as legendas automáticas (corrigir nomes próprios)
- [ ] Criar thumbnail no Canva (5–10 min)
- [ ] Upload no YouTube + preencher título/descrição/tags (já prontos)
- [ ] Agendar publicação (Terça ou Sexta, 14h–16h EST)

---

## PRÓXIMOS 5 SCRIPTS (ordem de produção)

1. ✅ `v01` — 50 Spine Facts (script pronto)
2. `v02` — 50 Brain Facts That Will Blow Your Mind
3. `v03` — What Happens to Your Body When You Stop Moving for 30 Days
4. `v04` — 40 Facts About Pain (The Science Most People Never Learn)
5. `v05` — The Truth About Inflammation: Why Your Body Is Fighting Itself

**Pedir ao Claude:** "Generate the complete 45-minute script for [TÍTULO] following the same format as the spine facts script."

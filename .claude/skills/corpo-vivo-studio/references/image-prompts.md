# Prompts de Imagem IA — Corpo Vivo Studio

Prompts prontos para usar com skills `generate-image` (FLUX/Gemini) ou `imagegen` (DALL-E).
Paleta Corpo Vivo: verde-musgo #1A4A40, branco #F8F9FA, dourado #C9A84C (acento).

## Prompts por tema clinico

### Hernia de Disco
```
A Brazilian professional woman in her 40s, holding her lower back in mild discomfort,
standing in a modern clean medical clinic in Alphaville SP, natural soft lighting,
warm and hopeful atmosphere, photorealistic, 4K, shallow depth of field,
green accents in the background, doctor's office visible
```

### Dor Lombar / Coluna
```
A compassionate male doctor in his 50s with distinguished appearance, wearing a white coat,
gently placing hands on a patient's back during examination, modern Brazilian clinic,
warm professional lighting, trust and care visible in the scene, photorealistic 4K,
dark green and white color palette
```

### Osteopatia / Quiropraxia
```
Close-up of skilled doctor's hands performing gentle spinal manipulation on a patient,
clinical setting, soft natural lighting, Brazilian healthcare environment,
professional and trustworthy atmosphere, ultra-detailed photorealistic, 4K,
green and white tones
```

### Pilates / Movimento
```
A Brazilian woman in her 45s doing pilates reformer exercise in a bright modern studio,
smiling, feeling strong and healthy, professional instructor visible in background,
natural daylight, motivational atmosphere, photorealistic 4K, clean aesthetic
```

### Ortomolecular / Metabolismo
```
Beautiful composition of natural supplements, fresh vegetables, and medical analysis
on a clean white surface with dark green accents, Brazilian clinical aesthetic,
professional product photography, 4K, health and wellness theme
```

### Ciatica / Dor nas Pernas
```
A Brazilian man in his 50s sitting at a desk with noticeable discomfort in his leg,
modern home office setting, realistic depiction of sciatic pain, warm lighting,
hopeful expression suggesting solution ahead, photorealistic 4K
```

### Pos-cirurgico / Reabilitacao
```
A patient in recovery doing light rehabilitation exercises with a caring physiotherapist,
modern Brazilian rehabilitation clinic, progress and hope visible, warm lighting,
photorealistic 4K, green and white medical setting
```

### Qualidade de Vida / Longevidade
```
An energetic Brazilian couple in their 60s, active and smiling outdoors in Alphaville SP,
representing health, vitality and pain-free living, golden hour lighting,
aspirational lifestyle photography, 4K photorealistic
```

## Prompts para elementos de design (carrossel)

### Background slide carrossel
```
Abstract medical green gradient background, dark forest green #1A4A40 to lighter green,
subtle geometric patterns, professional healthcare aesthetic, clean minimal,
suitable for text overlay, 1080x1080px
```

### Icones / elementos decorativos
```
Minimal flat design icon of [coluna vertebral / hernia / pilates mat / supplement capsule],
dark green on white background, medical professional style, vector-like clean design
```

## Configuracoes tecnicas por tool

### Para skill `generate-image` (FLUX)
```python
{
  "prompt": "[prompt acima]",
  "aspect_ratio": "1:1",      # Feed
  "aspect_ratio": "9:16",     # Reel/Story
  "aspect_ratio": "16:9",     # Facebook/LinkedIn
  "quality": "high",
  "style": "photorealistic"
}
```

### Para skill `imagegen` (DALL-E)
```python
{
  "prompt": "[prompt acima]",
  "size": "1024x1024",        # Feed
  "size": "1024x1792",        # Reel/Story
  "size": "1792x1024",        # Facebook/LinkedIn
  "quality": "hd",
  "style": "natural"          # sempre "natural" para foto medica — evitar "vivid"
}
```

## Pos-processamento com `image-enhancer`

Apos gerar qualquer imagem, sempre passar pela skill `image-enhancer` com:
- Sharpness: +20%
- Clarity: +15%
- Color grading: warm tones, slight vignette
- Output: 4K upscale se necessario

## Regras de uso das imagens

1. **Prioridade 1:** Fotos reais do Dr. Eduardo e da clinica (brand-voice.yaml > clinica_propria)
2. **Prioridade 2:** Fotos IA realistas com `generate-image` usando prompts acima
3. **Prioridade 3:** Imagens do banco Unsplash curado (brand-voice.yaml > categorias)
4. **Sempre:** Aplicar overlay verde-musgo nos covers com opacidade 0.55-0.72
5. **Nunca:** Texto branco sobre imagem sem overlay — garantir contraste minimo 4.5:1

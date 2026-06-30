# ElevenLabs API — Referencia

## Autenticacao
- Header: `xi-api-key: {ELEVENLABS_API_KEY}`
- Base URL: `https://api.elevenlabs.io/v1`

## Endpoint principal: Text-to-Speech

```
POST /text-to-speech/{voice_id}
```

### Body JSON
```json
{
  "text": "roteiro aqui",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.65,
    "similarity_boost": 0.80,
    "style": 0.20,
    "use_speaker_boost": true
  }
}
```

### Parametros recomendados para Dr. Eduardo (voz medica PT-BR)
- `stability`: 0.60-0.70 (mais natural, menos robotico)
- `similarity_boost`: 0.80-0.85 (fiel ao clone de voz)
- `style`: 0.15-0.25 (expressividade moderada — profissional mas humano)
- `use_speaker_boost`: true (melhora qualidade com microfone virtual)

### Response
- Content-Type: `audio/mpeg`
- Salvar diretamente como `.mp3`

## Listar vozes disponiveis
```
GET /voices
```

## Verificar uso/quota
```
GET /user/subscription
```

## Modelos disponiveis
| Modelo | Uso | Latencia |
|--------|-----|----------|
| `eleven_multilingual_v2` | PT-BR alta qualidade | ~5s |
| `eleven_turbo_v2_5` | PT-BR mais rapido | ~2s |
| `eleven_flash_v2_5` | Ultra rapido, menor qualidade | <1s |

Usar `eleven_multilingual_v2` para producao final.
Usar `eleven_turbo_v2_5` para testes rapidos.

## Limite de caracteres por chamada
- Maximo: 5000 caracteres por request
- Roteiros maiores: dividir em blocos e concatenar os MP3s

## Configurar voice_id do Dr. Eduardo
Apos criar clone de voz no painel ElevenLabs:
1. Ir em Voices > My Voices
2. Copiar o Voice ID (formato: `abc123def456...`)
3. Salvar em `studio-config.json` como `elevenlabs_voice_id`

# HeyGen API — Referencia

## Autenticacao
- Header: `X-Api-Key: {HEYGEN_API_KEY}`
- Base URL: `https://api.heygen.com`

## Fluxo de geracao de video

### 1. Criar video com audio proprio (Audio-Driven Avatar)

```
POST /v2/video/generate
```

#### Body JSON
```json
{
  "video_inputs": [{
    "character": {
      "type": "avatar",
      "avatar_id": "{AVATAR_ID}",
      "avatar_style": "normal"
    },
    "voice": {
      "type": "audio",
      "audio_url": "{URL_PUBLICA_DO_MP3}"
    },
    "background": {
      "type": "color",
      "value": "#1A4A40"
    }
  }],
  "dimension": {
    "width": 1080,
    "height": 1920
  },
  "aspect_ratio": "9:16",
  "test": false
}
```

#### Aspect ratios aceitos
| Formato | Width x Height | Uso |
|---------|---------------|-----|
| `9:16`  | 1080x1920     | Reel, Story, TikTok |
| `16:9`  | 1920x1080     | Facebook, YouTube, LinkedIn |
| `1:1`   | 1080x1080     | Instagram Feed |

#### Response
```json
{ "data": { "video_id": "abc123" }, "error": null }
```

### 2. Verificar status do video (polling)

```
GET /v1/video_status.get?video_id={video_id}
```

#### Status possiveis
- `pending` → aguardando
- `processing` → em processamento
- `completed` → pronto para download
- `failed` → erro

#### Response quando completed
```json
{
  "data": {
    "status": "completed",
    "video_url": "https://files.heygen.ai/...",
    "thumbnail_url": "https://files.heygen.ai/..."
  }
}
```

### 3. Download do video

```python
import requests
r = requests.get(video_url, stream=True)
with open("output.mp4", "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)
```

## Listar avatares disponiveis
```
GET /v2/avatars
```

## Configurar avatar_id do Dr. Eduardo
1. No painel HeyGen: Studio > Avatars > My Avatars
2. Criar Photo Avatar ou Instant Avatar com foto do Dr. Eduardo
3. Copiar o Avatar ID
4. Salvar em `studio-config.json` como `heygen_avatar_id`

## Limites e boas praticas
- Tempo medio de processamento: 1-3 minutos por video
- Rate limit: 5 videos simultaneos
- Audio deve ser URL publica (usar upload temporario ou bucket S3/GCS)
- Videos ficam disponiveis por 7 dias no HeyGen — baixar imediatamente

## Upload de audio para URL publica

O script `generate-video.py` faz upload do MP3 local para o endpoint de upload do HeyGen:

```
POST /v1/asset
Content-Type: multipart/form-data
field: file = audio.mp3
```

Response: `{ "data": { "url": "https://files.heygen.ai/..." } }`

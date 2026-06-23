# Setup do Pipeline — BodyTruth YouTube

## APIs necessárias (conseguir antes de rodar)

### 1. Anthropic API Key (Claude)
- Acesse: platform.anthropic.com/api-keys
- Criar nova key → copiar para .env como `ANTHROPIC_API_KEY`

### 2. ElevenLabs API Key + Voice ID
- Acesse: elevenlabs.io/app/settings/api-keys
- API Key → copiar para .env como `ELEVENLABS_API_KEY`
- My Voices → Dr. Eduardo (EN) → copiar ID para `ELEVENLABS_VOICE_ID`
- ⚠️ Key atual inválida — gerar nova

### 3. Pexels API Key (gratuito)
- Acesse: pexels.com/api → Join → criar app
- Copiar key para .env como `PEXELS_API_KEY`

### 4. YouTube Data API v3 (OAuth2)
Passo a passo:
1. Acesse console.cloud.google.com
2. Criar projeto: "BodyTruth Pipeline"
3. APIs & Services → Enable APIs → buscar "YouTube Data API v3" → Enable
4. Credentials → Create Credentials → OAuth 2.0 Client ID
5. Application type: Desktop App
6. Baixar JSON → renomear para `client_secrets.json`
7. Colocar em: youtube-pipeline/automation/client_secrets.json
8. No primeiro run, abre browser para autenticação → depois é automático

---

## Configurar .env

```bash
cp .env.example .env
# Editar .env com as keys
```

---

## Testar o pipeline (dry run — sem upload YouTube)

```bash
cd C:\Users\User\dreduardoleitao-assets\youtube-pipeline\automation

# Usando o script #1 já pronto (sem gastar tokens de script)
python pipeline.py \
  --title "50 Shocking Facts About Your Spine That Will Change How You See Your Body" \
  --script "..\scripts\v01-spine-facts-SCRIPT-COMPLETO.md" \
  --dry-run
```

## Rodar pipeline completo (com upload)

```bash
python pipeline.py --title "50 Shocking Facts About Your Spine That Will Change How You See Your Body" \
  --script "..\scripts\v01-spine-facts-SCRIPT-COMPLETO.md"
```

## Gerar vídeo novo do zero (script gerado automaticamente)

```bash
python pipeline.py --title "7 Hidden Reasons Your Back Pain Never Goes Away"
```

---

## Automação Make.com (após pipeline funcionando)

Criar cenário no Make.com:
1. Schedule trigger (toda Terça e Sexta)
2. HTTP module → POST para webhook local que roda o pipeline
3. Notificação WhatsApp quando upload concluído

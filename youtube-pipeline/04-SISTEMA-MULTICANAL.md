# Sistema Multi-Canal — Operação em Paralelo

## Conceito

Cada canal = nicho diferente = CPM diferente = conta Google diferente
Gestão centralizada com mesmo pipeline, mesmas ferramentas.

---

## 5 Canais (ranking por CPM + prioridade)

| # | Canal | Nicho | CPM médio | Config | Prioridade |
|---|---|---|---|---|---|
| 1 | **BodyTruth** | Saúde / Coluna / Corpo | US$10–15 | `config.json` | 🥇 PRIMEIRO |
| 2 | **CryptoTruth** | Criptomoedas / Bitcoin / DeFi | US$30–60 | `config-cryptotruth.json` | 🥈 SEGUNDO |
| 3 | **WealthCodes** | Finanças pessoais / Riqueza | US$15–25 | `config-wealthcodes.json` | 🥉 TERCEIRO |
| 4 | **CatFacts Daily** | Gatinhos / Raças / Curiosidades | US$5–10 | `config-catfacts.json` | 4° |
| 5 | **LuxuryDogs World** | Cachorros raros e caros do mundo | US$5–10 | `config-luxurydogs.json` | 5° |

> CryptoTruth tem o maior CPM do YouTube (~$60/15min). Canal de finanças (Graham Stephan style).

---

## Como rodar cada canal

```bash
cd C:\Users\User\dreduardoleitao-assets\youtube-pipeline\automation

# BodyTruth (saúde — padrão)
python pipeline.py --title "50 Shocking Facts About Your Spine" --channel bodytruth

# CryptoTruth (criptomoedas — maior CPM)
python pipeline.py --title "50 Bitcoin Facts That Will Blow Your Mind" --channel cryptotruth

# WealthCodes (financeiro)
python pipeline.py --title "50 Money Facts the Rich Don't Want You to Know" --channel wealthcodes

# CatFacts Daily (gatinhos)
python pipeline.py --title "25 Surprising Facts About Cats You Never Knew" --channel catfacts

# LuxuryDogs World (cachorros raros)
python pipeline.py --title "10 Rarest Dog Breeds That Cost More Than a Car" --channel luxurydogs

# Listar todos os canais
python pipeline.py --list-channels
```

---

## Estrutura de Contas Google

Para maximizar sem risco de banimento cruzado:

```
Conta Google 1 → Canal BodyTruth        → bodytruthechannel@gmail.com
Conta Google 2 → Canal CryptoTruth      → cryptotruthchannel@gmail.com
Conta Google 3 → Canal WealthCodes      → wealthcodesyoutube@gmail.com
Conta Google 4 → Canal CatFacts Daily   → catfactsdailyyoutube@gmail.com
Conta Google 5 → Canal LuxuryDogs World → luxurydogsworldyt@gmail.com
```

> Usar Gmail diferente para cada canal. Não vincular entre si.

---

## Calendário de Lançamento

### Mês 1 (Semanas 1–4): Apenas BodyTruth
- Criar canal + customização completa
- Publicar 2–3 vídeos/semana (Ter + Sex)
- Objetivo: 8–12 vídeos, validar pipeline completo

### Mês 2: BodyTruth + CryptoTruth
- BodyTruth: 2 vídeos/semana (ritmo de cruzeiro)
- CryptoTruth: começa com 2/semana (Ter + Sex 15h EST)
- Total: 4 vídeos/semana — CPM médio já sobe para ~$20

### Mês 3: + WealthCodes
- 3 canais ativos = 6 vídeos/semana
- Claude gera scripts em lote (5 por vez)

### Mês 4: + CatFacts Daily
- 4 canais = 8 vídeos/semana
- Canal pets tem volume alto de views (viraliza fácil)

### Mês 5: + LuxuryDogs World
- Sistema completo: 5 canais = 10 vídeos/semana
- Total projeção: R$40.000–R$80.000/mês

---

## Calendário de Publicação por Canal

| Canal | Dias | Horário |
|---|---|---|
| BodyTruth | Terça + Sexta | 14h EST |
| CryptoTruth | Terça + Sexta | 15h EST |
| WealthCodes | Quarta + Sábado | 14h EST |
| CatFacts Daily | Segunda + Quinta | 16h EST |
| LuxuryDogs World | Terça + Sexta | 17h EST |

> Horários escalonados para não competir entre si no algoritmo

---

## Primeiros 5 Títulos por Canal

### BodyTruth (Saúde)
1. "50 Shocking Facts About Your Spine That Will Change How You See Your Body"
2. "What Happens to Your Body When You Sit All Day For 8 Hours"
3. "7 Hidden Reasons Your Back Pain Never Goes Away"
4. "The Truth About Herniated Discs Doctors Never Tell You"
5. "50 Facts About Chronic Pain That Will Surprise You"

### CryptoTruth (Criptomoedas — Graham Stephan style)
1. "50 Bitcoin Facts That Will Blow Your Mind"
2. "The Untold History of Bitcoin: From $0 to $1 Million"
3. "What Happens to Your Money in a Crypto Crash — The Real Data"
4. "50 Facts About Ethereum That Will Shock You"
5. "How Institutional Investors Changed Bitcoin Forever — The Full Story"

### WealthCodes (Financeiro)
1. "50 Money Facts the Rich Know That Nobody Teaches You"
2. "What Compound Interest Actually Does to $1,000 Over 30 Years"
3. "7 Financial Habits That Separate the Wealthy From Everyone Else"
4. "The Truth About the Stock Market That Wall Street Hides"
5. "50 Facts About Passive Income That Changed How I Think About Money"

### CatFacts Daily (Gatinhos)
1. "25 Surprising Facts About Cats You Absolutely Never Knew"
2. "Why Cats Do These 10 Weird Things — Finally Explained"
3. "The 10 Rarest Cat Breeds in the World (And What They Cost)"
4. "50 Fun Facts About Kittens That Will Make You Smile"
5. "Why Your Cat Stares at You — 10 Behaviors Finally Explained"

### LuxuryDogs World (Cachorros Raros)
1. "10 Rarest Dog Breeds That Cost More Than a Car"
2. "The Most Expensive Dogs in the World — Price, History and Rarity"
3. "25 Dog Breeds You've Never Seen Before (From Around the World)"
4. "Why These 5 Dog Breeds Are Almost Extinct"
5. "The World's Fluffiest Dogs — 15 Adorable Rare Breeds"

---

## Gestão com Planilha de Controle

Criar planilha Google Sheets com abas:

```
ABA 1 — CANAIS
Canal | Conta Google | Nicho | Subs | Views Total | Monetizado | Receita/mês

ABA 2 — VÍDEOS EM PRODUÇÃO
Canal | Título | Status | Script | Voz | Vídeo | Upload | Data pub

ABA 3 — PERFORMANCE
Canal | Vídeo | Views | CTR | Retenção | Receita
```

---

## Workflow Semanal (5 canais ativos)

| Dia | Atividade | Tempo |
|---|---|---|
| Segunda | Gerar 10 scripts no Claude (2 por canal) — `pipeline.py --dry-run` | 2h |
| Terça | BodyTruth + CryptoTruth: gerar voz + montar vídeo | 3h |
| Quarta | WealthCodes: gerar voz + montar. Upload BodyTruth | 2h |
| Quinta | CatFacts: gerar voz + montar. Upload CryptoTruth + WealthCodes | 2h |
| Sexta | LuxuryDogs: gerar voz + montar. Upload CatFacts | 2h |
| Sábado | Upload LuxuryDogs + análise de performance + ajustes | 1h |

**Total: ~12h/semana = 10 vídeos/semana (2 por canal)**

---

## Automação Make.com (após pipeline validado)

```
TRIGGER: Agenda (Seg 9h) → Claude API: gera 10 roteiros
→ ElevenLabs API: gera áudio automaticamente
→ FFmpeg: monta vídeos (pipeline.py automático)
→ YouTube API: upload + agenda publicação
→ Notificação WhatsApp: "Semana produzida — 10 vídeos agendados"
```

---

## Regras Anti-Demonetização

1. **Nunca publicar script cru** — revisar, adicionar 1 exemplo real por vídeo
2. **Declarar IA nas configurações** (campo obrigatório YouTube desde 2024)
3. **Crypto**: SEMPRE incluir disclaimer "not financial advice"
4. **Saúde**: usar "studies suggest", "research shows" — nunca afirmações absolutas
5. **Variar formato** — intercalar listicle + documentário + história
6. **Engajar** — responder primeiros 10 comentários de cada vídeo (primeiras 24h)
7. **Música**: Epidemic Sound, Artlist ou YouTube Audio Library apenas

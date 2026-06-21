# Sistema Multi-Canal — Operação em Paralelo

## Conceito

Cada canal = nicho diferente = CPM diferente = conta Google diferente
Gestão centralizada com mesmo pipeline, mesmas ferramentas.

---

## 5 Canais Prioritários (ranking por CPM + concorrência)

| # | Canal | Nicho | CPM médio | Concorrência | Prioridade |
|---|---|---|---|---|---|
| 1 | **BodyTruth** | Saúde / Corpo / Coluna | US$10–15 | Média | 🥇 PRIMEIRO |
| 2 | **WealthCodes** | Finanças pessoais / Hábitos ricos | US$15–25 | Alta | 🥈 SEGUNDO |
| 3 | **MindBlown Facts** | Fatos científicos gerais | US$6–10 | Alta | 🥉 TERCEIRO |
| 4 | **AncientTruths** | História antiga / Mistérios | US$8–12 | Média | 4° |
| 5 | **SleepDoctor** | Sono / Descanso / Recuperação | US$12–18 | Baixa | 5° |

---

## Estrutura de Contas Google

Para maximizar sem risco de banimento cruzado:

```
Conta Google 1 → Canal BodyTruth (saúde)
Conta Google 2 → Canal WealthCodes (finanças)
Conta Google 3 → Canal MindBlown Facts (ciência)
...
```

> Usar Gmail diferente para cada canal. Não vincular entre si.
> Pode usar AdsPower para gerenciar os perfis separados.

---

## Calendário de Lançamento

### Mês 1 (Semana 1–4): Apenas BodyTruth
- Criar canal + customização completa
- Publicar 3 vídeos/semana
- Objetivo: 12 vídeos, entender o processo

### Mês 2: BodyTruth + WealthCodes
- BodyTruth: 2 vídeos/semana (ritmo de cruzeiro)
- WealthCodes: começa com 3/semana
- Total: 5 vídeos/semana

### Mês 3+: Adicionar 1 canal novo por mês
- Sistema já roda quase automático
- Claude gera scripts em lote (5 por vez)
- ElevenLabs gera voz em batch
- CapCut template salvo = edição em 20 min

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

## Workflow Semanal (quando rodando 3 canais)

| Dia | Atividade | Tempo |
|---|---|---|
| Segunda | Pesquisa de tópicos (3 canais) + gerar 6 scripts no Claude | 2h |
| Terça | Gerar vozes (ElevenLabs) + editar vídeo canal 1 | 2h |
| Quarta | Editar vídeo canal 2 + upload canal 1 | 2h |
| Quinta | Editar vídeo canal 3 + upload canal 2 | 2h |
| Sexta | Upload canal 3 + thumbnails da semana seguinte | 1h |
| Sábado | Análise de performance (CTR, retenção) + ajustes | 30min |

**Total: ~10h/semana para 3 canais com 2 vídeos/semana cada = 6 vídeos**

---

## Automação Futura (Make.com)

Quando o pipeline estiver validado:

```
TRIGGER: Novo script aprovado na planilha
→ ElevenLabs API: gera áudio automaticamente
→ GitHub: salva MP3
→ Notificação WhatsApp: "Áudio pronto para [canal] — [título]"
→ Você edita o vídeo no CapCut (única etapa manual)
→ YouTube API: upload agendado automático com título/descrição/tags
```

---

## Regras Anti-Demonetização

1. **Nunca publicar script cru do Claude** — sempre revisar, adicionar 1 exemplo real
2. **Declarar IA nas configurações do YouTube** (campo obrigatório desde 2024)
3. **Não fazer afirmações médicas sem embasamento** — usar "studies suggest", "research shows"
4. **Variar o formato** — não publicar 3 listicles seguidos. Intercalar com documentário
5. **Engage real** — responder os primeiros 10 comentários de cada vídeo (primeiras 24h)
6. **Sem música com copyright** — usar só Epidemic Sound, Artlist ou YouTube Audio Library

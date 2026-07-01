# Checkpoint — Magnetismo Abundante — 01/07/2026

## Status: 🔴 CAMPANHA PAUSADA — aguardando 4 correções

## Onde paramos
Audit completo da campanha Magnetismo Abundante revelou pixel Meta corrompido.
A campanha está PAUSADA. Todos os 5 ads estão PAUSED no Ads Manager.

## 4 Correções obrigatórias (em ordem)

### 1. Atomicat — Title da presell
- Atual: `Título` (placeholder)
- Trocar para: `Magnetismo Abundante | La Ley que Transforma tu Vida`

### 2. Atomicat — Meta Description da presell
- Atual: `Descrição` (placeholder)
- Trocar para: `Descubre la ley que atrae abundancia de forma natural. Miles de personas ya transformaron su vida. Acceso inmediato con garantía de 7 días.`

### 3. Atomicat — Pixel eventos (CRÍTICO)
- Problema: Purchase + InitiateCheckout disparando no page load junto com ViewContent
- Fix: na seção Pixel/Rastreamento do editor, deixar **apenas ViewContent** no page load
- Purchase e InitiateCheckout NÃO devem disparar na abertura da presell

### 4. Kiwify — Página de obrigado
- Adicionar o evento de compra real:
```javascript
fbq('track', 'Purchase', {value: 29.90, currency: 'BRL'});
```

## Por que o pixel está corrompido

| Evento Meta | Qtd reportada | Correto? |
|-------------|--------------|----------|
| ViewContent | 24.979 | ✅ |
| InitiateCheckout | 24.965 | ❌ dispara junto com ViewContent |
| Purchase | 24.993 | ❌ dispara junto com ViewContent |

ROAS fictício: R$4.975.301 em R$386 de gasto. Algoritmo do Meta corrompido.

## Após as correções → criar NOVA campanha
A campanha atual (ID: 120246324976510707) tem histórico corrompido.
Criar nova campanha do zero com os mesmos 5 ads.

## IDs dos ads (para recriar na nova campanha)

| Ad | ID atual (pausado) |
|----|-------------------|
| AD01_TK01_Descubrimiento | 120246324976500707 |
| AD02_TK02_Transformacion | 120246328034130707 |
| AD03_TK03_Bloqueo | 120246450671720707 |
| AD04_TK04_Ciencia | 120246450671740707 |
| AD05_TK05_Oferta | 120246450671730707 |

## Funil confirmado
- Presell: https://www.mevolablog.com/presell (Atomicat)
- Checkout: https://pay.kiwify.com.br/LYezNqi (Kiwify — R$29,90)
- Pixel: Magnetismo_Abundante_Pixel — ID 1429033345028801

## Scripts de auditoria nesta pasta
- `audit_magnetismo.py` — audit completo campanha + presell + pixel
- `audit_pixel.py` — análise detalhada dos fbq() calls na presell page

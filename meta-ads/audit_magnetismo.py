import sys, io, urllib.request, re, json, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv('ACCESS_TOKEN')

print('='*70)
print('  AUDIT COMPLETO — MAGNETISMO ABUNDANTE')
print('='*70)

# ─── PRESELL PAGE ─────────────────────────────────────────────────────────
print()
print('[A] PRESELL PAGE — www.mevolablog.com/presell')

try:
    req = urllib.request.Request(
        'https://www.mevolablog.com/presell',
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}
    )
    res = urllib.request.urlopen(req, timeout=15)
    html = res.read().decode('utf-8', errors='ignore')

    title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_m.group(1).strip() if title_m else 'NAO ENCONTRADO'

    desc_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', html, re.IGNORECASE)
    if not desc_m:
        desc_m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html, re.IGNORECASE)
    desc = desc_m.group(1) if desc_m else 'NAO ENCONTRADA'

    og_m = re.search(r'property=["\']og:title["\'][^>]+content=["\']([^"\']+)', html, re.IGNORECASE)
    og_title = og_m.group(1) if og_m else 'NAO ENCONTRADO'

    kiwify_m = re.search(r'https?://[^\s"\']*kiwify[^\s"\']*', html)
    kiwify_url = kiwify_m.group(0) if kiwify_m else 'NAO ENCONTRADO'

    pixel_m = re.search(r'fbq\s*\(|Meta\s*Pixel|FacebookPixel', html, re.IGNORECASE)
    has_pixel = 'SIM' if pixel_m else 'NAO'

    vturb_m = re.search(r'vturb|smartplayer|player\.vturb', html, re.IGNORECASE)
    has_vturb = 'SIM' if vturb_m else 'NAO'

    script_src = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    vturb_scripts = [s for s in script_src if 'vturb' in s.lower() or 'smartplayer' in s.lower()]

    print(f'  TITLE:            [{title}]')
    print(f'  META DESCRIPTION: [{desc[:80]}]')
    print(f'  OG:TITLE:         [{og_title}]')
    print(f'  KIWIFY LINK:      [{kiwify_url[:100]}]')
    print(f'  META PIXEL:       {has_pixel}')
    print(f'  VTURB/VIDEO:      {has_vturb}')
    if vturb_scripts:
        for v in vturb_scripts:
            print(f'    Script: {v[:80]}')
    print(f'  HTML SIZE:        {len(html):,} chars')

    # Check for CTAs/buttons
    btns = re.findall(r'<(?:a|button)[^>]*>(.*?)</(?:a|button)>', html, re.IGNORECASE | re.DOTALL)
    cta_btns = [b.strip() for b in btns if any(w in b.lower() for w in ['acessa', 'compra', 'quero', 'garantir', 'sim', 'clique', 'acesso', 'get', 'buy'])]
    print(f'  BOTOES CTA:       {len(cta_btns)}')
    for b in cta_btns[:5]:
        clean = re.sub(r'<[^>]+>', '', b).strip()[:70]
        print(f'    - {clean}')

    # ISSUES
    print()
    print('  ISSUES DETECTADAS:')
    issues = []
    if title in ['', 'Titulo', 'Título', 'titulo', 'Title', 'NAO ENCONTRADO']:
        issues.append(f'CRITICO: Title tag e placeholder "{title}" — precisa trocar')
    if desc in ['', 'NAO ENCONTRADA']:
        issues.append('AVISO: Meta description ausente')
    if kiwify_url == 'NAO ENCONTRADO':
        issues.append('CRITICO: Link Kiwify nao encontrado na pagina')
    if has_pixel == 'NAO':
        issues.append('CRITICO: Meta Pixel nao detectado')
    if has_vturb == 'NAO' and not vturb_scripts:
        issues.append('AVISO: VTurb nao detectado em HTML estatico (pode carregar via JS)')

    if not issues:
        print('  Nenhuma issue critica detectada!')
    for i in issues:
        print(f'  !!! {i}')

except Exception as e:
    print(f'  ERRO ao acessar presell: {e}')

# ─── PIXEL STATUS ─────────────────────────────────────────────────────────
print()
print('[B] PIXEL — ID: 1429033345028801')

pixel_id = '1429033345028801'
url = f'https://graph.facebook.com/v19.0/{pixel_id}?fields=name,creation_time,last_fired_time,is_unavailable&access_token={token}'
try:
    pix = json.loads(urllib.request.urlopen(url).read())
    print(f'  Nome:         {pix.get("name")}')
    print(f'  Ultimo fire:  {pix.get("last_fired_time","?")}')
    print(f'  Indisponivel: {pix.get("is_unavailable","?")}')
except Exception as e:
    print(f'  Erro: {e}')

# ─── AD04 STATUS ──────────────────────────────────────────────────────────
print()
print('[C] AD04 STATUS — ID: 120246450671710707')
url4 = f'https://graph.facebook.com/v19.0/120246450671710707?fields=name,status,effective_status&access_token={token}'
try:
    r4 = urllib.request.urlopen(url4)
    d4 = json.loads(r4.read())
    print(f'  Nome:   {d4.get("name")}')
    print(f'  Status: {d4.get("status")} / {d4.get("effective_status")}')
except urllib.error.HTTPError as e:
    err = json.loads(e.read())
    print(f'  ERRO: {err.get("error",{}).get("message","?")}')

# ─── LOCALES CHECK ────────────────────────────────────────────────────────
print()
print('[D] LOCALES [7, 23] = quais idiomas?')
# 7 = Portuguese (Brazil) — Locale ID
# 23 = Spanish (all)
locale_map = {
    7: 'Portugues (Brasil)',
    23: 'Espanhol (todos)',
    24: 'Espanhol (Espanha)',
    6: 'Alemao',
    2: 'Chines Simplificado',
    4: 'Frances',
    5: 'Holandes',
    8: 'Polones',
    9: 'Russo',
    10: 'Italiano',
    11: 'Japones',
    16: 'Ingles',
    25: 'Espanhol (Mexico)',
}
for loc in [7, 23]:
    print(f'  Locale {loc}: {locale_map.get(loc, "?")}')

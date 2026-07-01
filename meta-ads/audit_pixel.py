import sys, io, urllib.request, urllib.parse, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

req = urllib.request.Request(
    'https://www.mevolablog.com/presell',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'}
)
res = urllib.request.urlopen(req, timeout=15)
html = res.read().decode('utf-8', errors='ignore')

print('=== TODOS OS fbq() NO HTML ===')
fbq_calls = re.findall(r"fbq\s*\([^)]{0,400}\)", html, re.DOTALL)
if fbq_calls:
    for call in fbq_calls:
        clean = ' '.join(call.split())
        print(f'  {clean[:200]}')
else:
    print('  NENHUM fbq() encontrado no HTML estatico')
    print('  (Pixel pode carregar via script externo ou JS dinamico)')

print()
print('=== SCRIPTS EXTERNOS ===')
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
for s in scripts:
    if any(x in s.lower() for x in ['facebook', 'fbevents', 'pixel', 'analytics', 'gtag', 'gtm', 'kiwify', 'atomicat']):
        print(f'  {s[:120]}')

print()
print('=== HEAD COMPLETO ===')
head_m = re.search(r'<head[^>]*>(.*?)</head>', html, re.DOTALL | re.IGNORECASE)
if head_m:
    head = head_m.group(1)
    # Mostrar apenas linhas com pixel/tracking
    for line in head.split('\n'):
        if any(x in line.lower() for x in ['fbq', 'pixel', 'facebook', 'tracking', 'purchase', 'initiate', 'viewcontent', 'kiwify', 'gtm', 'gtag']):
            print(f'  {line.strip()[:200]}')

print()
print('=== BODY — procurando eventos de compra ===')
for keyword in ['Purchase', 'InitiateCheckout', 'ViewContent', 'AddToCart', 'fbq']:
    count = html.count(keyword)
    if count > 0:
        print(f'  Ocorrencias de "{keyword}": {count}')

print()
print('=== SCRIPTS INLINE COM EVENTOS ===')
inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
for i, script in enumerate(inline_scripts):
    if any(x in script for x in ['fbq', 'Purchase', 'InitiateCheckout', 'ViewContent', 'pixel']):
        print(f'\n-- Script inline #{i+1} --')
        clean = ' '.join(script.split())
        print(clean[:1000])

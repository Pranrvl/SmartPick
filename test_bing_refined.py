import urllib.request, urllib.parse, re, json

def search_bing_refined(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    # q=... phone gsmarena OR gadgets360 OR smartprix
    url = f'https://www.bing.com/images/search?q={urllib.parse.quote(query + " phone")}&first=1&scenario=ImageBasicHover'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    murls = re.findall(r'&quot;murl&quot;:&quot;(http[^&]+)&quot;', html)
    if not murls:
        murls = re.findall(r'"murl":"(http[^"]+)"', html)
    return murls

phones = [
    'Xiaomi Redmi Note 13 Pro Plus',
    'Vivo V60e',
    'iQOO Neo 10',
    'Realme GT 6 5G',
    'Motorola Edge 60 Pro',
    'Samsung Galaxy S24 Ultra'
]

for p in phones:
    urls = search_bing_refined(p)
    # filter for common image extensions
    valid = [u for u in urls if any(u.lower().endswith(ext) or ext in u.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])]
    print(p, '->', valid[0] if valid else 'NONE')

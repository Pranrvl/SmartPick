import urllib.request, urllib.parse, re, json

def search_bing_image(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = f'https://www.bing.com/images/search?q={urllib.parse.quote(query + " smartphone official")}&first=1'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    murls = re.findall(r'&quot;murl&quot;:&quot;(http[^&]+)&quot;', html)
    if not murls:
        murls = re.findall(r'"murl":"(http[^"]+)"', html)
    return murls

for phone in ['Xiaomi Redmi Note 13 Pro Plus', 'Vivo V60e', 'iQOO Neo 10', 'Realme GT 6 5G', 'Motorola Edge 60 Pro']:
    try:
        urls = search_bing_image(phone)
        print(f'{phone}: {urls[0] if urls else "NONE"}')
    except Exception as e:
        print(f'{phone}: Error {e}')

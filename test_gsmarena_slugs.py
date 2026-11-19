import urllib.request, re

def check_gsmarena_url(slug):
    url = f"https://fdn2.gsmarena.com/vv/bigpic/{slug}.jpg"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                return url
    except Exception:
        pass
    return None

test_slugs = [
    'xiaomi-redmi-note-13-pro-plus',
    'realme-gt-6',
    'realme-gt-6t',
    'vivo-v30e',
    'vivo-v40e',
    'samsung-galaxy-s24-ultra',
    'apple-iphone-15-pro-max',
    'motorola-edge-50-pro',
    'nothing-phone-2a',
    'infinix-note-40-pro',
    'iqoo-neo-9-pro'
]

for s in test_slugs:
    res = check_gsmarena_url(s)
    print(s, '->', res)

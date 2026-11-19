import urllib.request, urllib.parse, re, json

def search_yahoo_images(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    # Clean model name: remove (..GB RAM..)
    clean_query = re.sub(r'\s*\([^)]*\)', '', query).strip()
    url = f"https://images.search.yahoo.com/search/images?p={urllib.parse.quote(clean_query + ' smartphone')}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Yahoo images embeds imgurl in data or json
            # e.g., "iurl":"https:\/\/..."
            urls = re.findall(r'"imgurl":"(https?://[^"]+)"', html)
            if not urls:
                urls = re.findall(r'&imgurl=([^&"]+)', html)
                urls = [urllib.parse.unquote(u) for u in urls]
            if not urls:
                # also check <img data-src="..."
                urls = re.findall(r'src=["\'](https://tse[0-9]\.mm\.bing\.net/th\?id=[^"\']+)["\']', html)
            return clean_query, urls
    except Exception as e:
        return clean_query, [str(e)]

test_models = [
    'Xiaomi Redmi Note 13 Pro Plus (12GB RAM + 256GB)',
    'Vivo V60e (12GB RAM + 256GB)',
    'iQOO Neo 10 (16GB RAM + 512GB)',
    'Realme GT 6 5G (16GB RAM + 512GB)',
    'Motorola Edge 60 Pro (16GB RAM + 512GB)'
]

for m in test_models:
    cq, urls = search_yahoo_images(m)
    print(cq, '->', urls[:2] if urls else 'NONE')

import urllib.request, urllib.parse, json

def get_wiki_image(title):
    headers = {'User-Agent': 'SmartPickBot/1.0 (contact: test@example.com)'}
    # Wikipedia opensearch or action=query
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&pithumbsize=300&generator=search&gsrsearch={urllib.parse.quote(title + ' smartphone')}&gsrlimit=3"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                if 'thumbnail' in pdata:
                    return pdata['thumbnail']['source']
    except Exception as e:
        print(f"Error {title}: {e}")
    return None

for p in ['Samsung Galaxy S24', 'iPhone 15', 'Xiaomi 13', 'Realme GT', 'OnePlus 12', 'Google Pixel 8']:
    img = get_wiki_image(p)
    print(p, '->', img)

import urllib.request, urllib.parse, json

def search_commons_clean(query):
    params = {
        'action': 'query',
        'generator': 'search',
        'gsrsearch': query,
        'gsrlimit': '5',
        'prop': 'pageimages',
        'pithumbsize': '400',
        'format': 'json'
    }
    url = f"https://commons.wikimedia.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'SmartPickImageFinder/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                if 'thumbnail' in p:
                    return p['title'], p['thumbnail']['source']
    except Exception as e:
        print("Error:", e)
    return None, None

test_queries = [
    'Xiaomi Redmi Note 13',
    'Samsung Galaxy S24',
    'iPhone 15',
    'Realme GT',
    'Vivo phone',
    'Motorola Moto',
    'OnePlus',
    'Poco phone'
]

for q in test_queries:
    t, img = search_commons_clean(q)
    print(q, '->', t, ':', img)

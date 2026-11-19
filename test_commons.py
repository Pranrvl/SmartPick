import urllib.request, urllib.parse, json

def search_commons(query):
    # Search Wikimedia Commons for smartphone photos
    params = {
        'action': 'query',
        'generator': 'search',
        'gsrsearch': f'{query} smartphone filetype:bitmap',
        'gsrlimit': '3',
        'prop': 'pageimages|imageinfo',
        'pithumbsize': '400',
        'iiprop': 'url',
        'format': 'json'
    }
    url = f"https://commons.wikimedia.org/w/api.php?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'SmartPickCommons/1.0 (contact: student@univ.ac.id)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                if 'thumbnail' in p:
                    return p['title'], p['thumbnail']['source']
    except Exception as e:
        print("Commons err:", e)
    return None, None

for q in ['Xiaomi Redmi', 'Vivo smartphone', 'Realme smartphone', 'Samsung Galaxy', 'iPhone', 'Poco smartphone', 'Oppo smartphone', 'Infinix smartphone']:
    t, img = search_commons(q)
    print(q, '->', t, ':', img)

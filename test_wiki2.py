import urllib.request, urllib.parse, json

def search_wiki(query):
    # Try wikipedia search
    url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=5&prop=pageimages|extracts&piprop=thumbnail&pithumbsize=400&exintro=1&explaintext=1&exchars=100"
    req = urllib.request.Request(url, headers={'User-Agent': 'SmartPickApp/1.0 (contact: student@univ.ac.id)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                title = p.get('title', '')
                thumb = p.get('thumbnail', {}).get('source', '')
                extract = p.get('extract', '')
                if thumb and ('phone' in extract.lower() or 'smartphone' in extract.lower() or 'series' in extract.lower() or 'mobile' in extract.lower()):
                    return title, thumb
            # fallback to first thumb
            for pid, p in pages.items():
                if 'thumbnail' in p:
                    return p.get('title'), p['thumbnail']['source']
    except Exception as e:
        print("Err:", e)
    return None, None

for q in ['Redmi Note 13', 'Vivo V30', 'iQOO Neo', 'Realme GT', 'Motorola Edge']:
    t, img = search_wiki(q)
    print(q, '->', t, ':', img)

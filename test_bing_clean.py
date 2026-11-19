import urllib.request, urllib.parse, re, json

def search_bing_phone(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    # Clean query from parentheses (RAM, ROM specs)
    clean_name = re.sub(r'\s*\([^)]*\)', '', query).strip()
    
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(clean_name + ' smartphone official')}&first=1"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # Bing provides thumbnail URLs: "turl":"https://tse..." or src="https://tse..."
    turls = re.findall(r'&quot;turl&quot;:&quot;(https?://tse[^&]+)&quot;', html)
    if not turls:
        turls = re.findall(r'"turl":"(https?://tse[^"]+)"', html)
    
    # Also original murls
    murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+)&quot;', html)
    if not murls:
        murls = re.findall(r'"murl":"(https?://[^"]+)"', html)
    
    # Also fallback to src="https://tse...
    if not turls:
        turls = re.findall(r'src=["\'](https://tse[0-9]\.mm\.bing\.net/th\?id=[^"\']+)["\']', html)
        
    return clean_name, turls, murls

test_models = [
    'Xiaomi Redmi Note 13 Pro Plus (12GB RAM + 256GB)',
    'Vivo V60e (12GB RAM + 256GB)',
    'iQOO Neo 10 (16GB RAM + 512GB)',
    'Realme GT 6 5G (16GB RAM + 512GB)',
    'Motorola Edge 60 Pro (16GB RAM + 512GB)',
    'Samsung Galaxy M17 5G (8GB RAM + 128GB)',
    'Nothing Phone 3a Lite (8GB RAM + 256GB)',
    'Poco M7 Plus 5G (4GB RAM + 128GB)',
]

for m in test_models:
    try:
        cn, turls, murls = search_bing_phone(m)
        print(f"=== {cn} ===")
        print(f"Thumb: {turls[0] if turls else 'NONE'}")
        print(f"Full:  {murls[0] if murls else 'NONE'}")
    except Exception as e:
        print(f"Error {m}: {e}")

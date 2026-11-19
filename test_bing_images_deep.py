import urllib.request, urllib.parse, re, json

def get_bing_image_url(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    # Clean model query
    clean = re.sub(r'\s*\([^)]*\)', '', query).strip()
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(clean + ' smartphone official')}&first=1"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # 1. Look for murl inside json
            murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+)&quot;', html)
            if not murls:
                murls = re.findall(r'"murl":"(https?://[^"]+)"', html)
            
            # 2. Look for thumbnail urls (tse.mm.bing.net)
            turls = re.findall(r'&quot;turl&quot;:&quot;(https?://tse[^&]+)&quot;', html)
            if not turls:
                turls = re.findall(r'src=["\'](https://tse[0-9]\.mm\.bing\.net/th\?id=[^"\']+)["\']', html)
            
            # Filter murls for valid image extensions
            valid_murls = [u for u in murls if any(ext in u.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])]
            
            return {
                'clean': clean,
                'valid_murls': valid_murls[:3],
                'turls': turls[:3]
            }
    except Exception as e:
        return {'clean': clean, 'error': str(e)}

models = [
    'Xiaomi Redmi Note 13 Pro Plus',
    'Realme GT 6 5G',
    'Samsung Galaxy S24 Ultra',
    'iPhone 15 Pro',
    'Vivo V30'
]

for m in models:
    res = get_bing_image_url(m)
    print(m, res)

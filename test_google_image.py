import urllib.request, urllib.parse, re, json

def search_google_image(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    url = f'https://www.google.com/search?q={urllib.parse.quote(query + " smartphone gsmarena")}&tbm=isch'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # In google images html, image urls often appear in scripts or img tags
    # Let's inspect what img urls or data-src or original urls appear
    urls = re.findall(r'\["(https?://[^"]+\.(?:jpg|jpeg|png|webp))"', html)
    if not urls:
        urls = re.findall(r'src="(https?://[^"]+)"', html)
    return urls

print('Testing Google Images...')
urls = search_google_image('Xiaomi Redmi Note 13 Pro Plus')
print('Found:', len(urls))
for u in urls[:5]:
    print(u)

import urllib.request, urllib.parse, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
url = f'https://www.google.com/search?q={urllib.parse.quote("Xiaomi Redmi Note 13 Pro Plus official phone")}&udm=2'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=8) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# find encrypted-tbn0.gstatic.com or similar thumbnails
tbns = re.findall(r'(https://encrypted-tbn[0-9]\.gstatic\.com/images\?q=[^"&]+)', html)
print('TBN images count:', len(tbns))
for t in set(tbns[:5]):
    print(t)

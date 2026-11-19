import urllib.request, urllib.parse, re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# GSMArena search URL
url = "https://m.gsmarena.com/results.php3?sQuickSearch=yes&sName=" + urllib.parse.quote("Redmi Note 13 Pro+")
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        # find img src inside results
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+\.jpg)["\']', html)
        print("GSMArena imgs:", imgs[:5])
        links = re.findall(r'<a href=["\']([^"\']+\.php)["\']><img', html)
        print("GSMArena links:", links[:5])
except Exception as e:
    print("GSMArena error:", e)

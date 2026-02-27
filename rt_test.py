import urllib.request, re, json

url = 'https://www.rottentomatoes.com/search?search=Life+Is+Beautiful'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', errors='replace')

print(f"Page length: {len(html)}")

# Check for score patterns
patterns = [
    (r'"tomatoScore"\s*:\s*"?(\d+)"?', 'tomatoScore JSON'),
    (r'tomatometerscore="(\d+)"', 'tomatometerscore attr'),
    (r'data-tomatometerscore="(\d+)"', 'data-tomatometerscore'),
    (r'audiencescore="(\d+)"', 'audiencescore'),
]

for pat, name in patterns:
    m = re.search(pat, html, re.I)
    if m:
        print(f"MATCH [{name}]: {m.group(0)[:120]}")
    else:
        print(f"NO MATCH [{name}]")

# Check if it's a SPA that loads via JS
if 'search-page-media-row' in html:
    print("\nFound search-page-media-row web components (server rendered)")
    matches = re.findall(r'tomatometer[^"]*"(\d+)"', html, re.I)
    print(f"  tomatometer matches: {matches}")
else:
    print("\nNo search-page-media-row found - might be JS-rendered SPA")

# Save a snippet for analysis
with open('rt_debug.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\nSaved full HTML to rt_debug.html")

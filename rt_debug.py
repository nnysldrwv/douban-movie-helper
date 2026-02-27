import urllib.request, urllib.parse, re

url = f'https://www.rottentomatoes.com/search?search={urllib.parse.quote("Life Is Beautiful")}'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='replace')

# Find ALL matches of the full-domain pattern used in the script
all_full = list(re.finditer(r'rottentomatoes\.com/m/([^"\s]+)"', html))
print(f"Full-domain /m/ matches: {len(all_full)}")
for i, m in enumerate(all_full[:8]):
    start = max(0, m.start()-50)
    context = html[start:m.end()+5].replace('\n', ' ')
    print(f"  [{i}] slug={m.group(1)}")
    print(f"      context: ...{context}...")
    print()

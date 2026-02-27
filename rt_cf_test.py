import urllib.request, urllib.parse

# Test if RT returns Cloudflare challenge or actual content
url = 'https://www.rottentomatoes.com/search?search=Interstellar'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml'
})
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode('utf-8', errors='replace')

print(f'Status: {resp.status}')
print(f'Content length: {len(html)}')
print(f'Contains Cloudflare challenge: {"cf-challenge" in html.lower() or "cf_clearance" in html.lower() or "Just a moment" in html}')
print(f'Contains search results: {"/m/" in html}')

# Check if the movie page also works
url2 = 'https://www.rottentomatoes.com/m/interstellar_2014'
req2 = urllib.request.Request(url2, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
})
resp2 = urllib.request.urlopen(req2, timeout=10)
html2 = resp2.read().decode('utf-8', errors='replace')

print(f'\nMovie page status: {resp2.status}')
print(f'Movie page length: {len(html2)}')
print(f'Contains aggregateRating: {"aggregateRating" in html2}')
print(f'Contains Cloudflare: {"cf-challenge" in html2.lower() or "Just a moment" in html2}')

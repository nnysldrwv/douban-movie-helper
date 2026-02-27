import urllib.request, re, json

# Test 1: RT search page
url = 'https://www.rottentomatoes.com/search?search=Life+Is+Beautiful'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode('utf-8', errors='replace')
    
    # Save for analysis
    with open('rt_search.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Look for movie URLs
    urls = re.findall(r'/m/[a-z0-9_\-]+', html)
    print('Movie URLs found:', list(set(urls))[:10])
    
    # Look for any tomatometer
    for pattern in [r'tomatometerscore="(\d+)"', r'data-tomatometerscore="(\d+)"', 
                    r'"tomatoScore"\s*:\s*"?(\d+)"?', r'audiencescore="(\d+)"',
                    r'criticsScore.*?(\d+)', r'score.*?(\d+)%']:
        matches = re.findall(pattern, html, re.I)
        if matches:
            print(f'  Pattern [{pattern}]: {matches[:3]}')
    
    print(f'\nHTML length: {len(html)} chars')
    
    # Check if it's SPA (JavaScript rendered)
    if '<search-page-result' in html:
        print('Found search-page-result web component')
    if 'data-qa="data-row"' in html:
        print('Found data-row')
        
except Exception as e:
    print(f'Error: {e}')

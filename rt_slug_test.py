import urllib.request, urllib.parse, re

def test_slug_extraction(title):
    url = f'https://www.rottentomatoes.com/search?search={urllib.parse.quote(title)}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='replace')
    
    # Test the EXACT same regex from the userscript (line 212)
    m1 = re.search(r'rottentomatoes\.com/m/([^"\s]+)"', html)
    print(f'[{title}] Script regex: {m1.group(1) if m1 else "NONE"}')
    
    # Also check all /m/ patterns
    all_slugs = re.findall(r'/m/([^"\'<>\s]+)', html)
    print(f'[{title}] All /m/ slugs: {all_slugs[:5]}')
    print()

test_slug_extraction("Life Is Beautiful")
test_slug_extraction("Interstellar")
test_slug_extraction("The Shawshank Redemption")
test_slug_extraction("Erta perto demais")  # Non-English title test

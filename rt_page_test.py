import urllib.request, re

# Test: directly fetch the RT movie page for Life Is Beautiful
url = 'https://www.rottentomatoes.com/m/1084398-life_is_beautiful'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', errors='replace')

print(f"Page length: {len(html)}")

# Look for tomatometer score on the actual movie page
patterns = [
    (r'<rt-button[^>]*slot="criticsScore"[^>]*>.*?<rt-text[^>]*>(\d+)</rt-text>', 'criticsScore slot'),
    (r'"tomatometerScore"\s*:\s*(\d+)', 'tomatometerScore JSON'),
    (r'tomatometerscore.*?(\d+)', 'tomatometerscore'),
    (r'"scoreSentiment":"(\w+)"', 'scoreSentiment'),
    (r'critics-score.*?(\d+)%', 'critics-score'),
    (r'audience-score.*?(\d+)%', 'audience-score'),
    (r'<score-board[^>]*tomatometerscore="(\d+)"', 'score-board tomato'),
    (r'<score-board[^>]*audiencescore="(\d+)"', 'score-board audience'),
    (r'"ratingValue"\s*:\s*"?(\d+)"?', 'ratingValue LD+JSON'),
]

for pat, name in patterns:
    m = re.search(pat, html, re.I | re.S)
    if m:
        print(f"MATCH [{name}]: {m.group(0)[:150]}")
    else:
        print(f"NO MATCH [{name}]")

# Save for analysis
with open('rt_movie_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\nSaved to rt_movie_page.html")

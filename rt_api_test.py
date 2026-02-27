import urllib.request, json, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Test 1: RT napi search endpoint
print("=== Test 1: RT napi/search ===")
try:
    url = 'https://www.rottentomatoes.com/napi/search?query=Life+Is+Beautiful'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode())
    movies = data.get('movies', [])
    print(f"Found {len(movies)} movies")
    if movies:
        m = movies[0]
        print(f"  Title: {m.get('name')}")
        print(f"  URL: {m.get('url')}")
        print(f"  Year: {m.get('year')}")
        print(f"  Meter score: {m.get('meterScore')}")
        print(f"  Meter class: {m.get('meterClass')}")
        print(f"  Keys: {list(m.keys())}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: RT napi v2
print("\n=== Test 2: RT api/ripple ===")
try:
    url = 'https://www.rottentomatoes.com/api/ripple/movie/life_is_beautiful'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    print(f"Status: {resp.status}")
    data = resp.read().decode()
    print(f"Response: {data[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Direct RT movie page JSON-LD
print("\n=== Test 3: RT movie page ===")
try:
    url = 'https://www.rottentomatoes.com/m/life_is_beautiful'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode('utf-8', errors='replace')
    
    # Extract JSON-LD
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
    for block in ld_blocks:
        try:
            ld = json.loads(block)
            if 'aggregateRating' in ld:
                print(f"  Rating: {ld['aggregateRating']}")
        except:
            pass
    
    # Extract score from scoreboard or score-board element
    score_match = re.findall(r'(?:critics-score|criticsScore|tomatometer)[^>]*?(\d+)%?', html[:50000])
    print(f"  Score matches: {score_match[:5]}")
    
    # Look for score-board web component
    sb = re.findall(r'<score-board[^>]*>', html)
    if sb:
        print(f"  Score-board: {sb[0][:300]}")
    
    # Look for media-scorecard
    mc = re.findall(r'<media-scorecard[^>]*>', html)
    if mc:
        print(f"  Media-scorecard: {mc[0][:300]}")
    
    # Any percentage in the first portion
    pcts = re.findall(r'>(\d{1,3})%<', html[:100000])
    print(f"  Percentages found: {pcts[:10]}")
    
except Exception as e:
    print(f"Error: {e}")

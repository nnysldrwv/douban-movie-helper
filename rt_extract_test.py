import urllib.request, json, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Step 1: Fetch RT movie page
url = 'https://www.rottentomatoes.com/m/life_is_beautiful'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode('utf-8', errors='replace')

# Method 1: Look for score-details-audience-score-value or tomatometer
print("=== Method 1: ld+json ===")
ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
for i, block in enumerate(ld_blocks):
    try:
        ld = json.loads(block)
        if isinstance(ld, dict) and ld.get('@type') in ['Movie', 'TVSeries']:
            print(f"  Block {i}: type={ld.get('@type')}, rating={ld.get('aggregateRating')}")
    except:
        pass

# Method 2: media-scorecard attributes
print("\n=== Method 2: media-scorecard ===")
# Get everything around media-scorecard
mc_area = re.findall(r'<media-scorecard.*?</media-scorecard>', html, re.S)
if mc_area:
    area = mc_area[0][:2000]
    # Look for tomatometer/audience score
    tm = re.findall(r'tomatometerscore["\s:=]+(\d+)', area, re.I)
    aud = re.findall(r'audiencescore["\s:=]+(\d+)', area, re.I)
    print(f"  Tomatometer: {tm}")
    print(f"  Audience: {aud}")

# Method 3: scoreboard__info section  
print("\n=== Method 3: score-icon-critics ===")
critics = re.findall(r'score-icon-critics["\s].*?(\d+)%', html[:80000], re.S)
print(f"  Critics: {critics[:5]}")

# Method 4: JSON data in script tags
print("\n=== Method 4: scoreboard JSON ===")
sb_data = re.findall(r'"scoreboard"\s*:\s*(\{[^}]+\})', html)
if sb_data:
    for s in sb_data[:3]:
        print(f"  {s[:300]}")

# Method 5: __NEXT_DATA__ or any state JSON
print("\n=== Method 5: State JSON ===")
state = re.findall(r'<script[^>]*id="score-details-json"[^>]*>(.*?)</script>', html, re.S)
if state:
    print(f"  Score details JSON: {state[0][:500]}")

# Method 6: Look for mediaScorecard JSON (could be in initial-state)
print("\n=== Method 6: Direct score search ===")
# The simplest: find the tomatometer in a meta or data attribute
meta_tm = re.findall(r'(?:tomatometer|tomatometerScore|critics_?score)["\s:=]+["\s]*(\d+)', html, re.I)
print(f"  Tomatometer refs: {meta_tm[:10]}")

# Check for criticsScore in any JSON
critics_json = re.findall(r'"criticsScore"\s*:\s*(\d+)', html)
print(f"  criticsScore JSON: {critics_json[:5]}")

tom_json = re.findall(r'"tomatometerScore"\s*:\s*(\d+)', html)
print(f"  tomatometerScore JSON: {tom_json[:5]}")

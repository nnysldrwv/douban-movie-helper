import urllib.request, re, json

def test_rt(title):
    print(f"\n{'='*50}")
    print(f"Testing: {title}")
    print('='*50)
    
    # Step 1: Search
    search_url = f'https://www.rottentomatoes.com/search?search={urllib.parse.quote(title)}'
    req = urllib.request.Request(search_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='replace')
    
    slug_match = re.search(r'rottentomatoes\.com/m/([^"\s]+)"', html)
    if not slug_match:
        print('[Step1] No slug found!')
        # Debug
        all_m = re.findall(r'/m/([^"\'<>\s]+)', html)
        if all_m:
            print(f'[Debug] Found /m/ slugs: {all_m[:5]}')
        return
    
    slug = slug_match.group(1)
    print(f'[Step1] Found slug: {slug}')
    
    # Step 2: Fetch movie page
    page_url = f'https://www.rottentomatoes.com/m/{slug}'
    req2 = urllib.request.Request(page_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    html2 = urllib.request.urlopen(req2, timeout=10).read().decode('utf-8', errors='replace')
    print(f'[Step2] Page length: {len(html2)} chars')
    
    score = None
    
    # Method 1: JSON-LD
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>([\s\S]*?)</script>', html2, re.IGNORECASE)
    for block in ld_blocks:
        try:
            ld = json.loads(block)
            if isinstance(ld, dict) and 'aggregateRating' in ld:
                val = ld['aggregateRating'].get('ratingValue')
                print(f'[Method1-JSONLD] ratingValue: {val}')
                if val:
                    score = str(val)
        except Exception as e:
            pass
    
    # Method 2: tomatometerScore
    m1 = re.search(r"""tomatometerScore["']?\s*[:=]\s*["']?(\d+)""", html2, re.IGNORECASE)
    if m1:
        print(f'[Method2-tomatometer] {m1.group(1)}')
        if not score: score = m1.group(1)
    
    # Method 3: scoreboard/scorecard
    m2 = re.search(r'(?:score-board|media-scorecard|scoreboard)[\s\S]*?(\d{1,3})%', html2)
    if m2:
        print(f'[Method3-scoreboard] {m2.group(1)}%')
        if not score: score = m2.group(1)
    
    # Method 4: critics-score
    m3 = re.search(r'critics-score[\s\S]{0,200}?(\d{1,3})%', html2)
    if m3:
        print(f'[Method4-critics] {m3.group(1)}%')
        if not score: score = m3.group(1)
    
    # Method 5: Tomatometer keyword
    m4 = re.search(r'Tomatometer[\s\S]{0,300}?(\d{1,3})%', html2)
    if m4:
        print(f'[Method5-Tomatometer] {m4.group(1)}%')
        if not score: score = m4.group(1)
    
    # Debug: show context around first few percentages
    pct_matches = list(re.finditer(r'(\d{1,3})%', html2))
    if pct_matches:
        print(f'\n[Debug] Found {len(pct_matches)} percentage values in page')
        for m in pct_matches[:5]:
            start = max(0, m.start()-100)
            end = min(len(html2), m.end()+30)
            context = html2[start:end].replace('\n', ' ').replace('\r', '')
            print(f'  [{m.group(0)}] ...{context}...')
    
    print(f'\n>>> FINAL SCORE: {score}%' if score else '\n>>> FINAL SCORE: NONE')

import urllib.parse
test_rt("Life Is Beautiful")
test_rt("Interstellar")
test_rt("The Shawshank Redemption")

import urllib.request, json, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def get_rt_score(movie_slug):
    """Extract Tomatometer from RT movie page"""
    url = f'https://www.rottentomatoes.com/m/{movie_slug}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode('utf-8', errors='replace')
    
    # The first <rt-text> with a percentage in the media-scorecard area
    # should be the tomatometer score
    # More precise: look for the first percentage near score-icon-critics
    # But best: find the percentage inside the media-scorecard component
    
    # Strategy: Find <media-scorecard> block, then get first XX% from rt-text
    mc_match = re.search(r'<media-scorecard.*?</media-scorecard>', html, re.S)
    if mc_match:
        mc_html = mc_match.group(0)
        # First rt-text percentage = Tomatometer (critics), second = Audience
        pcts = re.findall(r'<rt-text[^>]*>(\d+%)</rt-text>', mc_html)
        if pcts:
            return pcts[0]  # First one is Tomatometer
    
    # Fallback: any percentage near score-icon-critics
    m = re.search(r'score-icon-critics.*?(\d+)%', html[:30000], re.S)
    if m:
        return m.group(1) + '%'
    
    return None

def search_rt_slug(movie_title):
    """Search RT and return first movie slug"""
    url = f'https://www.rottentomatoes.com/search?search={urllib.request.quote(movie_title)}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode('utf-8', errors='replace')
    
    # Find first /m/ link
    m = re.search(r'rottentomatoes\.com(/m/[^"]+)"', html)
    if m:
        return m.group(1).split('/')[-1]  # Just the slug part
    
    # Also try bare /m/ paths
    m2 = re.search(r'href="(/m/[^"]+)"', html)
    if m2:
        return m2.group(1).split('/')[-1]
    
    return None

# Test with known movies
test_cases = [
    ('Life Is Beautiful', 'life_is_beautiful', '1084398-life_is_beautiful'),
    ('The Shawshank Redemption', 'shawshank_redemption', None),
    ('Interstellar', 'interstellar_2014', None),
]

for title, known_slug, alt_slug in test_cases:
    slug = alt_slug or known_slug
    print(f"\n{title}:")
    try:
        score = get_rt_score(slug)
        print(f"  Direct fetch ({slug}): {score}")
    except Exception as e:
        print(f"  Direct fetch error: {e}")

# Test search
print("\n\n=== Search Test ===")
for query in ['Life Is Beautiful', 'Interstellar', 'The Shawshank Redemption']:
    try:
        slug = search_rt_slug(query)
        print(f"  '{query}' -> slug: {slug}")
        if slug:
            score = get_rt_score(slug)
            print(f"    -> score: {score}")
    except Exception as e:
        print(f"  '{query}' -> error: {e}")

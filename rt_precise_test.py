import urllib.request, json, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Test with two movies
for title, slug in [('Life Is Beautiful', 'life_is_beautiful'), ('The Shawshank Redemption', 'shawshank_redemption')]:
    print(f"\n{'='*50}")
    print(f"Movie: {title} ({slug})")
    
    url = f'https://www.rottentomatoes.com/m/{slug}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode('utf-8', errors='replace')
    
    # Method A: Find the first score-icon-critics percentage
    # Look for the pattern near "Tomatometer" or "critics"
    # Usually appears as: score-icon-critics-xxx ... >XX%<
    m = re.search(r'score-icon-critics[^>]*>[^<]*</rt-icon>\s*<span[^>]*>\s*(\d+)%', html, re.S)
    if m:
        print(f"  Method A (score-icon-critics span): {m.group(1)}%")
    
    # Method B: Find percentage near "Tomatometer"  
    m2 = re.search(r'Tomatometer.*?(\d+)%', html[:50000], re.S)
    if m2:
        print(f"  Method B (near Tomatometer): {m2.group(1)}%")
    
    # Method C: score-icon-critics followed by percentage in any child
    m3 = re.search(r'score-icon-critics[^"]*"[^>]*>.*?(\d+)%', html[:50000], re.S)
    if m3:
        print(f"  Method C (score-icon-critics child): {m3.group(1)}%")
    
    # Method D: Look for the actual structure from media-scorecard
    # Often: <rt-text ... context="label">XX%</rt-text>
    # within a critics section
    m4 = re.findall(r'<rt-text[^>]*>(\d+%)</rt-text>', html[:50000])
    if m4:
        print(f"  Method D (rt-text percentages): {m4[:5]}")
    
    # Method E: The simplest - slot="criticsScore" or similar
    m5 = re.search(r'slot="criticsScore"[^>]*>(\d+)', html, re.S)
    if m5:
        print(f"  Method E (slot criticsScore): {m5.group(1)}%")
    
    # Method F: data attributes on media-scorecard
    mc = re.search(r'<media-scorecard(.*?)>', html, re.S)
    if mc:
        attrs = mc.group(1)
        print(f"  Media-scorecard attrs: {attrs[:500]}")

print("\n\n=== Now test RT search to find slug ===")
# The key question: how to get the slug from a search
url = 'https://www.rottentomatoes.com/search?search=Life+Is+Beautiful'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode('utf-8', errors='replace')

# Save a portion for analysis
with open('rt_search_sample.html', 'w', encoding='utf-8') as f:
    f.write(html[:100000])

# Look for /m/ URLs
slugs = re.findall(r'href="(/m/[^"]+)"', html)
print(f"Movie slugs found: {slugs[:10]}")

# Also look in JSON data
json_slugs = re.findall(r'"url"\s*:\s*"(/m/[^"]+)"', html)
print(f"JSON movie slugs: {json_slugs[:10]}")

# Look for search-page data
search_data = re.findall(r'<search-page-media-row[^>]*>(.*?)</search-page-media-row>', html, re.S)
print(f"Search rows: {len(search_data)}")
if search_data:
    print(f"First row (200 chars): {search_data[0][:200]}")

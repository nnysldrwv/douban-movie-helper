import re

with open('rt_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find where "80" appears near "tomato" or "score"  
# Also look for the movie section vs TV section
# Check for movie-specific rows
for m in re.finditer(r'rottentomatoes\.com/m/', html):
    start = max(0, m.start() - 500)
    end = min(len(html), m.end() + 300)
    context = html[start:end]
    # Find tomatometerscore in this context
    score = re.search(r'tomatometerscore="(\d*)"', context)
    title = re.search(r'slot="title"[^>]*>([^<]+)<', context)
    year = re.search(r'releaseyear="(\d+)"', context)
    href = re.search(r'href="(https://www\.rottentomatoes\.com/m/[^"]+)"', context)
    print(f"Movie: title={title.group(1).strip() if title else '?'}, year={year.group(1) if year else '?'}, score={score.group(1) if score else 'N/A'}, href={href.group(1) if href else '?'}")

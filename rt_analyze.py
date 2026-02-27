import re

with open('rt_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all search-page-media-row tags and their attributes
tag_pattern = re.compile(r'<search-page-media-row([^>]*)>', re.S)
for i, m in enumerate(tag_pattern.finditer(html)):
    attrs = m.group(1)
    tomato = re.search(r'tomatometerscore="(\d+)"', attrs, re.I)
    year = re.search(r'(?:releaseyear|startyear)="(\d+)"', attrs, re.I)
    
    # Get the title from the content after this tag
    content_start = m.end()
    content_end = html.find('</search-page-media-row>', content_start)
    if content_end == -1:
        content_end = content_start + 2000
    content = html[content_start:content_end]
    
    title_match = re.search(r'slot="title"[^>]*>([^<]+)<', content)
    title = title_match.group(1).strip() if title_match else 'N/A'
    
    print(f"Row {i}: title={title}, year={year.group(1) if year else '?'}, tomato={tomato.group(1) if tomato else 'N/A'}")
    
    if i >= 8:
        break

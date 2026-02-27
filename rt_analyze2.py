import re

with open('rt_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all tomatometerscore occurrences with 500-char context
for m in re.finditer(r'tomatometerscore', html, re.I):
    start = max(0, m.start() - 300)
    end = min(len(html), m.end() + 200)
    context = html[start:end]
    print(f"=== Position {m.start()} ===")
    print(context)
    print()

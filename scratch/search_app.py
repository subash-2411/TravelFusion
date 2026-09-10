import os

app_path = r'c:\kutty\app.py'
output_path = r'c:\kutty\scratch\search_results.txt'

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines, 1):
    line_lower = line.lower()
    if 'google' in line_lower or 'oauth' in line_lower or 'def login' in line_lower or 'route(\'/login\'' in line_lower or 'route(\"/login\"' in line_lower:
        results.append(f"Line {i}: {line.strip()}")

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print(f"Done, found {len(results)} matches.")

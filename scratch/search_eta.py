with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f, 1):
        if 'eta_minutes' in line.lower() or 'eta_mins' in line.lower():
            print(f"{i}: {line.strip()}")

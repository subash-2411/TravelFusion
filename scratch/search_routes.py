with open('c:/Kutty/app.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '@app.route' in line:
        print(f"Line {i+1}: {line.strip()}")
        # print the next few lines too
        for j in range(1, 4):
            if i+j < len(lines):
                print(f"  {lines[i+j].strip()}")

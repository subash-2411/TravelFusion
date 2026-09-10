import sys
import os

# Get the project root directory dynamically (one level up from 'scratch' folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from custom_flask import template_to_py

template_path = os.path.join(BASE_DIR, 'templates', 'verify.html')
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

py_code = template_to_py(content)

output_path = os.path.join(BASE_DIR, 'scratch', 'compiled_verify.py')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(py_code)
print("Saved to compiled_verify.py")

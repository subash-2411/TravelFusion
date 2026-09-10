import custom_flask
import sys

with open('templates/journey_tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
try:
    py_code = custom_flask.template_to_py(content)
    # Mock compile
    compile(py_code, '<template>', 'exec')
    print("COMPILE SUCCESS")
except Exception as e:
    print("COMPILE FAILED")
    import traceback
    traceback.print_exc()
    sys.exit(1)

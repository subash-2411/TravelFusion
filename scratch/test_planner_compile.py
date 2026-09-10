import sys
sys.path.append('c:\\Kutty')
import custom_flask

with open('c:\\Kutty\\templates\\travel_planner.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
try:
    py_code = custom_flask.template_to_py(content)
    # just compile it
    exec(py_code, {'session': {}, 'routes_json': '{}', 'budget': 1000})
    print("COMPILE SUCCESS")
except Exception as e:
    print("COMPILE FAILED")
    import traceback
    traceback.print_exc()

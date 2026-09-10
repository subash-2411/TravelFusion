import custom_flask

with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
try:
    py_code = custom_flask.template_to_py(content)
    # print(py_code) # just compile it
    exec(py_code, {})
    print("COMPILE SUCCESS")
except Exception as e:
    print("COMPILE FAILED")
    import traceback
    traceback.print_exc()

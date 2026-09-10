import app
import custom_flask

# Mock session
custom_flask.session['admin_id'] = 1

try:
    response = app.admin_dashboard()
    print("SUCCESS")
    # print(response[:500])
except Exception as e:
    print("FAILED WITH ERROR:")
    import traceback
    traceback.print_exc()

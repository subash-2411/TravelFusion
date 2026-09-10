import app
import custom_flask

# Mock session and context
custom_flask.session._thread_local.session = {'admin_id': 1, 'admin_user': 'admin'}
try:
    response = app.admin_dashboard()
    print("SUCCESS")
    # check if response contains an error
    if "Template Compilation Error" in response:
        print("FOUND ERROR IN RESPONSE:")
        print(response)
except Exception as e:
    print("FAILED WITH EXCEPTION:")
    import traceback
    traceback.print_exc()

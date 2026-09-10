import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app
import database
from custom_flask import _local, session, Request

print("Checking Drivers table...")
drivers = database.fetch_all("SELECT * FROM Drivers")
print(f"Drivers found: {len(drivers)}")
for d in drivers:
    print(f"Driver ID: {d['id']}, Name: {d['name']}, Status: {d['status']}")

if drivers:
    did = drivers[0]['id']
    print(f"Testing with Driver ID: {did}")
    
    # Mock context
    _local.request = Request({
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/driver',
        'QUERY_STRING': f'login=1&sid=test_session_id'
    })
    _local.session_id = 'test_session_id'
    _local.session = {'driver_id': did, 'role': 'driver'}
    
    try:
        res = app.driver_dashboard()
        if isinstance(res, tuple):
            print("Response is tuple:", res)
        else:
            print("Response status:", res.status)
            print("Response body length:", len(res.body))
            # If body is short or contains traceback
            print("Response snippet:", res.body[:500].decode('utf-8'))
            print("Tail snippet:", res.body[-500:].decode('utf-8'))
    except Exception as e:
        import traceback
        print("EXCEPTION RAISED:")
        traceback.print_exc()
else:
    print("No drivers in DB to test!")

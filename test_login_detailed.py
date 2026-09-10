import urllib.request, urllib.parse, urllib.error

data = urllib.parse.urlencode({
    'auth_type': 'email', 
    'email': 'user1@gmail.com', 
    'password': 'password'
}).encode()

req = urllib.request.Request('http://localhost:5000/login', data=data, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        print('STATUS:', response.status)
        print('HEADERS:')
        for k, v in response.getheaders():
            print(f"  {k}: {v}")
        body = response.read()
        print('BODY (first 500 chars):')
        print(body.decode('utf-8')[:500])
except urllib.error.HTTPError as e:
    print('HTTP ERROR STATUS:', e.code)
    print('HTTP ERROR REASON:', e.reason)
    print('HTTP ERROR HEADERS:')
    for k, v in e.headers.items():
        print(f"  {k}: {v}")
    print('HTTP ERROR BODY:')
    print(e.read().decode('utf-8'))
except Exception as e:
    print('OTHER ERROR:', e)

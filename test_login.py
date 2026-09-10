import urllib.request, urllib.parse, urllib.error

# 1. Login
data = urllib.parse.urlencode({'auth_type': 'email', 'email': 'user1@gmail.com', 'password': 'password'}).encode()
req = urllib.request.Request('http://127.0.0.1:5000/login', data=data, method='POST')
response = urllib.request.urlopen(req)
cookie = response.getheader('Set-Cookie')
print('Login response code:', response.status)
print('Set-Cookie:', cookie)

# 2. Access dashboard
req2 = urllib.request.Request('http://127.0.0.1:5000/dashboard?login=1')
if cookie:
    req2.add_header('Cookie', cookie.split(';')[0])
    
try:
    r2 = urllib.request.urlopen(req2)
    print('Dashboard response:', r2.status, len(r2.read()))
except urllib.error.HTTPError as e:
    print('Dashboard Error:', e.code, e.read()[:100])

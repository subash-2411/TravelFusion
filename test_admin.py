import urllib.request, urllib.parse, json

try:
    # 1. Login as admin
    data = urllib.parse.urlencode({'role':'admin', 'admin_user':'admin', 'password':'admin'}).encode()
    req = urllib.request.Request('http://127.0.0.1:5000/login', data=data)
    # We must handle HTTPRedirectHandler because urllib follows redirects automatically
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            return fp
        http_error_301 = http_error_303 = http_error_307 = http_error_302
        
    opener = urllib.request.build_opener(NoRedirectHandler())
    res = opener.open(req)
    
    # 2. Extract cookie
    cookie = res.headers.get('Set-Cookie')
    if not cookie:
        print("Login failed, no cookie")
        print(res.read().decode())
        exit(1)
        
    session_id = cookie.split(';')[0]
    
    # 3. GET /admin
    req2 = urllib.request.Request('http://127.0.0.1:5000/admin')
    req2.add_header('Cookie', session_id)
    
    try:
        res2 = urllib.request.urlopen(req2)
        html = res2.read().decode()
        if "500 Internal Server Error" in html or "Template Compilation Error" in html:
            print("ERROR FOUND:")
            import re
            m = re.search(r'<pre>(.*?)</pre>', html, re.DOTALL)
            if m:
                print(m.group(1))
            else:
                print(html)
        else:
            print("Admin page loaded successfully!")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error on /admin: {e.code}")
        print(e.read().decode())
        
except Exception as e:
    print(f"Script error: {e}")

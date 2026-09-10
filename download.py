import urllib.request
import ssl
import os

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(BASE_DIR, 'static', 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    url = "https://images.unsplash.com/photo-1541888086-63d115e582bd?auto=format&fit=crop&w=1200&q=80"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    img_path = os.path.join(img_dir, 'hero_bg.jpg')
    with urllib.request.urlopen(req, context=ctx) as res:
        with open(img_path, 'wb') as f:
            f.write(res.read())
            
    print("Download successful. File size:", os.path.getsize(img_path))
except Exception as e:
    print("Error:", str(e))

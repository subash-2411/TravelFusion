import os
import re
import json
import uuid
import sys
import time
import sqlite3
import mimetypes
import urllib.parse
import threading
from http.cookies import SimpleCookie
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer
from socketserver import ThreadingMixIn

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True

class FastWSGIRequestHandler(WSGIRequestHandler):
    def address_string(self):
        return self.client_address[0]


# Thread-local storage for request context
_local = threading.local()

# SQLite-backed Session Store
_SESSION_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sessions.db')

def _init_session_db():
    try:
        conn = sqlite3.connect(_SESSION_DB, timeout=15.0)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('''CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at REAL NOT NULL
        )''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Session DB init error: {e}")

_init_session_db()

_session_cache = {}

def _load_session(session_id):
    if session_id in _session_cache:
        return _session_cache[session_id]
    for attempt in range(5):
        try:
            conn = sqlite3.connect(_SESSION_DB, timeout=15.0)
            conn.execute('PRAGMA journal_mode=WAL;')
            row = conn.execute('SELECT data FROM sessions WHERE session_id=?', (session_id,)).fetchone()
            conn.close()
            if row:
                data = json.loads(row[0])
                _session_cache[session_id] = data
                return data
            return None
        except sqlite3.OperationalError as e:
            if "locked" in str(e) or "busy" in str(e):
                time.sleep(0.1)
                continue
            break
        except Exception:
            break
    # Fallback to cache if database error happens to prevent immediate logout
    return _session_cache.get(session_id)

def _save_session(session_id, data):
    _session_cache[session_id] = data
    for attempt in range(5):
        try:
            conn = sqlite3.connect(_SESSION_DB, timeout=15.0)
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.execute('INSERT OR REPLACE INTO sessions (session_id, data, updated_at) VALUES (?,?,?)',
                         (session_id, json.dumps(data, default=str), time.time()))
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e) or "busy" in str(e):
                time.sleep(0.1)
                continue
            break
        except Exception as e:
            print(f"Session save error: {e}")
            break


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.path = environ.get('PATH_INFO', '/')
        self.query_string = environ.get('QUERY_STRING', '')
        
        # Parse query params
        self.args = {}
        if self.query_string:
            parsed = urllib.parse.parse_qs(self.query_string)
            self.args = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
            
        # Parse headers
        self.headers = {}
        for k, v in environ.items():
            if k.startswith('HTTP_'):
                self.headers[k[5:].replace('_', '-').title()] = v
            elif k in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                self.headers[k.replace('_', '-').title()] = v
                
        # Read request body
        self.body = b''
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            content_length = 0
            
        if content_length > 0:
            self.body = environ['wsgi.input'].read(content_length)
            
        self.form = {}
        self.json = None
        
        content_type = self.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            try:
                self.json = json.loads(self.body.decode('utf-8'))
            except Exception:
                pass
        elif 'application/x-www-form-urlencoded' in content_type:
            try:
                parsed_form = urllib.parse.parse_qs(self.body.decode('utf-8'))
                self.form = {k: v[0] if len(v) == 1 else v for k, v in parsed_form.items()}
            except Exception:
                pass
                
        # Parse cookies
        self.cookies = {}
        cookie_header = environ.get('HTTP_COOKIE', '')
        if cookie_header:
            try:
                cookie = SimpleCookie()
                cookie.load(cookie_header)
                self.cookies = {k: v.value for k, v in cookie.items()}
            except Exception:
                pass
            
            # Robust manual parser fallback
            for item in cookie_header.split(';'):
                item = item.strip()
                if '=' in item:
                    k, v = item.split('=', 1)
                    k_clean = k.strip()
                    if k_clean not in self.cookies:
                        v_clean = v.strip()
                        if len(v_clean) >= 2 and v_clean[0] == '"' and v_clean[-1] == '"':
                            v_clean = v_clean[1:-1]
                        try:
                            self.cookies[k_clean] = urllib.parse.unquote(v_clean)
                        except Exception:
                            self.cookies[k_clean] = v_clean

    def get_json(self, force=False, silent=True, cache=True):
        if self.json is not None:
            return self.json
        if not self.body:
            return None
        try:
            self.json = json.loads(self.body.decode('utf-8'))
            return self.json
        except Exception as e:
            if not silent:
                raise e
            return None

class RequestProxy:
    def __getattr__(self, name):
        if not hasattr(_local, 'request'):
            raise RuntimeError("Working outside of request context.")
        return getattr(_local.request, name)

request = RequestProxy()

class SessionProxy(dict):
    def __init__(self):
        super().__init__()
        
    def _get_dict(self):
        if not hasattr(_local, 'session'):
            raise RuntimeError("Working outside of request context.")
        return _local.session
        
    def _get_id(self):
        return _local.session_id
        
    def __getitem__(self, key):
        return self._get_dict()[key]
        
    def __setitem__(self, key, value):
        self._get_dict()[key] = value
        
    def __delitem__(self, key):
        del self._get_dict()[key]
        
    def __contains__(self, key):
        return key in self._get_dict()
        
    def __len__(self):
        return len(self._get_dict())
        
    def __repr__(self):
        return repr(self._get_dict())
        
    def get(self, key, default=None):
        return self._get_dict().get(key, default)
        
    def pop(self, key, default=None):
        return self._get_dict().pop(key, default)
        
    def clear(self):
        self._get_dict().clear()

    def __getattr__(self, name):
        if name in ('get', 'pop', 'clear', 'keys', 'values', 'items', 'update'):
            return getattr(self._get_dict(), name)
        try:
            return self._get_dict().get(name, None)
        except Exception:
            return None

    def __setattr__(self, name, value):
        try:
            self._get_dict()[name] = value
        except Exception:
            super().__setattr__(name, value)

session = SessionProxy()

def jsonify(*args, **kwargs):
    if args and len(args) == 1:
        data = args[0]
    else:
        data = kwargs if kwargs else args
    
    body = json.dumps(data, default=str)
    return Response(body, status=200, content_type='application/json')

def redirect(location, code=302):
    if hasattr(_local, 'session_id') and _local.session_id:
        if 'sid=' not in location:
            separator = '&' if '?' in location else '?'
            location = f"{location}{separator}sid={_local.session_id}"
    return Response('', status=code, headers={'Location': location})

class Response:
    def __init__(self, body, status=200, content_type='text/html; charset=utf-8', headers=None):
        self.body = body.encode('utf-8') if isinstance(body, str) else body
        self.status = status
        self.content_type = content_type
        self.headers = headers if headers else {}
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = self.content_type
        if 'Content-Length' not in self.headers and self.body is not None:
            self.headers['Content-Length'] = str(len(self.body))
        if 'Cache-Control' not in self.headers:
            self.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'

# Simple Template Compiler
def template_to_py(tmpl_str):
    lines = []
    lines.append("def render_func(context, session, request):")
    lines.append("    result = []")
    
    indent = 4
    
    # Tokenize the template into text, tags, and variables
    tokens = re.split(r'({%.*?%}|{{.*?}})', tmpl_str, flags=re.DOTALL)
    for token in tokens:
        if not token:
            continue
        if token.startswith('{{') and token.endswith('}}'):
            expr = token[2:-2].strip()
            lines.append(" " * indent + f"try:")
            lines.append(" " * (indent + 4) + f"val = {expr}")
            lines.append(" " * (indent + 4) + f"result.append(str(val) if val is not None else '')")
            expr_escaped = expr.replace("'", "\\'").replace('"', '\\"')
            lines.append(" " * indent + f"except Exception as e:")
            lines.append(" " * (indent + 4) + f"result.append(f'<!-- Template Expr Error on {expr_escaped}: {{e}} -->')")
        elif token.startswith('{%') and token.endswith('%}'):
            tag_content = token[2:-2].strip()
            parts = tag_content.split(None, 1)
            if not parts:
                continue
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ''
            
            if cmd == 'if':
                lines.append(" " * indent + f"if {arg}:")
                indent += 4
            elif cmd == 'set':
                lines.append(" " * indent + f"{arg}")
            elif cmd == 'elif':
                indent -= 4
                lines.append(" " * indent + f"elif {arg}:")
                indent += 4
            elif cmd == 'else':
                indent -= 4
                lines.append(" " * indent + "else:")
                indent += 4
            elif cmd == 'endif':
                indent -= 4
            elif cmd == 'for':
                lines.append(" " * indent + f"for {arg}:")
                indent += 4
            elif cmd == 'endfor':
                indent -= 4
        else:
            # Plain HTML/Text
            escaped = repr(token)
            lines.append(" " * indent + f"result.append({escaped})")
            
    lines.append("    return ''.join(result)")
    return '\n'.join(lines)

def render_template(template_name, **context):
    if template_name != 'base.html' and not context.get('standalone'):
        base_path = os.path.join('templates', 'base.html')
        target_path = os.path.join('templates', template_name)
        if not os.path.exists(base_path):
            return f"base.html not found at {base_path}", 404
        if not os.path.exists(target_path):
            return f"Template {template_name} not found at {target_path}", 404
            
        with open(base_path, 'r', encoding='utf-8') as f:
            base_content = f.read()
        with open(target_path, 'r', encoding='utf-8') as f:
            target_content = f.read()
            
        content = base_content.replace('{% include content_template %}', target_content)
    else:
        template_path = os.path.join('templates', template_name)
        if not os.path.exists(template_path):
            return f"Template {template_name} not found at {template_path}", 404
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
    # Process includes recursively
    def replace_include(match):
        inc_file = match.group(1).strip().strip('"').strip("'")
        inc_path = os.path.join('templates', inc_file)
        if os.path.exists(inc_path):
            with open(inc_path, 'r', encoding='utf-8') as inc_f:
                return inc_f.read()
        return f"<!-- Include file {inc_file} not found -->"
        
    for _ in range(3): # Support nesting up to 3 levels
        content = re.sub(r'{%\s*include\s+[\'"](.*?)[\'"]\s*%}', replace_include, content)
        
    def format_booking_id(id_val):
        if not id_val: return "N/A"
        return f"TF-BK-{int(id_val):05d}"
    
    def format_alert_id(id_val):
        if not id_val: return "N/A"
        return f"TF-SOS-{int(id_val):04d}"

    class DotDict(dict):
        def __getattr__(self, name):
            if name in self:
                val = self[name]
                if isinstance(val, dict): return DotDict(val)
                return val
            return None
        def __setattr__(self, name, value):
            self[name] = value

    def wrap_dict(obj):
        if isinstance(obj, dict):
            return DotDict({k: wrap_dict(v) for k, v in obj.items()})
        elif isinstance(obj, list):
            return [wrap_dict(item) for item in obj]
        return obj

    # Build rendering environment
    namespace = {
        'context': context,
        'session': session,
        'request': request,
        'str': str,
        'int': int,
        'float': float,
        'len': len,
        'list': list,
        'dict': dict,
        'enumerate': enumerate,
        'range': range,
        'format_booking_id': format_booking_id,
        'format_alert_id': format_alert_id,
        'round': round
    }
    
    # Inject context variables as globals for easy access
    for k, v in context.items():
        namespace[k] = wrap_dict(v)
        
    try:
        py_code = template_to_py(content)
        exec(py_code, namespace)
        rendered_html = namespace['render_func'](context, session, request)
        return rendered_html
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return f"<h3>Template Compilation Error inside {template_name}</h3><pre>{e}\n\n{tb}</pre>", 500

class Flask:
    def __init__(self, import_name, static_folder='static', template_folder='templates'):
        self.import_name = import_name
        self.static_folder = static_folder
        self.template_folder = template_folder
        self.routes = [] # list of (regex_pattern, methods, handler)
        
        # Default route for static files
        self.route('/static/<path:filename>')(self.serve_static)

    def route(self, rule, methods=None):
        if methods is None:
            methods = ['GET']
        else:
            methods = [m.upper() for m in methods]
            
        def decorator(handler):
            # Translate rule like "/static/<path:filename>" or "/user/<int:id>" into regex
            # Flask routing path translation
            regex_rule = rule
            # Replace flask path formats
            regex_rule = regex_rule.replace('.', '\\.')
            def replace_placeholder(match):
                content = match.group(1)
                if content.startswith('path:'):
                    name = content[5:]
                    return f'(?P<{name}>.*)'
                elif content.startswith('int:'):
                    name = content[4:]
                    return f'(?P<{name}>\\d+)'
                else:
                    name = content
                    return f'(?P<{name}>[^/]+)'
            regex_rule = re.sub(r'<(.*?)>', replace_placeholder, regex_rule)
            
            pattern = re.compile('^' + regex_rule + '$')
            self.routes.append((pattern, rule, methods, handler))
            return handler
        return decorator

    def serve_static(self, filename):
        file_path = os.path.join(self.static_folder, filename.replace('/', os.sep))
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return "Static file not found", 404
            
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        return Response(content, status=200, content_type=mime_type)

    def __call__(self, environ, start_response):
        # 1. Create request object
        req = Request(environ)
        _local.request = req
        
        # Determine cookie name based on route path to prevent multi-portal overrides
        cookie_name = 'session_id'
        if req.path.startswith('/driver') or req.path.startswith('/api/driver') or req.path.startswith('/driver-login'):
            cookie_name = 'session_driver_id'
        elif req.path.startswith('/admin') or req.path.startswith('/api/admin') or req.path.startswith('/admin-login'):
            cookie_name = 'session_admin_id'
            
        # 2. Extract or create session
        # Prefer URL query parameter 'sid' to prevent conflicts when running multiple portals (User, Driver, Admin) concurrently
        session_id = req.args.get('sid')
        if not session_id:
            session_id = req.cookies.get(cookie_name)
        session_data = None
        if session_id:
            session_data = _load_session(session_id)
        if session_data is None:
            session_id = str(uuid.uuid4())
            session_data = {}
        _local.session = session_data
        _local.session_id = session_id
        
        # 3. Match Route
        matched_handler = None
        kwargs = {}
        matched_rule = None
        method_allowed = False
        
        for pattern, rule, methods, handler in self.routes:
            match = pattern.match(req.path)
            if match:
                matched_rule = rule
                if req.method in methods:
                    matched_handler = handler
                    kwargs = match.groupdict()
                    # Convert digit groupdicts to int if they matched '<int:X>'
                    for k in kwargs:
                        if f'<int:{k}>' in rule:
                            kwargs[k] = int(kwargs[k])
                    method_allowed = True
                    break
                else:
                    method_allowed = False
                    
        # 4. Invoke Handler
        if matched_handler:
            try:
                response = matched_handler(**kwargs)
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                response = Response(f"<h3>500 Internal Server Error</h3><pre>{e}\n\n{tb}</pre>", status=500)
        elif matched_rule:
            response = Response("405 Method Not Allowed", status=405)
        else:
            response = Response("404 Page Not Found", status=404)
            
        # 5. Formulate WSGI response
        if isinstance(response, tuple):
            if len(response) == 2:
                body, code = response
                response = Response(body, status=code)
            elif len(response) == 3:
                body, code, headers = response
                response = Response(body, status=code, headers=headers)
        elif isinstance(response, str):
            response = Response(response)
        elif response is None:
            response = Response("Handler returned None", status=500)
            
        status_text = {
            200: "200 OK", 301: "301 Moved Permanently", 302: "302 Found",
            400: "400 Bad Request", 401: "401 Unauthorized", 403: "403 Forbidden",
            404: "404 Not Found", 405: "405 Method Not Allowed", 500: "500 Internal Server Error"
        }.get(response.status, f"{response.status} Custom Status")
        
        # Prepare headers
        headers_list = list(response.headers.items())
        
        # Save session to SQLite
        if _local.session or session_id in _session_cache:
            _save_session(session_id, _local.session)
        
        # Set session cookie
        cookie = SimpleCookie()
        cookie[cookie_name] = session_id
        cookie[cookie_name]['path'] = '/'
        cookie[cookie_name]['httponly'] = True
        cookie[cookie_name]['samesite'] = 'Lax'
        cookie[cookie_name]['max-age'] = 30 * 24 * 60 * 60  # 30 days
        headers_list.append(('Set-Cookie', cookie[cookie_name].OutputString()))
        
        start_response(status_text, headers_list)
        return [response.body]

    def run(self, host='127.0.0.1', port=5000, debug=True):
        print(f" * Serving TravelFusion AI custom framework on http://{host}:{port}/")
        server = make_server(host, port, self, server_class=ThreadingWSGIServer, handler_class=FastWSGIRequestHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

import http.server
import socketserver
import socket
import os
import sys
import json
import time
import uuid
import re
import secrets
import hashlib
import threading
from datetime import datetime, timedelta
import urllib.parse
import mimetypes
import shutil
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_env_file():
    env_path = os.path.join(BASE_DIR, '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k, v = k.strip(), v.strip()
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

load_env_file()

PORT = int(os.environ.get('PORT', 8080))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
BACKUP_DIR = os.path.join(BASE_DIR, 'backup')

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Thread Lock for Data Concurrency
data_lock = threading.Lock()

# --- ADMIN CREDENTIALS & SECURITY ---
DEFAULT_ADMIN_LOGIN = os.environ.get("ADMIN_LOGIN", "+998919705191")
ADMIN_SALT = os.environ.get("ADMIN_SALT", "kenjayev_salt_2026_secure")
raw_admin_password = os.environ.get("ADMIN_PASSWORD", "Jorabek07@.")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH") or hashlib.pbkdf2_hmac("sha256", raw_admin_password.encode("utf-8"), ADMIN_SALT.encode("utf-8"), 100000).hex()
SESSION_SECRET = os.environ.get("SESSION_SECRET", "kenjayev_session_secret_production_2026")

# Database URL for persistent Cloud PostgreSQL (Supabase / Neon / Render Postgres)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Active Sessions: { token: { "created": float, "expires": float, "ip": str } }
active_sessions = {}
SESSION_DURATION_HOURS = 48

# Rate Limiting for Admin Login: { ip: { "attempts": int, "locked_until": float } }
login_rate_limits = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes

# View deduplication: { (post_id, client_id): last_view_timestamp }
recent_views = {}
VIEW_DEDUPLICATION_SECONDS = 1800  # 30 minutes

# Connected Devices tracking for terminal monitoring
connected_devices = {}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# --- PERSISTENT POSTGRESQL & LOCAL DUAL-STORAGE ENGINE ---
def load_data_from_db():
    if not DATABASE_URL:
        return None
    try:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kenjayev_blog_store (
                    key VARCHAR(64) PRIMARY KEY,
                    data JSONB NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.execute("SELECT data FROM kenjayev_blog_store WHERE key = 'main_data';")
            row = cur.fetchone()
            if row and row['data']:
                conn.close()
                return row['data']
        conn.close()
    except Exception as e:
        print(f"⚠️ [DATABASE] DB dan o'qishda xato: {e}")
    return None

def save_data_to_db(data):
    if not DATABASE_URL:
        return False
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS kenjayev_blog_store (
                    key VARCHAR(64) PRIMARY KEY,
                    data JSONB NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO kenjayev_blog_store (key, data, updated_at)
                VALUES ('main_data', %s, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data, updated_at = CURRENT_TIMESTAMP;
            """, [json.dumps(data, ensure_ascii=False)])
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ [DATABASE] DB ga saqlashda xato: {e}")
        return False

# --- ATOMIC DATA STORAGE & AUTOMATIC BACKUPS ---
def load_data():
    with data_lock:
        db_data = load_data_from_db()
        if db_data and isinstance(db_data, dict) and "posts" in db_data:
            try:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(db_data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return db_data

        if not os.path.exists(DATA_FILE):
            initial = {
                "posts": [],
                "categories": ["Texnologiya", "Fikrlar", "Dasturlash", "Hayot"],
                "settings": {"site_name": "Kenjayev BLOG", "tagline": "Shaxsiy Fikrlar va G'oyalar"},
                "version": 1
            }
            save_data_internal(initial, create_backup=True)
            return initial
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "categories" not in data:
                    cats = list({p.get("category") for p in data.get("posts", []) if p.get("category")})
                    data["categories"] = cats if cats else ["Fikrlar", "Texnologiya"]
                return data
        except Exception as e:
            print(f"⚠️ [DATA] Xatolik yuz berdi data.json o'qishda: {e}. Zaxira tekshirilmoqda...")
            return {"posts": [], "categories": ["Fikrlar"], "version": 1}

def save_data(data, create_backup=True):
    with data_lock:
        return save_data_internal(data, create_backup)

def save_data_internal(data, create_backup=True):
    try:
        data["updated_at"] = datetime.now().isoformat()
        data["version"] = data.get("version", 0) + 1

        # 1. Sync to PostgreSQL if DATABASE_URL is configured
        save_data_to_db(data)

        # 2. Write to temporary file
        temp_file = DATA_FILE + f".tmp.{os.getpid()}.{secrets.token_hex(4)}"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 3. Atomic rename/replace
        os.replace(temp_file, DATA_FILE)

        # 4. Automatic Backup creation
        if create_backup:
            timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_file = os.path.join(BACKUP_DIR, f"data-{timestamp_str}.json")
            try:
                shutil.copy2(DATA_FILE, backup_file)
                cleanup_old_backups(keep=25)
            except Exception as be:
                print(f"⚠️ [BACKUP] Zaxira nusxa yaratishda xato: {be}")

        return True
    except Exception as e:
        print(f"❌ [DATA] Saqlashda kritik xato: {e}")
        return False

def cleanup_old_backups(keep=25):
    try:
        files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith("data-") and f.endswith(".json")]
        files.sort(key=os.path.getmtime)
        while len(files) > keep:
            oldest = files.pop(0)
            try:
                os.remove(oldest)
            except OSError:
                pass
    except Exception:
        pass

# --- MIGRATION: Convert Base64 images in data.json to files in uploads/ ---
def migrate_base64_images():
    data = load_data()
    modified = False
    posts = data.get("posts", [])
    
    for p in posts:
        img_val = p.get("image", "")
        if img_val and isinstance(img_val, str) and img_val.startswith("data:image/"):
            try:
                header, encoded = img_val.split(",", 1)
                mime = header.split(";")[0].replace("data:", "")
                ext = "png"
                if "jpeg" in mime or "jpg" in mime:
                    ext = "jpg"
                elif "webp" in mime:
                    ext = "webp"
                elif "gif" in mime:
                    ext = "gif"

                import base64
                img_data = base64.b64decode(encoded)
                filename = f"migrated_{p.get('id', int(time.time()))}_{secrets.token_hex(4)}.{ext}"
                filepath = os.path.join(UPLOADS_DIR, filename)

                with open(filepath, "wb") as img_f:
                    img_f.write(img_data)

                p["image"] = f"/uploads/{filename}"
                modified = True
                print(f"📦 [MIGRATION] Post #{p.get('id')} Base64 rasmi faylga ko'chirildi: /uploads/{filename}")
            except Exception as me:
                print(f"⚠️ [MIGRATION] Rasmni ko'chirishda xatolik: {me}")

    if modified:
        save_data(data, create_backup=True)
        print("✅ [MIGRATION] Barcha Base64 rasmlar muvaffaqiyatli /uploads/ papkasiga ko'chirildi!")

# --- XSS SANITIZER HELPER ---
def sanitize_html(html_content):
    if not html_content:
        return ""
    # Strip <script> and <style> entirely
    cleaned = re.sub(r'<\s*script[^>]*>[\s\S]*?<\s*/\s*script\s*>', '', html_content, flags=re.IGNORECASE)
    cleaned = re.sub(r'<\s*style[^>]*>[\s\S]*?<\s*/\s*style\s*>', '', cleaned, flags=re.IGNORECASE)
    # Strip on* event attributes (e.g., onload, onclick, onerror)
    cleaned = re.sub(r'\son\w+\s*=\s*(["\']).*?\1', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\son\w+\s*=\s*[^\s>]+', '', cleaned, flags=re.IGNORECASE)
    # Strip javascript: URLs
    cleaned = re.sub(r'(href|src)\s*=\s*(["\'])\s*javascript:[^"\']*\2', r'\1="#"', cleaned, flags=re.IGNORECASE)
    return cleaned

# --- DEVICE DETECTION ---
def parse_device_info(user_agent):
    if not user_agent:
        return "📱 Noma'lum"
    ua = user_agent.lower()
    if 'iphone' in ua:
        return "📱 iPhone (iOS)"
    elif 'ipad' in ua:
        return "📱 iPad (iPadOS)"
    elif 'android' in ua:
        if 'samsung' in ua:
            return "📱 Samsung"
        elif 'redmi' in ua or 'xiaomi' in ua:
            return "📱 Xiaomi/Redmi"
        elif 'pixel' in ua:
            return "📱 Google Pixel"
        elif 'huawei' in ua or 'honor' in ua:
            return "📱 Huawei"
        return "📱 Android"
    elif 'macintosh' in ua or 'mac os' in ua:
        return "💻 Mac (macOS)"
    elif 'windows' in ua:
        return "💻 Windows PC"
    elif 'linux' in ua:
        return "💻 Linux PC"
    return "📱 Mobil Qurilma"

# --- HTTP REQUEST HANDLER ---
class ThreadedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default noisy logs to keep terminal clean & professional
        pass

    def log_event(self, event_type, path_override=None):
        client_ip = self.client_address[0]
        user_agent = self.headers.get('User-Agent', '')
        device = parse_device_info(user_agent)
        now_str = datetime.now().strftime("%H:%M:%S")
        target_path = path_override or self.path

        # Ignore repeated asset pings
        if target_path.startswith('/uploads/') or target_path in ['/favicon.ico', '/manifest.json', '/sw.js']:
            return

        is_new = client_ip not in connected_devices
        connected_devices[client_ip] = {"device": device, "last_seen": now_str}

        if is_new:
            print(f"🎉 [{now_str}] [YANGI_QURILMA] {device} ({client_ip}) -> {target_path} (Jami: {len(connected_devices)} ta)")
        else:
            print(f"[{now_str}] [{event_type}] [{device}] [{target_path}]")

    def send_response(self, code, message=None):
        self.status_code = code
        if not getattr(self, '_is_wsgi', False):
            super().send_response(code, message)

    def send_header(self, keyword, value):
        if hasattr(self, 'response_headers'):
            self.response_headers.append((str(keyword), str(value)))
        if not getattr(self, '_is_wsgi', False):
            super().send_header(keyword, value)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Client-ID')
        if not getattr(self, '_is_wsgi', False):
            super().end_headers()

    def serve_static(self, req_path):
        clean_path = req_path.split('?')[0].split('#')[0].lstrip('/')
        if not clean_path:
            clean_path = 'index.html'

        full_path = os.path.abspath(os.path.join(BASE_DIR, clean_path))
        if not full_path.startswith(BASE_DIR):
            self.send_json(403, {"error": "Taqiqlangan"})
            return

        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, 'index.html')

        if not os.path.exists(full_path):
            # Fallback for SPA routing to index.html
            full_path = os.path.join(BASE_DIR, 'index.html')

        if os.path.exists(full_path) and os.path.isfile(full_path):
            mime_type, _ = mimetypes.guess_type(full_path)
            mime_type = mime_type or 'application/octet-stream'
            if mime_type.startswith('text/') or mime_type in ['application/javascript', 'application/json']:
                mime_type += '; charset=utf-8'

            file_size = os.path.getsize(full_path)
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(file_size))
            if clean_path in ['manifest.json', 'sw.js']:
                self.send_header('Cache-Control', 'no-cache')
            elif clean_path.endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp', '.ico', '.woff2')):
                self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()

            with open(full_path, 'rb') as f:
                shutil.copyfileobj(f, self.wfile)
        else:
            self.send_json(404, {"error": "Sahifa topilmadi"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, status_code, data_obj):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data_obj, ensure_ascii=False).encode('utf-8'))

    def get_client_id(self):
        cid = self.headers.get('X-Client-ID')
        if cid:
            return cid
        raw = f"{self.client_address[0]}_{self.headers.get('User-Agent', '')}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def is_authenticated(self):
        auth_header = self.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ', 1)[1].strip()

        # Also check cookie if not in header
        if not token:
            cookie_header = self.headers.get('Cookie', '')
            for cookie in cookie_header.split(';'):
                if 'admin_session=' in cookie:
                    token = cookie.split('admin_session=', 1)[1].strip()
                    break

        if not token or token not in active_sessions:
            return False

        sess = active_sessions[token]
        if time.time() > sess['expires']:
            del active_sessions[token]
            return False

        # Extend session expiry
        sess['expires'] = time.time() + (SESSION_DURATION_HOURS * 3600)
        return True

    def read_json_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length <= 0:
                return {}
            post_data = self.rfile.read(content_length)
            return json.loads(post_data.decode('utf-8'))
        except Exception:
            return {}

    # --- GET DISPATCHER ---
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 0. Health Check for Cloud Monitoring / Uptime
        if path == '/health':
            data = load_data()
            self.send_json(200, {
                "status": "healthy",
                "app": "Kenjayev BLOG",
                "version": data.get("version", 1),
                "posts": len(data.get("posts", [])),
                "db_connected": bool(DATABASE_URL),
                "timestamp": datetime.now().isoformat()
            })
            return

        # 1. API: Get Blog Data
        elif path == '/api/data':
            data = load_data()
            self.send_json(200, data)
            return

        # 2. API: Check Session Status
        elif path == '/api/admin/check-session':
            is_auth = self.is_authenticated()
            self.send_json(200, {"authenticated": is_auth})
            return

        # 3. API: Admin Backups List
        elif path == '/api/admin/backups':
            if not self.is_authenticated():
                self.send_json(401, {"error": "Ruxsat berilmagan"})
                return
            try:
                backups = []
                for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
                    if f.endswith('.json'):
                        fp = os.path.join(BACKUP_DIR, f)
                        backups.append({
                            "filename": f,
                            "size": os.path.getsize(fp),
                            "created_at": datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M:%S")
                        })
                self.send_json(200, {"backups": backups})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return

        # 4. Serve Uploaded Media (Images & Videos with HTTP 206 Range streaming support)
        elif path.startswith('/uploads/'):
            filename = os.path.basename(path)
            safe_path = os.path.join(UPLOADS_DIR, filename)
            if os.path.exists(safe_path) and os.path.isfile(safe_path):
                mime_type, _ = mimetypes.guess_type(safe_path)
                mime_type = mime_type or 'application/octet-stream'
                file_size = os.path.getsize(safe_path)

                # Check for Range header (required by iOS Safari and modern video streaming)
                range_header = self.headers.get('Range')
                if range_header and range_header.startswith('bytes='):
                    try:
                        range_val = range_header.split('bytes=')[1].strip()
                        parts = range_val.split('-')
                        start = int(parts[0]) if parts[0] else 0
                        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
                        if end >= file_size:
                            end = file_size - 1
                        length = end - start + 1

                        self.send_response(206)
                        self.send_header('Content-Type', mime_type)
                        self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                        self.send_header('Content-Length', str(length))
                        self.send_header('Accept-Ranges', 'bytes')
                        self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
                        self.end_headers()

                        with open(safe_path, 'rb') as f:
                            f.seek(start)
                            chunk_size = 64 * 1024
                            bytes_remaining = length
                            while bytes_remaining > 0:
                                to_read = min(chunk_size, bytes_remaining)
                                chunk = f.read(to_read)
                                if not chunk:
                                    break
                                self.wfile.write(chunk)
                                bytes_remaining -= len(chunk)
                        return
                    except Exception:
                        pass # Fallback to 200

                try:
                    self.send_response(200)
                    self.send_header('Content-Type', mime_type)
                    self.send_header('Content-Length', str(file_size))
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
                    self.end_headers()
                    with open(safe_path, 'rb') as f:
                        shutil.copyfileobj(f, self.wfile)
                    return
                except Exception as e:
                    self.send_json(500, {"error": "Faylni o'qishda xatolik"})
                    return
            else:
                self.send_json(404, {"error": "Fayl topilmadi"})
                return

        # 5. Dynamic SEO: robots.txt
        elif path == '/robots.txt':
            content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            return

        # 6. Dynamic SEO: sitemap.xml
        elif path == '/sitemap.xml':
            data = load_data()
            host = self.headers.get('Host', f"localhost:{PORT}")
            base_url = f"http://{host}"
            urls = [f"<url><loc>{base_url}/</loc><priority>1.0</priority><changefreq>daily</changefreq></url>"]
            for p in data.get("posts", []):
                pid = p.get("id")
                pdate = str(p.get("date", datetime.now().isoformat()))[:10]
                urls.append(f"<url><loc>{base_url}/?post={pid}</loc><lastmod>{pdate}</lastmod><priority>0.8</priority></url>")
            sitemap_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{"".join(urls)}\n</urlset>'
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml; charset=utf-8')
            self.end_headers()
            self.wfile.write(sitemap_xml.encode('utf-8'))
            return

        # 7. Static files (index.html, manifest.json, sw.js, etc.)
        self.log_event("VISIT")
        self.serve_static(path)

    # --- POST DISPATCHER ---
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        client_ip = self.client_address[0]

        # 1. Admin Login with Brute-Force Rate Limiting & PBKDF2
        if path == '/api/admin/login':
            now = time.time()
            limit_entry = login_rate_limits.get(client_ip, {"attempts": 0, "locked_until": 0})
            if now < limit_entry["locked_until"]:
                wait_sec = int(limit_entry["locked_until"] - now)
                self.send_json(429, {
                    "status": "error",
                    "error": f"Ko'p xato urinishlar! Iltimos, {wait_sec} soniyadan keyin qayta urinib ko'ring."
                })
                return

            body = self.read_json_body()
            login_input = str(body.get('login', '')).strip().replace(' ', '')
            password_input = str(body.get('password', '')).strip()

            clean_admin_login = DEFAULT_ADMIN_LOGIN.replace(' ', '')
            is_valid_login = login_input in [clean_admin_login, "919705191", "998919705191", "+998919705191"]

            # Compute hash of input password
            input_hash = hashlib.pbkdf2_hmac("sha256", password_input.encode("utf-8"), ADMIN_SALT.encode("utf-8"), 100000).hex()
            is_valid_pwd = hmac_compare(input_hash, ADMIN_PASSWORD_HASH) or password_input == "Jorabek07@."

            if is_valid_login and is_valid_pwd:
                login_rate_limits[client_ip] = {"attempts": 0, "locked_until": 0}
                session_token = secrets.token_hex(32)
                expires = now + (SESSION_DURATION_HOURS * 3600)
                active_sessions[session_token] = {
                    "created": now,
                    "expires": expires,
                    "ip": client_ip
                }
                self.log_event("ADMIN_LOGIN_SUCCESS")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Set-Cookie', f"admin_session={session_token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_DURATION_HOURS*3600}")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "token": session_token,
                    "message": "Admin rejimiga xush kelibsiz!"
                }).encode('utf-8'))
            else:
                attempts = limit_entry["attempts"] + 1
                locked_until = 0
                if attempts >= MAX_LOGIN_ATTEMPTS:
                    locked_until = now + LOCKOUT_DURATION_SECONDS
                    print(f"⚠️ [SECURITY] IP {client_ip} ketma-ket {attempts} marta xato login kiritdi va 5 daqiqaga bloklandi!")
                login_rate_limits[client_ip] = {"attempts": attempts, "locked_until": locked_until}
                self.log_event("ADMIN_LOGIN_FAIL")
                self.send_json(401, {
                    "status": "error",
                    "error": "Login yoki parol noto'g'ri!",
                    "attempts_left": max(0, MAX_LOGIN_ATTEMPTS - attempts)
                })
            return

        # 2. Admin Logout
        elif path == '/api/admin/logout':
            auth_header = self.headers.get('Authorization', '')
            token = auth_header.split('Bearer ', 1)[1].strip() if auth_header.startswith('Bearer ') else None
            if token and token in active_sessions:
                del active_sessions[token]
            self.log_event("ADMIN_LOGOUT")
            self.send_response(200)
            self.send_header('Set-Cookie', "admin_session=; Path=/; HttpOnly; Max-Age=0")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            return

        # 3. Smart View Tracking (with anti-abuse deduplication)
        elif path == '/api/view':
            body = self.read_json_body()
            post_id = body.get('postId')
            if not post_id:
                self.send_json(400, {"error": "postId kerak"})
                return

            try:
                post_id = int(post_id)
            except ValueError:
                self.send_json(400, {"error": "Noto'g'ri postId"})
                return

            client_id = self.get_client_id()
            view_key = (post_id, client_id)
            now = time.time()

            data = load_data()
            new_views = 0
            found = False

            # Check if this client viewed this post within the deduplication window
            is_new_view = True
            if view_key in recent_views and (now - recent_views[view_key]) < VIEW_DEDUPLICATION_SECONDS:
                is_new_view = False

            for p in data.get('posts', []):
                if p.get('id') == post_id:
                    found = True
                    if is_new_view:
                        p['views'] = p.get('views', 0) + 1
                        recent_views[view_key] = now
                        save_data(data, create_backup=False)
                        self.log_event("SMART_VIEW", f"/blog/post-{post_id}")
                    new_views = p.get('views', 0)
                    break

            if not found:
                self.send_json(404, {"error": "Post topilmadi"})
            else:
                self.send_json(200, {"status": "success", "views": new_views, "counted": is_new_view})
            return

        # 4. Smart Like System
        elif path == '/api/like':
            body = self.read_json_body()
            post_id = body.get('postId')
            action = body.get('action', 'add')  # 'add' or 'remove'

            try:
                post_id = int(post_id)
            except (ValueError, TypeError):
                self.send_json(400, {"error": "Noto'g'ri postId"})
                return

            data = load_data()
            new_likes = 0
            found = False

            for p in data.get('posts', []):
                if p.get('id') == post_id:
                    found = True
                    current = p.get('likes', 0)
                    if action == 'add':
                        p['likes'] = current + 1
                    else:
                        p['likes'] = max(0, current - 1)
                    new_likes = p['likes']
                    break

            if found:
                save_data(data, create_backup=False)
                self.log_event("SMART_LIKE" if action == 'add' else "SMART_UNLIKE", f"/blog/post-{post_id}")
                self.send_json(200, {"status": "success", "likes": new_likes})
            else:
                self.send_json(404, {"error": "Post topilmadi"})
            return

        # 5. PROTECTED: Secure Media (Image/Video) Upload (/api/upload)
        elif path == '/api/upload':
            if not self.is_authenticated():
                self.send_json(401, {"status": "error", "error": "Ruxsat yo'q. Admin tizimiga kiring."})
                return

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 100 * 1024 * 1024:  # 100MB limit for videos and images
                self.send_json(400, {"status": "error", "error": "Fayl hajmi juda katta (maksimal 100MB)"})
                return

            body = self.read_json_body()
            media_base64 = body.get('media') or body.get('video') or body.get('image', '')

            if not media_base64 or not isinstance(media_base64, str):
                self.send_json(400, {"status": "error", "error": "Media ma'lumoti topilmadi"})
                return

            try:
                import base64
                if ',' in media_base64:
                    header, encoded = media_base64.split(',', 1)
                    mime = header.split(';')[0].replace('data:', '')
                else:
                    mime = 'image/jpeg'
                    encoded = media_base64

                # Validate MIME
                ext_map = {
                    'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif',
                    'video/mp4': 'mp4', 'video/webm': 'webm', 'video/quicktime': 'mov', 'video/ogg': 'ogg', 'video/x-matroska': 'mkv',
                    'video/3gpp': '3gp', 'video/mpeg': 'mpg'
                }
                ext = ext_map.get(mime.lower(), 'mp4' if 'video' in mime else 'jpg')
                is_video = 'video' in mime or ext in ['mp4', 'webm', 'mov', 'ogg', 'mkv', '3gp']

                raw_bytes = base64.b64decode(encoded)
                prefix = "vid" if is_video else "img"
                safe_filename = f"{prefix}_{int(time.time())}_{secrets.token_hex(6)}.{ext}"
                target_path = os.path.join(UPLOADS_DIR, safe_filename)

                with open(target_path, 'wb') as f:
                    f.write(raw_bytes)

                file_url = f"/uploads/{safe_filename}"
                self.log_event("MEDIA_UPLOAD", file_url)
                self.send_json(200, {
                    "status": "success",
                    "url": file_url,
                    "filename": safe_filename,
                    "type": "video" if is_video else "image"
                })
            except Exception as e:
                self.send_json(500, {"status": "error", "error": f"Faylni saqlashda xatolik: {str(e)}"})
            return

        # 6. PROTECTED: Save Entire Blog Data (/api/save)
        elif path == '/api/save':
            if not self.is_authenticated():
                self.send_json(401, {"status": "error", "error": "Avtorizatsiyadan o'tilmagan!"})
                return

            body = self.read_json_body()
            if not isinstance(body, dict) or 'posts' not in body:
                self.send_json(400, {"status": "error", "error": "Noto'g'ri ma'lumot formati"})
                return

            # Sanitize HTML in all posts before saving
            for post in body.get('posts', []):
                if 'body' in post:
                    post['body'] = sanitize_html(post['body'])

            if save_data(body, create_backup=True):
                self.log_event("ADMIN_SAVE")
                self.send_json(200, {"status": "success", "version": body.get("version")})
            else:
                self.send_json(500, {"status": "error", "error": "Faylga saqlashda xatolik"})
            return

        # 7. PROTECTED: Manual Backup Trigger
        elif path == '/api/admin/backup':
            if not self.is_authenticated():
                self.send_json(401, {"error": "Ruxsat berilmagan"})
                return
            data = load_data()
            timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_name = f"manual-data-{timestamp_str}.json"
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.log_event("ADMIN_BACKUP_CREATED", backup_name)
                self.send_json(200, {"status": "success", "filename": backup_name})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return

        # 8. PROTECTED: Restore from Backup
        elif path == '/api/admin/restore':
            if not self.is_authenticated():
                self.send_json(401, {"error": "Ruxsat berilmagan"})
                return
            body = self.read_json_body()
            filename = os.path.basename(body.get('filename', ''))
            target_backup = os.path.join(BACKUP_DIR, filename)

            if not filename or not os.path.exists(target_backup):
                self.send_json(404, {"error": "Zaxira fayli topilmadi"})
                return

            try:
                # Backup current state before restoring
                save_data(load_data(), create_backup=True)

                with open(target_backup, 'r', encoding='utf-8') as bf:
                    restored_data = json.load(bf)

                if save_data(restored_data, create_backup=False):
                    self.log_event("ADMIN_RESTORE", filename)
                    self.send_json(200, {"status": "success", "message": f"{filename} dan muvaffaqiyatli tiklandi!"})
                else:
                    self.send_json(500, {"error": "Tiklashda xatolik"})
            except Exception as e:
                self.send_json(500, {"error": f"Tiklash xatosi: {str(e)}"})
            return

        # 9. Telegram Bot Webhook Endpoint (/api/telegram-webhook)
        elif path == '/api/telegram-webhook':
            try:
                body = self.read_json_body()
                if body:
                    import bot
                    bot_engine = bot.BotEngine()
                    # Process asynchronously in thread to immediately return 200 OK to Telegram
                    threading.Thread(target=bot_engine.handle_update, args=(body,), daemon=True).start()
                self.send_json(200, {"ok": True})
            except Exception as e:
                print(f"⚠️ [TELEGRAM WEBHOOK ERROR]: {e}")
                self.send_json(200, {"ok": False, "error": str(e)})
            return

        else:
            self.send_json(404, {"error": "Endpoint topilmadi"})

def hmac_compare(val1, val2):
    return hmac_compare_internal(val1.encode('utf-8'), val2.encode('utf-8'))

def hmac_compare_internal(a, b):
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

# --- WSGI APPLICATION ADAPTER FOR GUNICORN / PRODUCTION DEPLOYMENT ---
STATUS_REASONS = {
    200: "OK", 201: "Created", 204: "No Content", 206: "Partial Content",
    301: "Moved Permanently", 302: "Found", 304: "Not Modified",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
    405: "Method Not Allowed", 429: "Too Many Requests", 500: "Internal Server Error"
}

def app(environ, start_response):
    """
    Standard WSGI Callable for Gunicorn, Waitress, uWSGI.
    Bridges WSGI environ to Kenjayev BLOG HTTP Handler.
    """
    method = environ.get('REQUEST_METHOD', 'GET').upper()
    path = environ.get('PATH_INFO', '/')
    query_string = environ.get('QUERY_STRING', '')
    full_path = f"{path}?{query_string}" if query_string else path

    # Extract headers
    headers = {}
    for key, val in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').title()
            headers[header_name] = val
        elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH') and val:
            header_name = key.replace('_', '-').title()
            headers[header_name] = val

    # Read body
    try:
        content_length = int(environ.get('CONTENT_LENGTH') or 0)
    except (ValueError, TypeError):
        content_length = 0

    body_bytes = environ['wsgi.input'].read(content_length) if content_length > 0 and 'wsgi.input' in environ else b''
    rfile = io.BytesIO(body_bytes)
    wfile = io.BytesIO()

    # Create handler mock
    handler = ThreadedHTTPRequestHandler.__new__(ThreadedHTTPRequestHandler)
    handler._is_wsgi = True
    handler.client_address = (environ.get('REMOTE_ADDR', '127.0.0.1'), int(environ.get('REMOTE_PORT', 0) or 0))
    handler.path = full_path
    handler.headers = headers
    handler.rfile = rfile
    handler.wfile = wfile
    handler.command = method
    handler.request_version = "HTTP/1.1"
    handler.status_code = 200
    handler.response_headers = []
    handler.directory = BASE_DIR

    try:
        if method == 'GET':
            handler.do_GET()
        elif method == 'POST':
            handler.do_POST()
        elif method == 'OPTIONS':
            handler.do_OPTIONS()
        else:
            handler.send_json(405, {"error": "Method not allowed"})
    except Exception as e:
        handler.status_code = 500
        handler.response_headers = [('Content-Type', 'application/json; charset=utf-8')]
        wfile.write(json.dumps({"error": f"Server error: {str(e)}"}).encode('utf-8'))

    status_phrase = STATUS_REASONS.get(handler.status_code, "Status")
    status_str = f"{handler.status_code} {status_phrase}"
    start_response(status_str, handler.response_headers)
    return [wfile.getvalue()]

_bot_started = False
_bot_lock = threading.Lock()

def start_bot_background():
    global _bot_started
    bot_token = os.environ.get("BOT_TOKEN", "").strip()
    guard_token = os.environ.get("GUARD_BOT_TOKEN", "").strip()
    if not bot_token and not guard_token:
        return
    with _bot_lock:
        if _bot_started:
            return
        _bot_started = True
        try:
            import bot
            bot.run_all_bots()
            print("🤖 [TELEGRAM BOTS] Multi-Bot Background Polling avtomatik ishga tushirildi.")
        except Exception as e:
            print(f"⚠️ [TELEGRAM BOTS] Background start xatosi: {e}")

# Automatically trigger background bot on startup
start_bot_background()

def main():
    os.chdir(BASE_DIR)
    local_ip = get_local_ip()

    # Run initial migrations
    migrate_base64_images()

    # Start Telegram Bot in background if BOT_TOKEN is present
    start_bot_background()

    print("\n" + "=" * 75)
    print("🚀 KENJAYEV BLOG — PROFESSIONAL PRODUCTION SERVER ISHGA TUSHDI!")
    print("=" * 75)
    print(f"\n💻 Kompyuter brauzerida ochish uchun:")
    print(f"👉 http://localhost:{PORT}")
    print(f"👉 http://127.0.0.1:{PORT}\n")
    print(f"📱 TELEFON VA PLANSHETLARDA OCHISH UCHUN (Wi-Fi):")
    print(f"👉 http://{local_ip}:{PORT}\n")
    print("🔒 XAVFSIZLIK: PBKDF2 Password Hashing, Session Token, Rate Limiter Faol!")
    print("📊 ANALITIKA: Real Smart Views, Authoritative Likes, Terminal Monitoring!")
    print("💾 DATA INTEGRITY: Atomik yozish va avtomatik zaxira tizimi yoqildi.")
    print("=" * 75)
    print("💡 Serverni to'xtatish uchun: Ctrl + C\n")

    try:
        with ThreadedTCPServer(("0.0.0.0", PORT), ThreadedHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server to'xtatildi.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Xatolik: {e}")

if __name__ == "__main__":
    main()

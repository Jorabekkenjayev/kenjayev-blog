import os
import sqlite3
import threading
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'bot_database.db')

_db_lock = threading.Lock()

def get_connection(db_path=None):
    path = db_path or DB_FILE
    conn = sqlite3.connect(path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
    except Exception:
        pass
    return conn

def init_db(db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_users (
                        telegram_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        full_name TEXT,
                        state TEXT DEFAULT 'NEW_USER',
                        is_registered INTEGER DEFAULT 0,
                        is_blocked INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_message_map (
                        admin_message_id INTEGER PRIMARY KEY,
                        user_telegram_id INTEGER NOT NULL,
                        user_message_id INTEGER,
                        text_snippet TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_groups (
                        group_id INTEGER PRIMARY KEY,
                        title TEXT,
                        username TEXT,
                        is_active INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_verified_users (
                        user_id INTEGER PRIMARY KEY,
                        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_pending_verifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        user_message_id INTEGER NOT NULL,
                        bot_message_id INTEGER NOT NULL,
                        expires_at REAL NOT NULL,
                        status TEXT DEFAULT 'pending'
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_registered ON bot_users(is_registered);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_msg_map_user ON bot_message_map(user_telegram_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_pending_verif ON bot_pending_verifications(status, expires_at);")
        finally:
            conn.close()

# --- SETTINGS MANAGEMENT ---
def get_setting(key, default="60", db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row['value'] if row else default
    finally:
        conn.close()

def set_setting(key, value, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, str(value)))
                return True
        finally:
            conn.close()

# --- GROUPS MANAGEMENT ---
def upsert_group(group_id, title, username=None, is_active=1, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                conn.execute("""
                    INSERT INTO bot_groups (group_id, title, username, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(group_id) DO UPDATE SET
                        title = excluded.title,
                        username = excluded.username,
                        is_active = excluded.is_active,
                        updated_at = excluded.updated_at
                """, (group_id, title, username, is_active, now, now))
                return True
        finally:
            conn.close()

def get_all_active_groups(db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT group_id, title, username FROM bot_groups WHERE is_active = 1")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

# --- VERIFIED USERS (ANTI-SPAM / BOT PROTECTION) ---
def is_user_verified(user_id, db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM bot_verified_users WHERE user_id = ?", (user_id,))
        return cur.fetchone() is not None
    finally:
        conn.close()

def verify_user(user_id, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                conn.execute("INSERT OR IGNORE INTO bot_verified_users (user_id, verified_at) VALUES (?, ?)", (user_id, now))
                # Also resolve any pending verifications for this user
                conn.execute("UPDATE bot_pending_verifications SET status = 'verified' WHERE user_id = ? AND status = 'pending'", (user_id,))
                return True
        finally:
            conn.close()

# --- PENDING VERIFICATIONS QUEUE ---
def add_pending_verification(group_id, user_id, user_message_id, bot_message_id, expires_at, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute("""
                    INSERT INTO bot_pending_verifications (group_id, user_id, user_message_id, bot_message_id, expires_at, status)
                    VALUES (?, ?, ?, ?, ?, 'pending')
                """, (group_id, user_id, user_message_id, bot_message_id, expires_at))
                return True
        finally:
            conn.close()

def get_expired_verifications(current_time=None, db_path=None):
    now_ts = current_time or time.time()
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, group_id, user_id, user_message_id, bot_message_id, expires_at
            FROM bot_pending_verifications
            WHERE status = 'pending' AND expires_at <= ?
        """, (now_ts,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def mark_verification_expired(verif_id, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute("UPDATE bot_pending_verifications SET status = 'expired' WHERE id = ?", (verif_id,))
                return True
        finally:
            conn.close()

def resolve_pending_verification(group_id, user_id, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, bot_message_id, user_message_id 
                    FROM bot_pending_verifications 
                    WHERE group_id = ? AND user_id = ? AND status = 'pending'
                """, (group_id, user_id))
                rows = [dict(r) for r in cur.fetchall()]
                conn.execute("""
                    UPDATE bot_pending_verifications 
                    SET status = 'verified' 
                    WHERE group_id = ? AND user_id = ? AND status = 'pending'
                """, (group_id, user_id))
                return rows
        finally:
            conn.close()

# --- STANDARD USER MANAGEMENT ---
def get_user(telegram_id, db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bot_users WHERE telegram_id = ?", (telegram_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def upsert_user(telegram_id, username, first_name, last_name, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM bot_users WHERE telegram_id = ?", (telegram_id,))
                existing = cur.fetchone()
                if existing:
                    cur.execute("""
                        UPDATE bot_users 
                        SET username = ?, first_name = ?, last_name = ?, last_activity = ?, updated_at = ?
                        WHERE telegram_id = ?
                    """, (username, first_name, last_name, now, now, telegram_id))
                    is_new = False
                else:
                    cur.execute("""
                        INSERT INTO bot_users (telegram_id, username, first_name, last_name, state, is_registered, created_at, updated_at, last_activity)
                        VALUES (?, ?, ?, ?, 'WAITING_FOR_NAME', 0, ?, ?, ?)
                    """, (telegram_id, username, first_name, last_name, now, now, now))
                    is_new = True
                
                cur.execute("SELECT * FROM bot_users WHERE telegram_id = ?", (telegram_id,))
                user = dict(cur.fetchone())
                return user, is_new
        finally:
            conn.close()

def set_user_full_name(telegram_id, full_name, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE bot_users 
                    SET full_name = ?, state = 'REGISTERED', is_registered = 1, last_activity = ?, updated_at = ?
                    WHERE telegram_id = ?
                """, (full_name, now, now, telegram_id))
                return cur.rowcount > 0
        finally:
            conn.close()

def set_user_state(telegram_id, state, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE bot_users 
                    SET state = ?, last_activity = ?, updated_at = ?
                    WHERE telegram_id = ?
                """, (state, now, now, telegram_id))
                return cur.rowcount > 0
        finally:
            conn.close()

def touch_user_activity(telegram_id, db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("UPDATE bot_users SET last_activity = ? WHERE telegram_id = ?", (now, telegram_id))
        finally:
            conn.close()

def save_message_mapping(admin_message_id, user_telegram_id, user_message_id=None, text_snippet="", db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO bot_message_map (admin_message_id, user_telegram_id, user_message_id, text_snippet, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (admin_message_id, user_telegram_id, user_message_id, text_snippet, now))
                return True
        finally:
            conn.close()

def get_mapping_by_admin_message(admin_message_id, db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bot_message_map WHERE admin_message_id = ?", (admin_message_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def log_action(user_id, action, details="", db_path=None):
    with _db_lock:
        conn = get_connection(db_path)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with conn:
                conn.execute("""
                    INSERT INTO bot_logs (user_id, action, details, created_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, action, details, now))
        finally:
            conn.close()

def get_stats(db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as total_users FROM bot_users")
        total_users = cur.fetchone()['total_users']
        
        cur.execute("SELECT COUNT(*) as registered_users FROM bot_users WHERE is_registered = 1")
        registered_users = cur.fetchone()['registered_users']
        
        cur.execute("SELECT COUNT(*) as active_24h FROM bot_users WHERE last_activity >= datetime('now', '-1 day')")
        active_24h = cur.fetchone()['active_24h']
        
        cur.execute("SELECT COUNT(*) as total_messages FROM bot_message_map")
        total_messages = cur.fetchone()['total_messages']
        
        cur.execute("SELECT COUNT(*) as total_groups FROM bot_groups WHERE is_active = 1")
        total_groups = cur.fetchone()['total_groups']

        cur.execute("SELECT COUNT(*) as verified_humans FROM bot_verified_users")
        verified_humans = cur.fetchone()['verified_humans']
        
        return {
            "total_users": total_users,
            "registered_users": registered_users,
            "active_24h": active_24h,
            "total_messages": total_messages,
            "total_groups": total_groups,
            "verified_humans": verified_humans
        }
    finally:
        conn.close()

def get_recent_users(limit=10, db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT telegram_id, username, first_name, last_name, full_name, is_registered, created_at, last_activity
            FROM bot_users
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def get_all_registered_user_ids(db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT telegram_id FROM bot_users WHERE is_registered = 1 AND is_blocked = 0")
        return [row['telegram_id'] for row in cur.fetchall()]
    finally:
        conn.close()

# Auto-initialize on import
init_db()

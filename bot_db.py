import os
import json
import sqlite3
import threading
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'bot_database.db')
DATA_JSON_FILE = os.path.join(BASE_DIR, 'data.json')

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
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS quiz_leaderboard (
                        user_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        username TEXT,
                        points INTEGER DEFAULT 0,
                        correct_count INTEGER DEFAULT 0,
                        total_solved INTEGER DEFAULT 0,
                        best_streak INTEGER DEFAULT 0,
                        current_streak INTEGER DEFAULT 0,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS quiz_user_progress (
                        user_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        section_id TEXT,
                        is_correct INTEGER DEFAULT 0,
                        points INTEGER DEFAULT 0,
                        solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, question_id)
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_registered ON bot_users(is_registered);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_msg_map_user ON bot_message_map(user_telegram_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_pending_verif ON bot_pending_verifications(status, expires_at);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_leaderboard_rank ON quiz_leaderboard(points DESC, correct_count DESC);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_prog_sec ON quiz_user_progress(user_id, section_id);")
                
                # Auto-sync data.json -> SQLite if SQLite was newly created or has fewer records
                sync_leaderboard_from_json(conn)
        finally:
            conn.close()

def sync_leaderboard_from_json(conn):
    """Loads and merges persistent leaderboard and progress from data.json into SQLite."""
    if not os.path.exists(DATA_JSON_FILE):
        return
    try:
        with open(DATA_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        json_lb = data.get('quiz_leaderboard', [])
        json_prog = data.get('quiz_user_progress', [])

        for u in json_lb:
            uid = str(u.get('user_id', '')).strip()
            if not uid: continue
            conn.execute("""
                INSERT INTO quiz_leaderboard (user_id, name, username, points, correct_count, total_solved, best_streak, current_streak, last_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    points = MAX(quiz_leaderboard.points, excluded.points),
                    correct_count = MAX(quiz_leaderboard.correct_count, excluded.correct_count),
                    total_solved = MAX(quiz_leaderboard.total_solved, excluded.total_solved),
                    best_streak = MAX(quiz_leaderboard.best_streak, excluded.best_streak),
                    name = CASE WHEN excluded.name != '' THEN excluded.name ELSE quiz_leaderboard.name END,
                    username = CASE WHEN excluded.username != '' THEN excluded.username ELSE quiz_leaderboard.username END
            """, (
                uid,
                u.get('name', 'Foydalanuvchi'),
                u.get('username', ''),
                int(u.get('points', 0)),
                int(u.get('correct_count', 0)),
                int(u.get('total_solved', 0)),
                int(u.get('best_streak', 0)),
                int(u.get('current_streak', 0)),
                u.get('last_active', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                u.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ))

        for p in json_prog:
            uid = str(p.get('user_id', '')).strip()
            qid = str(p.get('question_id', '')).strip()
            if not uid or not qid: continue
            conn.execute("""
                INSERT INTO quiz_user_progress (user_id, question_id, section_id, is_correct, points, solved_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, question_id) DO NOTHING
            """, (
                uid,
                qid,
                p.get('section_id', ''),
                1 if p.get('is_correct') else 0,
                int(p.get('points', 0)),
                p.get('solved_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ))
    except Exception as e:
        print(f"[LeaderboardSyncFromJSON] Error: {e}")

def sync_leaderboard_to_json(conn):
    """Saves SQLite leaderboard & progress state into data.json for persistent survival."""
    if not os.path.exists(DATA_JSON_FILE):
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM quiz_leaderboard ORDER BY points DESC, correct_count DESC")
        all_lb = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT * FROM quiz_user_progress")
        all_prog = [dict(r) for r in cur.fetchall()]

        with open(DATA_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data['quiz_leaderboard'] = all_lb
        data['quiz_user_progress'] = all_prog

        tmp_path = DATA_JSON_FILE + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_JSON_FILE)
    except Exception as e:
        print(f"[LeaderboardSyncToJSON] Error: {e}")

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

# --- QUIZ LEADERBOARD & RANKING MANAGEMENT ---
def upsert_leaderboard_user(user_id, name, username=None, db_path=None):
    if not user_id or not name:
        return None
    user_id_str = str(user_id).strip()
    name_str = str(name).strip()[:100]
    username_str = str(username).strip().lstrip('@')[:50] if username else ""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute("""
                    INSERT INTO quiz_leaderboard (user_id, name, username, points, correct_count, total_solved, best_streak, current_streak, last_active, created_at)
                    VALUES (?, ?, ?, 0, 0, 0, 0, 0, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        name = CASE WHEN excluded.name != '' THEN excluded.name ELSE quiz_leaderboard.name END,
                        username = CASE WHEN excluded.username != '' THEN excluded.username ELSE quiz_leaderboard.username END,
                        last_active = excluded.last_active
                """, (user_id_str, name_str, username_str, now, now))
                sync_leaderboard_to_json(conn)
                return True
        finally:
            conn.close()

def update_leaderboard_score(user_id, name, username=None, points_earned=0, is_correct=False, current_streak=0, db_path=None):
    if not user_id:
        return None
    user_id_str = str(user_id).strip()
    name_str = str(name).strip()[:100] if name else "Ismsiz Ishtirokchi"
    username_str = str(username).strip().lstrip('@')[:50] if username else ""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    inc_correct = 1 if is_correct else 0
    pts = max(0, int(points_earned))
    streak_val = max(0, int(current_streak))

    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                # 1. Upsert initial if not exists
                conn.execute("""
                    INSERT INTO quiz_leaderboard (user_id, name, username, points, correct_count, total_solved, best_streak, current_streak, last_active, created_at)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        name = CASE WHEN excluded.name != '' AND excluded.name != 'Ismsiz Ishtirokchi' THEN excluded.name ELSE quiz_leaderboard.name END,
                        username = CASE WHEN excluded.username != '' THEN excluded.username ELSE quiz_leaderboard.username END,
                        points = quiz_leaderboard.points + excluded.points,
                        correct_count = quiz_leaderboard.correct_count + excluded.correct_count,
                        total_solved = quiz_leaderboard.total_solved + 1,
                        current_streak = excluded.current_streak,
                        best_streak = MAX(quiz_leaderboard.best_streak, excluded.current_streak),
                        last_active = excluded.last_active
                """, (user_id_str, name_str, username_str, pts, inc_correct, streak_val, streak_val, now, now))
                sync_leaderboard_to_json(conn)
                return True
        finally:
            conn.close()

def get_leaderboard_top(limit=50, db_path=None):
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, name, username, points, correct_count, total_solved, best_streak, current_streak, last_active
            FROM quiz_leaderboard
            WHERE total_solved > 0
            ORDER BY points DESC, correct_count DESC, (CAST(correct_count AS FLOAT) / MAX(total_solved, 1)) DESC, last_active ASC
            LIMIT ?
        """, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        
        # Calculate dynamic ranks and badges
        result = []
        for idx, row in enumerate(rows):
            rank = idx + 1
            tot = max(1, row.get('total_solved', 0))
            cor = row.get('correct_count', 0)
            acc = round((cor / tot) * 100)
            pts = row.get('points', 0)

            # Badges and Titles
            if rank == 1:
                badge = "🥇"
                title = "Oltin Peshqadam"
            elif rank == 2:
                badge = "🥈"
                title = "Kumush Peshqadam"
            elif rank == 3:
                badge = "🥉"
                title = "Bronza Peshqadam"
            elif rank <= 10:
                badge = "🎖"
                title = "Grossmeyster"
            elif pts >= 100:
                badge = "⭐"
                title = "Usta"
            else:
                badge = "🎯"
                title = "Ishtirokchi"

            row['rank'] = rank
            row['accuracy'] = acc
            row['badge'] = badge
            row['title'] = title
            result.append(row)

        return result
    finally:
        conn.close()

def get_user_leaderboard_rank(user_id, db_path=None):
    if not user_id:
        return None
    user_id_str = str(user_id).strip()
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM quiz_leaderboard WHERE user_id = ?", (user_id_str,))
        user_row = cur.fetchone()
        if not user_row:
            return None
        
        user_dict = dict(user_row)
        user_points = user_dict.get('points', 0)
        user_correct = user_dict.get('correct_count', 0)

        # Count how many users have strictly better score
        cur.execute("""
            SELECT COUNT(*) as rank_above
            FROM quiz_leaderboard
            WHERE total_solved > 0 AND (
                points > ? OR
                (points = ? AND correct_count > ?)
            )
        """, (user_points, user_points, user_correct))
        
        rank = cur.fetchone()['rank_above'] + 1
        tot = max(1, user_dict.get('total_solved', 0))
        cor = user_dict.get('correct_count', 0)
        user_dict['rank'] = rank
        user_dict['accuracy'] = round((cor / tot) * 100)

        if rank == 1:
            user_dict['badge'] = "🥇"
            user_dict['title'] = "Oltin Peshqadam"
            user_dict['points_to_next'] = 0
        elif rank == 2:
            user_dict['badge'] = "🥈"
            user_dict['title'] = "Kumush Peshqadam"
        elif rank == 3:
            user_dict['badge'] = "🥉"
            user_dict['title'] = "Bronza Peshqadam"
        elif rank <= 10:
            user_dict['badge'] = "🎖"
            user_dict['title'] = "Grossmeyster"
        else:
            user_dict['badge'] = "🎯"
            user_dict['title'] = "Ishtirokchi"

        return user_dict
    finally:
        conn.close()

# --- USER QUESTION PROGRESS & PERSISTENCE ---
def record_user_question_progress(user_id, question_id, section_id=None, is_correct=False, points=0, db_path=None):
    if not user_id or not question_id:
        return False
    user_id_str = str(user_id).strip()
    question_id_str = str(question_id).strip()
    section_id_str = str(section_id).strip() if section_id else ""
    correct_val = 1 if is_correct else 0
    points_val = max(0, int(points))
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                conn.execute("""
                    INSERT INTO quiz_user_progress (user_id, question_id, section_id, is_correct, points, solved_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, question_id) DO UPDATE SET
                        section_id = excluded.section_id,
                        is_correct = excluded.is_correct,
                        points = excluded.points,
                        solved_at = excluded.solved_at
                """, (user_id_str, question_id_str, section_id_str, correct_val, points_val, now))
                sync_leaderboard_to_json(conn)
                return True
        finally:
            conn.close()

def get_user_solved_question_ids(user_id, section_id=None, db_path=None):
    if not user_id:
        return []
    user_id_str = str(user_id).strip()
    conn = get_connection(db_path)
    try:
        cur = conn.cursor()
        if section_id:
            cur.execute("""
                SELECT question_id, section_id, is_correct, points, solved_at
                FROM quiz_user_progress
                WHERE user_id = ? AND section_id = ?
            """, (user_id_str, str(section_id).strip()))
        else:
            cur.execute("""
                SELECT question_id, section_id, is_correct, points, solved_at
                FROM quiz_user_progress
                WHERE user_id = ?
            """, (user_id_str,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def reset_user_section_progress(user_id, section_id=None, db_path=None):
    if not user_id:
        return False
    user_id_str = str(user_id).strip()
    with _db_lock:
        conn = get_connection(db_path)
        try:
            with conn:
                if section_id:
                    conn.execute("""
                        DELETE FROM quiz_user_progress
                        WHERE user_id = ? AND section_id = ?
                    """, (user_id_str, str(section_id).strip()))
                else:
                    conn.execute("""
                        DELETE FROM quiz_user_progress
                        WHERE user_id = ?
                    """, (user_id_str,))
                sync_leaderboard_to_json(conn)
                return True
        finally:
            conn.close()

# Auto-initialize on import
init_db()

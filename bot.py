import os
import sys
import json
import time
import re
import html
import random
import logging
import urllib.request
import urllib.parse
import urllib.error
import threading
from collections import deque
from datetime import datetime

import bot_db

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

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [TelegramBot] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("KenjayevBot")

# --- ENVIRONMENT VARIABLES & CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
GUARD_BOT_TOKEN = os.environ.get("GUARD_BOT_TOKEN", "").strip()

ADMIN_CHAT_ID_RAW = os.environ.get("ADMIN_CHAT_ID", "").strip()
try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW) if ADMIN_CHAT_ID_RAW else None
except ValueError:
    ADMIN_CHAT_ID = None

WEB_APP_URL = os.environ.get("WEB_APP_URL", "").strip() or "https://kenjayev-blog.onrender.com"
if not WEB_APP_URL.startswith("http"):
    WEB_APP_URL = "https://" + WEB_APP_URL

MAIN_BOT_USERNAME = os.environ.get("MAIN_BOT_USERNAME", "KenjayevJorabekBot").strip()
GUARD_BOT_USERNAME = os.environ.get("GUARD_BOT_USERNAME", "Botlarni_tekshiruvchi_Bot").strip()

# Quiz savollari manbasi (server.py data.json ni yangilab boradi)
DATA_JSON_PATH = os.path.join(BASE_DIR, "data.json")

# Sticker: admin @Stickers orqali yoki botga sticker yuborib olingan file_id'larni
# .env ga yozadi (masalan STICKER_WELCOME=CAAC...). Bo'sh bo'lsa sticker yuborilmaydi.
STICKER_KEYS = ("welcome", "register", "correct", "wrong", "rating", "reply")

# In-memory Rate Limiter: { user_id: [timestamp1, timestamp2, ...] }
_rate_limits = {}
_rate_lock = threading.Lock()
RATE_LIMIT_WINDOW = 10.0  # seconds
RATE_LIMIT_MAX_COUNT = 8   # max messages per window

# Bot ichida yechilgan savollar uchun ketma-ketlik (streak) holati
_streaks = {}
_streak_lock = threading.Lock()


# --- TELEGRAM BOT API CLIENT ---
class TelegramClient:
    def __init__(self, token=None, default_username="KenjayevJorabekBot"):
        self.token = token or BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.bot_username = default_username
        self._username_resolved = False

    def _request(self, method, data=None):
        if not self.token:
            logger.warning("BOT_TOKEN o'rnatilmagan! Telegram API so'rovi amalga oshirilmadi.")
            return None
        
        url = f"{self.base_url}/{method}"
        headers = {"Content-Type": "application/json"}
        req_data = json.dumps(data).encode("utf-8") if data else None

        try:
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST" if req_data else "GET")
            with urllib.request.urlopen(req, timeout=35) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                if not res_json.get("ok"):
                    logger.error(f"Telegram API xatolik ({method}): {res_json.get('description')}")
                    return None
                return res_json.get("result")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Telegram HTTP xatosi ({method} - {e.code}): {err_msg}")
            return None
        except Exception as e:
            logger.error(f"Telegram tarmoq xatosi ({method}): {e}")
            return None

    def get_me(self):
        res = self._request("getMe")
        if res and "username" in res:
            self.bot_username = res["username"]
        self._username_resolved = True
        return res

    def ensure_username(self):
        """Har bir client uchun bir marta haqiqiy usernameni Telegram'dan oladi."""
        if not self._username_resolved and self.token:
            self.get_me()
            self._username_resolved = True
        return self.bot_username

    def set_my_commands(self, commands):
        return self._request("setMyCommands", {"commands": commands})

    def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML", reply_to_message_id=None, disable_web_page_preview=True):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        return self._request("sendMessage", payload)

    def delete_message(self, chat_id, message_id):
        payload = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        return self._request("deleteMessage", payload)

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._request("editMessageText", payload)

    def send_sticker(self, chat_id, file_id):
        if not file_id:
            return None
        return self._request("sendSticker", {"chat_id": chat_id, "sticker": file_id})

    def get_file(self, file_id):
        return self._request("getFile", {"file_id": file_id})

    def set_message_reaction(self, chat_id, message_id, emoji="❤️"):
        """Telegram Bot API 7.0+ setMessageReaction"""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": emoji}],
            "is_big": False
        }
        return self._request("setMessageReaction", payload)

    def copy_message(self, chat_id, from_chat_id, message_id, caption=None, parse_mode="HTML", reply_markup=None):
        payload = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "parse_mode": parse_mode
        }
        if caption:
            payload["caption"] = caption
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._request("copyMessage", payload)

    def forward_message(self, chat_id, from_chat_id, message_id):
        payload = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
        return self._request("forwardMessage", payload)

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        payload = {"callback_query_id": callback_query_id, "show_alert": show_alert}
        if text:
            payload["text"] = text
        return self._request("answerCallbackQuery", payload)

    def get_updates(self, offset=None, timeout=30):
        payload = {"timeout": timeout, "allowed_updates": ["message", "callback_query", "my_chat_member"]}
        if offset is not None:
            payload["offset"] = offset
        return self._request("getUpdates", payload)


# --- VALIDATION ENGINE ---
def validate_full_name(text):
    if not text or not isinstance(text, str):
        return None
    
    cleaned = text.strip()
    if len(cleaned) < 3 or len(cleaned) > 100:
        return None

    if re.search(r'(https?://|www\.|\.com|\.uz|@|[0-9]{3,}|[<>{}\[\]=_\+])', cleaned, re.IGNORECASE):
        return None

    words = [w.strip() for w in re.split(r'\s+', cleaned) if w.strip()]
    if len(words) < 2:
        return None

    for w in words:
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁoʻo'gʻg'OʻO'GʻG'\-']+$", w, re.UNICODE):
            return None

    formatted = " ".join([w.capitalize() for w in words])
    return formatted


def check_rate_limit(user_id):
    now = time.time()
    with _rate_lock:
        if user_id not in _rate_limits:
            _rate_limits[user_id] = [now]
            return True
        
        _rate_limits[user_id] = [t for t in _rate_limits[user_id] if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_limits[user_id]) >= RATE_LIMIT_MAX_COUNT:
            return False
        _rate_limits[user_id].append(now)
        return True


# --- QUIZ BANK (data.json) ---
_quiz_cache = {"mtime": 0.0, "questions": [], "sections": {}, "lock": threading.Lock()}
_recent_questions = {}
_recent_lock = threading.Lock()

OPTION_LABELS = ["A", "B", "C", "D", "E", "F"]

_SUPERSCRIPT = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
                "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "n": "ⁿ", "N": "ᴺ",
                "+": "⁺", "-": "⁻", "x": "ˣ", "T": "ᵀ"}


def _sup(text):
    return "".join(_SUPERSCRIPT.get(ch, "^" + ch) for ch in text)


def clean_math(raw):
    """LaTeX ($...$, \\frac, ^{...}) ni Telegram o'qiydigan oddiy matnga aylantiradi."""
    if not raw:
        return ""
    t = str(raw)
    t = t.replace("$", " ")

    def _frac(m):
        num, den = m.group(1).strip(), m.group(2).strip()
        wrap = lambda s: f"({s})" if re.search(r"[+\-*/ ]", s) else s
        return f"{wrap(num)}/{wrap(den)}"

    while "frac{" in t:
        new = re.sub(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}", _frac, t)
        if new == t:
            break
        t = new

    t = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"√(\1)", t)
    t = re.sub(r"\^\{([^{}]*)\}", lambda m: _sup(m.group(1)), t)
    t = re.sub(r"_\{([^{}]*)\}", r"_\1", t)

    replacements = {
        r"\\implies": "⇒", r"\\Rightarrow": "⇒", r"\\rightarrow": "→", r"\\leq": "≤",
        r"\\geq": "≥", r"\\neq": "≠", r"\\approx": "≈", r"\\times": "×", r"\\div": "÷",
        r"\\pm": "±", r"\\cdot": "·", r"\\pi": "π", r"\\alpha": "α", r"\\beta": "β",
        r"\\gamma": "γ", r"\\theta": "θ", r"\\lambda": "λ", r"\\mu": "μ", r"\\sigma": "σ",
        r"\\degree": "°", r"^\\circ": "°", r"\\ln": "ln", r"\\log": "log", r"\\sin": "sin",
        r"\\cos": "cos", r"\\tan": "tan", r"\\Delta": "Δ", r"\\infty": "∞",
        r"\\left": "", r"\\right": "", r"\\,": " ", r"\\;": " ", r"\\!": "",
        r"\\mathrm": "", r"\\text": "", r"\\quad": "  ", r"\\\\": " ",
    }
    for pattern, repl in replacements.items():
        t = re.sub(pattern, repl, t)

    t = t.replace("{", "").replace("}", "").replace("\\", "")
    return re.sub(r"\s+", " ", t).strip()


def load_quiz_questions():
    """data.json dagi savollarni cache bilan o'qiydi."""
    try:
        mtime = os.path.getmtime(DATA_JSON_PATH)
    except OSError:
        return []

    with _quiz_cache["lock"]:
        if _quiz_cache["mtime"] != mtime or not _quiz_cache["questions"]:
            try:
                with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                questions = []
                for q in data.get("quizzes", []):
                    if not isinstance(q, dict) or not q.get("title"):
                        continue
                    options = q.get("options")
                    correct = q.get("correct_option")
                    if not isinstance(options, list) or len(options) < 2:
                        continue
                    if not isinstance(correct, int) or not (0 <= correct < len(options)):
                        continue
                    questions.append(q)
                _quiz_cache["questions"] = questions
                _quiz_cache["sections"] = {
                    s.get("id"): s.get("title", "")
                    for s in data.get("quiz_sections", [])
                    if isinstance(s, dict) and s.get("id")
                }
                _quiz_cache["mtime"] = mtime
                logger.info(f"📚 Quiz bazasi yuklandi: {len(questions)} ta savol.")
            except Exception as e:
                logger.error(f"Quiz bazasini o'qishda xatolik: {e}")
                _quiz_cache["questions"] = []
        return list(_quiz_cache["questions"])


def reset_quiz_cache():
    with _quiz_cache["lock"]:
        _quiz_cache["mtime"] = 0.0
        _quiz_cache["questions"] = []
        _quiz_cache["sections"] = {}


def get_section_title(section_id):
    if not section_id:
        return None
    load_quiz_questions()
    return _quiz_cache["sections"].get(section_id)


def find_question_by_id(qid):
    for q in load_quiz_questions():
        if q.get("id") == qid:
            return q
    return None


def pick_quiz_question(difficulty=None, user_id=None):
    """Daraja bo'yicha takrorlanmaydigan tasodifiy savol tanlaydi."""
    all_q = load_quiz_questions()
    if not all_q:
        return None

    pool = [q for q in all_q if str(q.get("difficulty", "")).lower() == difficulty] if difficulty else list(all_q)
    if not pool:
        pool = all_q

    with _recent_lock:
        recent = _recent_questions.setdefault(user_id, deque(maxlen=12))
        fresh = [q for q in pool if q.get("id") not in recent]
        if not fresh:
            recent.clear()
            fresh = pool
        chosen = random.choice(fresh)
        recent.append(chosen.get("id"))
    return chosen


def bump_streak(user_id, is_correct):
    with _streak_lock:
        current = _streaks.get(user_id, 0)
        current = current + 1 if is_correct else 0
        _streaks[user_id] = current
        return current


# --- STICKER SUPPORT ---
def get_sticker_file_id(key):
    env_val = os.environ.get(f"STICKER_{key.upper()}", "").strip()
    if env_val:
        return env_val
    try:
        return (bot_db.get_setting(f"sticker_{key}", "") or "").strip()
    except Exception:
        return ""


def send_sticker_by_key(client, chat_id, key):
    file_id = get_sticker_file_id(key)
    if not file_id:
        return False
    try:
        return bool(client.send_sticker(chat_id, file_id))
    except Exception as e:
        logger.debug(f"Sticker yuborishda ogohlantirish ({key}): {e}")
        return False


# --- UI BUILDERS ---
def get_main_menu_keyboard():
    """Asosiy menyu: 7 ta ishlaydigan tugma."""
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🎯 QUIZ TESTGA KIRISH",
                    "web_app": {"url": WEB_APP_URL}
                },
                {
                    "text": "📝 BOTDA TEST YECHISH",
                    "callback_data": "test_menu"
                }
            ],
            [
                {
                    "text": "🟢 OSON SAVOL",
                    "callback_data": "test:oson"
                },
                {
                    "text": "🔴 QIYIN SAVOL",
                    "callback_data": "test:qiyin"
                }
            ],
            [
                {
                    "text": "📊 NATIJALARIM",
                    "callback_data": "my_stats"
                },
                {
                    "text": "🏆 REYTING TOP-10",
                    "callback_data": "show_rating"
                }
            ],
            [
                {
                    "text": "🛡 GURUH HIMOYASI",
                    "callback_data": "anti_spam_info"
                },
                {
                    "text": "ℹ️ BOT HAQIDA",
                    "callback_data": "about_bot"
                }
            ],
            [
                {
                    "text": "💬 Jo’rabekka yozish",
                    "callback_data": "write_to_admin"
                }
            ]
        ]
    }


def get_test_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🟢 Oson (10 ball)",
                    "callback_data": "test:oson"
                },
                {
                    "text": "🔴 Qiyin (25 ball)",
                    "callback_data": "test:qiyin"
                }
            ],
            [
                {
                    "text": "🎳 TASODIFIY SAVOL",
                    "callback_data": "test:random"
                }
            ],
            [
                {
                    "text": "🏠 Bosh menyu",
                    "callback_data": "menu:main"
                }
            ]
        ]
    }


def get_question_keyboard(question, chosen_index=None):
    """Savol variantlari yoki javob tekshirilgandan keyingi natija tugmalari."""
    options = question.get("options", [])
    correct = int(question.get("correct_option", 0))
    qid = question.get("id", "")

    if chosen_index is None:
        rows = []
        for idx, opt in enumerate(options[:len(OPTION_LABELS)]):
            label = clean_math(opt)
            if len(label) > 48:
                label = label[:45] + "…"
            rows.append([{
                "text": f"{OPTION_LABELS[idx]}] {label}",
                "callback_data": f"ans:{qid}:{idx}"
            }])
        rows.append([{
            "text": "🏠 Bosh menyu",
            "callback_data": "menu:main"
        }])
        return {"inline_keyboard": rows}

    rows = []
    for idx in range(min(len(options), len(OPTION_LABELS))):
        if idx == correct:
            text = f"✅ {OPTION_LABELS[idx]}] To’g’ri javob shu"
        elif idx == chosen_index:
            text = f"❌ {OPTION_LABELS[idx]}] Sizning javobingiz"
        else:
            text = f"⚪ {OPTION_LABELS[idx]}]"
        rows.append([{"text": text, "callback_data": f"noop:{qid}"}])

    difficulty = str(question.get("difficulty", "oson")).lower()
    rows.append([
        {
            "text": "🔘 KEYINGI SAVOL",
            "callback_data": f"test:{difficulty if difficulty in ('oson', 'qiyin') else 'random'}"
        },
        {
            "text": "📊 NATIJALARIM",
            "callback_data": "my_stats"
        }
    ])
    rows.append([
        {
            "text": "🏠 Bosh menyu",
            "callback_data": "menu:main"
        }
    ])
    return {"inline_keyboard": rows}


def format_question_text(question, section_title=None):
    title = clean_math(question.get("title", ""))
    options = question.get("options", [])
    lines = []
    for idx, opt in enumerate(options[:len(OPTION_LABELS)]):
        lines.append(f"<b>{OPTION_LABELS[idx]}]</b> {html.escape(clean_math(opt))}")
    difficulty = str(question.get("difficulty", "oson")).lower()
    badge = "🟢 Oson" if difficulty == "oson" else "🔴 Qiyin"
    points = question.get("points", 10)

    head = f"📝 <b>SAVOL</b> — {badge} ({points} ball)\n"
    if section_title:
        head += f"📚 {html.escape(section_title)}\n"
    return head + "\n" + html.escape(title) + "\n\n" + "\n".join(lines)


def get_welcome_text():
    return (
        "🌟 <b>Kenjayev Jo’rabek botiga xush kelibsiz!</b>\n\n"
        "Bu yerda siz:\n"
        "• 🎯 Matematika bo’yicha jonli quiz yechasiz\n"
        "• 📝 Botning ichidanoq test savollariga javob berib ball to’playabsiz\n"
        "• 🏆 Reytingda o’rningizni kuzatib borasiz\n"
        "• 🛡 Guruhingizni spamdan himoya qilasiz\n\n"
        "<i>Kenjayev Jo’rabek bu yerda o’z blogini yuritadi.</i>\n\n"
        "👇 <b>Kerakli tugmani bosing:</b>"
    )


def get_leaderboard_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🎯 QUIZ TESTGA KIRISH",
                    "web_app": {"url": WEB_APP_URL}
                },
                {
                    "text": "🔄 YANGILASH",
                    "callback_data": "show_rating"
                }
            ],
            [
                {
                    "text": "📊 NATIJALARIM",
                    "callback_data": "my_stats"
                },
                {
                    "text": "🏠 Bosh menyu",
                    "callback_data": "menu:main"
                }
            ]
        ]
    }


def get_about_text():
    return (
        "ℹ️ <b>BOT HAQIDA</b>\n\n"
        "<b>@KenjayevJorabekBot</b> — matematika quizlari va guruh himoyasi uchun yordamchi.\n\n"
        "🎓 <b>Imkoniyatlar:</b>\n"
        "• Mini App orqali 295+ savol, formulalar va izohli yechimlar\n"
        "• Bot ichida oson/qiyin test yechib ball to’plash\n"
        "• Jonli reyting va shaxsiy statistika\n"
        "• Guruhlarni 18+ spam va reklamalardan tozalash\n\n"
        "📚 <b>Buyruqlar:</b>\n"
        "<code>/start</code> — bosh menyu\n"
        "<code>/test</code> — darhol savol olish\n"
        "<code>/reyting</code> — jonli top-10\n"
        "<code>/stat</code> — mening natijalarim\n"
        "<code>/app</code> — Mini App\n"
        "<code>/help</code> — yordam"
    )


def schedule_message_deletion(client, group_id, user_id, user_msg_id, bot_msg_id, timeout_sec):
    """Guaranteed instant timer that deletes unverified message precisely after timeout_sec."""
    def timer_task():
        if bot_db.is_user_verified(user_id):
            return
        
        # 1. Delete user message
        try:
            client.delete_message(group_id, user_msg_id)
            logger.info(f"🗑 [EXACT TIMER] Guruhdan ({group_id}) xabar o'chirildi (MsgID: {user_msg_id})")
        except Exception as e:
            logger.error(f"❌ User message delete xatosi ({group_id}/{user_msg_id}): {e}")

        # 2. Delete bot warning prompt
        try:
            client.delete_message(group_id, bot_msg_id)
            logger.info(f"🗑 [EXACT TIMER] Guruhdan ({group_id}) bot ogohlantirishi o'chirildi (MsgID: {bot_msg_id})")
        except Exception as e:
            logger.error(f"❌ Bot prompt delete xatosi ({group_id}/{bot_msg_id}): {e}")

    t = threading.Timer(max(1.0, float(timeout_sec)), timer_task)
    t.daemon = True
    t.start()


# --- SHARED CAPTCHA EXPIRATION WORKER ---
class ExpirationCoordinator:
    """Barcha botlar uchun bitta tozalovchi. Har bir update'da yangi thread ochilmaydi."""
    _instance = None
    _instance_lock = threading.Lock()

    def __init__(self):
        self._clients = []
        self._thread = None
        self._running = False
        self._lock = threading.Lock()

    @classmethod
    def get(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = ExpirationCoordinator()
            return cls._instance

    @classmethod
    def reset(cls):
        """Testlar va qayta ishga tushirish uchun coordinator'ni tozalaydi."""
        with cls._instance_lock:
            if cls._instance is not None:
                cls._instance.stop()
                cls._instance._clients = []
                cls._instance._thread = None
                cls._instance = None

    def register_client(self, client):
        with self._lock:
            if client not in self._clients:
                self._clients.append(client)

    def stop(self):
        self._running = False

    def _delete_with_any_client(self, group_id, message_id):
        with self._lock:
            clients = list(self._clients)
        for client in clients:
            try:
                if client.delete_message(group_id, message_id):
                    return True
            except Exception:
                continue
        return False

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True, name="CaptchaExpirationWorker")
            self._thread.start()

    def _loop(self):
        while self._running:
            try:
                for item in bot_db.get_expired_verifications(time.time()):
                    ok_user = self._delete_with_any_client(item["group_id"], item["user_message_id"])
                    ok_bot = self._delete_with_any_client(item["group_id"], item["bot_message_id"])
                    bot_db.mark_verification_expired(item["id"])
                    if ok_user or ok_bot:
                        logger.info(f"🗑 [CAPTCHA EXPIRED] {item['group_id']} xabarlari tozalandi.")
            except Exception as e:
                logger.debug(f"Expiration worker xatosi: {e}")
            time.sleep(1)


# --- MAIN BOT ENGINE (Kenjayev Jo'rabek Bot) ---
class BotEngine:
    def __init__(self, client=None):
        self.client = client or TelegramClient(BOT_TOKEN, MAIN_BOT_USERNAME)
        self._running = True
        ExpirationCoordinator.get().register_client(self.client)

    def stop(self):
        self._running = False

    def handle_update(self, update):
        try:
            if "message" in update:
                self.process_message(update["message"])
            elif "callback_query" in update:
                self.process_callback_query(update["callback_query"])
            elif "my_chat_member" in update:
                self.process_my_chat_member(update["my_chat_member"])
        except Exception as e:
            logger.error(f"Update qayta ishlashda kutilmagan xatolik: {e}", exc_info=True)

    def process_my_chat_member(self, mcm):
        chat = mcm.get("chat", {})
        chat_id = chat.get("id")
        chat_title = chat.get("title", "")
        chat_username = chat.get("username")
        new_status = mcm.get("new_chat_member", {}).get("status")

        if chat_id and chat.get("type") in ["group", "supergroup"]:
            is_active = 1 if new_status in ["administrator", "member"] else 0
            bot_db.upsert_group(chat_id, chat_title, chat_username, is_active=is_active)
            logger.info(f"Guruh statusi yangilandi: {chat_title} ({chat_id}) -> {new_status}")

    def process_callback_query(self, cq):
        cq_id = cq.get("id")
        user_data = cq.get("from", {})
        user_id = user_data.get("id")
        data = cq.get("data", "")
        message = cq.get("message", {})
        chat_id = message.get("chat", {}).get("id", user_id)
        bot_msg_id = message.get("message_id")

        if not user_id:
            return

        bot_db.touch_user_activity(user_id)

        # 1. Anti-spam / 18+ reklamani o'chirish info button
        if data == "anti_spam_info":
            self.client.answer_callback_query(cq_id)
            timeout = bot_db.get_setting("captcha_timeout", "60")
            bot_uname = self.client.ensure_username()
            
            info_text = (
                "🛡 <b>Guruhni 18+ spam va reklamalardan tozalash:</b>\n\n"
                "Botni guruhingizga qo'shib, <b>admin</b> huquqini bersangiz:\n"
                f"• Guruhga yozgan har bir yangi a'zo bot emasligini tasdiqlashi kerak bo'ladi.\n"
                f"• Agar <b>{timeout} soniya</b> ichida tasdiqlamasa, uning xabari avtomatik o'chiriladi!\n"
                "• Bir marta tasdiqlagan odamdan keyingi safar qayta so'ralmaydi.\n\n"
                "👇 Pastdagi tugma orqali botni guruhingizga admin sifatida qo'shing:"
            )
            
            add_group_kb = {
                "inline_keyboard": [
                    [
                        {
                            "text": "➕ Guruhga admin sifatida qo'shish",
                            "url": f"https://t.me/{bot_uname}?startgroup=true&admin=delete_messages+restrict_members"
                        }
                    ]
                ]
            }
            self.client.send_message(chat_id, info_text, reply_markup=add_group_kb)
            return

        # 2. Captcha: "Men bot emasman" Verification
        if data.startswith("verify_human:"):
            parts = data.split(":")
            if len(parts) >= 4:
                target_user_id = int(parts[1])
                user_msg_id = int(parts[2])
                group_id = int(parts[3])

                if user_id != target_user_id:
                    self.client.answer_callback_query(cq_id, text="⚠️ Bu tugma siz uchun emas!", show_alert=True)
                    return

                bot_db.verify_user(user_id)
                self.client.answer_callback_query(cq_id, text="✅ Rahmat! Siz bot emasligingiz tasdiqlandi.")

                try:
                    self.client.delete_message(group_id, bot_msg_id)
                except Exception as e:
                    logger.debug(f"Bot prompt delete xatosi: {e}")

                bot_db.resolve_pending_verification(group_id, user_id)
                return

        # 3. Bosh menyuni qayta ko'rsatish (eski "check_test" ham shu yerga tushadi)
        if data in ("menu:main", "menu", "start_menu", "check_test"):
            self.client.answer_callback_query(cq_id)
            self.client.send_message(chat_id, get_welcome_text(), reply_markup=get_main_menu_keyboard())
            return

        # 4. Test yechish menyusi (daraja tanlash)
        if data == "test_menu":
            self.client.answer_callback_query(cq_id)
            self.client.send_message(
                chat_id,
                "📝 <b>BOTDA TEST YECHISH</b>\n\n"
                "🟢 <b>Oson</b> savol — 10 ball\n"
                "🔴 <b>Qiyin</b> savol — 25 ball\n\n"
                "To’g’ri javob berilsa ballingiz reytingga qo’shiladi. Darajani tanlang:",
                reply_markup=get_test_menu_keyboard()
            )
            return

        # 5. Yangi savol olish
        if data.startswith("test:"):
            self.client.answer_callback_query(cq_id)
            self.send_random_question(chat_id, user_id, data.split(":", 1)[1])
            return

        # 6. Javobni tekshirish
        if data.startswith("ans:"):
            self.handle_answer(chat_id, bot_msg_id, cq_id, user_id, user_data, data)
            return

        # 7. Javob berilgan savolning tugmalari (qayta bosilsa)
        if data.startswith("noop:"):
            self.client.answer_callback_query(cq_id, text="ℹ️ Bu savolga javob berilgan.", show_alert=True)
            return

        # 8. Natijalarim
        if data == "my_stats":
            self.client.answer_callback_query(cq_id)
            user, _ = bot_db.upsert_user(
                user_id,
                user_data.get("username", ""),
                user_data.get("first_name", ""),
                user_data.get("last_name", "")
            )
            self.handle_user_stat_command(user, chat_id)
            return

        # 9. Jonli reyting
        if data == "show_rating":
            self.client.answer_callback_query(cq_id)
            self.handle_leaderboard_command(chat_id)
            return

        # 10. Bot haqida
        if data == "about_bot":
            self.client.answer_callback_query(cq_id)
            self.client.send_message(chat_id, get_about_text(), reply_markup=get_main_menu_keyboard())
            return

        # 11. Jo'rabekka yozish button handler
        if data == "write_to_admin":
            bot_db.set_user_state(user_id, "WRITING_TO_ADMIN")
            self.client.answer_callback_query(cq_id)
            prompt_text = (
                "✍️ <b>Jo’rabekka xabaringizni yozing.</b>\n\n"
                "Xabaringiz to’g’ridan-to’g’ri unga yuboriladi.\n"
                "<i>Bekor qilish uchun: /start</i>"
            )
            self.client.send_message(chat_id, prompt_text)
            return

    def send_random_question(self, chat_id, user_id, difficulty=""):
        difficulty = str(difficulty or "").strip().lower()
        if difficulty not in ("oson", "qiyin"):
            difficulty = None

        question = pick_quiz_question(difficulty, user_id)
        if not question:
            self.client.send_message(
                chat_id,
                "⚠️ <b>Hozircha savol bazasi bo\'sh.</b>\n\n"
                "🎯 <b>QUIZ TESTGA KIRISH</b> tugmasi orqali saytdan foydalanib ko’ring."
            )
            return

        text = format_question_text(question, get_section_title(question.get("section_id")))
        res = self.client.send_message(chat_id, text, reply_markup=get_question_keyboard(question))
        if not res:
            self.client.send_message(chat_id, "⚠️ Savolni yuborishda xatolik bo\'ldi, qayta urinib ko’ring.")

    def handle_answer(self, chat_id, bot_msg_id, cq_id, user_id, user_data, data):
        parts = str(data).split(":")
        if len(parts) < 3:
            self.client.answer_callback_query(cq_id)
            return

        qid = parts[1]
        try:
            chosen = int(parts[2])
        except ValueError:
            self.client.answer_callback_query(cq_id, text="⚠️ Noto’g’ri tugma.", show_alert=True)
            return

        question = find_question_by_id(qid)
        if not question:
            self.client.answer_callback_query(cq_id, text="⚠️ Bu savol bazadan topilmadi.", show_alert=True)
            return

        # Bir savolga faqat bir marta ball beriladi — qayta bosish hisobga olinmaydi
        try:
            already_answered = any(
                str(row.get("question_id")) == str(qid)
                for row in bot_db.get_user_solved_question_ids(f"tg_{user_id}")
            )
        except Exception:
            already_answered = False
        if already_answered:
            self.client.answer_callback_query(cq_id, text="ℹ️ Bu savolga allaqachon javob bergansiz.", show_alert=True)
            return

        correct = int(question.get("correct_option", 0))
        is_correct = chosen == correct
        points = max(0, int(question.get("points", 10) or 0))
        streak = bump_streak(user_id, is_correct)

        user, _ = bot_db.upsert_user(
            user_id,
            user_data.get("username", ""),
            user_data.get("first_name", ""),
            user_data.get("last_name", "")
        )
        display_name = user.get("full_name") or user_data.get("first_name") or f"User {user_id}"
        username = user_data.get("username", "") or ""

        bot_db.record_user_question_progress(
            f"tg_{user_id}", qid, question.get("section_id", ""), is_correct, points if is_correct else 0
        )
        bot_db.update_leaderboard_score(
            f"tg_{user_id}", display_name, username,
            points if is_correct else 0, is_correct, streak
        )

        section_title = get_section_title(question.get("section_id"))
        base_text = format_question_text(question, section_title)
        explanation = clean_math(question.get("explanation", ""))

        if is_correct:
            result_block = f"\n\n✅ <b>TO’G’RI!</b> 🎁 <b>+{points} ball</b>"
            if streak > 1:
                result_block += f"  🔥 {streak} ta ketma-ket!"
            alert_text = f"✅ To’g’ri! +{points} ball"
        else:
            correct_label = OPTION_LABELS[correct] if correct < len(OPTION_LABELS) else "?"
            result_block = f"\n\n❌ <b>XATO.</b> To’g’ri javob: <b>{correct_label}]</b>"
            alert_text = "❌ Afsuski, noto’g’ri."

        if explanation:
            result_block += f"\n\n💡 <b>Yechim:</b> {html.escape(explanation)}"

        self.client.edit_message_text(
            chat_id,
            bot_msg_id,
            base_text + result_block + "\n\n👇 Keyingi savolga o’ting:",
            reply_markup=get_question_keyboard(question, chosen)
        )
        self.client.answer_callback_query(cq_id, text=alert_text, show_alert=not is_correct)

        if is_correct:
            send_sticker_by_key(self.client, chat_id, "correct")

    def process_message(self, message):
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type", "private")
        from_user = message.get("from", {})
        user_id = from_user.get("id")
        message_id = message.get("message_id")
        text = message.get("text", "")
        reply_to_msg = message.get("reply_to_message")

        if not chat_id:
            return

        # GROUP / SUPERGROUP MESSAGE PROCESSING
        if chat_type in ["group", "supergroup"]:
            chat_title = chat.get("title", "Group")
            chat_username = chat.get("username")
            bot_db.upsert_group(chat_id, chat_title, chat_username, is_active=1)

            if not user_id or from_user.get("is_bot") or message.get("sender_chat"):
                return

            if bot_db.is_user_verified(user_id):
                return

            timeout_sec = int(bot_db.get_setting("captcha_timeout", "60"))
            user_name = html.escape(from_user.get("first_name") or "Foydalanuvchi", quote=False)

            warning_text = (
                f"⚠️ <a href=\"tg://user?id={user_id}\">{user_name}</a>, guruhda spam va 18+ reklamalarni oldini olish uchun "
                f"pastdagi tugmani bosib <b>bot emasligingizni tasdiqlang</b>, aks holda xabaringiz <b>{timeout_sec} soniyada</b> o'chiriladi!"
            )
            captcha_kb = {
                "inline_keyboard": [
                    [
                        {
                            "text": "✅ Men bot emasman",
                            "callback_data": f"verify_human:{user_id}:{message_id}:{chat_id}"
                        }
                    ]
                ]
            }

            prompt_res = self.client.send_message(
                chat_id,
                warning_text,
                reply_markup=captcha_kb,
                reply_to_message_id=message_id
            )

            if prompt_res and "message_id" in prompt_res:
                bot_prompt_id = prompt_res["message_id"]
                expires_at = time.time() + timeout_sec
                bot_db.add_pending_verification(chat_id, user_id, message_id, bot_prompt_id, expires_at)
                schedule_message_deletion(self.client, chat_id, user_id, message_id, bot_prompt_id, timeout_sec)
            return

        # PRIVATE CHAT (USER / ADMIN) PROCESSING
        if not user_id:
            return

        if not check_rate_limit(user_id):
            self.client.send_message(
                chat_id,
                "⏳ <i>Iltimos, ketma-ket ko'p xabar yubormang. Birozdan so'ng qayta urinib ko'ring.</i>"
            )
            return

        username = from_user.get("username", "")
        first_name = from_user.get("first_name", "")
        last_name = from_user.get("last_name", "")

        # ADMIN REPLY DISPATCHER
        if ADMIN_CHAT_ID and chat_id == ADMIN_CHAT_ID and reply_to_msg:
            self.handle_admin_reply(message)
            return

        # ADMIN COMMANDS
        if ADMIN_CHAT_ID and chat_id == ADMIN_CHAT_ID and text.startswith("/"):
            if self.handle_admin_commands(message):
                return

        # Yuborilgan sticker qabul qilib olish (file_id'ni sozlamalarga saqlash)
        sticker = message.get("sticker")
        if sticker:
            self.handle_incoming_sticker(chat_id, user_id, message, sticker)
            return

        user, is_new = bot_db.upsert_user(user_id, username, first_name, last_name)
        bot_db.touch_user_activity(user_id)

        normalized = text.strip().lower()

        # /START COMMAND FLOW
        if normalized == "/start":
            self.handle_start_flow(user, chat_id, message_id)
            return

        # /MENU yoki bosh menyu tugma matni
        if normalized in ["/menu", "🏠 bosh menyu", "menyu", "bosh menyu"]:
            self.client.send_message(chat_id, get_welcome_text(), reply_markup=get_main_menu_keyboard())
            return

        # /TEST COMMAND (darhol savol)
        if normalized in ["/test", "/savol", "test", "savol"]:
            self.send_random_question(chat_id, user_id, "")
            return

        if normalized in ["📝 botda test yechish", "botda test yechish"]:
            self.client.send_message(
                chat_id,
                "📝 <b>BOTDA TEST YECHISH</b>\n\nDarajani tanlang:",
                reply_markup=get_test_menu_keyboard()
            )
            return

        # /REYTING /TOP /LEADERBOARD COMMAND
        if normalized in ["/reyting", "/top", "/leaderboard", "🏆 reyting", "reyting"]:
            self.handle_leaderboard_command(chat_id)
            return

        # /STAT /PROFIL COMMAND
        if normalized in ["/stat", "/stats", "/profil", "/profile", "📊 natijalarim", "stat"]:
            self.handle_user_stat_command(user, chat_id)
            return

        # /APP COMMAND
        if normalized in ["/app", "/quiz", "/mini_app", "🌐 saytga kirish"]:
            self.client.send_message(
                chat_id,
                "🌐 <b>Matematika Quiz Hub Mini App</b>\n\nPastdagi tugma orqali ilovani oching:",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # /HELP COMMAND
        if normalized in ["/help", "/yordam", "help", "yordam"]:
            self.client.send_message(chat_id, get_about_text(), reply_markup=get_main_menu_keyboard())
            return

        user_state = user.get("state", "NEW_USER")
        is_registered = user.get("is_registered", 0)

        if user_state == "WAITING_FOR_NAME" or not is_registered:
            self.handle_name_input(user, message)
            return

        self.handle_user_message_to_admin(user, message)

    def handle_incoming_sticker(self, chat_id, user_id, message, sticker):
        """Sticker file_id'ni oladi. Admin caption bilan yuborsa sozlamaga saqlanadi."""
        file_id = sticker.get("file_id", "")
        if not file_id:
            thumbs = sticker.get("thumbs") or []
            file_id = next((t.get("file_id", "") for t in thumbs if t.get("file_id")), "")
        if not file_id:
            return

        logger.info(f"🎨 Sticker qabul qilindi: file_id={file_id} (emoji: {sticker.get('emoji', '')})")

        is_admin = ADMIN_CHAT_ID and chat_id == ADMIN_CHAT_ID
        if not is_admin:
            self.client.send_message(
                chat_id,
                "🎨 <b>Bu bot sticker yuborish orqali boshqariladi.</b>\n\n"
                "Bot haqidagi ma'lumot olish uchun <code>/help</code> ni yuboring."
            )
            return

        key = (message.get("caption") or "").strip().lower().replace("sticker_", "")
        if key in STICKER_KEYS:
            bot_db.set_setting(f"sticker_{key}", file_id)
            self.client.send_message(
                chat_id,
                f"✅ <b>Sticker saqlandi:</b> <code>{key}</code>\n\n"
                f"<code>file_id:</code> <code>{file_id}</code>\n\n"
                "Endi ushbu holatda shu sticker yuboriladi. Boshqa tugmalar uchun "
                f"{', '.join(STICKER_KEYS)} caption bilan yuboring."
            )
            return

        self.client.send_message(
            chat_id,
            "🎨 <b>Sticker file_id olindi.</b>\n\n"
            f"<code>{file_id}</code>\n\n"
            "Saqlash uchun stickerga caption yozing (masalan: <code>welcome</code>, "
            "<code>register</code>, <code>correct</code>, <code>wrong</code>, "
            "<code>rating</code>, <code>reply</code>) va qayta yuboring.\n\n"
            "Yoki .env fayliga yozing: <code>STICKER_WELCOME=&lt;file_id&gt;</code>"
        )

    def handle_leaderboard_command(self, chat_id):
        top = bot_db.get_leaderboard_top(limit=10)
        if not top:
            self.client.send_message(
                chat_id,
                "🏆 <b>REYTING</b>\n\nHozircha birorta ham natija yo\'q. "
                "Birinchi bo\'lib test yeching va 1-o\'rinni egallang! 👇",
                reply_markup=get_test_menu_keyboard()
            )
            return

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        lines = ["🏆 <b>JONLI MATEMATIKA REYTINGI — TOP 10</b>\n"]
        for row in top:
            rank = row["rank"]
            badge = medals.get(rank, f"{rank}.")
            name = html.escape(str(row.get("name") or "Ishtirokchi"), quote=False)
            lines.append(
                f"{badge} <b>{name}</b> — {row.get('points', 0)} ball "
                f"({row.get('correct_count', 0)}/{row.get('total_solved', 0)}, {row.get('accuracy', 0)}%) {row.get('title', '')}"
            )
        lines.append("\n<i>Ballar har bir to’g’ri javobdan keyin yangilanadi.</i>")

        self.client.send_message(chat_id, "\n".join(lines), reply_markup=get_leaderboard_keyboard())

    def handle_user_stat_command(self, user, chat_id):
        user_id = user["telegram_id"]
        full_name = html.escape(user.get("full_name") or user.get("first_name") or "Foydalanuvchi")
        user_rank = bot_db.get_user_leaderboard_rank(f"tg_{user_id}")

        if not user_rank or user_rank.get('total_solved', 0) == 0:
            text = (
                f"👤 <b>Foydalanuvchi:</b> {full_name}\n\n"
                f"ℹ️ Siz hali birorta ham savol yechmadingiz.\n\n"
                f"📝 <b>BOTDA TEST YECHISH</b> tugmasini bosing yoki Mini App’ga kiring — "
                f"har bir to’g’ri javobga 10–25 ball beriladi!"
            )
        else:
            text = (
                f"📊 <b>{full_name} — Shaxsiy Quiz Statistikasi</b>\n\n"
                f"🏆 <b>O'rningiz:</b> #{user_rank['rank']} ({user_rank['title']})\n"
                f"🎯 <b>Jami to'plangan ball:</b> {user_rank['points']} ball\n"
                f"✅ <b>To'g'ri javoblar:</b> {user_rank['correct_count']} ta\n"
                f"📝 <b>Jami yechilgan:</b> {user_rank['total_solved']} ta\n"
                f"📈 <b>Aniqlik darajasi:</b> {user_rank['accuracy']}%\n"
                f"🔥 <b>Maksimal streak:</b> {user_rank['best_streak']} ta ketma-ket\n"
            )

        kb = {
            "inline_keyboard": [
                [
                    {
                        "text": "🎯 Mini App",
                        "web_app": {"url": WEB_APP_URL}
                    },
                    {
                        "text": "📝 Test yechish",
                        "callback_data": "test_menu"
                    }
                ],
                [
                    {
                        "text": "🏆 Jonli Reyting TOP-10",
                        "callback_data": "show_rating"
                    }
                ],
                [
                    {
                        "text": "🏠 Bosh menyu",
                        "callback_data": "menu:main"
                    }
                ]
            ]
        }
        self.client.send_message(chat_id, text, reply_markup=kb)

    def handle_start_flow(self, user, chat_id, message_id):
        user_id = user["telegram_id"]
        is_registered = user.get("is_registered", 0)
        full_name = user.get("full_name")
        username = user.get("username", "")

        if is_registered and full_name:
            bot_db.set_user_state(user_id, "REGISTERED")
            bot_db.upsert_leaderboard_user(f"tg_{user_id}", full_name, username)
            self.client.send_message(
                chat_id,
                get_welcome_text(),
                reply_markup=get_main_menu_keyboard()
            )
            send_sticker_by_key(self.client, chat_id, "welcome")
        else:
            bot_db.set_user_state(user_id, "WAITING_FOR_NAME")
            ask_text = (
                "👋 <b>Keling, tanishamiz!</b>\n\n"
                "Ism va familiyangizni kiriting (reyting va natijalar shu ism bilan chiqadi):\n\n"
                "<i>Masalan: Ali Valiyev</i>\n\n"
                "<i>Bekor qilish: /start</i>"
            )
            self.client.send_message(chat_id, ask_text)

    def handle_name_input(self, user, message):
        chat_id = message["chat"]["id"]
        user_id = user["telegram_id"]
        username = user.get("username", "")
        message_id = message["message_id"]
        text = message.get("text", "")

        valid_name = validate_full_name(text)
        if not valid_name:
            error_text = (
                "⚠️ <b>Ism-familiya to’g’ri kiritilmadi.</b>\n\n"
                "Kamida ikki so’z bo’lishi kerak: <b>ism va familiya</b>\n\n"
                "<i>Masalan: Ali Valiyev yoki A Valiyev</i>\n\n"
                "<i>Raqam, havola yoki belgi yubormang. Bekor qilish: /start</i>"
            )
            self.client.send_message(chat_id, error_text)
            return

        try:
            self.client.set_message_reaction(chat_id, message_id, emoji="❤️")
        except Exception as e:
            logger.debug(f"Reaction qo'yishda ogohlantirish: {e}")

        bot_db.set_user_full_name(user_id, valid_name)
        bot_db.verify_user(user_id)
        bot_db.upsert_leaderboard_user(f"tg_{user_id}", valid_name, username)
        bot_db.log_action(user_id, "REGISTERED", f"Name: {valid_name}")

        self.notify_admin_new_user(user, valid_name)

        self.client.send_message(
            chat_id,
            get_welcome_text(),
            reply_markup=get_main_menu_keyboard()
        )
        send_sticker_by_key(self.client, chat_id, "register")

    def notify_admin_new_user(self, user, full_name):
        if not ADMIN_CHAT_ID:
            return

        user_id = user["telegram_id"]
        username_val = f"@{user['username']}" if user.get("username") else "Mavjud emas"
        first_name_val = html.escape(user.get("first_name") or "")
        last_name_val = html.escape(user.get("last_name") or "")
        joined_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        display_profile = f"{first_name_val} {last_name_val}".strip() or f"User {user_id}"
        profile_link = f'<a href="tg://user?id={user_id}">{display_profile}</a>'

        admin_card = (
            "👤 <b>YANGI FOYDALANUVCHI</b>\n\n"
            f"<b>Botdagi ism-familiya:</b>\n{html.escape(full_name, quote=False)}\n\n"
            f"<b>Telegram profili:</b>\n{username_val} ({profile_link})\n\n"
            f"<b>Telegram ID:</b>\n<code>{user_id}</code>\n\n"
            f"<b>Telegram first name:</b>\n{first_name_val or '—'}\n\n"
            f"<b>Telegram last name:</b>\n{last_name_val or '—'}\n\n"
            f"<b>Joined:</b>\n{joined_time}"
        )
        self.client.send_message(ADMIN_CHAT_ID, admin_card)

    def handle_user_message_to_admin(self, user, message):
        user_id = user["telegram_id"]
        chat_id = message["chat"]["id"]
        message_id = message["message_id"]
        text_content = message.get("text", "")
        caption_content = message.get("caption", "")

        user_name = user.get("full_name") or user.get("first_name") or f"User {user_id}"
        username_str = f"@{user['username']}" if user.get("username") else "Username mavjud emas"
        profile_link = f'<a href="tg://user?id={user_id}">{html.escape(user_name, quote=False)}</a>'

        if not ADMIN_CHAT_ID:
            logger.warning("ADMIN_CHAT_ID sozlanmagan — xabar adminga yuborilmadi.")
            self.client.send_message(
                chat_id,
                "⚠️ <i>Afsuski, hozirda Jo’rabekga xabar yuborish vaqtinchalik mavjud emas.</i>\n\n"
                "👇 <b>Bosh menyuga qayting:</b>",
                reply_markup=get_main_menu_keyboard()
            )
            return

        admin_header = (
            "📩 <b>YANGI XABAR</b>\n\n"
            f"👤 <b>User:</b> {html.escape(user_name, quote=False)} ({profile_link})\n"
            f"📱 <b>Telegram:</b> {username_str}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        )

        admin_msg_res = None
        if text_content:
            full_admin_text = f"{admin_header}\n💬 <b>Xabar:</b>\n{html.escape(text_content, quote=False)}"
            admin_msg_res = self.client.send_message(ADMIN_CHAT_ID, full_admin_text)
            snippet = text_content[:100]
        else:
            caption = f"{admin_header}\n💬 <b>Izoh:</b>\n{html.escape(caption_content, quote=False)}" if caption_content else admin_header
            admin_msg_res = self.client.copy_message(
                ADMIN_CHAT_ID,
                chat_id,
                message_id,
                caption=caption
            )
            snippet = f"[Media: {caption_content[:50]}]"

        if admin_msg_res and "message_id" in admin_msg_res:
            admin_message_id = admin_msg_res["message_id"]
            bot_db.save_message_mapping(admin_message_id, user_id, message_id, snippet)
            self.client.send_message(
                chat_id,
                "✅ <i>Xabaringiz Jo’rabekka yetkazildi. Tez orada javob olasiz!</i>"
            )
        else:
            logger.error(f"Xabar adminga yetkazilmadi (user={user_id})")
            self.client.send_message(
                chat_id,
                "⚠️ <i>Afsuski, xabaringiz yetib bormadi. Birozdan so’ng qayta urinib ko’ring.</i>"
            )
        bot_db.set_user_state(user_id, "REGISTERED")

    def handle_admin_reply(self, message):
        reply_to = message.get("reply_to_message", {})
        replied_msg_id = reply_to.get("message_id")
        admin_text = message.get("text", "")
        caption_text = message.get("caption", "")

        mapping = bot_db.get_mapping_by_admin_message(replied_msg_id)
        if not mapping:
            self.client.send_message(
                ADMIN_CHAT_ID,
                "⚠️ <i>Ushbu xabar bo'yicha foydalanuvchi topilmadi yoki xabar muddati eskirgan.</i>",
                reply_to_message_id=message.get("message_id")
            )
            return

        target_user_id = mapping["user_telegram_id"]

        reply_header = "✍️ <b>Jo’rabekdan javob:</b>\n\n"
        res = None
        if admin_text:
            user_msg = f"{reply_header}{html.escape(admin_text, quote=False)}"
            res = self.client.send_message(target_user_id, user_msg)
        else:
            caption = f"{reply_header}{html.escape(caption_text, quote=False)}" if caption_text else reply_header
            res = self.client.copy_message(target_user_id, ADMIN_CHAT_ID, message["message_id"], caption=caption)

        if res:
            send_sticker_by_key(self.client, target_user_id, "reply")
            self.client.send_message(
                ADMIN_CHAT_ID,
                f"✅ <i>Javobingiz foydalanuvchiga (ID: <code>{target_user_id}</code>) muvaffaqiyatli yuborildi!</i>",
                reply_to_message_id=message.get("message_id")
            )
        else:
            self.client.send_message(
                ADMIN_CHAT_ID,
                f"❌ <i>Foydalanuvchiga javob yuborishda xatolik yuz berdi (Bot bloklangan bo'lishi mumkin).</i>",
                reply_to_message_id=message.get("message_id")
            )

    def handle_admin_commands(self, message):
        text = message.get("text", "").strip()
        chat_id = message["chat"]["id"]

        if text == "/start":
            timeout = bot_db.get_setting("captcha_timeout", "60")
            welcome_admin = (
                "👑 <b>Assalomu alaykum, Jo’rabek!</b>\n\n"
                "Siz botning boshqaruv panelidasiz.\n\n"
                "<b>Mavjud buyruqlar:</b>\n"
                "📊 /stats — Bot va guruhlar statistikasi\n"
                "👥 /users — Oxirgi foydalanuvchilar\n"
                "🛡 /groups — Ulangan guruhlar ro'yxati\n"
                f"⏱ /set_timeout [soniya] — Guruhda tekshirish vaqtini belgilash (Hozir: {timeout}s)\n"
                "📢 /broadcast [matn] — Barcha userlar va guruhlarga xabar tarqatish\n\n"
                "<i>Foydalanuvchilar yozgan xabarlarga Telegram 'Reply' orqali bevosita javob bera olasiz.</i>"
            )
            self.client.send_message(chat_id, welcome_admin)
            return True

        elif text == "/stats":
            stats = bot_db.get_stats()
            timeout = bot_db.get_setting("captcha_timeout", "60")
            stats_text = (
                "📊 <b>BOT VA GURUHLAR STATISTIKASI</b>\n\n"
                f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']}\n"
                f"✅ <b>Ro'yxatdan o'tganlar:</b> {stats['registered_users']}\n"
                f"🛡 <b>Ulangan guruhlar:</b> {stats['total_groups']}\n"
                f"👤 <b>Tasdiqlangan odamlar (Anti-bot):</b> {stats['verified_humans']}\n"
                f"🔥 <b>Oxirgi 24 soatda faol:</b> {stats['active_24h']}\n"
                f"💬 <b>Yetkazilgan xabarlar:</b> {stats['total_messages']}\n"
                f"⏱ <b>O'chirish vaqti:</b> {timeout} soniya"
            )
            self.client.send_message(chat_id, stats_text)
            return True

        elif text.startswith("/set_timeout"):
            parts = text.split()
            if len(parts) < 2 or not parts[1].isdigit():
                cur = bot_db.get_setting("captcha_timeout", "60")
                self.client.send_message(
                    chat_id,
                    f"ℹ️ Hozirgi tekshirish vaqti: <b>{cur} soniya</b>.\n\nO'zgartirish uchun: <code>/set_timeout 60</code> (10 dan 300 gacha soniya kiriting)."
                )
                return True
            new_val = int(parts[1])
            if new_val < 5 or new_val > 600:
                self.client.send_message(chat_id, "⚠️ Iltimos, 5 dan 600 gacha bo'lgan soniya kiriting.")
                return True
            bot_db.set_setting("captcha_timeout", str(new_val))
            self.client.send_message(chat_id, f"✅ <b>Guruhdagi tekshirish vaqti {new_val} soniyaga o'rnatildi!</b>")
            return True

        elif text == "/groups":
            groups = bot_db.get_all_active_groups()
            if not groups:
                self.client.send_message(chat_id, "ℹ️ Hozircha ulangan guruhlar mavjud emas.")
                return True
            lines = ["🛡 <b>ULANGAN GURUHLAR RO'YXATI:</b>\n"]
            for idx, g in enumerate(groups, 1):
                uname = f"(@{g['username']})" if g.get('username') else ""
                lines.append(f"{idx}. <b>{html.escape(g['title'] or 'Group', quote=False)}</b> {uname} (ID: <code>{g['group_id']}</code>)")
            self.client.send_message(chat_id, "\n".join(lines))
            return True

        elif text == "/users":
            users = bot_db.get_recent_users(10)
            if not users:
                self.client.send_message(chat_id, "ℹ️ Foydalanuvchilar mavjud emas.")
                return True
            
            lines = ["👥 <b>OXIRGI 10 TA FOYDALANUVCHI:</b>\n"]
            for idx, u in enumerate(users, 1):
                name = html.escape(u.get("full_name") or u.get("first_name") or "User", quote=False)
                uid = u["telegram_id"]
                reg = "✅" if u.get("is_registered") else "⏳"
                lines.append(f"{idx}. {reg} <a href=\"tg://user?id={uid}\">{name}</a> (<code>{uid}</code>) — {u['created_at'][:16]}")
            
            self.client.send_message(chat_id, "\n".join(lines))
            return True

        elif text.startswith("/broadcast"):
            parts = text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                self.client.send_message(
                    chat_id,
                    "⚠️ <i>Xabar matnini kiriting. Masalan:</i>\n<code>/broadcast Yangi maqolamiz chiqdi!</code>"
                )
                return True

            broadcast_text = parts[1].strip()
            all_ids = bot_db.get_all_registered_user_ids()
            all_groups = bot_db.get_all_active_groups()

            self.client.send_message(
                chat_id,
                f"📢 <i>{len(all_ids)} ta foydalanuvchi va {len(all_groups)} ta guruhga xabar yuborish boshlandi...</i>"
            )

            sent_users = 0
            sent_groups = 0
            fail_count = 0

            for uid in all_ids:
                try:
                    res = self.client.send_message(uid, broadcast_text)
                    if res:
                        sent_users += 1
                    else:
                        fail_count += 1
                    time.sleep(0.04)
                except Exception:
                    fail_count += 1

            for g in all_groups:
                try:
                    gid = g["group_id"]
                    res = self.client.send_message(gid, broadcast_text)
                    if res:
                        sent_groups += 1
                    else:
                        fail_count += 1
                    time.sleep(0.05)
                except Exception:
                    fail_count += 1

            self.client.send_message(
                chat_id,
                f"✅ <b>Tarqatish yakunlandi!</b>\n\n"
                f"👤 Foydalanuvchilarga yetkazildi: <b>{sent_users}</b> ta\n"
                f"🛡 Guruhlarga yetkazildi: <b>{sent_groups}</b> ta\n"
                f"❌ Yetib bormadi (bloklangan/chiqarilgan): <b>{fail_count}</b> ta"
            )
            return True

        return False

    def setup_commands_menu(self):
        commands = [
            {"command": "start", "description": "🏠 Bosh sahifa / Menyu"},
            {"command": "test", "description": "📝 Botda test yechish"},
            {"command": "reyting", "description": "🏆 Jonli quiz reytingi (Top 10)"},
            {"command": "stat", "description": "📊 Mening natijalarim va ballarim"},
            {"command": "app", "description": "🎯 Matematika Quiz Hub (Mini App)"},
            {"command": "help", "description": "ℹ️ Bot haqida va yordam"}
        ]
        self.client.set_my_commands(commands)

    def run_polling(self):
        logger.info(f"🤖 Main Bot Long Polling rejimida ishga tushmoqda...")
        if not self.client.token:
            logger.error("❌ BOT_TOKEN topilmadi! Iltimos, .env ni tekshiring.")
            return

        bot_info = self.client.get_me()
        if not bot_info:
            logger.error("❌ Main Bot Telegram API bilan ulanish o'rnatilmadi.")
            return

        logger.info(f"✅ Main Bot muvaffaqiyatli ulandi: @{bot_info.get('username')} ({bot_info.get('first_name')})")
        self.setup_commands_menu()

        offset = None
        while self._running:
            try:
                updates = self.client.get_updates(offset=offset, timeout=25)
                if updates:
                    for update in updates:
                        offset = update["update_id"] + 1
                        self.handle_update(update)
            except KeyboardInterrupt:
                self._running = False
                break
            except Exception as e:
                logger.error(f"Main Bot Polling xatosi: {e}")
                time.sleep(3)


# --- DEDICATED GUARD BOT ENGINE (@Botlarni_tekshiruvchi_Bot) ---
class GuardBotEngine:
    def __init__(self, client=None):
        self.client = client or TelegramClient(GUARD_BOT_TOKEN, GUARD_BOT_USERNAME)
        self._running = True
        self.bot_username = GUARD_BOT_USERNAME
        ExpirationCoordinator.get().register_client(self.client)

    def stop(self):
        self._running = False

    def handle_update(self, update):
        try:
            if "message" in update:
                self.process_message(update["message"])
            elif "callback_query" in update:
                self.process_callback_query(update["callback_query"])
            elif "my_chat_member" in update:
                self.process_my_chat_member(update["my_chat_member"])
        except Exception as e:
            logger.error(f"Guard Bot update xatosi: {e}", exc_info=True)

    def process_my_chat_member(self, mcm):
        chat = mcm.get("chat", {})
        chat_id = chat.get("id")
        chat_title = chat.get("title", "")
        chat_username = chat.get("username")
        new_status = mcm.get("new_chat_member", {}).get("status")

        if chat_id and chat.get("type") in ["group", "supergroup"]:
            is_active = 1 if new_status in ["administrator", "member"] else 0
            bot_db.upsert_group(chat_id, chat_title, chat_username, is_active=is_active)
            logger.info(f"Guard Bot guruh statusi: {chat_title} ({chat_id}) -> {new_status}")

    def process_callback_query(self, cq):
        cq_id = cq.get("id")
        user_data = cq.get("from", {})
        user_id = user_data.get("id")
        data = cq.get("data", "")
        message = cq.get("message", {})
        bot_msg_id = message.get("message_id")

        if not user_id:
            return

        if data == "guard_info":
            timeout = bot_db.get_setting("captcha_timeout", "60")
            self.client.answer_callback_query(
                cq_id,
                text=f"⏱ Hozirgi tekshirish vaqti: {timeout} soniya\n(O'zgartirish faqat admin uchun: /set_timeout)",
                show_alert=True
            )
            return

        if data.startswith("verify_human:"):
            parts = data.split(":")
            if len(parts) >= 4:
                target_user_id = int(parts[1])
                user_msg_id = int(parts[2])
                group_id = int(parts[3])

                if user_id != target_user_id:
                    self.client.answer_callback_query(cq_id, text="⚠️ Bu tugma siz uchun emas!", show_alert=True)
                    return

                bot_db.verify_user(user_id)
                self.client.answer_callback_query(cq_id, text="✅ Rahmat! Siz bot emasligingiz tasdiqlandi.")

                try:
                    self.client.delete_message(group_id, bot_msg_id)
                except Exception as e:
                    logger.debug(f"Guard prompt delete xatosi: {e}")

                bot_db.resolve_pending_verification(group_id, user_id)
                return

    def process_message(self, message):
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type", "private")
        from_user = message.get("from", {})
        user_id = from_user.get("id")
        message_id = message.get("message_id")
        text = message.get("text", "")

        if not chat_id:
            return

        # GROUP MESSAGE HANDLING
        if chat_type in ["group", "supergroup"]:
            chat_title = chat.get("title", "Group")
            chat_username = chat.get("username")
            bot_db.upsert_group(chat_id, chat_title, chat_username, is_active=1)

            if not user_id or from_user.get("is_bot") or message.get("sender_chat"):
                return

            if bot_db.is_user_verified(user_id):
                return

            timeout_sec = int(bot_db.get_setting("captcha_timeout", "60"))
            user_name = html.escape(from_user.get("first_name") or "Foydalanuvchi", quote=False)

            warning_text = (
                f"⚠️ <a href=\"tg://user?id={user_id}\">{user_name}</a>, guruhda spam va 18+ reklamalarni oldini olish uchun "
                f"pastdagi tugmani bosib <b>bot emasligingizni tasdiqlang</b>, aks holda xabaringiz <b>{timeout_sec} soniyada</b> o'chiriladi!"
            )
            captcha_kb = {
                "inline_keyboard": [
                    [
                        {
                            "text": "✅ Men bot emasman",
                            "callback_data": f"verify_human:{user_id}:{message_id}:{chat_id}"
                        }
                    ]
                ]
            }

            prompt_res = self.client.send_message(
                chat_id,
                warning_text,
                reply_markup=captcha_kb,
                reply_to_message_id=message_id
            )

            if prompt_res and "message_id" in prompt_res:
                bot_prompt_id = prompt_res["message_id"]
                expires_at = time.time() + timeout_sec
                bot_db.add_pending_verification(chat_id, user_id, message_id, bot_prompt_id, expires_at)
                schedule_message_deletion(self.client, chat_id, user_id, message_id, bot_prompt_id, timeout_sec)
            return

        # PRIVATE CHAT HANDLING
        if not user_id:
            return

        timeout = bot_db.get_setting("captcha_timeout", "60")
        bot_uname = self.client.ensure_username()
        user_name = html.escape(from_user.get("first_name") or "Foydalanuvchi", quote=False)

        # ADMIN PANEL COMMANDS
        if ADMIN_CHAT_ID and chat_id == ADMIN_CHAT_ID and text.startswith("/"):
            if text == "/start":
                admin_panel_text = (
                    "👑 <b>Assalomu alaykum, Jo’rabek!</b>\n\n"
                    "Siz <b>\"Tekshiruvchi\" (@Botlarni_tekshiruvchi_Bot)</b> botining boshqaruv panelidasiz.\n\n"
                    "<b>Mavjud buyruqlar:</b>\n"
                    "📊 /stats — Guruhlar va anti-bot statistikasi\n"
                    "🛡 /groups — Ulangan guruhlar ro'yxati\n"
                    f"⏱ /set_timeout [soniya] — O'chirish vaqtini sozlash (Hozir: {timeout}s)\n"
                    "📢 /broadcast [matn] — Barcha ulangan guruhlarga xabar yuborish"
                )
                self.client.send_message(chat_id, admin_panel_text)
                return

            elif text == "/stats":
                stats = bot_db.get_stats()
                stats_text = (
                    "📊 <b>\"TEKSHIRUVCHI\" BOT STATISTIKASI</b>\n\n"
                    f"🛡 <b>Ulangan guruhlar:</b> {stats['total_groups']} ta\n"
                    f"👤 <b>Tasdiqlangan odamlar (Anti-bot):</b> {stats['verified_humans']} ta\n"
                    f"⏱ <b>O'chirish vaqti:</b> {timeout} soniya"
                )
                self.client.send_message(chat_id, stats_text)
                return

            elif text == "/groups":
                groups = bot_db.get_all_active_groups()
                if not groups:
                    self.client.send_message(chat_id, "ℹ️ Hozircha ulangan guruhlar mavjud emas.")
                    return
                lines = ["🛡 <b>ULANGAN GURUHLAR RO'YXATI:</b>\n"]
                for idx, g in enumerate(groups, 1):
                    uname = f"(@{g['username']})" if g.get('username') else ""
                    lines.append(f"{idx}. <b>{html.escape(g['title'] or 'Group', quote=False)}</b> {uname} (ID: <code>{g['group_id']}</code>)")
                self.client.send_message(chat_id, "\n".join(lines))
                return

            elif text.startswith("/set_timeout"):
                parts = text.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    new_val = int(parts[1])
                    if 5 <= new_val <= 600:
                        bot_db.set_setting("captcha_timeout", str(new_val))
                        self.client.send_message(chat_id, f"✅ <b>Guruhdagi tekshirish vaqti {new_val} soniyaga o'rnatildi!</b>")
                        return
                self.client.send_message(chat_id, f"ℹ️ Hozirgi tekshirish vaqti: <b>{timeout} soniya</b>.\n\nO'zgartirish uchun: <code>/set_timeout 60</code>")
                return

            elif text.startswith("/broadcast"):
                parts = text.split(maxsplit=1)
                if len(parts) < 2 or not parts[1].strip():
                    self.client.send_message(chat_id, "⚠️ <i>Xabar matnini kiriting. Masalan:</i>\n<code>/broadcast Guruhlar uchun e'lon!</code>")
                    return
                bcast_msg = parts[1].strip()
                all_groups = bot_db.get_all_active_groups()
                self.client.send_message(chat_id, f"📢 <i>{len(all_groups)} ta guruhga xabar yuborish boshlandi...</i>")
                sent = 0
                failed = 0
                for g in all_groups:
                    try:
                        res = self.client.send_message(g["group_id"], bcast_msg)
                        if res:
                            sent += 1
                        else:
                            failed += 1
                        time.sleep(0.05)
                    except Exception:
                        failed += 1
                self.client.send_message(chat_id, f"✅ <b>Guruhlarga tarqatish yakunlandi!</b>\n\nYuborildi: <b>{sent}</b> ta\nYetib bormadi: <b>{failed}</b> ta")
                return

        # REGULAR USER WELCOME MESSAGE (faqat /start, /help yoki birinchi tanishuvda)
        normalized = text.strip().lower()
        if normalized.startswith("/") and normalized not in ("/start", "/help", "/yordam", "/start "):
            self.client.send_message(
                chat_id,
                "ℹ️ <b>Buyruq topilmadi.</b>\n\nMavjud: <code>/start</code> — botni guruhga qo'shish bo'yicha yo'riqnoma"
            )
            return

        if normalized not in ("/start", "/help", "/yordam", ""):
            self.client.send_message(
                chat_id,
                "🛡 <i>Men guruhlar uchun himoya botman. Buyruqlar ro'yxati uchun</i> <code>/start</code> <i>ni yuboring.</i>"
            )
            return

        welcome_guard = (
            f"🛡 <b>Assalomu alaykum, {user_name}!</b>\n\n"
            "Men <b>\"Tekshiruvchi\"</b> — guruhlarni 18+ reklamalar, spam va keraksiz botlardan tozalovchi botman.\n\n"
            "Meni guruhingizga qo'shib, <b>admin</b> huquqini bersangiz:\n"
            "• Guruhga yozgan har bir yangi a'zodan bot emasligini tasdiqlash so'raladi.\n"
            f"• Agar <b>{timeout} soniya</b> ichida tasdiqlamasa, uning xabari avtomatik o'chiriladi!\n"
            "• Bir marta tasdiqlagan odam qayta bezovta qilinmaydi.\n\n"
            "👇 Pastdagi tugma orqali meni guruhingizga qo'shing:"
        )

        kb = {
            "inline_keyboard": [
                [
                    {
                        "text": "➕ Guruhga admin sifatida qo'shish",
                        "url": f"https://t.me/{bot_uname}?startgroup=true&admin=delete_messages+restrict_members"
                    }
                ],
                [
                    {
                        "text": "⏱ Tekshirish vaqtini sozlash",
                        "callback_data": "guard_info"
                    }
                ]
            ]
        }
        self.client.send_message(chat_id, welcome_guard, reply_markup=kb)
        send_sticker_by_key(self.client, chat_id, "welcome")

    def run_polling(self):
        if not self.client.token:
            return
        bot_info = self.client.get_me()
        if not bot_info:
            logger.error("❌ Guard Bot Telegram API bilan ulanish o'rnatilmadi.")
            return

        logger.info(f"✅ Guard Bot muvaffaqiyatli ulandi: @{bot_info.get('username')} ({bot_info.get('first_name')})")

        offset = None
        while self._running:
            try:
                updates = self.client.get_updates(offset=offset, timeout=25)
                if updates:
                    for update in updates:
                        offset = update["update_id"] + 1
                        self.handle_update(update)
            except KeyboardInterrupt:
                self._running = False
                break
            except Exception as e:
                logger.error(f"Guard Bot Polling xatosi: {e}")
                time.sleep(3)


# --- MULTI-BOT RUNNER ---
_shared_engine = None
_shared_engine_lock = threading.Lock()


def get_shared_engine():
    """Webhook uchun bitta engine (har so'rovda yangi thread ochilmaydi)."""
    global _shared_engine
    with _shared_engine_lock:
        if _shared_engine is None:
            _shared_engine = BotEngine(TelegramClient(BOT_TOKEN, MAIN_BOT_USERNAME))
        return _shared_engine


def run_all_bots():
    threads = []

    # 0. Bitta umumiy captcha tozalovchisi
    ExpirationCoordinator.get().start()

    # 1. Start Main Bot
    if BOT_TOKEN:
        main_bot = BotEngine(TelegramClient(BOT_TOKEN, MAIN_BOT_USERNAME))
        t1 = threading.Thread(target=main_bot.run_polling, daemon=True, name="MainTelegramBot")
        t1.start()
        threads.append(t1)

    # 2. Start Guard Bot
    if GUARD_BOT_TOKEN:
        guard_bot = GuardBotEngine(TelegramClient(GUARD_BOT_TOKEN, GUARD_BOT_USERNAME))
        t2 = threading.Thread(target=guard_bot.run_polling, daemon=True, name="GuardTelegramBot")
        t2.start()
        threads.append(t2)

    logger.info(f"🚀 {len(threads)} ta Telegram Bot parallel ishga tushirildi.")
    return threads


if __name__ == "__main__":
    threads = run_all_bots()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ExpirationCoordinator.get().stop()
        logger.info("🛑 Barcha botlar to'xtatildi.")

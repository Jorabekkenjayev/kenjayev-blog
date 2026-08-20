import os
import sys
import json
import time
import re
import html
import logging
import urllib.request
import urllib.parse
import urllib.error
import threading
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

WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://kenjayev.uz").strip()
if not WEB_APP_URL.startswith("http"):
    WEB_APP_URL = "https://" + WEB_APP_URL

# In-memory Rate Limiter: { user_id: [timestamp1, timestamp2, ...] }
_rate_limits = {}
_rate_lock = threading.Lock()
RATE_LIMIT_WINDOW = 10.0  # seconds
RATE_LIMIT_MAX_COUNT = 5   # max messages per window


# --- TELEGRAM BOT API CLIENT ---
class TelegramClient:
    def __init__(self, token=None):
        self.token = token or BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.bot_username = "KenjayevBlogBot"

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
        return res

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
        if len(w) < 2:
            return None
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


# --- UI BUILDERS ---
def get_main_menu_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "🌐 Saytga kirish",
                    "web_app": {"url": WEB_APP_URL}
                }
            ],
            [
                {
                    "text": "🔞 18+ reklamani o'chirish",
                    "callback_data": "anti_spam_info"
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


def get_welcome_text():
    return (
        "<b>Kenjayev Jo’rabek botiga xush kelibsiz!</b>\n\n"
        "Kenjayev Jo’rabek bu yerda o’z blogini yuritadi."
    )


# --- MAIN BOT ENGINE (Kenjayev Jo'rabek Bot) ---
class BotEngine:
    def __init__(self, client=None):
        self.client = client or TelegramClient(BOT_TOKEN)
        self._expiration_thread = None
        self._running = True
        self.start_expiration_worker()

    def start_expiration_worker(self):
        if self._expiration_thread and self._expiration_thread.is_alive():
            return

        def worker():
            while self._running:
                try:
                    now_ts = time.time()
                    expired_items = bot_db.get_expired_verifications(now_ts)
                    for item in expired_items:
                        v_id = item["id"]
                        group_id = item["group_id"]
                        user_msg_id = item["user_message_id"]
                        bot_msg_id = item["bot_message_id"]

                        try:
                            self.client.delete_message(group_id, user_msg_id)
                        except Exception as e:
                            logger.debug(f"User message delete xatosi: {e}")

                        try:
                            self.client.delete_message(group_id, bot_msg_id)
                        except Exception as e:
                            logger.debug(f"Bot warning delete xatosi: {e}")

                        bot_db.mark_verification_expired(v_id)
                except Exception as e:
                    logger.debug(f"Expiration worker xatosi: {e}")
                time.sleep(2)

        self._expiration_thread = threading.Thread(target=worker, daemon=True, name="CaptchaExpirationWorker")
        self._expiration_thread.start()

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
            bot_uname = self.client.bot_username or "KenjayevJorabekBot"
            
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

        # 3. Jo'rabekka yozish button handler
        if data == "write_to_admin":
            bot_db.set_user_state(user_id, "WRITING_TO_ADMIN")
            self.client.answer_callback_query(cq_id)
            prompt_text = (
                "✍️ <b>Jo’rabekka xabaringizni yozing.</b>\n\n"
                "Xabaringiz to’g’ridan-to’g’ri unga yuboriladi."
            )
            self.client.send_message(chat_id, prompt_text)
            return

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

        user, is_new = bot_db.upsert_user(user_id, username, first_name, last_name)
        bot_db.touch_user_activity(user_id)

        # /START COMMAND FLOW
        if text.strip() == "/start":
            self.handle_start_flow(user, chat_id, message_id)
            return

        user_state = user.get("state", "NEW_USER")
        is_registered = user.get("is_registered", 0)

        if user_state == "WAITING_FOR_NAME" or not is_registered:
            self.handle_name_input(user, message)
            return

        self.handle_user_message_to_admin(user, message)

    def handle_start_flow(self, user, chat_id, message_id):
        user_id = user["telegram_id"]
        is_registered = user.get("is_registered", 0)
        full_name = user.get("full_name")

        if is_registered and full_name:
            bot_db.set_user_state(user_id, "REGISTERED")
            self.client.send_message(
                chat_id,
                get_welcome_text(),
                reply_markup=get_main_menu_keyboard()
            )
        else:
            bot_db.set_user_state(user_id, "WAITING_FOR_NAME")
            ask_text = (
                "Ism va familiyangizni kiriting:\n\n"
                "<i>Masalan: Ali Valiyev</i>"
            )
            self.client.send_message(chat_id, ask_text)

    def handle_name_input(self, user, message):
        chat_id = message["chat"]["id"]
        user_id = user["telegram_id"]
        message_id = message["message_id"]
        text = message.get("text", "")

        valid_name = validate_full_name(text)
        if not valid_name:
            error_text = (
                "Iltimos, ism va familiyangizni to’liq kiriting.\n\n"
                "<i>Masalan: Ali Valiyev</i>"
            )
            self.client.send_message(chat_id, error_text)
            return

        try:
            self.client.set_message_reaction(chat_id, message_id, emoji="❤️")
        except Exception as e:
            logger.debug(f"Reaction qo'yishda ogohlantirish: {e}")

        bot_db.set_user_full_name(user_id, valid_name)
        bot_db.verify_user(user_id)
        bot_db.log_action(user_id, "REGISTERED", f"Name: {valid_name}")

        self.notify_admin_new_user(user, valid_name)

        self.client.send_message(
            chat_id,
            get_welcome_text(),
            reply_markup=get_main_menu_keyboard()
        )

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
            self.client.send_message(
                chat_id,
                "✅ <i>Xabaringiz qabul qilindi. Tez orada javob beriladi!</i>"
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
            {"command": "start", "description": "Bosh sahifa / Menyu"}
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
        self.client = client or TelegramClient(GUARD_BOT_TOKEN)
        self._running = True
        self.bot_username = "Botlarni_tekshiruvchi_Bot"

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
            return

        # PRIVATE CHAT HANDLING
        if not user_id:
            return

        timeout = bot_db.get_setting("captcha_timeout", "60")
        bot_uname = self.client.bot_username or "Botlarni_tekshiruvchi_Bot"
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

        # REGULAR USER WELCOME MESSAGE
        welcome_guard = (
            f"🛡 <b>Assalomu alaykum, {user_name}!</b>\n\n"
            "<b>Kenjayev BLOG — \"Tekshiruvchi\"</b> botiga xush kelibsiz!\n\n"
            "Men guruhlarni 18+ reklamalar, spam va keraksiz botlardan tozalovchi rasmiy botman.\n\n"
            "Meni guruhingizga qo'shib, <b>admin</b> huquqini bersangiz:\n"
            "• Guruhga yozgan har bir yangi a'zodan bot emasligini tasdiqlash so'raladi.\n"
            f"• Agar <b>{timeout} soniya</b> ichida tasdiqlamasa, uning xabari avtomatik o'chiriladi!\n"
            "• Bir marta tasdiqlagan odam qayta bezovta qilinmaydi.\n\n"
            "Shuningdek, pastdagi tugma orqali <b>Kenjayev BLOG</b> saytiga kirishingiz mumkin:"
        )

        kb = {
            "inline_keyboard": [
                [
                    {
                        "text": "🌐 Kenjayev BLOG (Saytga kirish)",
                        "web_app": {"url": WEB_APP_URL}
                    }
                ],
                [
                    {
                        "text": "➕ Guruhga admin sifatida qo'shish",
                        "url": f"https://t.me/{bot_uname}?startgroup=true&admin=delete_messages+restrict_members"
                    }
                ]
            ]
        }
        self.client.send_message(chat_id, welcome_guard, reply_markup=kb)

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
def run_all_bots():
    threads = []
    
    # 1. Start Main Bot
    if BOT_TOKEN:
        main_bot = BotEngine(TelegramClient(BOT_TOKEN))
        t1 = threading.Thread(target=main_bot.run_polling, daemon=True, name="MainTelegramBot")
        t1.start()
        threads.append(t1)

    # 2. Start Guard Bot
    if GUARD_BOT_TOKEN:
        guard_bot = GuardBotEngine(TelegramClient(GUARD_BOT_TOKEN))
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
        logger.info("🛑 Barcha botlar to'xtatildi.")

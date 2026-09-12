import os
import sys
import unittest
import tempfile
import shutil
import json
import time

import bot_db
import bot

class MockTelegramClient:
    def __init__(self):
        self.sent_messages = []
        self.deleted_messages = []
        self.sent_reactions = []
        self.sent_copies = []
        self.answered_callbacks = []
        self.my_commands = []
        self.token = "mock_test_token"
        self.bot_username = "KenjayevBlogBot"

    def get_me(self):
        return {"id": 999999, "is_bot": True, "first_name": "Kenjayev Bot", "username": "KenjayevBlogBot"}

    def set_my_commands(self, commands):
        self.my_commands = commands
        return True

    def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML", reply_to_message_id=None, disable_web_page_preview=True):
        msg_id = len(self.sent_messages) + 1000
        msg_obj = {
            "message_id": msg_id,
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
            "parse_mode": parse_mode,
            "reply_to_message_id": reply_to_message_id
        }
        self.sent_messages.append(msg_obj)
        return msg_obj

    def delete_message(self, chat_id, message_id):
        del_obj = {"chat_id": chat_id, "message_id": message_id}
        self.deleted_messages.append(del_obj)
        return True

    def set_message_reaction(self, chat_id, message_id, emoji="❤️"):
        react_obj = {"chat_id": chat_id, "message_id": message_id, "emoji": emoji}
        self.sent_reactions.append(react_obj)
        return True

    def copy_message(self, chat_id, from_chat_id, message_id, caption=None, parse_mode="HTML", reply_markup=None):
        msg_id = len(self.sent_copies) + 2000
        copy_obj = {
            "message_id": msg_id,
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "original_message_id": message_id,
            "caption": caption
        }
        self.sent_copies.append(copy_obj)
        return copy_obj

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False):
        self.answered_callbacks.append({"id": callback_query_id, "text": text, "show_alert": show_alert})
        return True


class TestKenjayevTelegramBot(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_bot.db")
        self.orig_data_json = bot_db.DATA_JSON_FILE
        self.test_data_json = os.path.join(self.temp_dir, "test_data.json")
        with open(self.test_data_json, 'w') as f:
            json.dump({}, f)
        bot_db.DATA_JSON_FILE = self.test_data_json
        bot_db.init_db(self.db_path)
        bot_db.DB_FILE = self.db_path

        # Setup Mock Bot
        self.mock_client = MockTelegramClient()
        self.bot_engine = bot.BotEngine(self.mock_client)

        # Configure Bot Admin ID
        bot.ADMIN_CHAT_ID = 987654321
        bot.WEB_APP_URL = "https://kenjayev.uz"
        bot._rate_limits.clear()

    def tearDown(self):
        bot_db.DATA_JSON_FILE = self.orig_data_json
        self.bot_engine._running = False
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_name_validation(self):
        self.assertEqual(bot.validate_full_name("Ali Valiyev"), "Ali Valiyev")
        self.assertEqual(bot.validate_full_name("jo'rabek kenjayev"), "Jo'rabek Kenjayev")
        self.assertEqual(bot.validate_full_name("G'ayrat O'ktamov"), "G'ayrat O'ktamov")
        self.assertEqual(bot.validate_full_name("Otabek Sultonov"), "Otabek Sultonov")
        self.assertEqual(bot.validate_full_name("Shaxzoda Raximova"), "Shaxzoda Raximova")

        self.assertIsNone(bot.validate_full_name("Ali"))
        self.assertIsNone(bot.validate_full_name(""))
        self.assertIsNone(bot.validate_full_name("Ali 12345"))
        self.assertIsNone(bot.validate_full_name("Spam http://site.com"))

    def test_onboarding_and_anti_spam_buttons(self):
        user_id = 12345
        chat_id = 12345

        # 1. /start
        self.bot_engine.handle_update({
            "update_id": 1,
            "message": {
                "message_id": 101,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id, "username": "alivaliyev", "first_name": "Ali", "last_name": "Valiyev"},
                "text": "/start"
            }
        })
        self.assertIn("Ism va familiyangizni kiriting", self.mock_client.sent_messages[0]["text"])

        # 2. Valid name
        self.bot_engine.handle_update({
            "update_id": 2,
            "message": {
                "message_id": 102,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id, "username": "alivaliyev", "first_name": "Ali", "last_name": "Valiyev"},
                "text": "Ali Valiyev"
            }
        })

        welcome_msg = [m for m in self.mock_client.sent_messages if m["chat_id"] == chat_id and "Kenjayev Jo’rabek botiga xush kelibsiz" in m["text"]][0]
        buttons = welcome_msg["reply_markup"]["inline_keyboard"]
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons[0][0]["text"], "🌐 Saytga kirish")
        self.assertEqual(buttons[1][0]["text"], "💬 Jo’rabekka yozish")
        self.assertEqual(buttons[1][0]["callback_data"], "write_to_admin")

        # 3. User clicks "💬 Jo’rabekka yozish"
        self.bot_engine.handle_update({
            "update_id": 3,
            "callback_query": {
                "id": "cq_write",
                "from": {"id": user_id},
                "data": "write_to_admin",
                "message": {"chat": {"id": chat_id}, "message_id": welcome_msg["message_id"]}
            }
        })
        prompt_admin_msg = self.mock_client.sent_messages[-1]
        self.assertIn("Jo’rabekka xabaringizni yozing", prompt_admin_msg["text"])

    def test_group_anti_spam_verification_flow(self):
        group_id = -100123456789
        user_id = 777111

        # 1. Unverified user sends message in group
        self.bot_engine.handle_update({
            "update_id": 10,
            "message": {
                "message_id": 501,
                "chat": {"id": group_id, "type": "supergroup", "title": "Test Group"},
                "from": {"id": user_id, "first_name": "Botir"},
                "text": "Salom hammaga!"
            }
        })

        # Check prompt message sent
        prompt_msg = [m for m in self.mock_client.sent_messages if m["chat_id"] == group_id and "bot emasligingizni tasdiqlang" in m["text"]][0]
        self.assertIsNotNone(prompt_msg)
        prompt_btn = prompt_msg["reply_markup"]["inline_keyboard"][0][0]
        self.assertEqual(prompt_btn["text"], "✅ Men bot emasman")
        callback_data = prompt_btn["callback_data"]

        # 2. Another user (imposter) clicks the button -> Rejected
        self.bot_engine.handle_update({
            "update_id": 11,
            "callback_query": {
                "id": "cq_imposter",
                "from": {"id": 999999},  # different user
                "data": callback_data,
                "message": {"chat": {"id": group_id}, "message_id": prompt_msg["message_id"]}
            }
        })
        self.assertTrue(self.mock_client.answered_callbacks[-1]["show_alert"])
        self.assertIn("Bu tugma siz uchun emas", self.mock_client.answered_callbacks[-1]["text"])

        # 3. The actual user clicks the button -> Approved
        self.bot_engine.handle_update({
            "update_id": 12,
            "callback_query": {
                "id": "cq_correct",
                "from": {"id": user_id},
                "data": callback_data,
                "message": {"chat": {"id": group_id}, "message_id": prompt_msg["message_id"]}
            }
        })
        self.assertTrue(bot_db.is_user_verified(user_id, self.db_path))
        # Bot prompt deleted
        self.assertTrue(any(d["message_id"] == prompt_msg["message_id"] for d in self.mock_client.deleted_messages))

        # 4. Same verified user sends another message -> No warning, allowed freely!
        init_count = len(self.mock_client.sent_messages)
        self.bot_engine.handle_update({
            "update_id": 13,
            "message": {
                "message_id": 502,
                "chat": {"id": group_id, "type": "supergroup", "title": "Test Group"},
                "from": {"id": user_id, "first_name": "Botir"},
                "text": "Ikkinchi xabarim!"
            }
        })
        # No new messages sent by bot in group
        self.assertEqual(len(self.mock_client.sent_messages), init_count)

    def test_timeout_expiration_deletion(self):
        group_id = -100999
        user_id = 888

        # Unverified user posts
        self.bot_engine.handle_update({
            "update_id": 20,
            "message": {
                "message_id": 601,
                "chat": {"id": group_id, "type": "supergroup", "title": "Test Group 2"},
                "from": {"id": user_id, "first_name": "SpamBot"},
                "text": "18+ Reklama havolasi http://bad.com"
            }
        })

        prompt_msg = self.mock_client.sent_messages[-1]

        # Trigger expiration worker with simulated future timestamp
        future_ts = time.time() + 100
        expired = bot_db.get_expired_verifications(future_ts, self.db_path)
        self.assertEqual(len(expired), 1)

        # Worker deletes user message and prompt message
        self.mock_client.delete_message(group_id, expired[0]["user_message_id"])
        self.mock_client.delete_message(group_id, expired[0]["bot_message_id"])
        bot_db.mark_verification_expired(expired[0]["id"], self.db_path)

        self.assertTrue(any(d["message_id"] == 601 for d in self.mock_client.deleted_messages))
        self.assertTrue(any(d["message_id"] == prompt_msg["message_id"] for d in self.mock_client.deleted_messages))

    def test_admin_set_timeout_and_broadcast_groups(self):
        # 1. Admin /set_timeout 45
        self.bot_engine.handle_update({
            "update_id": 30,
            "message": {
                "message_id": 701,
                "chat": {"id": bot.ADMIN_CHAT_ID, "type": "private"},
                "from": {"id": bot.ADMIN_CHAT_ID},
                "text": "/set_timeout 45"
            }
        })
        self.assertEqual(bot_db.get_setting("captcha_timeout", "60", self.db_path), "45")

        # 2. Add group and user
        bot_db.upsert_group(-100111, "Dasturchilar", "dasturchilar_uz", 1, self.db_path)
        bot_db.upsert_user(1234, "ali", "Ali", "V", self.db_path)
        bot_db.set_user_full_name(1234, "Ali V", self.db_path)

        # 3. Admin /broadcast
        self.bot_engine.handle_update({
            "update_id": 31,
            "message": {
                "message_id": 702,
                "chat": {"id": bot.ADMIN_CHAT_ID, "type": "private"},
                "from": {"id": bot.ADMIN_CHAT_ID},
                "text": "/broadcast Hammaga salom!"
            }
        })

        # Verify broadcast reached both user and group
        user_bcast = next((m for m in self.mock_client.sent_messages if m["chat_id"] == 1234 and m["text"] == "Hammaga salom!"), None)
        group_bcast = next((m for m in self.mock_client.sent_messages if m["chat_id"] == -100111 and m["text"] == "Hammaga salom!"), None)
        self.assertIsNotNone(user_bcast)
        self.assertIsNotNone(group_bcast)

    def test_guard_bot_engine(self):
        guard_client = MockTelegramClient()
        guard_engine = bot.GuardBotEngine(guard_client)

        # 1. Regular user /start on Guard Bot
        guard_engine.handle_update({
            "update_id": 50,
            "message": {
                "message_id": 801,
                "chat": {"id": 554433, "type": "private"},
                "from": {"id": 554433, "first_name": "Sardor"},
                "text": "/start"
            }
        })
        user_msg = guard_client.sent_messages[-1]
        self.assertIn("Assalomu alaykum, Sardor!", user_msg["text"])
        self.assertIn("Tekshiruvchi", user_msg["text"])

        # 2. Admin /start on Guard Bot
        guard_engine.handle_update({
            "update_id": 51,
            "message": {
                "message_id": 802,
                "chat": {"id": bot.ADMIN_CHAT_ID, "type": "private"},
                "from": {"id": bot.ADMIN_CHAT_ID},
                "text": "/start"
            }
        })
        admin_msg = guard_client.sent_messages[-1]
        self.assertIn("Assalomu alaykum, Jo’rabek!", admin_msg["text"])
        self.assertIn("Tekshiruvchi", admin_msg["text"])

    def test_wsgi_webhook_endpoint(self):
        import server
        import io

        webhook_payload = json.dumps({
            "update_id": 9999,
            "message": {
                "message_id": 777,
                "chat": {"id": 12345, "type": "private"},
                "from": {"id": 12345, "first_name": "Test"},
                "text": "Salom"
            }
        }).encode("utf-8")

        environ = {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/api/telegram-webhook",
            "QUERY_STRING": "",
            "CONTENT_TYPE": "application/json",
            "CONTENT_LENGTH": str(len(webhook_payload)),
            "wsgi.input": io.BytesIO(webhook_payload)
        }

        response_status = []
        response_headers = []

        def start_response(status, headers):
            response_status.append(status)
            response_headers.append(headers)

        body = server.app(environ, start_response)
        res_text = b"".join(body).decode("utf-8")
        res_json = json.loads(res_text)

        self.assertTrue(response_status[0].startswith("200"))
        self.assertTrue(res_json.get("ok"))
        time.sleep(0.05)

    def test_leaderboard_and_stat_commands(self):
        user_id = 888999
        chat_id = user_id
        
        # 1. User sends /start and registers
        self.bot_engine.handle_update({
            "update_id": 100,
            "message": {
                "message_id": 1,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id, "username": "shox_math", "first_name": "Shoxrux"},
                "text": "Shoxrux Bek"
            }
        })

        # 2. Add score to user in leaderboard
        bot_db.update_leaderboard_score(f"tg_{user_id}", "Shoxrux Bek", "shox_math", points_earned=350, is_correct=True, current_streak=7)

        # 3. User requests /reyting
        self.bot_engine.handle_update({
            "update_id": 101,
            "message": {
                "message_id": 2,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id},
                "text": "/reyting"
            }
        })
        msg = self.mock_client.sent_messages[-1]
        self.assertIn("vaqtinchalik yopildi", msg["text"])

        # 4. User requests /stat
        self.bot_engine.handle_update({
            "update_id": 102,
            "message": {
                "message_id": 3,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id},
                "text": "/stat"
            }
        })
        stat_msg = self.mock_client.sent_messages[-1]
        self.assertIn("Shoxrux Bek — Shaxsiy Quiz Statistikasi", stat_msg["text"])
        self.assertIn("350 ball", stat_msg["text"])
        self.assertIn("100%", stat_msg["text"])


if __name__ == "__main__":
    unittest.main()

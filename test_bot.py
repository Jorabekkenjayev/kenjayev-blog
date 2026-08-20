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
        self.sent_reactions = []
        self.sent_copies = []
        self.answered_callbacks = []
        self.my_commands = []
        self.token = "mock_test_token"

    def get_me(self):
        return {"id": 999999, "is_bot": True, "first_name": "Kenjayev Bot", "username": "kenjayev_test_bot"}

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
        self.answered_callbacks.append({"id": callback_query_id, "text": text})
        return True


class TestKenjayevTelegramBot(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_bot.db")
        bot_db.init_db(self.db_path)

        # Patch bot_db DB_FILE
        bot_db.DB_FILE = self.db_path

        # Setup Mock Bot
        self.mock_client = MockTelegramClient()
        self.bot_engine = bot.BotEngine(self.mock_client)

        # Configure Bot Admin ID
        bot.ADMIN_CHAT_ID = 987654321
        bot.WEB_APP_URL = "https://kenjayev.uz"

        # Clear rate limits
        bot._rate_limits.clear()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_name_validation(self):
        # Valid names
        self.assertEqual(bot.validate_full_name("Ali Valiyev"), "Ali Valiyev")
        self.assertEqual(bot.validate_full_name("jo'rabek kenjayev"), "Jo'rabek Kenjayev")
        self.assertEqual(bot.validate_full_name("G'ayrat O'ktamov"), "G'ayrat O'ktamov")
        self.assertEqual(bot.validate_full_name("Otabek Sultonov"), "Otabek Sultonov")
        self.assertEqual(bot.validate_full_name("Shaxzoda Raximova"), "Shaxzoda Raximova")
        self.assertEqual(bot.validate_full_name("Muhammad Ali Valiyev"), "Muhammad Ali Valiyev")

        # Invalid names
        self.assertIsNone(bot.validate_full_name("Ali"))  # only 1 word
        self.assertIsNone(bot.validate_full_name(""))
        self.assertIsNone(bot.validate_full_name("   "))
        self.assertIsNone(bot.validate_full_name("Ali 12345"))  # numbers
        self.assertIsNone(bot.validate_full_name("Spam http://site.com"))  # URL
        self.assertIsNone(bot.validate_full_name("<script>alert()</script>"))  # XSS
        self.assertIsNone(bot.validate_full_name("A B"))  # too short words
        self.assertIsNone(bot.validate_full_name("Ali @username"))  # symbols

    def test_database_lifecycle(self):
        user, is_new = bot_db.upsert_user(111, "testuser", "Ali", "Valiyev", self.db_path)
        self.assertTrue(is_new)
        self.assertEqual(user["state"], "WAITING_FOR_NAME")

        bot_db.set_user_full_name(111, "Ali Valiyev", self.db_path)
        user = bot_db.get_user(111, self.db_path)
        self.assertEqual(user["full_name"], "Ali Valiyev")
        self.assertEqual(user["is_registered"], 1)

        # Message mapping
        bot_db.save_message_mapping(5001, 111, 101, "Test snippet", self.db_path)
        mapping = bot_db.get_mapping_by_admin_message(5001, self.db_path)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping["user_telegram_id"], 111)

        # Stats
        stats = bot_db.get_stats(self.db_path)
        self.assertEqual(stats["total_users"], 1)
        self.assertEqual(stats["registered_users"], 1)
        self.assertEqual(stats["total_messages"], 1)

    def test_full_onboarding_flow(self):
        user_id = 12345
        chat_id = 12345

        # 1. User sends /start
        update_start = {
            "update_id": 1,
            "message": {
                "message_id": 101,
                "chat": {"id": chat_id},
                "from": {"id": user_id, "username": "alivaliyev", "first_name": "Ali", "last_name": "Valiyev"},
                "text": "/start"
            }
        }
        self.bot_engine.handle_update(update_start)

        # Should ask for name
        self.assertEqual(len(self.mock_client.sent_messages), 1)
        self.assertIn("Ism va familiyangizni kiriting", self.mock_client.sent_messages[0]["text"])

        # 2. User sends invalid single name
        update_invalid_name = {
            "update_id": 2,
            "message": {
                "message_id": 102,
                "chat": {"id": chat_id},
                "from": {"id": user_id, "username": "alivaliyev", "first_name": "Ali", "last_name": "Valiyev"},
                "text": "Ali"
            }
        }
        self.bot_engine.handle_update(update_invalid_name)
        self.assertEqual(len(self.mock_client.sent_messages), 2)
        self.assertIn("Iltimos, ism va familiyangizni to’liq kiriting", self.mock_client.sent_messages[1]["text"])

        # 3. User sends valid full name "Ali Valiyev"
        update_valid_name = {
            "update_id": 3,
            "message": {
                "message_id": 103,
                "chat": {"id": chat_id},
                "from": {"id": user_id, "username": "alivaliyev", "first_name": "Ali", "last_name": "Valiyev"},
                "text": "Ali Valiyev"
            }
        }
        self.bot_engine.handle_update(update_valid_name)

        # 3a. Heart reaction check
        self.assertEqual(len(self.mock_client.sent_reactions), 1)
        self.assertEqual(self.mock_client.sent_reactions[0]["emoji"], "❤️")
        self.assertEqual(self.mock_client.sent_reactions[0]["message_id"], 103)

        # 3b. Admin notification check
        # Sent messages index 2: Admin Notification, index 3: User Welcome
        admin_notif = next((m for m in self.mock_client.sent_messages if m["chat_id"] == bot.ADMIN_CHAT_ID), None)
        self.assertIsNotNone(admin_notif)
        self.assertIn("YANGI FOYDALANUVCHI", admin_notif["text"])
        self.assertIn("Ali Valiyev", admin_notif["text"])
        self.assertIn("12345", admin_notif["text"])

        # 3c. User welcome message check
        user_welcome = [m for m in self.mock_client.sent_messages if m["chat_id"] == chat_id and "Kenjayev Jo’rabek botiga xush kelibsiz" in m["text"]][0]
        self.assertIsNotNone(user_welcome)
        self.assertIn("Kenjayev Jo’rabek bu yerda o’z blogini yuritadi", user_welcome["text"])

        # Check inline keyboard buttons
        buttons = user_welcome["reply_markup"]["inline_keyboard"]
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons[0][0]["text"], "🌐 Saytga kirish")
        self.assertEqual(buttons[0][0]["web_app"]["url"], "https://kenjayev.uz")
        self.assertEqual(buttons[1][0]["text"], "💬 Jo’rabekka yozish")
        self.assertEqual(buttons[1][0]["callback_data"], "write_to_admin")

        # Check user database state
        db_user = bot_db.get_user(user_id, self.db_path)
        self.assertEqual(db_user["is_registered"], 1)
        self.assertEqual(db_user["full_name"], "Ali Valiyev")

    def test_duplicate_start_registered_user(self):
        user_id = 999
        chat_id = 999
        # Pre-register user
        bot_db.upsert_user(user_id, "existing", "Jon", "Doe", self.db_path)
        bot_db.set_user_full_name(user_id, "Jon Doe", self.db_path)

        update = {
            "update_id": 1,
            "message": {
                "message_id": 201,
                "chat": {"id": chat_id},
                "from": {"id": user_id, "username": "existing", "first_name": "Jon", "last_name": "Doe"},
                "text": "/start"
            }
        }
        self.bot_engine.handle_update(update)

        # Directly receives welcome message and buttons (no asking for name again)
        self.assertEqual(len(self.mock_client.sent_messages), 1)
        self.assertIn("Kenjayev Jo’rabek botiga xush kelibsiz", self.mock_client.sent_messages[0]["text"])

    def test_message_routing_and_admin_reply(self):
        user_id = 55555
        chat_id = 55555

        # Register user
        bot_db.upsert_user(user_id, "alisher", "Alisher", "Navoiy", self.db_path)
        bot_db.set_user_full_name(user_id, "Alisher Navoiy", self.db_path)

        # User writes a message to Jo'rabek
        update_user_msg = {
            "update_id": 10,
            "message": {
                "message_id": 301,
                "chat": {"id": chat_id},
                "from": {"id": user_id, "username": "alisher", "first_name": "Alisher", "last_name": "Navoiy"},
                "text": "Salom Jo'rabek, blogingiz juda ajoyib!"
            }
        }
        self.bot_engine.handle_update(update_user_msg)

        # Verify Admin received formatted notification
        admin_msg = next((m for m in self.mock_client.sent_messages if m["chat_id"] == bot.ADMIN_CHAT_ID and "YANGI XABAR" in m["text"]), None)
        self.assertIsNotNone(admin_msg)
        self.assertIn("Alisher Navoiy", admin_msg["text"])
        self.assertIn("Salom Jo'rabek, blogingiz juda ajoyib!", admin_msg["text"])

        admin_received_msg_id = admin_msg["message_id"]

        # Verify user received confirmation
        user_conf = next((m for m in self.mock_client.sent_messages if m["chat_id"] == chat_id and "Xabaringiz Jo’rabekka yetkazildi" in m["text"]), None)
        self.assertIsNotNone(user_conf)

        # Now Admin replies to that message
        update_admin_reply = {
            "update_id": 11,
            "message": {
                "message_id": 901,
                "chat": {"id": bot.ADMIN_CHAT_ID},
                "from": {"id": bot.ADMIN_CHAT_ID, "username": "jorabek", "first_name": "Jo'rabek", "last_name": "Kenjayev"},
                "text": "Rahmat Alisher, xursandman!",
                "reply_to_message": {
                    "message_id": admin_received_msg_id,
                    "text": admin_msg["text"]
                }
            }
        }
        self.bot_engine.handle_update(update_admin_reply)

        # Verify user received the reply from Jo'rabek
        user_reply = next((m for m in self.mock_client.sent_messages if m["chat_id"] == user_id and "Jo’rabekdan javob" in m["text"]), None)
        self.assertIsNotNone(user_reply)
        self.assertIn("Rahmat Alisher, xursandman!", user_reply["text"])

    def test_admin_commands(self):
        # Admin /stats command
        update_stats = {
            "update_id": 20,
            "message": {
                "message_id": 801,
                "chat": {"id": bot.ADMIN_CHAT_ID},
                "from": {"id": bot.ADMIN_CHAT_ID},
                "text": "/stats"
            }
        }
        self.bot_engine.handle_update(update_stats)
        stats_msg = next((m for m in self.mock_client.sent_messages if m["chat_id"] == bot.ADMIN_CHAT_ID and "BOT STATISTIKASI" in m["text"]), None)
        self.assertIsNotNone(stats_msg)

        # Admin /users command
        update_users = {
            "update_id": 21,
            "message": {
                "message_id": 802,
                "chat": {"id": bot.ADMIN_CHAT_ID},
                "from": {"id": bot.ADMIN_CHAT_ID},
                "text": "/users"
            }
        }
        self.bot_engine.handle_update(update_users)
        users_msg = next((m for m in self.mock_client.sent_messages if m["chat_id"] == bot.ADMIN_CHAT_ID and "OXIRGI 10 TA" in m["text"] or "Foydalanuvchilar" in m["text"]), None)
        self.assertIsNotNone(users_msg)

    def test_rate_limiting(self):
        user_id = 777
        chat_id = 777
        bot_db.upsert_user(user_id, "spammer", "Spam", "User", self.db_path)
        bot_db.set_user_full_name(user_id, "Spam User", self.db_path)

        # Send 6 rapid messages
        for i in range(6):
            update = {
                "update_id": 100 + i,
                "message": {
                    "message_id": 500 + i,
                    "chat": {"id": chat_id},
                    "from": {"id": user_id, "username": "spammer", "first_name": "Spam", "last_name": "User"},
                    "text": f"Message {i}"
                }
            }
            self.bot_engine.handle_update(update)

        # The 6th message should trigger rate limit warning
        rate_warn = next((m for m in self.mock_client.sent_messages if m["chat_id"] == chat_id and "Iltimos, ketma-ket ko'p xabar yubormang" in m["text"]), None)
        self.assertIsNotNone(rate_warn)

    def test_wsgi_webhook_endpoint(self):
        import server
        import io

        webhook_payload = json.dumps({
            "update_id": 9999,
            "message": {
                "message_id": 777,
                "chat": {"id": 12345},
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


if __name__ == "__main__":
    unittest.main()

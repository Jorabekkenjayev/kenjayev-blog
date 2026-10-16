import os
import sys
import unittest
import tempfile
import shutil
import json
import time
import threading

import bot_db
import bot

# Testlar hech qachon real Telegram API ga ulanmasligi kerak
bot.BOT_TOKEN = ""
bot.GUARD_BOT_TOKEN = ""

QUIZ_FIXTURE = {
    "quiz_sections": [
        {"id": "sec_algebra", "title": "Algebra va Tenglamalar"},
        {"id": "sec_analiz", "title": "Analiz va Hosilalar"},
    ],
    "quizzes": [
        {
            "id": "q_alg_01",
            "section_id": "sec_algebra",
            "title": "$2x + 7 = 19$ tenglamani yeching.",
            "options": ["$x = 6$", "$x = 5$", "$x = 12$", "$x = 8$"],
            "correct_option": 0,
            "points": 10,
            "difficulty": "oson",
            "explanation": "$2x = 12 \\implies x = 6$."
        },
        {
            "id": "q_ana_01",
            "section_id": "sec_analiz",
            "title": "Hosilani toping: $f(x) = x^3$",
            "options": ["$3x^2$", "$x^2$", "$3x$", "$3x^3$"],
            "correct_option": 0,
            "points": 25,
            "difficulty": "qiyin",
            "explanation": "$(x^n)' = n x^{n-1}$."
        },
        {
            "id": "q_alg_02",
            "section_id": "sec_algebra",
            "title": "$x^2 = 49$ bo'lsa $x > 0$ uchun $x$ ni toping.",
            "options": ["$7$", "$49$", "$-7$", "$14$"],
            "correct_option": 0,
            "points": 10,
            "difficulty": "oson",
            "explanation": "$x = \\sqrt{49} = 7$."
        },
        {
            "id": "q_alg_03",
            "section_id": "sec_algebra",
            "title": "$3x - 9 = 0$ bo'lsa $x$ nechaga teng?",
            "options": ["$3$", "$9$", "$-3$", "$0$"],
            "correct_option": 0,
            "points": 10,
            "difficulty": "oson",
            "explanation": "$3x = 9 \\implies x = 3$."
        }
    ]
}


class MockTelegramClient:
    def __init__(self):
        self.sent_messages = []
        self.edited_messages = []
        self.sent_stickers = []
        self.deleted_messages = []
        self.sent_reactions = []
        self.sent_copies = []
        self.answered_callbacks = []
        self.my_commands = []
        self.token = "mock_test_token"
        self.bot_username = "KenjayevJorabekBot"

    def get_me(self):
        return {"id": 999999, "is_bot": True, "first_name": "Kenjayev Bot", "username": "KenjayevJorabekBot"}

    def ensure_username(self):
        return self.bot_username

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

    def edit_message_text(self, chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
        obj = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "reply_markup": reply_markup
        }
        self.edited_messages.append(obj)
        return obj

    def send_sticker(self, chat_id, file_id):
        obj = {"chat_id": chat_id, "file_id": file_id}
        self.sent_stickers.append(obj)
        return obj

    def get_file(self, file_id):
        return {"file_id": file_id, "file_unique_id": "uniq"}

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

        # Quiz bazasi uchun fixture
        self.orig_quiz_path = bot.DATA_JSON_PATH
        self.quiz_path = os.path.join(self.temp_dir, "quiz_data.json")
        with open(self.quiz_path, 'w', encoding='utf-8') as f:
            json.dump(QUIZ_FIXTURE, f, ensure_ascii=False)
        bot.DATA_JSON_PATH = self.quiz_path
        bot.reset_quiz_cache()
        bot._recent_questions.clear()
        bot._streaks.clear()

        # Setup Mock Bot
        bot.ExpirationCoordinator.reset()
        self.mock_client = MockTelegramClient()
        self.bot_engine = bot.BotEngine(self.mock_client)

        # Configure Bot Admin ID
        bot.ADMIN_CHAT_ID = 987654321
        bot.WEB_APP_URL = "https://kenjayev-blog.onrender.com"
        bot._rate_limits.clear()

    def tearDown(self):
        bot_db.DATA_JSON_FILE = self.orig_data_json
        bot.DATA_JSON_PATH = self.orig_quiz_path
        bot.reset_quiz_cache()
        self.bot_engine.stop()
        bot.ExpirationCoordinator.reset()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # --- YORDAMCHI ---
    def register_user(self, user_id=12345, username="alivaliyev", first="Ali", last="Valiyev", name="Ali Valiyev"):
        chat_id = user_id
        self.bot_engine.handle_update({
            "update_id": 1,
            "message": {
                "message_id": 101,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id, "username": username, "first_name": first, "last_name": last},
                "text": "/start"
            }
        })
        self.bot_engine.handle_update({
            "update_id": 2,
            "message": {
                "message_id": 102,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id, "username": username, "first_name": first, "last_name": last},
                "text": name
            }
        })
        return chat_id

    def click(self, data, user_id=12345, message_id=1000, chat_id=None):
        self.bot_engine.handle_update({
            "update_id": 999,
            "callback_query": {
                "id": "cq_" + str(len(self.mock_client.answered_callbacks)),
                "from": {"id": user_id},
                "data": data,
                "message": {"chat": {"id": chat_id or user_id}, "message_id": message_id}
            }
        })

    # --- TESTLAR ---
    def test_name_validation(self):
        self.assertEqual(bot.validate_full_name("Ali Valiyev"), "Ali Valiyev")
        self.assertEqual(bot.validate_full_name("jo'rabek kenjayev"), "Jo'rabek Kenjayev")
        self.assertEqual(bot.validate_full_name("G'ayrat O'ktamov"), "G'ayrat O'ktamov")
        self.assertEqual(bot.validate_full_name("A Valiyev"), "A Valiyev")
        self.assertEqual(bot.validate_full_name("Shaxzoda Raximova"), "Shaxzoda Raximova")

        self.assertIsNone(bot.validate_full_name("Ali"))
        self.assertIsNone(bot.validate_full_name(""))
        self.assertIsNone(bot.validate_full_name("Ali 12345"))
        self.assertIsNone(bot.validate_full_name("Spam http://site.com"))

    def test_main_menu_has_all_working_buttons(self):
        chat_id = self.register_user()
        welcome_msg = [
            m for m in self.mock_client.sent_messages
            if m["chat_id"] == chat_id and "botiga xush kelibsiz" in m["text"]
        ][0]
        rows = welcome_msg["reply_markup"]["inline_keyboard"]

        flat = {c["callback_data"]: c["text"] for r in rows for c in r if "callback_data" in c}
        web_app = [c for r in rows for c in r if "web_app" in c]

        # 9 ta tugma: 1 web_app + 8 callback
        self.assertEqual(sum(len(r) for r in rows), 9)
        self.assertEqual(len(web_app), 1)
        self.assertEqual(web_app[0]["web_app"]["url"], "https://kenjayev-blog.onrender.com")

        for expected in ("test_menu", "test:oson", "test:qiyin", "my_stats",
                         "show_rating", "anti_spam_info", "about_bot", "write_to_admin"):
            self.assertIn(expected, flat, f"{expected} tugmasi menyuda yo'q")

        # Hech qanday tugma o'lik "tez orada" matniga olib bormasin
        self.assertNotIn("check_test", flat)

    def test_legacy_check_test_button_still_works(self):
        self.register_user()
        before = len(self.mock_client.sent_messages)
        self.click("check_test")
        self.assertEqual(len(self.mock_client.sent_messages), before + 1)
        self.assertIn("botiga xush kelibsiz", self.mock_client.sent_messages[-1]["text"])

    def test_inline_quiz_correct_answer_awards_points(self):
        chat_id = self.register_user()
        self.click("test:oson")

        question_msg = [m for m in self.mock_client.sent_messages if "SAVOL" in m["text"]][-1]
        self.assertIn("Algebra va Tenglamalar", question_msg["text"])

        options = question_msg["reply_markup"]["inline_keyboard"]
        # 4 variant + bosh menyu
        self.assertEqual(len(options), 5)
        correct_cb = options[0][0]["callback_data"]
        self.assertTrue(correct_cb.startswith("ans:"))
        asked_qid = correct_cb.split(":")[1]

        self.click(correct_cb, message_id=question_msg["message_id"], chat_id=chat_id)

        edited = self.mock_client.edited_messages[-1]
        self.assertIn("TO’G’RI", edited["text"])
        self.assertIn("+10 ball", edited["text"])
        self.assertIn("Yechim", edited["text"])

        rank = bot_db.get_user_leaderboard_rank(f"tg_{chat_id}", self.db_path)
        self.assertEqual(rank["points"], 10)
        self.assertEqual(rank["correct_count"], 1)
        self.assertEqual(rank["total_solved"], 1)
        self.assertEqual(rank["accuracy"], 100)

        progress = bot_db.get_user_solved_question_ids(f"tg_{chat_id}", None, self.db_path)
        self.assertTrue(any(p.get("question_id") == asked_qid for p in progress))

    def test_inline_quiz_wrong_answer_no_points(self):
        chat_id = self.register_user()
        self.click("test:oson")
        question_msg = [m for m in self.mock_client.sent_messages if "SAVOL" in m["text"]][-1]
        wrong_cb = question_msg["reply_markup"]["inline_keyboard"][1][0]["callback_data"]

        self.click(wrong_cb, message_id=question_msg["message_id"], chat_id=chat_id)

        edited = self.mock_client.edited_messages[-1]
        self.assertIn("XATO", edited["text"])

        rank = bot_db.get_user_leaderboard_rank(f"tg_{chat_id}", self.db_path)
        self.assertEqual(rank["points"], 0)
        self.assertEqual(rank["total_solved"], 1)
        self.assertEqual(rank["correct_count"], 0)

        # Javob berilgan savol qayta hisoblanmaydi
        before = len(self.mock_client.edited_messages)
        self.click(wrong_cb, message_id=question_msg["message_id"], chat_id=chat_id)
        self.assertEqual(len(self.mock_client.edited_messages), before)
        rank2 = bot_db.get_user_leaderboard_rank(f"tg_{chat_id}", self.db_path)
        self.assertEqual(rank2["total_solved"], 1)

    def test_quiz_streak_and_next_question(self):
        chat_id = self.register_user()
        for _ in range(2):
            self.click("test:oson")
            q_msg = [m for m in self.mock_client.sent_messages if "SAVOL" in m["text"]][-1]
            self.click(q_msg["reply_markup"]["inline_keyboard"][0][0]["callback_data"],
                       message_id=q_msg["message_id"], chat_id=chat_id)

        last_edit = self.mock_client.edited_messages[-1]
        self.assertIn("2 ta ketma-ket", last_edit["text"])

        rank = bot_db.get_user_leaderboard_rank(f"tg_{chat_id}", self.db_path)
        self.assertEqual(rank["best_streak"], 2)

        # "Keyingi savol" tugma oldingi savolni takrorlamasin
        ids_before = [m["text"] for m in self.mock_client.sent_messages if "SAVOL" in m["text"]]
        next_cb = None
        for row in last_edit["reply_markup"]["inline_keyboard"]:
            for c in row:
                if c.get("callback_data", "").startswith("test:"):
                    next_cb = c["callback_data"]
        self.assertIsNotNone(next_cb)
        self.click(next_cb, chat_id=chat_id)
        new_question = [m for m in self.mock_client.sent_messages if "SAVOL" in m["text"]][-1]
        self.assertNotIn(new_question["text"], ids_before)

    def test_difficulty_filters_questions(self):
        chat_id = self.register_user()
        self.click("test:qiyin")
        q_msg = [m for m in self.mock_client.sent_messages if "SAVOL" in m["text"]][-1]
        self.assertIn("🔴 Qiyin (25 ball)", q_msg["text"])
        self.assertIn("Analiz", q_msg["text"])

    def test_about_stats_rating_buttons(self):
        chat_id = self.register_user()

        self.click("about_bot", chat_id=chat_id)
        self.assertIn("BOT HAQIDA", self.mock_client.sent_messages[-1]["text"])

        # Hali natija yo'q -> bo'sh reyting holati
        self.click("show_rating", chat_id=chat_id)
        self.assertIn("birorta ham natija yo\'q", self.mock_client.sent_messages[-1]["text"])

        # Bir savolni to'g'ri yechib, reytingda ko'rinadigan qilamiz
        self.click("test:oson", chat_id=chat_id)
        q_msg = [m for m in self.mock_client.sent_messages if "SAVOL" in m["text"]][-1]
        self.click(q_msg["reply_markup"]["inline_keyboard"][0][0]["callback_data"],
                   message_id=q_msg["message_id"], chat_id=chat_id)

        self.click("show_rating", chat_id=chat_id)
        rating_msg = self.mock_client.sent_messages[-1]
        self.assertIn("JONLI MATEMATIKA REYTINGI", rating_msg["text"])
        self.assertIn("Ali Valiyev", rating_msg["text"])
        self.assertIn("10 ball", rating_msg["text"])

        self.click("my_stats", chat_id=chat_id)
        stat_msg = self.mock_client.sent_messages[-1]
        self.assertIn("Shaxsiy Quiz Statistikasi", stat_msg["text"])
        # Reyting bo'limi endi o'lik #leaderboard havolasiga olib bormasin
        for row in stat_msg["reply_markup"]["inline_keyboard"]:
            for c in row:
                self.assertNotIn("#leaderboard", c.get("web_app", {}).get("url", ""))

    def test_sticker_file_id_capture_by_admin(self):
        os.environ["STICKER_CORRECT"] = "MOCK_CORRECT_STICKER"
        try:
            self.bot_engine.handle_update({
                "update_id": 300,
                "message": {
                    "message_id": 900,
                    "chat": {"id": bot.ADMIN_CHAT_ID, "type": "private"},
                    "from": {"id": bot.ADMIN_CHAT_ID},
                    "sticker": {"file_id": "ADMIN_STICKER_ID", "emoji": "🎉"},
                    "caption": "correct"
                }
            })
            self.assertEqual(bot_db.get_setting("sticker_correct", "", self.db_path), "ADMIN_STICKER_ID")
            self.assertIn("Sticker saqlandi", self.mock_client.sent_messages[-1]["text"])

            # Endi to'g'ri javobda shu sticker yuboriladi
            chat_id = self.register_user()
            self.click("test:oson")
            q_msg = [m for m in self.mock_client.sent_messages if "SAVOL" in m["text"]][-1]
            self.click(q_msg["reply_markup"]["inline_keyboard"][0][0]["callback_data"],
                       message_id=q_msg["message_id"], chat_id=chat_id)
            self.assertTrue(any(s["file_id"] == "MOCK_CORRECT_STICKER" for s in self.mock_client.sent_stickers))
        finally:
            os.environ.pop("STICKER_CORRECT", None)

    def test_onboarding_and_anti_spam_buttons(self):
        chat_id = self.register_user()

        self.click("anti_spam_info", chat_id=chat_id)
        info_msg = self.mock_client.sent_messages[-1]
        self.assertIn("Guruhni 18+ spam", info_msg["text"])
        self.assertIn("KenjayevJorabekBot", info_msg["reply_markup"]["inline_keyboard"][0][0]["url"])

        self.click("write_to_admin", chat_id=chat_id)
        self.assertIn("Jo’rabekka xabaringizni yozing", self.mock_client.sent_messages[-1]["text"])

        # Keyin kelgan matn adminga forward bo'ladi
        self.bot_engine.handle_update({
            "update_id": 4,
            "message": {
                "message_id": 105,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": chat_id, "first_name": "Ali"},
                "text": "Salom, savolim bor edi"
            }
        })
        self.assertTrue(any(m["chat_id"] == bot.ADMIN_CHAT_ID and "Salom, savolim bor edi" in m["text"]
                            for m in self.mock_client.sent_messages))

    def test_group_anti_spam_verification_flow(self):
        group_id = -100123456789
        user_id = 777111

        self.bot_engine.handle_update({
            "update_id": 10,
            "message": {
                "message_id": 501,
                "chat": {"id": group_id, "type": "supergroup", "title": "Test Group"},
                "from": {"id": user_id, "first_name": "Botir"},
                "text": "Salom hammaga!"
            }
        })

        prompt_msg = [m for m in self.mock_client.sent_messages if m["chat_id"] == group_id and "bot emasligingizni tasdiqlang" in m["text"]][0]
        prompt_btn = prompt_msg["reply_markup"]["inline_keyboard"][0][0]
        self.assertEqual(prompt_btn["text"], "✅ Men bot emasman")
        callback_data = prompt_btn["callback_data"]

        # Imposter -> rad etiladi
        self.bot_engine.handle_update({
            "update_id": 11,
            "callback_query": {
                "id": "cq_imposter",
                "from": {"id": 999999},
                "data": callback_data,
                "message": {"chat": {"id": group_id}, "message_id": prompt_msg["message_id"]}
            }
        })
        self.assertTrue(self.mock_client.answered_callbacks[-1]["show_alert"])
        self.assertIn("Bu tugma siz uchun emas", self.mock_client.answered_callbacks[-1]["text"])

        # Haqiqiy foydalanuvchi -> tasdiqlanadi
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
        self.assertTrue(any(d["message_id"] == prompt_msg["message_id"] for d in self.mock_client.deleted_messages))

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
        self.assertEqual(len(self.mock_client.sent_messages), init_count)

    def test_timeout_expiration_deletion(self):
        group_id = -100999
        user_id = 888

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

        coordinator = bot.ExpirationCoordinator.get()
        coordinator.register_client(self.mock_client)
        future_items = bot_db.get_expired_verifications(time.time() + 100, self.db_path)
        self.assertEqual(len(future_items), 1)

        ok_user = coordinator._delete_with_any_client(group_id, future_items[0]["user_message_id"])
        ok_bot = coordinator._delete_with_any_client(group_id, future_items[0]["bot_message_id"])
        bot_db.mark_verification_expired(future_items[0]["id"], self.db_path)

        self.assertTrue(ok_user and ok_bot)
        self.assertTrue(any(d["message_id"] == 601 for d in self.mock_client.deleted_messages))
        self.assertTrue(any(d["message_id"] == prompt_msg["message_id"] for d in self.mock_client.deleted_messages))

    def test_shared_expiration_worker_is_single(self):
        coordinator = bot.ExpirationCoordinator.get()
        coordinator.start()
        first_thread = coordinator._thread
        bot.BotEngine(MockTelegramClient())
        bot.GuardBotEngine(MockTelegramClient())
        coordinator.start()
        self.assertIs(first_thread, coordinator._thread)
        coordinator.stop()

    def test_admin_set_timeout_and_broadcast_groups(self):
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

        bot_db.upsert_group(-100111, "Dasturchilar", "dasturchilar_uz", 1, self.db_path)
        bot_db.upsert_user(1234, "ali", "Ali", "V", self.db_path)
        bot_db.set_user_full_name(1234, "Ali V", self.db_path)

        self.bot_engine.handle_update({
            "update_id": 31,
            "message": {
                "message_id": 702,
                "chat": {"id": bot.ADMIN_CHAT_ID, "type": "private"},
                "from": {"id": bot.ADMIN_CHAT_ID},
                "text": "/broadcast Hammaga salom!"
            }
        })

        user_bcast = next((m for m in self.mock_client.sent_messages if m["chat_id"] == 1234 and m["text"] == "Hammaga salom!"), None)
        group_bcast = next((m for m in self.mock_client.sent_messages if m["chat_id"] == -100111 and m["text"] == "Hammaga salom!"), None)
        self.assertIsNotNone(user_bcast)
        self.assertIsNotNone(group_bcast)

    def test_guard_bot_engine(self):
        guard_client = MockTelegramClient()
        guard_client.bot_username = "Botlarni_tekshiruvchi_Bot"
        guard_engine = bot.GuardBotEngine(guard_client)

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
        self.assertIn("Botlarni_tekshiruvchi_Bot", user_msg["reply_markup"]["inline_keyboard"][0][0]["url"])

        # Oddiy matn -> spam emas, qisqa yo'riqnoma
        guard_engine.handle_update({
            "update_id": 53,
            "message": {
                "message_id": 803,
                "chat": {"id": 554433, "type": "private"},
                "from": {"id": 554433, "first_name": "Sardor"},
                "text": "salom"
            }
        })
        self.assertIn("/start", guard_client.sent_messages[-1]["text"])

        guard_engine.handle_update({
            "update_id": 51,
            "message": {
                "message_id": 804,
                "chat": {"id": bot.ADMIN_CHAT_ID, "type": "private"},
                "from": {"id": bot.ADMIN_CHAT_ID},
                "text": "/start"
            }
        })
        admin_msg = guard_client.sent_messages[-1]
        self.assertIn("Assalomu alaykum, Jo’rabek!", admin_msg["text"])
        self.assertIn("Tekshiruvchi", admin_msg["text"])

        guard_engine.handle_update({
            "update_id": 52,
            "callback_query": {
                "id": "cq_guard_info",
                "from": {"id": 554433},
                "data": "guard_info",
                "message": {"chat": {"id": 554433}, "message_id": 801}
            }
        })
        self.assertIn("tekshirish vaqti", guard_client.answered_callbacks[-1]["text"])

    def test_wsgi_webhook_endpoint_uses_shared_engine(self):
        import server
        import io

        bot._shared_engine = None
        webhook_payload = json.dumps({
            "update_id": 9999,
            "message": {
                "message_id": 777,
                "chat": {"id": 12345, "type": "private"},
                "from": {"id": 12345, "first_name": "Test"},
                "text": "/start"
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

        statuses = []

        def start_response(status, headers):
            statuses.append(status)

        body = server.app(environ, start_response)
        res_json = json.loads(b"".join(body).decode("utf-8"))

        self.assertTrue(statuses[0].startswith("200"))
        self.assertTrue(res_json.get("ok"))
        time.sleep(0.1)

        shared = bot.get_shared_engine()
        self.assertIs(shared, bot.get_shared_engine())
        threads_before = threading.active_count()
        for _ in range(10):
            bot.get_shared_engine()
        self.assertEqual(threads_before, threading.active_count())
        bot._shared_engine = None

    def test_leaderboard_and_stat_commands(self):
        user_id = 888999
        chat_id = user_id

        self.bot_engine.handle_update({
            "update_id": 100,
            "message": {
                "message_id": 1,
                "chat": {"id": chat_id, "type": "private"},
                "from": {"id": user_id, "username": "shox_math", "first_name": "Shoxrux"},
                "text": "Shoxrux Bek"
            }
        })

        bot_db.update_leaderboard_score(f"tg_{user_id}", "Shoxrux Bek", "shox_math", points_earned=350, is_correct=True, current_streak=7)

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
        self.assertIn("REYTINGI", msg["text"])
        self.assertNotIn("vaqtinchalik yopildi", msg["text"])
        self.assertIn("350 ball", msg["text"])

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

    def test_math_cleaning(self):
        self.assertEqual(bot.clean_math("$2x + 7 = 19$ tenglamani yeching."), "2x + 7 = 19 tenglamani yeching.")
        self.assertIn("⇒", bot.clean_math("$2x = 12$ \\implies $x = 6$"))
        self.assertEqual(bot.clean_math("\\frac{a+b}{2}"), "(a+b)/2")
        self.assertEqual(bot.clean_math("\\frac{1}{3}"), "1/3")
        self.assertEqual(bot.clean_math("\\sqrt{49} = 7"), "√(49) = 7")
        self.assertIn("≥", bot.clean_math("x \\geq 0"))
        self.assertNotIn("$", bot.clean_math("$x^2$"))


if __name__ == "__main__":
    unittest.main()

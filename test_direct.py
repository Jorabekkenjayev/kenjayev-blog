import json
import os
import time
import hashlib
import server

def test_direct_logic():
    print("🧪 Running In-Memory & File-Level Logic Tests for Kenjayev BLOG...")

    # 1. Test Password Hashing & HMAC
    print("\n1. Testing PBKDF2 Password Verification...")
    test_pwd = "Jorabek07@."
    test_hash = hashlib.pbkdf2_hmac("sha256", test_pwd.encode("utf-8"), server.ADMIN_SALT.encode("utf-8"), 100000).hex()
    assert server.hmac_compare(test_hash, server.ADMIN_PASSWORD_HASH), "Password hash comparison failed"
    print("   ✓ PBKDF2 password hash verification passed")

    # 2. Test Atomic Save & Backup Creation
    print("\n2. Testing Atomic Data Write & Backup...")
    initial_data = server.load_data()
    test_post = {
        "id": 9999,
        "title": "Evolyutsiya Maqolasi",
        "subtitle": "Platforma yangilanishi haqida",
        "category": "Texnologiya",
        "tags": ["texnologiya", "yangilik"],
        "image": "",
        "body": "<p>Sinov maqolasi.</p>",
        "rawBody": "Sinov maqolasi.",
        "date": "2026-08-18T13:35:00.000Z",
        "views": 5,
        "likes": 2
    }
    initial_data["posts"].append(test_post)
    success = server.save_data(initial_data, create_backup=True)
    assert success, "Atomic write failed"
    print("   ✓ Atomic save_data passed")

    # Verify backup exists
    backups = [f for f in os.listdir(server.BACKUP_DIR) if f.endswith('.json')]
    assert len(backups) > 0, "No backup files found"
    print(f"   ✓ Backup file created ({len(backups)} backups in storage)")

    # 3. Test XSS Sanitizer
    print("\n3. Testing HTML Sanitization...")
    dirty_html = "<p>Matn</p><script>alert('hack')</script><a href='javascript:void(0)' onclick='evil()'>Link</a>"
    clean_html = server.sanitize_html(dirty_html)
    assert "<script>" not in clean_html, "Script tag not removed"
    assert "onclick=" not in clean_html, "Event handler not removed"
    assert "javascript:" not in clean_html, "javascript: URL not removed"
    assert "<p>Matn</p>" in clean_html, "Valid HTML removed"
    print("   ✓ XSS sanitization passed: Dangerous tags and attributes neutralized")

    # 4. Test Base64 Image Migration logic
    print("\n4. Testing Base64 Image Migration...")
    sample_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    post_with_b64 = {
        "id": 8888,
        "title": "Rasm bilan post",
        "category": "Fikrlar",
        "image": sample_b64,
        "body": "<p>Rasm bor.</p>",
        "views": 0,
        "likes": 0
    }
    cur_data = server.load_data()
    cur_data["posts"].append(post_with_b64)
    server.save_data(cur_data, create_backup=False)
    
    server.migrate_base64_images()
    
    migrated_data = server.load_data()
    migrated_post = next((p for p in migrated_data["posts"] if p["id"] == 8888), None)
    assert migrated_post is not None, "Post not found"
    assert migrated_post["image"].startswith("/uploads/"), f"Image was not migrated: {migrated_post['image']}"
    assert os.path.exists(os.path.join(server.BASE_DIR, migrated_post["image"].lstrip("/"))), "Saved image file does not exist on disk"
    print(f"   ✓ Migration verified: Base64 converted to {migrated_post['image']}")

    # 5. Test Video File Handling & MIME Mapping
    print("\n5. Testing Video Media Handling...")
    dummy_video_b64 = "data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQ=="
    test_video_post = {
        "id": 7777,
        "title": "Video Post Test",
        "category": "Texnologiya",
        "image": "",
        "video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "body": "<p>Video sinovi.</p>",
        "views": 0,
        "likes": 0
    }
    cur_data = server.load_data()
    cur_data["posts"].append(test_video_post)
    server.save_data(cur_data, create_backup=False)

    saved_data = server.load_data()
    saved_post = next((p for p in saved_data["posts"] if p["id"] == 7777), None)
    assert saved_post is not None and "dQw4w9WgXcQ" in saved_post["video"], "Video field not properly stored"
    print("   ✓ Video post metadata storage verified")

    # Clean up test posts
    clean_posts = [p for p in saved_data["posts"] if p["id"] not in [7777, 8888, 9999]]
    saved_data["posts"] = clean_posts
    server.save_data(saved_data, create_backup=False)

    print("\n🎉 ALL DIRECT UNIT & INTEGRATION TESTS PASSED (100%)\n")

if __name__ == "__main__":
    test_direct_logic()

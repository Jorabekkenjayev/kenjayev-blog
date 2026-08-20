import urllib.request
import json
import time
import subprocess
import os
import sys

PORT = 8080
BASE_URL = f"http://127.0.0.1:{PORT}"

def run_tests():
    print("🧪 Running Kenjayev BLOG Full Automated Verification Suite...\n")
    
    # 1. Test Static & SEO Endpoints
    print("1. Testing Static & SEO Endpoints...")
    for endpoint in ['/', '/robots.txt', '/sitemap.xml', '/manifest.json', '/sw.js', '/api/data']:
        req = urllib.request.Request(f"{BASE_URL}{endpoint}")
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()
            assert status == 200, f"Endpoint {endpoint} returned status {status}"
            print(f"   ✓ GET {endpoint} -> {status} OK")

    # 2. Test Admin Login (Invalid & Valid)
    print("\n2. Testing Admin Security & Login...")
    # Invalid login
    login_data = json.dumps({"login": "+998919705191", "password": "WrongPassword123"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/admin/login", data=login_data, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
        assert False, "Should fail on wrong password"
    except urllib.error.HTTPError as e:
        assert e.code == 401, f"Expected 401, got {e.code}"
        print("   ✓ Invalid login correctly rejected with 401")

    # Valid login
    login_data = json.dumps({"login": "+998919705191", "password": "Jorabek07@."}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/admin/login", data=login_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        assert resp.getcode() == 200
        res_json = json.loads(resp.read().decode('utf-8'))
        assert res_json.get('status') == 'success'
        token = res_json.get('token')
        assert token, "Session token must be returned"
        print(f"   ✓ Valid login successful! Token received: {token[:10]}...")

    # Check Session
    req = urllib.request.Request(f"{BASE_URL}/api/admin/check-session", headers={'Authorization': f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        res_json = json.loads(resp.read().decode('utf-8'))
        assert res_json.get('authenticated') is True
        print("   ✓ Session token validation passed")

    # 3. Test Unauthorized Access Protection
    print("\n3. Testing Protected Endpoints Security...")
    unauth_req = urllib.request.Request(f"{BASE_URL}/api/save", data=json.dumps({"posts": []}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(unauth_req)
        assert False, "Unauthorized POST /api/save should be rejected"
    except urllib.error.HTTPError as e:
        assert e.code == 401
        print("   ✓ Unauthorized /api/save blocked with 401")

    # 4. Test Post Creation & Authorized Save
    print("\n4. Testing Authorized Post Creation & HTML Sanitization...")
    test_post = {
        "id": 1001,
        "title": "Sun'iy Idrok va Kelajak Tahlili",
        "subtitle": "Zamonaviy texnologiyalar hayotimizni qanday o'zgartirmoqda",
        "category": "Texnologiya",
        "tags": ["texnologiya", "ai"],
        "image": "",
        "body": "<p>Ushbu maqola sun'iy idrok haqida.</p><script>alert('xss')</script>",
        "rawBody": "Ushbu maqola sun'iy idrok haqida.",
        "date": "2026-08-18T13:30:00.000Z",
        "views": 0,
        "likes": 0
    }
    save_data = json.dumps({"posts": [test_post], "categories": ["Texnologiya", "Fikrlar"]}).encode('utf-8')
    auth_save_req = urllib.request.Request(f"{BASE_URL}/api/save", data=save_data, headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"})
    with urllib.request.urlopen(auth_save_req) as resp:
        assert resp.getcode() == 200
        print("   ✓ Authorized post save passed")

    # Verify XSS sanitization in saved data
    with urllib.request.urlopen(f"{BASE_URL}/api/data") as resp:
        data = json.loads(resp.read().decode('utf-8'))
        saved_body = data['posts'][0]['body']
        assert '<script>' not in saved_body, "XSS script tag must be sanitized"
        print("   ✓ XSS payload successfully sanitized on server")

    # 5. Test Smart View Tracking (with deduplication)
    print("\n5. Testing Smart View Deduplication...")
    view_data = json.dumps({"postId": 1001}).encode('utf-8')
    req1 = urllib.request.Request(f"{BASE_URL}/api/view", data=view_data, headers={'Content-Type': 'application/json', 'X-Client-ID': 'client_test_device_1'})
    with urllib.request.urlopen(req1) as resp:
        res1 = json.loads(resp.read().decode('utf-8'))
        assert res1.get('counted') is True
        print(f"   ✓ First view counted: {res1.get('views')} views")

    # Rapid second view by same client should be deduplicated
    req2 = urllib.request.Request(f"{BASE_URL}/api/view", data=view_data, headers={'Content-Type': 'application/json', 'X-Client-ID': 'client_test_device_1'})
    with urllib.request.urlopen(req2) as resp:
        res2 = json.loads(resp.read().decode('utf-8'))
        assert res2.get('counted') is False
        assert res2.get('views') == res1.get('views')
        print(f"   ✓ Rapid refresh view correctly deduplicated (no inflation)")

    # 6. Test Smart Like System
    print("\n6. Testing Smart Like Toggle...")
    like_data = json.dumps({"postId": 1001, "action": "add"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/like", data=like_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        assert res.get('likes') == 1
        print(f"   ✓ Like added: {res.get('likes')} like")

    unlike_data = json.dumps({"postId": 1001, "action": "remove"}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/like", data=unlike_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        assert res.get('likes') == 0
        print(f"   ✓ Like removed: {res.get('likes')} likes")

    # 7. Test Admin Backup & Restore
    print("\n7. Testing Admin Backup & Restore...")
    b_req = urllib.request.Request(f"{BASE_URL}/api/admin/backup", data=b'{}', headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"})
    with urllib.request.urlopen(b_req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        backup_filename = res.get('filename')
        assert backup_filename
        print(f"   ✓ Backup created: {backup_filename}")

    # List backups
    l_req = urllib.request.Request(f"{BASE_URL}/api/admin/backups", headers={'Authorization': f"Bearer {token}"})
    with urllib.request.urlopen(l_req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        assert len(res.get('backups', [])) > 0
        print(f"   ✓ Backups listed ({len(res['backups'])} available)")

    print("\n🎉 ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100%)")

if __name__ == '__main__':
    run_tests()

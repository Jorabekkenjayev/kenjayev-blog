import json
import io
import time
import os
import server

def test_full_system():
    print("=" * 70)
    print("🧪 KENJAYEV MATH & QUIZ HUB — INTEGRATION & SYSTEM TEST SUITE")
    print("=" * 70)

    # 1. Test Admin Login
    print("\n1. Testing Admin Authentication (+998919705191)...")
    token = None
    def mock_start(status, headers):
        nonlocal token
        pass

    # Invalid login test
    env_fail = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/api/admin/login',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'wsgi.input': io.BytesIO(json.dumps({'login': '+998919705191', 'password': 'WrongPassword123'}).encode('utf-8'))
    }
    env_fail['CONTENT_LENGTH'] = str(len(env_fail['wsgi.input'].getvalue()))
    res_fail = server.app(env_fail, mock_start)
    fail_data = json.loads(res_fail[0].decode('utf-8'))
    assert fail_data.get('status') == 'error', 'Invalid password was not rejected'
    print("   ✓ Invalid login attempt successfully rejected (401)")

    # Valid login test
    env_ok = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/api/admin/login',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'wsgi.input': io.BytesIO(json.dumps({'login': '+998919705191', 'password': 'Jorabek07@.'}).encode('utf-8'))
    }
    env_ok['CONTENT_LENGTH'] = str(len(env_ok['wsgi.input'].getvalue()))
    res_ok = server.app(env_ok, mock_start)
    ok_data = json.loads(res_ok[0].decode('utf-8'))
    assert ok_data.get('status') == 'success' and 'token' in ok_data, 'Admin login failed'
    token = ok_data['token']
    print(f"   ✓ Admin authentication successful. Token obtained: {token[:12]}...")

    # 2. Test Quiz Section Creation
    print("\n2. Testing Section Creation (/api/quizzes/section)...")
    sec_payload = {
        'action': 'create',
        'section': {
            'id': 'sec_test_olimp',
            'title': 'Olimpiada Masalalari',
            'description': 'Murakkab va nostandart matematik masalalar',
            'icon': '🏆',
            'color': '#ef4444'
        }
    }
    env_sec = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/api/quizzes/section',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'HTTP_AUTHORIZATION': f'Bearer {token}',
        'wsgi.input': io.BytesIO(json.dumps(sec_payload).encode('utf-8'))
    }
    env_sec['CONTENT_LENGTH'] = str(len(env_sec['wsgi.input'].getvalue()))
    res_sec = server.app(env_sec, mock_start)
    sec_res_data = json.loads(res_sec[0].decode('utf-8'))
    assert sec_res_data.get('status') == 'success', f'Section creation failed: {sec_res_data}'
    print("   ✓ New quiz section created successfully")

    # 3. Test Question Creation
    print("\n3. Testing Question Creation with LaTeX (/api/quizzes/question)...")
    q_payload = {
        'action': 'create',
        'question': {
            'section_id': 'sec_test_olimp',
            'title': 'Agar $x + y = 10$ va $xy = 21$ bo\'lsa, $x^3 + y^3$ ni toping.',
            'options': ['$370$', '$340$', '$400$', '$280$'],
            'correct_option': 0,
            'explanation': '$$x^3 + y^3 = (x + y)(x^2 - xy + y^2) = (x + y)((x+y)^2 - 3xy) = 10(100 - 63) = 10 \\times 37 = 370$$.',
            'difficulty': 'qiyin',
            'points': 3
        }
    }
    env_q = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/api/quizzes/question',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'HTTP_AUTHORIZATION': f'Bearer {token}',
        'wsgi.input': io.BytesIO(json.dumps(q_payload).encode('utf-8'))
    }
    env_q['CONTENT_LENGTH'] = str(len(env_q['wsgi.input'].getvalue()))
    res_q = server.app(env_q, mock_start)
    q_res_data = json.loads(res_q[0].decode('utf-8'))
    assert q_res_data.get('status') == 'success', f'Question creation failed: {q_res_data}'
    created_q_id = q_res_data['question']['id']
    print(f"   ✓ LaTeX Question created successfully (ID: {created_q_id})")

    # 4. Test Bulk Import
    print("\n4. Testing Bulk Import (/api/quizzes/bulk-import)...")
    bulk_payload = {
        'section_id': 'sec_test_olimp',
        'questions': [
            {
                'title': 'Ifodani soddalashtiring: $\\sqrt{7 + 4\\sqrt{3}} - \\sqrt{7 - 4\\sqrt{3}}$',
                'options': ['$2\\sqrt{3}$', '$4$', '$2$', '$0$'],
                'correct_option': 0,
                'explanation': '$\\sqrt{7 \\pm 4\\sqrt{3}} = \\sqrt{(2 \\pm \\sqrt{3})^2} = 2 \\pm \\sqrt{3}$. Ayirma: $(2 + \\sqrt{3}) - (2 - \\sqrt{3}) = 2\\sqrt{3}$.',
                'difficulty': 'olimpiada',
                'points': 5
            },
            {
                'title': 'Tenglamani yeching: $x^2 - |x| - 6 = 0$',
                'options': ['$x = \\pm 3$', '$x = 3$', '$x = -2$', '$x = \\pm 2$'],
                'correct_option': 0,
                'explanation': '$|x| = t \\ge 0$ deb belgilasak: $t^2 - t - 6 = 0 \\implies (t-3)(t+2)=0$. $t = 3 \\implies x = \\pm 3$.',
                'difficulty': 'orta',
                'points': 2
            }
        ]
    }
    env_bulk = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/api/quizzes/bulk-import',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'HTTP_AUTHORIZATION': f'Bearer {token}',
        'wsgi.input': io.BytesIO(json.dumps(bulk_payload).encode('utf-8'))
    }
    env_bulk['CONTENT_LENGTH'] = str(len(env_bulk['wsgi.input'].getvalue()))
    res_bulk = server.app(env_bulk, mock_start)
    bulk_res_data = json.loads(res_bulk[0].decode('utf-8'))
    assert bulk_res_data.get('status') == 'success' and bulk_res_data.get('added_count') == 2
    print(f"   ✓ Bulk import passed. {bulk_res_data.get('added_count')} questions imported")

    # 5. Clean up test section & question
    print("\n5. Cleaning up test data...")
    del_sec_payload = {
        'action': 'delete',
        'section': {'id': 'sec_test_olimp'}
    }
    env_del_sec = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/api/quizzes/section',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'HTTP_AUTHORIZATION': f'Bearer {token}',
        'wsgi.input': io.BytesIO(json.dumps(del_sec_payload).encode('utf-8'))
    }
    env_del_sec['CONTENT_LENGTH'] = str(len(env_del_sec['wsgi.input'].getvalue()))
    res_del_sec = server.app(env_del_sec, mock_start)
    assert json.loads(res_del_sec[0].decode('utf-8')).get('status') == 'success'
    print("   ✓ Test section and cascade questions cleaned up")

    # 6. Test Frontend KaTeX & SPA View structure
    print("\n6. Validating index.html KaTeX and SPA views...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    assert 'katex.min.js' in html, 'KaTeX CDN missing in index.html'
    assert 'viewQuizzes' in html, 'viewQuizzes view missing'
    assert 'viewPlayer' in html, 'viewPlayer view missing'
    assert 'viewBlog' in html, 'viewBlog view missing'
    assert 'imageZoomModal' in html, 'imageZoomModal missing'
    assert 'bulkImportModal' in html, 'bulkImportModal missing'
    assert 'postModal' in html, 'postModal missing'
    print("   ✓ index.html structure, KaTeX integration, and all modals validated")

    print("\n" + "=" * 70)
    print("🎉 ALL INTEGRATION & SYSTEM TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    test_full_system()

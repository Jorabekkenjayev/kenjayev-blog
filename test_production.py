import os
import sys
import json
import io
import server

def test_wsgi_pipeline():
    print('🧪 Testing Production WSGI Pipeline & Health Check...')

    # 1. Test /health via WSGI
    headers_captured = []
    status_captured = []

    def start_response(status, headers):
        status_captured.append(status)
        headers_captured.extend(headers)

    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/health',
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8080',
        'wsgi.input': io.BytesIO(b'')
    }

    body = server.app(environ, start_response)
    assert '200 OK' in status_captured[0], f'Expected 200 OK, got {status_captured}'
    payload = json.loads(body[0].decode('utf-8'))
    assert payload.get('status') == 'healthy', 'Health check did not report healthy'
    assert 'posts' in payload, 'Posts count missing from health check'
    print('   ✓ /health returned HTTP 200 OK with valid health status')

    # 2. Test /api/data via WSGI
    headers_captured.clear()
    status_captured.clear()
    environ['PATH_INFO'] = '/api/data'
    body = server.app(environ, start_response)
    assert '200 OK' in status_captured[0]
    data = json.loads(body[0].decode('utf-8'))
    assert 'posts' in data, 'Missing posts array in /api/data'
    print(f'   ✓ /api/data returned {len(data["posts"])} posts via WSGI')

    # 3. Test static file serving via WSGI (e.g., robots.txt)
    headers_captured.clear()
    status_captured.clear()
    environ['PATH_INFO'] = '/robots.txt'
    body = server.app(environ, start_response)
    assert '200 OK' in status_captured[0]
    assert b'User-agent' in body[0]
    print('   ✓ /robots.txt dynamic SEO route served successfully via WSGI')

    # 4. Test Environment Variable Overrides
    assert server.PORT > 0, 'Invalid PORT'
    assert len(server.DEFAULT_ADMIN_LOGIN) > 0, 'Admin login missing'
    assert len(server.ADMIN_PASSWORD_HASH) > 0, 'Password hash missing'
    print('   ✓ Environment variables & security configs active')

    print("\n🎉 ALL PRODUCTION & WSGI TESTS PASSED (100% SUCCESS)\n")

if __name__ == '__main__':
    test_wsgi_pipeline()

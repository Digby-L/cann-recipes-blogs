#!/usr/bin/env python3
"""
GitCode CORS Proxy for CANN Recipes Blog
Zero dependencies — uses only Python stdlib.

Usage:
    python proxy.py

Then open index.html in your browser.
"""
import http.server
import urllib.request
import urllib.parse
import json
import base64
import sys

PORT = 8081

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        params = dict(urllib.parse.parse_qsl(
            urllib.parse.urlparse(self.path).query
        ))
        repo   = params.get('repo', '')
        path   = params.get('path', '')
        branch = params.get('branch', 'master')

        if not repo or not path:
            self.send_response(400)
            self._cors_headers()
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Missing repo or path param.\n'
                b'Example: /?repo=cann-recipes-infer'
                b'&path=docs/models/deepseek-r1/deepseek_r1_decode_optimization.md'
                b'&branch=master')
            return

        ns = 'cann'
        repo_id = f'{ns}%2F{repo}'
        api_url = (
            f'https://web-api.gitcode.com/api/v2/projects/{repo_id}/repository/files'
            f'?repoId={urllib.parse.quote(repo_id)}'
            f'&ref={urllib.parse.quote(branch)}'
            f'&file_path={urllib.parse.quote(path)}'
            f'&ref_replace_web={urllib.parse.quote(branch)}'
        )

        req = urllib.request.Request(api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://gitcode.com',
            'Referer': f'https://gitcode.com/{ns}/{repo}/blob/{branch}/{path}',
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            if 'content' not in data:
                raise ValueError('No content field in API response')

            body = base64.b64decode(data['content'])
            content_type = data.get('file_type', 'application/octet-stream')

            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'public, max-age=300')
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            msg = f'Fetch failed: {e}'.encode('utf-8')
            print(f'[proxy] error for {repo}/{path}: {e}', file=sys.stderr)
            self.send_response(502)
            self._cors_headers()
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(msg)

    def log_message(self, fmt, *args):
        print(f'[proxy] {args[0]}')


if __name__ == '__main__':
    server = http.server.HTTPServer(('127.0.0.1', PORT), ProxyHandler)
    print(f'\n  GitCode Proxy running at http://localhost:{PORT}')
    print(f'  Open index.html in your browser.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')

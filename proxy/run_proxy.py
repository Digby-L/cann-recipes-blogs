Run this once in a terminal, then open `index.html` in your browser:

```bash
cd recipe_blog
node proxy.js
```

You should see:
```
GitCode Proxy running at http://localhost:8081
Open index.html in your browser.
```

Keep that terminal open while browsing. The proxy must be running for report content to load.

**Requirements:** Node.js installed (`node --version` to check). If you don't have Node.js, an alternative is Python:

```bash
cd recipe_blog
python3 -c "
import http.server, urllib.request, urllib.parse, json, base64, threading

class H(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
    def do_GET(self):
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        repo, path, branch = q.get('repo',''), q.get('path',''), q.get('branch','master')
        rid = urllib.parse.quote(f'cann/{repo}', safe='')
        url = f'https://web-api.gitcode.com/api/v2/projects/{rid}/repository/files?repoId={urllib.parse.quote(rid)}&ref={branch}&file_path={urllib.parse.quote(path)}&ref_replace_web={branch}'
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Accept':'application/json','Origin':'https://gitcode.com','Referer':f'https://gitcode.com/cann/{repo}/blob/{branch}/{path}'})
        try:
            with urllib.request.urlopen(req) as r:
                d = json.load(r)
                content = base64.b64decode(d['content'])
                self.send_response(200); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Content-Type','text/plain; charset=utf-8'); self.end_headers(); self.wfile.write(content)
        except Exception as e:
            self.send_response(502); self.end_headers(); self.wfile.write(str(e).encode())
    def log_message(self, *a): pass

print('GitCode Proxy running at http://localhost:8081'); http.server.HTTPServer(('127.0.0.1',8081),H).serve_forever()
"

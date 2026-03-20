#!/usr/bin/env python3
"""
Proxy server to fetch raw content from GitCode.
Uses jina.ai to extract content from JavaScript-rendered pages.
Run this alongside the HTML server.
"""
import http.server
import socketserver
import urllib.request
import urllib.error
import urllib.parse
import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8081

# Use jina.ai to extract content from GitCode
JINA_API_URL = "https://r.jina.ai/http://"

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the path /proxy?url=...
        if self.path.startswith('/proxy?'):
            # Extract the URL parameter
            parsed = urllib.parse.parse_qs(self.path[7:])
            if 'url' in parsed:
                target_url = parsed['url'][0]
                try:
                    # Use jina.ai to extract content from GitCode
                    # Replace https:// with http:// for jina.ai compatibility
                    jina_url = JINA_API_URL + target_url.replace('https://', 'http://')

                    req = urllib.request.Request(
                        jina_url,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'text/plain,*/*;q=0.9'
                        }
                    )
                    with urllib.request.urlopen(req, timeout=60) as response:
                        content = response.read().decode('utf-8', errors='ignore')

                        # Parse jina.ai response to extract markdown
                        # Response format: {"data":...} or raw text
                        try:
                            # Try to parse as JSON
                            data = json.loads(content)
                            if isinstance(data, dict) and 'data' in data:
                                content = data['data']
                            elif isinstance(data, dict):
                                # Check for common content fields
                                content = data.get('content') or data.get('text') or str(data)
                        except json.JSONDecodeError:
                            # Not JSON, might be raw text
                            pass

                        # Clean up jina.ai response - extract markdown content
                        content = self.clean_jina_response(content)

                        if not content or len(content.strip()) < 50:
                            raise Exception("No content extracted")

                        self.send_response(200)
                        self.send_header('Content-Type', 'text/plain; charset=utf-8')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Cache-Control', 'no-cache')
                        self.end_headers()
                        self.wfile.write(content.encode('utf-8'))
                except Exception as e:
                    print(f"Error fetching {target_url}: {e}")
                    # Fallback - return error so frontend can show iframe
                    self.send_response(503)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': str(e),
                        'url': target_url
                    }).encode('utf-8'))
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing url parameter'}).encode('utf-8'))
        else:
            # Serve static files
            super().do_GET()

    def clean_jina_response(self, content):
        """Clean up jina.ai extracted content"""
        if not content:
            return ""

        # Remove title and metadata lines at the start
        lines = content.split('\n')
        cleaned_lines = []
        in_metadata = True
        found_content = False

        for i, line in enumerate(lines):
            # Skip title and metadata at the beginning
            if in_metadata:
                if line.strip() == '':
                    continue
                if 'Title:' in line or 'URL Source:' in line or 'Published Time:' in line or 'Markdown Content:' in line:
                    if 'Markdown Content:' in line:
                        in_metadata = False
                    continue
                in_metadata = False

            # Skip lines that are just URL references like [](http://...)
            # But keep lines that have actual content
            if re.match(r'^\[\]\(http[s]?://[^)]+\)$', line.strip()):
                continue

            # Remove reference links like [name](url#section) but keep the text
            line = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', line)

            # Also remove empty reference links
            line = re.sub(r'\[([^]]*)\]\[\]', r'\1', line)

            cleaned_lines.append(line)

        # Remove excessive empty lines
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result.strip()

    def extract_markdown_from_html(self, html):
        """Try to extract markdown content from GitCode's HTML page"""
        # Try multiple extraction strategies

        # Strategy 1: Look for file content in data attributes or script tags
        # GitCode may store content in JSON data
        json_patterns = [
            r'"content"\s*:\s*"([^"]+)"',
            r'"rawContent"\s*:\s*"([^"]+)"',
            r'data-content="([^"]+)"',
        ]

        for pattern in json_patterns:
            match = re.search(pattern, html)
            if match:
                content = match.group(1)
                # Decode unicode escapes
                try:
                    content = bytes(content, 'utf-8').decode('unicode_escape')
                except:
                    pass
                if len(content.strip()) > 100:
                    return content

        # Strategy 2: Look for pre/code tags with file content
        code_patterns = [
            r'<pre[^>]*id="(?:read|file)-content"[^>]*>(.*?)</pre>',
            r'<code[^>]*class="(?:\w+\s+)?file-data[^>]*>(.*?)</code>',
            r'class="blob-code blob-code-inner[^>]*>(.*?)</span>',
        ]

        for pattern in code_patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1)
                # Clean HTML
                content = re.sub(r'<[^>]+>', '', content)
                content = content.replace('&nbsp;', ' ')
                content = content.replace('&lt;', '<')
                content = content.replace('&gt;', '>')
                content = content.replace('&amp;', '&')
                if len(content.strip()) > 50:
                    return content

        # Strategy 3: Try to find any readable text content
        # Remove script and style tags first
        clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)

        # Look for readable paragraphs
        paragraphs = re.findall(r'<p[^>]*>([^<]{50,})</p>', clean, re.IGNORECASE)
        if paragraphs:
            content = '\n\n'.join(paragraphs[:10])  # Limit to first 10 paragraphs
            if len(content) > 200:
                return content

        # If no markdown found, return a message
        return None

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    print(f"Starting proxy server on port {PORT}")
    server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f"Proxy server running at http://localhost:{PORT}")
    print(f"Use: http://localhost:{PORT}/proxy?url=<encoded_url>")
    server.serve_forever()

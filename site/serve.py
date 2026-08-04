#!/usr/bin/env python3
"""Serve the site locally with index.html fallback for document routes."""

import argparse
import functools
import http.server
import os
from pathlib import Path


class SpaHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        requested_path = self.translate_path(self.path.split("?", 1)[0])
        if not os.path.exists(requested_path) and "text/html" in self.headers.get("Accept", "text/html"):
            self.path = "/site/index.html"
        return super().send_head()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    handler = functools.partial(SpaHandler, directory=str(repo_root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"CANN Recipes Blog: http://127.0.0.1:{args.port}/site/")
    server.serve_forever()

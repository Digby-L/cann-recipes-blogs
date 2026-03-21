#!/usr/bin/env python3
"""
Pre-fetch all markdown reports and commit dates from GitCode repos.
Dynamically discovers models and reports via the GitCode repository tree API.

Outputs static JSON files under content/ for GitHub Pages to serve directly.

Structure:
  content/reports/<category>/<model>/<report>.json  — {markdown, commitDate, images: {relPath: base64}}
  content/index.json                                — manifest with discovered models + reports
"""

import json
import os
import re
import sys
import base64
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

GITCODE_API = "https://web-api.gitcode.com/api/v2"
GITCODE_RAW = "https://gitcode.com/cann"
NS = "cann"

# Repo configuration: each category maps to a GitCode repo.
# scanPaths: list of base directories to scan for model subdirectories.
#   Each scanPath is scanned recursively for .md files.
REPO_CONFIG = {
    "Infer": {
        "repo": "cann-recipes-infer",
        "branch": "master",
        "scanPaths": ["docs/models"],
    },
    "Train": {
        "repo": "cann-recipes-train",
        "branch": "master",
        "scanPaths": ["docs"],
    },
    "Spatial Intelligence": {
        "repo": "cann-recipes-spatial-intelligence",
        "branch": "master",
        "scanPaths": ["docs/models"],
    },
    "Embodied Intelligence": {
        "repo": "cann-recipes-embodied-intelligence",
        "branch": "master",
        "scanPaths": ["docs"],
    },
}


def api_request(url):
    """Make an API request and return parsed JSON, or None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None


def list_tree(repo, branch, path):
    """List directory contents via GitCode tree API. Returns list of {name, path, type}."""
    repo_id = urllib.parse.quote(f"{NS}/{repo}", safe="")
    url = (
        f"{GITCODE_API}/projects/{repo_id}/repository/tree"
        f"?ref={urllib.parse.quote(branch)}"
        f"&path={urllib.parse.quote(path)}"
        f"&per_page=100"
    )
    data = api_request(url)
    if data is None:
        return []
    # API returns {content: [...]} or a list
    items = data.get("content", []) if isinstance(data, dict) else data
    return items if isinstance(items, list) else []


def discover_models(repo, branch, scan_path):
    """
    Discover models under a scan path. Returns list of
    {"name": str, "docPath": str (relative to scan_path), "reports": [str]}

    Strategy: list the scan_path directory. For each subdirectory, recursively
    find all .md files. A "model" is any subdirectory that contains at least
    one .md file (directly or nested).
    """
    models = []
    top_items = list_tree(repo, branch, scan_path)

    for item in top_items:
        if item.get("type") != "tree":
            continue
        model_name = item["name"]
        model_path = item["path"]  # e.g. "docs/models/deepseek-r1"

        # Recursively find all .md files under this model directory
        md_files = find_md_files_recursive(repo, branch, model_path)

        if md_files:
            # docPath is relative to scanPath
            doc_path = model_path[len(scan_path):].lstrip("/")
            models.append({
                "name": model_name,
                "docPath": doc_path,
                "fullPath": model_path,
                "reports": md_files,
            })

    return models


def find_md_files_recursive(repo, branch, dir_path, max_depth=5):
    """
    Recursively find all .md files under a directory.
    Returns list of {"file": filename, "dirPath": directory path relative to dir_path's parent}.
    For simplicity, returns list of dicts with full path info.
    """
    if max_depth <= 0:
        return []

    items = list_tree(repo, branch, dir_path)
    results = []

    for item in items:
        if item.get("type") == "blob" and item["name"].endswith(".md"):
            results.append({
                "file": item["name"],
                "fullDir": dir_path,
            })
        elif item.get("type") == "tree" and item["name"] != "figures":
            # Recurse into subdirectories (skip 'figures' dirs)
            sub_results = find_md_files_recursive(repo, branch, item["path"], max_depth - 1)
            results.extend(sub_results)

    return results


def api_fetch_file(repo, branch, file_path):
    """Fetch file content via GitCode API (returns base64-encoded content)."""
    repo_id = urllib.parse.quote(f"{NS}/{repo}", safe="")
    url = (
        f"{GITCODE_API}/projects/{repo_id}/repository/files"
        f"?repoId={repo_id}"
        f"&ref={urllib.parse.quote(branch)}"
        f"&file_path={urllib.parse.quote(file_path)}"
        f"&ref_replace_web={urllib.parse.quote(branch)}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "content" in data:
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] API fetch failed for {file_path}: {e}")
    return None


def raw_fetch_file(repo, branch, file_path):
    """Fetch file content via raw GitCode URL."""
    url = f"{GITCODE_RAW}/{repo}/raw/{branch}/{file_path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            if not text.strip().startswith("<!DOCTYPE") and not text.strip().startswith("<html"):
                return text
    except Exception as e:
        print(f"  [WARN] Raw fetch failed for {file_path}: {e}")
    return None


def fetch_file(repo, branch, file_path):
    """Fetch file content, trying API first then raw."""
    content = api_fetch_file(repo, branch, file_path)
    if content:
        return content
    return raw_fetch_file(repo, branch, file_path)


def fetch_binary_file_base64(repo, branch, file_path):
    """Fetch a binary file (image) and return as base64 data URI."""
    ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else "png"
    mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}
    mime = mime_map.get(ext, "image/png")

    # Method 1: Try GitCode API (returns base64 content)
    repo_id = urllib.parse.quote(f"{NS}/{repo}", safe="")
    api_url = (
        f"{GITCODE_API}/projects/{repo_id}/repository/files"
        f"?repoId={repo_id}"
        f"&ref={urllib.parse.quote(branch)}"
        f"&file_path={urllib.parse.quote(file_path)}"
        f"&ref_replace_web={urllib.parse.quote(branch)}"
    )
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "content" in data:
                b64 = data["content"]
                return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"    [WARN] API image fetch failed: {e}")

    # Method 2: Try raw URL (may not work due to redirects)
    url = f"{GITCODE_RAW}/{repo}/raw/{branch}/{file_path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if not data[:20].strip().startswith(b"<!DOCTYPE") and not data[:20].strip().startswith(b"<html"):
                b64 = base64.b64encode(data).decode("ascii")
                return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"    [WARN] Raw image fetch failed: {e}")
    return None


def fetch_commit_date(repo, branch, file_path):
    """Fetch latest commit date for a file."""
    repo_id = urllib.parse.quote(f"{NS}/{repo}", safe="")
    url = (
        f"{GITCODE_API}/projects/{repo_id}/repository/commits"
        f"?ref_name={urllib.parse.quote(branch)}"
        f"&path={urllib.parse.quote(file_path)}"
        f"&per_page=1"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            commits = data if isinstance(data, list) else data.get("content", [])
            if isinstance(commits, list) and commits:
                date_str = (commits[0].get("committed_date")
                            or commits[0].get("authored_date")
                            or commits[0].get("created_at"))
                if date_str:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    return dt.strftime("%B %d, %Y")
    except Exception as e:
        print(f"  [WARN] Commit date fetch failed for {file_path}: {e}")
    return None


def resolve_path(base_dir, relative_src):
    """Resolve a relative path against a base directory, handling '..' segments."""
    parts = (base_dir.rstrip("/") + "/" + relative_src).split("/")
    out = []
    for p in parts:
        if p == "..":
            if out:
                out.pop()
        elif p and p != ".":
            out.append(p)
    return "/".join(out)


def find_relative_images(md_content):
    """Find all relative image paths in markdown (both ![alt](src) and <img src="...">)."""
    images = set()
    for m in re.finditer(r'!\[[^\]]*\]\((?!https?://)([^)]+)\)', md_content):
        images.add(m.group(1))
    for m in re.finditer(r'<img\b[^>]*\bsrc\s*=\s*"(?!https?://)([^"]+)"', md_content, re.IGNORECASE):
        images.add(m.group(1))
    return images


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "content", "reports")
    os.makedirs(out_dir, exist_ok=True)

    # manifest: category -> list of models, each with reports
    manifest = {}
    total = 0
    success = 0
    failed = 0

    for category, config in REPO_CONFIG.items():
        repo = config["repo"]
        branch = config["branch"]
        scan_paths = config["scanPaths"]

        print(f"\n=== Discovering models for {category} (repo: {repo}) ===")

        # Discover models from all scan paths
        all_models = []
        for scan_path in scan_paths:
            print(f"  Scanning: {scan_path}")
            models = discover_models(repo, branch, scan_path)
            for m in models:
                print(f"    Found model: {m['name']} ({len(m['reports'])} reports)")
                for r in m["reports"]:
                    print(f"      - {r['file']} (in {r['fullDir']})")
            all_models.extend(models)

        if not all_models:
            print(f"  No models found for {category}")
            manifest[category] = {"models": [], "reports": []}
            continue

        cat_models = []
        cat_reports = []
        safe_category = category.replace(" ", "_")

        for model in all_models:
            model_reports = []

            for report_info in model["reports"]:
                total += 1
                report_file = report_info["file"]
                report_dir_full = report_info["fullDir"]
                file_path = f"{report_dir_full}/{report_file}"

                print(f"\n[{total}] Fetching {category}/{model['name']}/{report_file} ...")

                md = fetch_file(repo, branch, file_path)
                if not md:
                    print(f"  FAILED to fetch markdown")
                    failed += 1
                    continue

                # Fetch commit date
                commit_date = fetch_commit_date(repo, branch, file_path)
                print(f"  Commit date: {commit_date or 'N/A'}")

                # Find and fetch images
                rel_images = find_relative_images(md)
                images = {}
                for img_src in rel_images:
                    resolved = resolve_path(report_dir_full, img_src)
                    print(f"  Fetching image: {img_src} -> {resolved}")
                    data_uri = fetch_binary_file_base64(repo, branch, resolved)
                    if data_uri:
                        images[img_src] = data_uri
                        print(f"    OK ({len(data_uri)} chars)")
                    else:
                        print(f"    FAILED")

                # Save report JSON
                safe_model = model["name"]
                report_out_dir = os.path.join(out_dir, safe_category, safe_model)
                os.makedirs(report_out_dir, exist_ok=True)

                report_data = {
                    "markdown": md,
                    "commitDate": commit_date,
                    "images": images,
                }

                out_file = os.path.join(report_out_dir, report_file.replace(".md", ".json"))
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, ensure_ascii=False)

                print(f"  Saved: {out_file} ({len(md)} chars, {len(images)} images)")
                success += 1

                report_entry = {
                    "reportFile": report_file,
                    "commitDate": commit_date,
                    "path": f"content/reports/{safe_category}/{safe_model}/{report_file.replace('.md', '.json')}",
                    "docDir": report_dir_full,
                }
                model_reports.append(report_entry)
                cat_reports.append({**report_entry, "model": model["name"]})

            cat_models.append({
                "name": model["name"],
                "docPath": model["docPath"],
                "reports": [r["reportFile"] for r in model_reports],
            })

        manifest[category] = {
            "repo": repo,
            "branch": branch,
            "models": cat_models,
            "reports": cat_reports,
        }

    # Write manifest
    manifest_path = os.path.join(script_dir, "content", "index.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {success}/{total} reports fetched ({failed} failed)")
    print(f"Manifest: {manifest_path}")

    if failed > 0:
        print(f"WARNING: {failed} reports failed to fetch", file=sys.stderr)


if __name__ == "__main__":
    main()

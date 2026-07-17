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
# GitCode namespace (repo owner). All categories currently live under one repo.
NS = "tian-ccs"
GITCODE_RAW = f"https://gitcode.com/{NS}"
# raw.gitcode.com serves full binary bytes (no auth/headers, no truncation),
# unlike the web-api files endpoint which caps binaries at ~8 KB (is_limited).
GITCODE_RAW_CDN = f"https://raw.gitcode.com/{NS}"

# Full browser-like headers. GitCode's CloudWAF returns HTTP 418 (a challenge
# page) for requests with a bare "Mozilla/5.0" UA, so we mirror what proxy.py
# sends. A generic Referer of https://gitcode.com/ is enough to pass the WAF.
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://gitcode.com",
    "Referer": "https://gitcode.com/",
}

# Repo configuration. Source: GitCode tian-ccs/cann-recipes-docs.
# Layout is 4-level: basePath(Category) / Subcategory / Model / Report.md
#   basePath: the category's top directory in the repo.
#   flat:     True for categories whose .md files sit directly under basePath
#             (no Subcategory/Model layer), e.g. cann_features.
REPO_CONFIG = {
    "Infer":                 {"repo": "cann-recipes-docs", "branch": "main", "basePath": "infer"},
    "Train":                 {"repo": "cann-recipes-docs", "branch": "main", "basePath": "train"},
    "Embodied Intelligence": {"repo": "cann-recipes-docs", "branch": "main", "basePath": "embodied"},
    "CANN Features":         {"repo": "cann-recipes-docs", "branch": "main", "basePath": "cann_features", "flat": True},
}


def api_request(url):
    """Make an API request and return parsed JSON, or None on failure."""
    try:
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
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


def list_md_files(repo, branch, dir_path):
    """List .md files directly inside dir_path (non-recursive). Returns [filename]."""
    return sorted(
        item["name"]
        for item in list_tree(repo, branch, dir_path)
        if item.get("type") == "blob" and item["name"].endswith(".md")
    )


def discover_subcategories(repo, branch, base_path):
    """
    Walk the 4-level layout: base_path / Subcategory / Model / *.md
    Returns a list of subcategories:
      [{ "name": str,
         "models": [{ "name": str,
                      "docPath": "<sub>/<model>",   # relative to base_path
                      "reports": [filename, ...] }] }]
    A Model is any directory under a Subcategory that contains .md files
    (the 'figures' image dir is skipped).
    """
    subcategories = []
    for sub in list_tree(repo, branch, base_path):
        if sub.get("type") != "tree":
            continue
        sub_name = sub["name"]
        models = []
        for model in list_tree(repo, branch, sub["path"]):
            if model.get("type") != "tree" or model["name"] == "figures":
                continue
            reports = list_md_files(repo, branch, model["path"])
            if reports:
                models.append({
                    "name": model["name"],
                    "docPath": f"{sub_name}/{model['name']}",
                    "reports": reports,
                })
        if models:
            subcategories.append({"name": sub_name, "models": models})
    return subcategories


def discover_flat_reports(repo, branch, base_path):
    """Flat category (e.g. cann_features): .md files directly under base_path."""
    return list_md_files(repo, branch, base_path)


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
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
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
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
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

    # Method 1: raw.gitcode.com CDN — serves full bytes, no truncation.
    cdn_url = f"{GITCODE_RAW_CDN}/{repo}/raw/{branch}/{file_path}"
    try:
        req = urllib.request.Request(cdn_url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if not data[:20].strip().startswith(b"<!DOCTYPE") and not data[:20].strip().startswith(b"<html"):
                b64 = base64.b64encode(data).decode("ascii")
                return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"    [WARN] CDN image fetch failed: {e}")

    # Method 2 (fallback): GitCode files API — NOTE truncates binaries to ~8 KB
    # (is_limited), so large images come back corrupt. Only used if the CDN host
    # is unreachable; a truncated image is better than a broken link.
    repo_id = urllib.parse.quote(f"{NS}/{repo}", safe="")
    api_url = (
        f"{GITCODE_API}/projects/{repo_id}/repository/files"
        f"?repoId={repo_id}"
        f"&ref={urllib.parse.quote(branch)}"
        f"&file_path={urllib.parse.quote(file_path)}"
        f"&ref_replace_web={urllib.parse.quote(branch)}"
    )
    try:
        req = urllib.request.Request(api_url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "content" in data:
                b64 = data["content"]
                return f"data:{mime};base64,{b64}"
    except Exception as e:
        print(f"    [WARN] API image fetch failed: {e}")
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
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
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


def process_report(repo, branch, safe_category, model_key, doc_dir, report_file, out_dir, idx):
    """Fetch one report's markdown + images + commit date and save a report JSON.
      doc_dir     : full repo dir containing the .md (e.g. 'infer/llm/deepseek_r1')
      model_key   : subdir under the category for the saved JSON (model name, or
                    the category itself for flat categories)
    Returns (commit_date, site_relative_json_path) on success, or (None, None).
    """
    file_path = f"{doc_dir}/{report_file}" if doc_dir else report_file
    print(f"\n[{idx}] Fetching {file_path} ...")
    md = fetch_file(repo, branch, file_path)
    if not md:
        print("  FAILED to fetch markdown")
        return None, None

    commit_date = fetch_commit_date(repo, branch, file_path)
    print(f"  Commit date: {commit_date or 'N/A'}")

    images = {}
    for img_src in find_relative_images(md):
        resolved = resolve_path(doc_dir, img_src)
        data_uri = fetch_binary_file_base64(repo, branch, resolved)
        if data_uri:
            images[img_src] = data_uri
        else:
            print(f"    [WARN] image FAILED: {img_src}")

    report_out_dir = os.path.join(out_dir, safe_category, model_key)
    os.makedirs(report_out_dir, exist_ok=True)
    out_file = os.path.join(report_out_dir, report_file.replace(".md", ".json"))
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"markdown": md, "commitDate": commit_date, "images": images}, f, ensure_ascii=False)
    print(f"  Saved: {out_file} ({len(md)} chars, {len(images)} images)")

    site_path = f"content/reports/{safe_category}/{model_key}/{report_file.replace('.md', '.json')}"
    return commit_date, site_path


def _fetch_reports(repo, branch, safe_category, model_key, doc_dir, report_files, out_dir, counts):
    """Process a list of report filenames; update counts in place.
    Returns the list of report filenames that were fetched successfully."""
    kept = []
    for report_file in report_files:
        counts["total"] += 1
        commit_date, site_path = process_report(
            repo, branch, safe_category, model_key, doc_dir, report_file, out_dir, counts["total"])
        if site_path is not None:
            counts["success"] += 1
            kept.append(report_file)
        else:
            counts["failed"] += 1
    return kept


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "content", "reports")
    os.makedirs(out_dir, exist_ok=True)

    # manifest: category -> 4-level tree (or flat), matching content/index.json schema
    manifest = {}
    counts = {"total": 0, "success": 0, "failed": 0}

    for category, config in REPO_CONFIG.items():
        repo = config["repo"]
        branch = config["branch"]
        base_path = config["basePath"]
        is_flat = config.get("flat", False)
        safe_category = category.replace(" ", "_")

        print(f"\n=== Discovering {category} (repo: {repo}, base: {base_path}, flat={is_flat}) ===")

        cat_entry = {"ns": NS, "repo": repo, "branch": branch, "basePath": base_path}

        if is_flat:
            report_files = discover_flat_reports(repo, branch, base_path)
            print(f"  Found {len(report_files)} flat reports")
            cat_entry["flat"] = True
            cat_entry["reports"] = _fetch_reports(
                repo, branch, safe_category, safe_category, base_path, report_files, out_dir, counts)
        else:
            subs = discover_subcategories(repo, branch, base_path)
            print(f"  Found {len(subs)} subcategories")
            out_subs = []
            for sub in subs:
                out_models = []
                for model in sub["models"]:
                    doc_dir = f"{base_path}/{model['docPath']}"
                    kept = _fetch_reports(
                        repo, branch, safe_category, model["name"], doc_dir,
                        model["reports"], out_dir, counts)
                    if kept:
                        out_models.append({
                            "name": model["name"],
                            "docPath": model["docPath"],
                            "reports": kept,
                        })
                if out_models:
                    out_subs.append({"name": sub["name"], "models": out_models})
            cat_entry["subcategories"] = out_subs

        manifest[category] = cat_entry

    total, success, failed = counts["total"], counts["success"], counts["failed"]

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

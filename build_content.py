#!/usr/bin/env python3
"""
Build a lightweight report metadata manifest from GitCode repositories.
Dynamically discovers models and reports via the GitCode repository tree API.

Report bodies and images are cached only when PREFETCH_REPORTS=1 (the Pages
build); normal local builds keep using remote GitCode content. Display titles
are derived in the browser by removing the .md suffix from each filename.

Output:
  content/index.json — manifest with discovered models and report filenames
"""

import json
import os
import re
import sys
import base64
import hashlib
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
PREFETCH_REPORTS = os.environ.get("PREFETCH_REPORTS") == "1"
REPORT_CACHE_DIR = None
ASSET_CACHE_DIR = None

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

SOURCE_REPOS = {
    "Infer": ("cann-recipes-infer", "https://gitcode.com/cann/cann-recipes-infer"),
    "Train": ("cann-recipes-train", "https://gitcode.com/cann/cann-recipes-train"),
    "Embodied Intelligence": ("cann-recipes-embodied-ai", "https://gitcode.com/cann/cann-recipes-embodied-ai"),
    "CANN Features": ("cann-recipes-docs", "https://gitcode.com/tian-ccs/cann-recipes-docs"),
}

# Some aggregated Markdown files were copied without their adjacent figure
# directory. Keep an explicit link to the canonical upstream image directory.
IMAGE_SOURCE_FALLBACKS = {
    "infer/multimodal/hunyuan_image_3_0/figures/": (
        "cann", "cann-recipes-infer", "master", "docs/models/hunyuan-image-3.0/figures/"
    ),
    "train/pretrain/deepseek_v3_2/figures/": (
        "cann", "cann-recipes-train", "master", "docs/llm_pretrain/figures/"
    ),
    "train/rl/qwen3_235b/figures/": (
        "cann", "cann-recipes-train", "master", "docs/llm_rl/figures/"
    ),
    "embodied/": (
        "cann", "cann-recipes-embodied-ai", "master", "docs/"
    ),
    "models/longcat-flash/figures/": (
        "cann", "cann-recipes-infer", "master", "docs/models/longcat_flash/figures/"
    ),
}

TAG_RULES = [
    ("Prefill", ("prefill",)),
    ("Decode", ("decode",)),
    ("RL", ("_rl_", "rl_train")),
    ("Pretrain", ("pre_train", "pretrain")),
    ("Inference", ("inference", "_infer_")),
    ("Operator", ("operator", "ascendc", "pypto", "tilelang", "autofuse", "_mhc_")),
    ("Communication", ("shmem", "communication")),
    ("Evaluation", ("evaluation", "accurancy", "accuracy")),
    ("3D Vision", ("gaussian", "hunyuan3d", "vggt", "3d")),
    ("Image Generation", ("hunyuan_image",)),
    ("Recommendation", ("hstu",)),
    ("Manipulation", ("gr00t", "pi0")),
    ("Navigation", ("alpamayo",)),
    ("World Model", ("cosmos",)),
    ("Load Balance", ("load_balance",)),
    ("Culling", ("culling",)),
    ("Graph", ("graph",)),
    ("Prefetch", ("prefetch",)),
    ("Multi Stream", ("multi_stream",)),
    ("Super Kernel", ("super_kernel",)),
]


def extract_first_image(markdown_content):
    """Return the first Markdown or HTML image source in a report."""
    patterns = (
        r'!\[[^\]]*\]\((?:<)?([^)>\s]+)(?:>)?(?:\s+["\'][^"\']*["\'])?\)',
        r'<img\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\']',
    )
    matches = []
    for pattern in patterns:
        match = re.search(pattern, markdown_content, re.IGNORECASE)
        if match:
            matches.append((match.start(), match.group(1)))
    return min(matches, default=(None, None), key=lambda item: item[0])[1]


def report_entry(category, model_key, repo, branch, doc_dir, report_file):
    """Build tags and a remote cover URL without persisting report content."""
    normalized = report_file.lower()
    tags = [tag for tag, needles in TAG_RULES if any(needle in normalized for needle in needles)]
    file_path = f"{doc_dir}/{report_file}" if doc_dir else report_file
    markdown = fetch_file(repo, branch, file_path)
    images = {}
    if PREFETCH_REPORTS:
        if not markdown:
            raise RuntimeError(f"Failed to prefetch required report: {file_path}")
        safe_category = category.replace(" ", "_")
        safe_model = model_key.replace(" ", "_")
        report_dir = os.path.join(REPORT_CACHE_DIR, safe_category, safe_model)
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, report_file.replace(".md", ".json"))
        images = cache_report_images(markdown, repo, branch, doc_dir)
        with open(report_path, "w", encoding="utf-8") as report_output:
            json.dump({"markdown": markdown, "images": images}, report_output, ensure_ascii=False)
    image_src = extract_first_image(markdown) if markdown else None
    cover_image = None
    if image_src:
        if image_src in images:
            cover_image = images[image_src]
        elif image_src.startswith(("http://", "https://", "data:")):
            cover_image = image_src
        else:
            resolved = resolve_path(doc_dir, urllib.parse.unquote(image_src.split("?", 1)[0]))
            cover_image = f"{GITCODE_RAW_CDN}/{repo}/raw/{branch}/{resolved}"
    source_repo, source_repo_url = SOURCE_REPOS[category]
    return {
        "file": report_file,
        "tags": tags,
        "coverImage": cover_image,
        "sourceRepo": source_repo,
        "sourceRepoUrl": source_repo_url,
        "sourcePath": file_path,
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


def find_image_sources(markdown):
    """Return image sources from Markdown and HTML, preserving source spelling."""
    sources = set()
    markdown_pattern = r'!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+["\'][^"\']*["\'])?\s*\)'
    for match in re.finditer(markdown_pattern, markdown):
        sources.add(match.group(1) or match.group(2))
    html_pattern = r'<img\b[^>]*\bsrc\s*=\s*(["\'])(.*?)\1'
    for match in re.finditer(html_pattern, markdown, re.IGNORECASE):
        sources.add(match.group(2))
    return sorted(src for src in sources if src and not src.startswith(("data:", "#")))


def fetch_binary_url(url):
    """Download complete image bytes, rejecting HTML error/challenge pages."""
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
        content_type = resp.headers.get_content_type()
    prefix = data[:256].lstrip().lower()
    if not data or prefix.startswith((b"<!doctype", b"<html")):
        raise RuntimeError("response is empty or HTML")
    if not content_type.startswith("image/") and not url.lower().split("?", 1)[0].endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp")):
        raise RuntimeError(f"unexpected content type: {content_type}")
    return data


def cache_report_images(markdown, repo, branch, doc_dir):
    """Cache every report image in the Pages artifact and return its src map."""
    images = {}
    for src in find_image_sources(markdown):
        decoded_src = urllib.parse.unquote(src)
        parsed = urllib.parse.urlparse(decoded_src)
        if parsed.scheme in ("http", "https"):
            source_url = decoded_src
            clean_path = parsed.path
            raw_match = re.match(
                r'^/(?:[^/]+)/([^/]+)/raw/([^/]+)/(.*)$', clean_path
            ) if parsed.netloc in ("gitcode.com", "raw.gitcode.com") else None
            if raw_match:
                source_repo, source_branch, source_path = raw_match.groups()
                source_url = f"{GITCODE_RAW_CDN}/{source_repo}/raw/{source_branch}/{source_path}"
                asset_rel = f"{source_repo}/{source_path}"
            else:
                ext = os.path.splitext(clean_path)[1].lower()
                if not re.fullmatch(r'\.[a-z0-9]{1,5}', ext):
                    ext = ".img"
                digest = hashlib.sha256(decoded_src.encode("utf-8")).hexdigest()
                asset_rel = f"external/{digest}{ext}"
        elif parsed.scheme:
            continue
        else:
            source_path = resolve_path(doc_dir, parsed.path)
            source_url = f"{GITCODE_RAW_CDN}/{repo}/raw/{branch}/{urllib.parse.quote(source_path, safe='/')}"
            asset_rel = f"{repo}/{source_path}"

        asset_rel = asset_rel.replace("\\", "/").lstrip("/")
        destination = os.path.abspath(os.path.join(ASSET_CACHE_DIR, *asset_rel.split("/")))
        if os.path.commonpath((ASSET_CACHE_DIR, destination)) != ASSET_CACHE_DIR:
            raise RuntimeError(f"Unsafe image path: {src}")
        try:
            if not os.path.isfile(destination) or os.path.getsize(destination) == 0:
                try:
                    data = fetch_binary_url(source_url)
                except urllib.error.HTTPError as primary_error:
                    fallback = next(
                        ((prefix, value) for prefix, value in IMAGE_SOURCE_FALLBACKS.items()
                         if source_path.startswith(prefix)),
                        None,
                    )
                    if not fallback or primary_error.code != 404:
                        raise
                    source_prefix, fallback_config = fallback
                    fallback_ns, fallback_repo, fallback_branch, fallback_dir = fallback_config
                    fallback_path = fallback_dir + source_path[len(source_prefix):]
                    fallback_url = (
                        f"https://raw.gitcode.com/{fallback_ns}/{fallback_repo}/raw/"
                        f"{fallback_branch}/{urllib.parse.quote(fallback_path, safe='/')}"
                    )
                    data = fetch_binary_url(fallback_url)
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                with open(destination, "wb") as image_output:
                    image_output.write(data)
            images[src] = "content/assets/" + urllib.parse.quote(asset_rel, safe="/")
        except Exception as error:
            raise RuntimeError(f"Failed to cache image {src} from {source_url}: {error}") from error
    return images


def main():
    global REPORT_CACHE_DIR, ASSET_CACHE_DIR
    script_dir = os.path.dirname(os.path.abspath(__file__))
    REPORT_CACHE_DIR = os.path.join(script_dir, "content", "reports")
    ASSET_CACHE_DIR = os.path.join(script_dir, "content", "assets")
    # manifest: category -> 4-level tree (or flat), matching content/index.json schema
    manifest = {}
    for category, config in REPO_CONFIG.items():
        repo = config["repo"]
        branch = config["branch"]
        base_path = config["basePath"]
        is_flat = config.get("flat", False)
        print(f"\n=== Discovering {category} (repo: {repo}, base: {base_path}, flat={is_flat}) ===")

        cat_entry = {"ns": NS, "repo": repo, "branch": branch, "basePath": base_path}

        if is_flat:
            report_files = discover_flat_reports(repo, branch, base_path)
            if PREFETCH_REPORTS and not report_files:
                raise RuntimeError(f"No reports discovered for required category: {category}")
            print(f"  Found {len(report_files)} flat reports")
            cat_entry["flat"] = True
            cat_entry["reports"] = [
                report_entry(category, category, repo, branch, base_path, report_file)
                for report_file in report_files
            ]
        else:
            subs = discover_subcategories(repo, branch, base_path)
            if PREFETCH_REPORTS and not subs:
                raise RuntimeError(f"No subcategories discovered for required category: {category}")
            print(f"  Found {len(subs)} subcategories")
            out_subs = []
            for sub in subs:
                out_models = []
                for model in sub["models"]:
                    if model["reports"]:
                        out_models.append({
                            "name": model["name"],
                            "docPath": model["docPath"],
                            "reports": [
                                report_entry(
                                    category, model["name"], repo, branch,
                                    f"{base_path}/{model['docPath']}", report_file
                                )
                                for report_file in model["reports"]
                            ],
                        })
                if out_models:
                    out_subs.append({"name": sub["name"], "models": out_models})
            cat_entry["subcategories"] = out_subs

        manifest[category] = cat_entry

    # Write manifest
    manifest_path = os.path.join(script_dir, "content", "index.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("\nDone! Report metadata manifest generated")
    print(f"Manifest: {manifest_path}")
    if PREFETCH_REPORTS:
        print(f"Static report cache: {REPORT_CACHE_DIR}")


if __name__ == "__main__":
    main()

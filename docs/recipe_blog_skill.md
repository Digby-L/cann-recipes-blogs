# Recipe Blog Website - Technical Documentation

> Last updated: 2026-03-21 — pre-fetch architecture, dynamic discovery, GitHub Pages deployment, image/TOC fixes.

## Overview

The CANN Recipes Blog website displays tech reports from 4 GitCode repositories. Reports are **pre-fetched at build time** into static JSON files, eliminating the need for a local proxy or CORS workarounds when deployed to GitHub Pages.

## Source Repositories

| Category | GitCode Repo | Scan Paths |
|----------|-------------|------------|
| Infer | cann/cann-recipes-infer | `docs/models` |
| Train | cann/cann-recipes-train | `docs` |
| Spatial Intelligence | cann/cann-recipes-spatial-intelligence | `docs/models` |
| Embodied Intelligence | cann/cann-recipes-embodied-intelligence | `docs` |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  GitHub Actions (daily cron + push to main)                     │
│                                                                 │
│  1. Checkout repo                                               │
│  2. Run build_content.py                                        │
│     ├── Discover models via GitCode tree API                    │
│     ├── Fetch markdown + images + commit dates                  │
│     └── Write content/index.json + content/reports/**/*.json    │
│  3. Deploy entire repo (incl. content/) to GitHub Pages         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Browser (index.html on GitHub Pages)                           │
│                                                                 │
│  1. loadManifest() fetches content/index.json                   │
│  2. loadModelsFromManifest() populates sidebar from manifest    │
│     (falls back to hardcoded repoModels if manifest unavailable)│
│  3. fetchReportContent() loads pre-fetched JSON (Method 0)      │
│     Falls back to: proxy → corsproxy.io → raw GitCode URL       │
│  4. renderMarkdownWithImages() injects base64 images,           │
│     then renderMarkdown() via marked.js                         │
└─────────────────────────────────────────────────────────────────┘
```

## Content Pre-fetch System

### `build_content.py`

Dynamically discovers all models and reports via the GitCode repository tree API. No hardcoded model lists — new reports are picked up automatically.

**Key functions:**
| Function | Purpose |
|----------|---------|
| `list_tree(repo, branch, path)` | List directory contents via GitCode tree API |
| `discover_models(repo, branch, scan_path)` | Find model subdirectories containing `.md` files |
| `find_md_files_recursive(repo, branch, dir_path)` | Recursively find all `.md` files (skips `figures/` dirs) |
| `fetch_file(repo, branch, file_path)` | Fetch markdown content (API first, then raw URL fallback) |
| `fetch_binary_file_base64(repo, branch, file_path)` | Fetch images as base64 data URIs via GitCode API |
| `fetch_commit_date(repo, branch, file_path)` | Get latest commit date for a file |

**Output structure:**
```
content/
├── index.json                                    # Manifest
└── reports/
    ├── Infer/
    │   ├── deepseek-r1/
    │   │   ├── deepseek_r1_decode_optimization.json
    │   │   └── deepseek_r1_prefill_optimization.json
    │   └── ...
    ├── Train/
    ├── Spatial_Intelligence/
    └── Embodied_Intelligence/
```

**Report JSON format:**
```json
{
  "markdown": "# Full markdown content...",
  "commitDate": "March 15, 2026",
  "images": {
    "./figures/arch.png": "data:image/png;base64,iVBOR...",
    "../common/images/flow.png": "data:image/png;base64,..."
  }
}
```

**Manifest (`content/index.json`) format:**
```json
{
  "Infer": {
    "repo": "cann-recipes-infer",
    "branch": "master",
    "models": [
      { "name": "deepseek-r1", "docPath": "deepseek-r1", "reports": ["report.md"] }
    ],
    "reports": [
      { "reportFile": "report.md", "commitDate": "March 15, 2026",
        "path": "content/reports/Infer/deepseek-r1/report.json",
        "docDir": "docs/models/deepseek-r1", "model": "deepseek-r1" }
    ]
  }
}
```

### Why images are base64-encoded

GitCode's raw URLs (`gitcode.com/cann/.../raw/...`) return HTML pages, not binary data (the site is an SPA). The GitCode file API returns base64-encoded content, so `build_content.py` fetches images via the API and embeds them as `data:` URIs directly in the report JSON.

## GitHub Actions Deployment

### Workflow (`.github/workflows/deploy.yml`)

- **Triggers:** push to `main`, daily cron at 2:17 AM UTC, manual dispatch
- **Permissions:** `contents: read`, `pages: write`, `id-token: write`
- **No git push** — the workflow does NOT commit or push back to the repo (avoids branch protection conflicts)
- **Graceful fallback:** if `build_content.py` fails, committed `content/` is used as baseline

```yaml
- name: Fetch content from GitCode repos
  run: |
    python build_content.py || echo "WARNING: GitCode fetch failed, using committed content"
```

### Content freshness strategy

1. **Committed baseline:** `content/` directory is committed to git (not in `.gitignore`)
2. **Build-time refresh:** GitHub Actions runs `build_content.py` which overwrites `content/` with fresh data
3. **Daily auto-refresh:** Cron schedule re-fetches content even without code pushes
4. The deployed GitHub Pages site always has the latest content from the most recent successful build

## Frontend (`index.html`)

### Design
- **Color Theme:** Primary #E77A1D (orange), Background #F9F8F6 (beige), Text #3E2723 (coffee brown)
- **Fonts:** Public Sans (display), Inter (body)
- **Icons:** Material Symbols Outlined (Google Fonts)
- **Framework:** Tailwind CSS (CDN)
- **Markdown:** marked.js v4.3.0, highlight.js for code blocks
- **Effects:** Glassmorphism cards with backdrop-filter blur

### Key Features

1. **Left Sidebar Navigation** — Collapsible (w-72), categories with nested models, toggle button on right edge
2. **Three Main Views** — Home (recent + popular reports), Category (grid), Report (full article)
3. **Search** — Filters sidebar and content by keyword
4. **Floating Nav** — Back-to-top / go-to-bottom buttons (fixed bottom-right)
5. **Subscribe** — Opens `https://mailweb.cann.osinfra.cn/mailman3/lists/recipes.cann.osinfra.cn/`
6. **Report Metadata** — Shows latest commit date (from manifest or GitCode API)

### Key JavaScript Functions

| Function | Purpose |
|----------|---------|
| `loadManifest()` | Fetches `content/index.json`, caches as `prefetchedManifest` |
| `loadModelsFromManifest()` | Populates `repoModels` from manifest (keeps hardcoded fallback if manifest empty) |
| `fetchReportContent(cat, model, file)` | Method 0: pre-fetched JSON → Method 1: proxy → Method 2: corsproxy.io → Method 3: raw URL |
| `renderMarkdownWithImages(md, images)` | Replaces relative image paths with base64 data URIs from pre-fetched data |
| `renderMarkdown(md, repo, branch, dir)` | marked.js rendering with custom heading IDs, link targets, image URL rewriting |
| `slugify(text)` | Generates heading IDs for TOC/chapter jumper (handles CJK characters) |
| `showReport(cat, model, title, file)` | Displays report with breadcrumb, fetches commit date |
| `showCategory(category)` | Renders all models for a category (with or without reports) |
| `toggleSidebar()` | Animate sidebar show/hide |
| `getPrefetchedPath(cat, model, file)` | Computes `content/reports/<Category>/<model>/<file>.json` path |

### Content Fetching Chain

```
fetchReportContent(category, model, reportFile)
  │
  ├── Method 0: Pre-fetched static JSON (GitHub Pages)
  │   GET content/reports/<Category>/<model>/<report>.json
  │   ├── renderMarkdownWithImages(json.markdown, json.images)
  │   └── Returns rendered HTML
  │
  ├── Method 1: Local proxy (development only)
  │   GET http://localhost:8081/?repo=...&branch=...&path=...
  │
  ├── Method 2: CORS proxy fallback
  │   GET https://corsproxy.io/?url=...
  │
  └── Method 3: Raw GitCode URL (unreliable — returns HTML)
      GET https://gitcode.com/cann/{repo}/raw/{branch}/{path}
```

### Markdown Rendering Pipeline

1. `renderMarkdownWithImages(md, images)` — Replaces relative image paths (`./figures/x.png`) with pre-fetched base64 `data:` URIs
2. `renderMarkdown(md, repo, branch, baseDir)` — marked.js with custom renderer:
   - **Headings:** Custom `heading` renderer generates `id` attributes via `slugify()` for TOC/anchor links
   - **Links:** Open in `_blank` with `noopener`
   - **Images:** Rewrites remaining relative paths to proxy URLs (skips `https://`, `http://`, and `data:` URIs)
   - **HTML `<img>` tags:** Same rewriting with `data:` exclusion to avoid clobbering pre-fetched base64 images

Critical regex for image rewriting (avoids double-rewriting base64):
```javascript
// Markdown images — skip absolute URLs and data: URIs
md = md.replace(/!\[([^\]]*)\]\((?!https?:\/\/|data:)([^)]+)\)/g, ...);
// HTML <img> tags — skip absolute URLs and data: URIs
md = md.replace(/<img\b([^>]*)\bsrc\s*=\s*"(?!https?:\/\/|data:)([^"]+)"([^>]*)>/gi, ...);
```

## File Structure

```
cann-recipes-blogs/
├── .github/workflows/deploy.yml   # GitHub Pages deployment workflow
├── .gitignore                     # Ignores __pycache__, .claude/
├── .nojekyll                      # Bypass Jekyll processing on GitHub Pages
├── index.html                     # Main website (single-page app)
├── build_content.py               # Pre-fetch script (runs in CI)
├── content/
│   ├── index.json                 # Manifest (models + reports metadata)
│   └── reports/                   # Pre-fetched report JSON files
│       ├── Infer/
│       ├── Train/
│       ├── Spatial_Intelligence/
│       └── Embodied_Intelligence/
├── docs/
│   ├── recipe_blog_skill.md       # This documentation
│   └── blog.md                    # Original task specification
├── proxy/                         # Local proxy implementations (dev only)
│   ├── proxy.js
│   ├── proxy_server.py
│   └── run_proxy.py
├── proxy.py                       # Simple local proxy (dev only)
├── start_proxy.bat                # Windows proxy launcher
├── start_proxy.sh                 # Linux/Mac proxy launcher
├── assets/                        # Static assets
└── README.md
```

## Bug Fixes History

### 2026-03-21 (Pre-fetch + deployment overhaul)

| Bug | Fix |
|-----|-----|
| Visitors must run local proxy to load reports | Pre-fetch content at build time; serve static JSON from GitHub Pages |
| New reports not picked up automatically | Dynamic discovery via GitCode tree API in `build_content.py` |
| Images always fail to load | Embed images as base64 data URIs; fix regex to skip `data:` URIs |
| No reports shown after deployment (empty repoModels) | Hardcoded fallback + manifest-driven loading via `loadModelsFromManifest()` |
| GitHub Actions deploy fails (branch protection) | Removed git push; deploy only uses `contents: read` permission |
| GitCode commit API returns `{content: [...]}` not list | Handle both list and object response formats |
| Chapter jumper / TOC not working | Custom `heading` renderer with `slugify()` for anchor IDs |
| Sidebar toggle arrow in wrong position | Moved to right edge with `translate-x-1/2` |
| Subscribe button missing action | Opens mailman3 mailing list URL |
| "Technical Writer" text shown | Replaced with dynamic commit date display |

### 2026-03-18 (Initial fixes)

| Bug | Fix |
|-----|-----|
| Slow content via jina.ai proxy | Direct GitCode API fetch |
| Broken images and code blocks | marked.js replaces regex renderer |
| Wrong title | Changed to "CANN RECIPES BLOGS" |
| Missing models in category view | `showCategory()` renders all models |

## Local Development

```bash
# Serve locally (reports load from pre-fetched content/)
python -m http.server 8080

# Or with live proxy for real-time GitCode access
python proxy.py        # starts on http://localhost:8081
python -m http.server 8080  # in another terminal

# Re-fetch content manually
python build_content.py
```

## How Content Stays Updated

1. New reports are added to GitCode repos by upstream authors
2. Daily cron (2:17 AM UTC) triggers GitHub Actions workflow
3. `build_content.py` discovers new models/reports via tree API
4. Fresh `content/` is built and deployed to GitHub Pages
5. No manual intervention needed — fully automatic

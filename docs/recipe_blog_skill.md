# Recipe Blog Website - Technical Documentation

> Last updated: 2026-06-23 — added feature inventory chapter.

## Overview

The CANN Recipes Blog website displays tech reports from 4 GitCode repositories. Reports are **pre-fetched at build time** into static JSON files, eliminating the need for a local proxy or CORS workarounds when deployed to GitHub Pages.

## Supported Features

### 1. Content Browsing

| Feature | Description |
|---------|-------------|
| **Four-category navigation** | Reports organized under Infer, Train, Spatial Intelligence, Embodied Intelligence |
| **Hierarchical sidebar** | Collapsible left sidebar (w-72) with categories → models → reports tree |
| **Dynamic model discovery** | `build_content.py` auto-discovers new models/reports from GitCode repos via tree API — no hardcoded lists |
| **Three main views** | Home (recent + popular), Category (card grid), Report (full article) |
| **Home page recommendations** | "Recent Reports" (sorted by commitDate) and "Popular Reports" sections on landing page |
| **Breadcrumb navigation** | Category → Model → Report path displayed in report view |

### 2. Report Rendering

| Feature | Description |
|---------|-------------|
| **Markdown rendering** | Full markdown via marked.js v4.3.0 (headings, lists, tables, blockquotes, links) |
| **Code syntax highlighting** | highlight.js with Atom One Dark theme, supports all major languages |
| **Copy-to-clipboard** | Each code block has a "Copy" button with visual feedback |
| **Embedded images** | Images pre-fetched as base64 data URIs, no external requests at view time（⚠️ 部分图片渲染异常，待修复，详见 requirements.md 3.1.3） |
| **Commit date display** | Shows latest commit date per report (from manifest or GitCode API) |
| **Heading anchors** | Custom `slugify()` generates IDs for CJK + Latin headings, supporting TOC/anchor links |

### 3. Search

| Feature | Description |
|---------|-------------|
| **Keyword search** | Filters by model name, report title, and category |
| **Real-time results** | Results displayed as card grid with count ("N results for ...") |
| **No-result fallback** | Friendly message when nothing matches |

### 4. UI / UX

| Feature | Description |
|---------|-------------|
| **Glassmorphism design** | Cards and sidebar use backdrop-filter blur + translucent backgrounds |
| **Responsive grid** | 2-3 report cards per row with hover scale/shadow effects |
| **Sidebar toggle** | Hide/show button on right edge with smooth width animation |
| **Floating nav buttons** | Fixed bottom-right: back-to-top and go-to-bottom |
| **Custom scrollbar** | Orange-tinted thin scrollbar on WebKit browsers |
| **Fade-in animations** | View transitions use CSS keyframe `fadeIn` |
| **Material icons** | Google Material Symbols Outlined for all UI icons |

### 5. Deployment & CI/CD

| Feature | Description |
|---------|-------------|
| **GitHub Pages hosting** | Static site deployed via GitHub Actions |
| **Daily auto-refresh** | Cron at 2:17 AM UTC re-fetches content from upstream repos |
| **Graceful fallback** | If `build_content.py` fails, committed `content/` is used as baseline |
| **No git push needed** | Workflow uses `actions/deploy-pages`, avoids branch protection issues |
| **Manual dispatch** | Can trigger rebuild manually from GitHub Actions UI |

### 6. Development Support

| Feature | Description |
|---------|-------------|
| **Local proxy** | `proxy.py` (Python, zero-dependency, localhost:8081) for live GitCode access |
| **Multi-method fetch chain** | Pre-fetched JSON → local proxy → corsproxy.io → raw URL (4 fallbacks) |
| **Cross-platform launchers** | `start_proxy.sh` (Linux/Mac) and `start_proxy.bat` (Windows) |
| **Static serve mode** | Works with any HTTP server (`python -m http.server`) using pre-fetched content |

### 7. Subscriptions & External Links

| Feature | Description |
|---------|-------------|
| **Subscribe button** | Opens CANN recipes mailing list (mailman3) |
| **Browse Repo links** | Models without dedicated reports link to their GitCode repo folder |
| **External link handling** | All links open in new tab with `rel="noopener"` |

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

---

## 开发约束（DO NOT）

以下规则为硬性约束，所有对本项目的修改必须遵守：

| # | 禁止事项 | 原因 |
|---|----------|------|
| 1 | 引入 npm / node / webpack / vite 等构建工具 | 项目定位为零构建静态站，部署环境只有 Python + HTTP server |
| 2 | 将 `index.html` 拆分为多个文件 | 单文件 SPA 是核心设计决策，简化部署链路 |
| 3 | 给 `build_content.py` 添加第三方 pip 依赖 | CI 环境无 `pip install` 步骤，脚本必须纯标准库运行 |
| 4 | 引入需要后端/数据库的功能 | 纯静态站，GitHub/GitCode Pages 无服务端能力 |
| 5 | 硬编码模型列表（绕过 manifest 动态发现） | 动态发现是核心设计，不可退化为手动维护 |
| 6 | 删除 4 级内容加载 fallback 中的任何一级 | 保证开发/部署/离线等各种环境下内容可加载 |
| 7 | 引入外部 CDN 库时不提供 fallback | CDN 不可用时页面不能白屏 |
| 8 | 修改已有功能但不执行回归测试 | 任何修改都可能影响现有功能，必须验证 |

---

## 测试规范

### 基础验证（每次提交前必须通过）

```bash
# 1. 构建脚本无报错
python build_content.py

# 2. 启动本地服务
python -m http.server 8080
```

然后在浏览器中依次验证：

| # | 检查项 | 预期结果 |
|---|--------|----------|
| 1 | 打开 `http://localhost:8080` | 首页正常加载，无 console error |
| 2 | 侧边栏展示 | 四个分类均可展开，模型列表正确 |
| 3 | 点击任一报告 | Markdown 渲染正常（标题、代码块、表格） |
| 4 | 搜索框输入关键词 | 结果卡片正确展示，数量提示准确 |
| 5 | 代码块 Copy 按钮 | 点击后文本复制到剪贴板，按钮显示 "Copied!" |

### 回归验证（修改已有功能时额外执行）

| # | 检查项 | 预期结果 |
|---|--------|----------|
| 6 | 侧边栏折叠/展开 | 动画流畅，内容区自动填满 |
| 7 | 视图切换 | Home → Category → Report → Home 循环无异常 |
| 8 | 面包屑导航 | 每级可点击跳转，路径正确 |
| 9 | 浮动按钮 | 回到顶部/跳到底部正常工作 |
| 10 | 报告 commit 日期 | 显示且格式正确（如 "March 15, 2026"） |
| 11 | 外部链接 | 新标签页打开，无安全警告 |
| 12 | 无网络时 | 使用已有 `content/` 静态文件仍能正常浏览 |

### 功能专项验证（新功能开发时）

- 执行 `recipe_blog_requirements.md` 中对应章节的"验证方法"，逐条通过
- 确保 DevTools Console 无新增 error/warning
- 如涉及 `build_content.py` 改动，确认 `content/index.json` 格式未破坏

### 浏览器兼容性

最低要求支持：
- Chrome/Edge 90+
- Firefox 90+
- Safari 15+

关键依赖：`backdrop-filter`（玻璃拟态）、`<details>` 元素、ES6+ 语法。

---

## 与 requirements.md 的关系

| 文档 | 职责 | 何时使用 |
|------|------|----------|
| **本文档 (skill.md)** | 技术规范：架构细节、API 格式、开发约束、测试规范 | 写代码时参考"怎么做"和"不能做什么" |
| **requirements.md** | 需求源：需求背景、方案设计、验证方法、验收标准 | 接任务时参考"做什么"和"做到什么程度" |

**协作流程：** requirements.md 定义目标和验收标准 → skill.md 提供技术约束和测试规范 → 开发者在两者框架内实现 → 按 requirements 的验证方法确认完成 → 按 skill 的测试规范确认无回归。

---

## Deploying to GitCode Pages (Migration Guide)

GitCode (gitcode.com) is based on GitLab, uses GitLab CI/CD (`.gitlab-ci.yml`)，Pages 功能与 GitLab Pages 基本一致。从当前 GitHub Pages 部署迁移到 GitCode Pages，需要修改以下内容：

### Overview of Changes

| Component | Current (GitHub) | Target (GitCode) |
|-----------|-----------------|-------------------|
| CI config file | `.github/workflows/deploy.yml` | `.gitlab-ci.yml` |
| Deploy mechanism | `actions/deploy-pages@v4` | GitLab Pages (artifact → `public/`) |
| Pages URL | `https://<user>.github.io/cann-recipes-blogs/` | `https://<user>.gitcode.io/cann-recipes-blogs/` 或自定义域名 |
| Jekyll bypass | `.nojekyll` file | 不需要 (GitLab Pages 不用 Jekyll) |
| Cron scheduling | GitHub Actions `schedule` | GitLab CI `schedules` (在 Web UI 中配置) |

---

### Step 1: Create `.gitlab-ci.yml`

在项目根目录创建 `.gitlab-ci.yml`，替代 `.github/workflows/deploy.yml`：

```yaml
image: python:3.11-slim

stages:
  - build
  - deploy

build_content:
  stage: build
  script:
    - python build_content.py || echo "WARNING: GitCode fetch failed, using committed content"
  artifacts:
    paths:
      - content/
    expire_in: 1 hour

pages:
  stage: deploy
  dependencies:
    - build_content
  script:
    - mkdir -p public
    - cp -r index.html content/ assets/ public/
    - cp .nojekyll public/ 2>/dev/null || true
  artifacts:
    paths:
      - public
  only:
    - main
    - master
```

**Key points:**
- GitLab Pages 要求部署产物放在 `public/` 目录
- `pages` 是 GitLab 的保留 job 名称，用这个名字才会触发 Pages 部署
- `artifacts.paths: [public]` 是 GitLab Pages 的固定要求

---

### Step 2: Adjust file copying in the deploy script

`index.html` 中通过相对路径 `content/index.json` 和 `content/reports/...` 加载内容。迁移时需确保 `public/` 目录下的结构与原来一致：

```
public/
├── index.html
├── content/
│   ├── index.json
│   └── reports/...
└── assets/
```

如果项目根目录还有其他需要 serve 的文件（如 favicon），也一并复制到 `public/`。

---

### Step 3: Handle sub-path deployment (if repo name ≠ `<user>.gitcode.io`)

如果仓库不是用户/组织的同名仓库（即 URL 会是 `https://<user>.gitcode.io/cann-recipes-blogs/` 而不是根路径），需要确认 `index.html` 中的资源路径是否使用相对路径。

**当前代码已使用相对路径** (`content/index.json`, `content/reports/...`)，所以无需修改。但如果未来加入了 `<base href="/">` 或绝对路径，则需要改为相对路径或添加正确的 base path。

---

### Step 4: Configure scheduled pipeline (替代 GitHub Actions cron)

GitLab/GitCode 的定时任务不在 `.gitlab-ci.yml` 中声明，而是在 Web UI 配置：

1. 进入项目 → **CI/CD** → **Schedules**（或 **流水线** → **定时任务**）
2. 点击 **New schedule**
3. 配置：
   - Description: `Daily content refresh`
   - Cron: `17 2 * * *` (UTC 2:17 AM，与当前 GitHub 一致)
   - Target branch: `main` (或 `master`)
4. 保存

---

### Step 5: Adjust `build_content.py` (if needed)

`build_content.py` 调用的是 GitCode 的 API (`https://web-api.gitcode.com/api/v2`)。这些 API 在 GitCode CI 环境中应该**无需修改**即可访问（同平台内部调用，无跨域问题）。

但需注意：
- GitCode CI runner 的网络是否能访问 `web-api.gitcode.com`（通常可以）
- 如果 GitCode 对 API 有 rate limit，CI 环境中可能需要配置 Token：
  ```yaml
  build_content:
    variables:
      GITCODE_TOKEN: $GITCODE_API_TOKEN  # 在 CI/CD Settings → Variables 中配置
  ```
  并在 `build_content.py` 中的请求头加上 `Authorization: Bearer ${GITCODE_TOKEN}`（当前脚本未使用 token，公开仓库通常不需要）。

---

### Step 6: Remove GitHub-specific files (optional)

迁移完成后可以清理：

| File | Action |
|------|--------|
| `.github/workflows/deploy.yml` | 删除（GitCode 不使用） |
| `.nojekyll` | 可保留（无害）或删除 |
| `README.md` | 更新部署说明中的 URL |

---

### Step 7: Verify deployment

1. Push 代码到 GitCode 仓库的 `main`/`master` 分支
2. 进入 **CI/CD** → **Pipelines**，确认流水线执行成功
3. 进入 **Settings** → **Pages**，查看部署 URL
4. 打开 Pages URL，验证：
   - 首页加载正常（sidebar、cards）
   - 点击报告能正常渲染 markdown
   - 搜索功能正常
   - 图片正常显示（base64 不依赖外部请求）

---

### 完整修改清单 (Checklist)

- [ ] 创建 `.gitlab-ci.yml`（见 Step 1）
- [ ] 确认 `public/` 中的文件结构正确
- [ ] 在 GitCode Web UI 配置定时流水线 (Schedule)
- [ ] （可选）在 CI/CD Variables 中添加 `GITCODE_API_TOKEN`
- [ ] Push 并验证 Pages 部署
- [ ] 更新 README.md 中的部署 URL
- [ ] （可选）删除 `.github/workflows/deploy.yml`

---

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Pages 页面 404 | 确认 `pages` job 的 `artifacts.paths` 是 `["public"]`，且 `public/index.html` 存在 |
| 内容加载失败 | 检查 `public/content/index.json` 是否存在；确认 `cp -r content/ public/` 在 `build_content` 之后执行 |
| 图片不显示 | 图片已是 base64，不应有此问题；若有新增非 base64 图片，检查相对路径 |
| 定时任务不触发 | GitCode Schedules 需要项目有活跃的 CI runner；确认 schedule 状态为 Active |
| CI 中 `build_content.py` 超时 | GitCode API rate limit；配置 token 或在脚本中增加 retry/sleep |

# Recipe Blog Website - Technical Documentation

> Last updated: 2026-03-18 — fixed markdown rendering, content fetching, title, and category view completeness.

## Overview

This documentation explains how to recreate the CANN Recipes Blog website for browsing tech reports from GitCode repositories.

## Source Repositories

The website displays tech reports from 4 different GitCode repos:

| Category | GitCode Repo URL | Docs Location |
|----------|-----------------|---------------|
| Infer | https://gitcode.com/cann/cann-recipes-infer | docs/models/ (folder per model) |
| Train | https://gitcode.com/cann/cann-recipes-train | docs/features/ (flat .md files) |
| Spatial Intelligence | https://gitcode.com/cann/cann-recipes-spatial-intelligence | docs/models/ |
| Embodied Intelligence | https://gitcode.com/cann/cann-recipes-embodied-intelligence | docs/manipulation/ |

## Design Reference

- **Color Theme** (from example.html and example_full.html):
  - Primary/Accent: #E77A1D (orange)
  - Background Light: #F9F8F6 (beige)
  - Text: #3E2723 (coffee brown)
- **Font**: Public Sans (display), Inter (body)
- **Icons**: Material Symbols Outlined from Google Fonts
- **Framework**: Tailwind CSS (CDN)
- **Markdown Renderer**: marked.js v4.3.0 (CDN) — replaces custom regex renderer

## Bug Fixes Applied (2026-03-18)

| Bug | Fix |
|-----|-----|
| Slow content load via jina.ai/localhost proxy | Fetch raw markdown directly from `gitcode.com/cann/{repo}/raw/{branch}/{path}` |
| Images broken, code blocks wrong, extra UI noise | Replaced regex renderer with `marked.js`; images resolved to absolute raw URLs; CSS via `.report-markdown` class |
| Title showed "CANN-RECIPES" / "BLOG" | Changed to "CANN RECIPES BLOGS" |
| Category view missing models with no reports | `showCategory()` now renders all models; models without reports show a "Browse GitCode Repo" card |

## Key Features Implemented

### 1. Left Sidebar Navigation
- Collapsible vertical sidebar (w-72)
- Categories: Infer, Train, Embodied Intelligence, Spatial Intelligence
- Models organized alphabetically under each category
- Nested details elements for models with multiple reports
- "Browse Repo" button for each category (links to GitCode repo)
- Toggle button to hide/show sidebar (chevron_left/chevron_right)

### 2. Main Content Area
Three views with JavaScript switching:
- **Home View**: Recent reports (6 cards), Popular reports (4 titles), Newsletter signup, Categories
- **Category View**: Grid of reports for selected category
- **Report View**: Full markdown-style article display with breadcrumb

### 3. Search Bar
- Located at top right of header
- Placeholder: "Search tech reports..."
- Input event triggers filterContent() function

### 4. Floating Navigation Buttons
- Back to top button (keyboard_arrow_up)
- Go to bottom button (keyboard_arrow_down)
- Fixed position bottom-right

### 5. Glassmorphism Effects
- Glass cards with backdrop-filter: blur(12px)
- Semi-transparent backgrounds
- Subtle borders

## Data Structure

```javascript
// GitCode Repo Configuration
const repoConfig = {
  "Infer": { repo: "cann-recipes-infer", docFolders: ["common", "design", "models"] },
  "Train": { repo: "cann-recipes-train", docFolders: ["llm_pretrain", "llm_rl"], ignoreFolders: ["features"] },
  "Spatial Intelligence": { repo: "cann-recipes-spatial-intelligence", docFolders: ["models"] },
  "Embodied Intelligence": { repo: "cann-recipes-embodied-intelligence", docFolders: ["manipulation"] }
};

// Model data from GitCode repos
const repoModels = {
  "Infer": [
    { name: "deepseek-r1", reports: ["deepseek_r1_decode_optimization.md", "deepseek_r1_prefill_optimization.md"] },
    { name: "deepseek-v3.2-exp", reports: [] },
    // ... more models
  ],
  // ... other categories
};
```

## Key JavaScript Functions

| Function | Purpose |
|----------|---------|
| toggleSidebar() | Show/hide left sidebar with animation |
| showHome() | Display home view, show sidebar |
| showCategory(category) | Display ALL models for a category (with or without reports), hide sidebar |
| showReport(category, model, title, reportFile) | Display full report, hide sidebar |
| fetchReportContent(category, model, reportFile) | Fetch raw markdown from GitCode directly; falls back to corsproxy.io |
| renderMarkdown(md, baseUrl) | Parse markdown via marked.js; resolves relative image paths to absolute raw URLs |
| getCategoryCounts() | Count total reports per category |
| renderCategories() | Render category list with counts |

## Content Fetching Architecture

### Why a local proxy is required
GitCode's web API (`web-api.gitcode.com`) returns:
```
Access-Control-Allow-Origin: https://gitcode.com
```
This blocks any browser origin other than gitcode.com (file://, localhost, etc.).
A direct `/raw/` URL exists but returns HTML (not raw text) — the site is a JS SPA.

### Local proxy (`proxy.js`)
```
node proxy.js   # starts on http://localhost:8081
```
The proxy receives:
```
GET /?repo={repo}&branch={branch}&path={full/file/path}
```
Then calls:
```
GET https://web-api.gitcode.com/api/v2/projects/cann%2F{repo}/repository/files
    ?repoId=cann%252F{repo}&ref={branch}&file_path={encoded_path}&ref_replace_web={branch}
```
with headers:
- `Origin: https://gitcode.com`
- `Referer: https://gitcode.com/cann/{repo}/blob/{branch}/{path}`

Response JSON has `content` field (base64). Proxy decodes and returns raw bytes with CORS `*`.

This approach is much faster than the old jina.ai proxy because it calls the REST API directly (no JS rendering, no HTML parsing).

### Image resolution
`renderMarkdown(md, repo, branch, baseDir)` rewrites relative image paths:
```javascript
// ./images/arch.png  →  http://localhost:8081/?repo=...&branch=master&path=docs/models/.../images/arch.png
```
Uses `resolvePath(baseDir, relativeSrc)` to collapse `..` segments.

### marked.js configuration
```javascript
const r = new marked.Renderer();
r.link = (href, title, text) =>
  `<a href="${href}" target="_blank" rel="noopener">${text}</a>`;
marked.setOptions({ renderer: r, breaks: true, gfm: true });
```
Rendered output is wrapped in `<div class="report-markdown">` for CSS targeting.

### `.report-markdown` CSS
All markdown output elements (h1–h4, p, pre, code, img, table, blockquote, etc.) are styled via `.report-markdown *` rules in the `<style>` block — no inline Tailwind classes needed on the rendered HTML.

## File Structure

```
recipe_blog/
├── index.html   # Final website (renamed from recipe_blog.html)
├── recipe_blog_skill.md  # This documentation
├── demo.html          # Demo version (same as final)
├── blog.md           # Original task specification
├── example.html      # Design reference 1
└── example_full.html # Design reference 2
```

## How to Update Data

To add new models or reports:

1. **Add model to sidebar**: Add entry to `repoModels` object in JavaScript
2. **Add nested reports**: Use `<details>` element for collapsible list
3. **Update counts**: Automatic via `getCategoryCounts()`

Example for adding a new model with reports:
```javascript
{ name: "new-model", reports: ["report1.md", "report2.md"] }
```

Example for single report model:
```javascript
{ name: "single-model", reports: ["readme.md"] }
```

## Deployment

The website is a single HTML file that can be:
1. Opened locally in browser (file://)
2. Served via HTTP server
3. Deployed to any static hosting (Netlify, Vercel, GitHub Pages, etc.)

To serve locally:
```bash
cd recipe_blog
python -m http.server 8080
# or
npx serve .
```

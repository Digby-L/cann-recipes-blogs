# CANN Recipes Blog - Implemented Features

Updated: 2026-07-21

This list records features currently implemented on the `new_docs` branch. The detailed requirements and design decisions remain in `recipe_blog_requirements.md`.

## Content And Navigation

- Four-level content navigation: category, subcategory, model, and report.
- Expandable sidebar tree generated from `content/index.json`.
- Remote Markdown loading from GitCode without persisting report bodies locally.
- Markdown headings, lists, links, quotes, code blocks, images, and tables.
- Syntax highlighting and copy buttons for code blocks.
- Mermaid diagram rendering.
- KaTeX formula rendering.
- Report breadcrumbs with clickable parent levels.
- Report table of contents with active-section tracking.
- Previous and next report navigation.
- Reading progress indicator.
- Wide tables constrained to the report column with horizontal scrolling.

## Homepage

- Recent Reports list generated from manifest data.
- Report cover images extracted from the first image in remote Markdown.
- Category-specific CSS cover placeholders when a report has no image or an image fails to load.
- Repository shortcuts for Infer, Train, Embodied Intelligence, and Docs.
- Single sidebar-level `Browse Docs Repo` link.

## Search And Discovery

- Live keyword search across report filename titles, model names, and categories.
- Search can be repeated with Enter without changing the keyword.
- Full-width responsive search result cards.
- Complete, non-cropped report covers in search results.
- Filename-derived report tags stored in the manifest.
- Convenient Tags popover beside the search box.
- Tag-only filtering and combined keyword plus tag filtering.
- Clickable tag chips on report and search-result cards.
- Active-filter summary and one-click clear action.

## Report Covers

- `build_content.py` transiently reads Markdown to locate its first Markdown or HTML image.
- Manifest stores remote GitCode cover URLs, not Base64 image data.
- Covers use `object-fit: contain` so technical diagrams are not cropped.
- Browser manifest loading bypasses stale cache.
- Remote cover loading retries once before falling back to a category placeholder.

## Feedback And Interaction

- Feedback entry at the bottom of every real report.
- Floating feedback shortcut in report view.
- Four Issue types: content correction, bug report, feature suggestion, and technical discussion.
- Pre-filled Issue title, report path, reading URL, and Markdown template.
- Automatic Issue routing by category to Infer, Train, Embodied AI, or Docs.
- Compatibility with both `title` / `body` and GitLab-style Issue query parameters.
- Modal close through its close button, backdrop click, or Escape.

## Visual And Accessibility

- Glass-style interface with restrained orange accents.
- Light and dark themes.
- Material Symbols for navigation and actions.
- Responsive report cards and search results.
- Long titles and repository names wrap within their containers.
- Keyboard-focusable horizontally scrollable tables.
- Tooltips or accessible labels on icon-only controls.

## Build And Deployment

- Standard-library Python manifest generator.
- Dynamic GitCode directory discovery.
- Manifest metadata for file paths, tags, covers, and source repository routing.
- GitHub Pages deployment workflow.
- Scheduled content refresh workflow.
- Local static server plus optional read-only GitCode proxy.

## Explicitly Cancelled

- Popular Reports ranking and visit statistics: reliable ranking requires persistent page-view storage, deduplication, a database, and a backend aggregation API.
- Mailing-list subscription: removed from the current product scope.

## Main Files

- `index.html`: application UI, rendering, search, filters, report reader, covers, and feedback.
- `build_content.py`: GitCode discovery and manifest metadata generation.
- `content/index.json`: generated report metadata.
- `docs/recipe_blog_requirements.md`: detailed requirements and design decisions.

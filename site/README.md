# CANN Recipes Blog Site

Static website code for browsing the Markdown reports stored in the parent
`cann-recipes-docs` repository.

## Features

- Browse tech reports across four categories: Infer, Train, Embodie_AI, CANN Features
- Responsive design with collapsible sidebar
- Direct same-origin fetching of Markdown content from the parent repository
- Fallback to the previous GitCode/proxy content path when needed
- Glassmorphism UI with Tailwind CSS

## Deployment

The repository-level GitHub Actions workflow builds the local content index and
uploads this `site/` directory as the Pages artifact.

### Deploy to GitHub Pages

1. Create a new repository on GitHub (e.g., `cann-recipes-blog`).
2. Push this code to the `main` branch:
   ```bash
   git remote add origin https://github.com/[your-username]/cann-recipes-blog.git
   git branch -M main
   git push -u origin main
   ```
3. Go to your repository **Settings** → **Pages**.
4. Under **Build and deployment**, select **GitHub Actions** as the source.
5. The workflow will deploy the site to `https://[your-username].github.io/cann-recipes-blog/`.

### Local Development

1. From the repository root, build the navigation and search index:
   ```bash
   python site/build_content.py
   ```

2. Start the local server from the repository root:
   ```bash
   python site/serve.py --port 8001
   ```

3. Open `http://127.0.0.1:8001/site/`.

   The local proxy is only needed when testing the fallback remote path:
   ```bash
   ./site/start_proxy.sh   # or site\start_proxy.bat on Windows
   ```

## Project Structure

```
├── index.html              # Main website
├── build_content.py        # Builds site/content index files from ../ docs
├── content/                # Generated lightweight manifest and search index
├── docs/                   # Site documentation
├── proxy/                  # Local proxy server (Node.js/Python)
├── serve.py                # Local SPA server
├── start_proxy.sh          # Shell script to start proxy
├── start_proxy.bat         # Batch script to start proxy
├── .nojekyll               # Disable Jekyll processing
└── README.md               # This file
```

## Content Source

Reports are read from the parent repository directories:

| Category | Path |
|----------|------|
| Infer | `../infer` |
| Train | `../train` |
| Embodie_AI | `../embodied` |
| CANN Features | `../cann_features` |

## License

MIT

# CANN Recipes Blog

A static website for browsing technical reports from CANN GitCode repositories.

## Features

- Browse tech reports across four categories: Infer, Train, Spatial Intelligence, Embodied Intelligence
- Responsive design with collapsible sidebar
- Direct fetching of markdown content from GitCode repositories
- Fallback to CORS proxy for cross-origin requests
- Glassmorphism UI with Tailwind CSS

## Deployment

This site is configured for GitHub Pages deployment. The repository includes a GitHub Actions workflow that automatically deploys the site when you push to the `main` branch.

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

1. Clone the repository:
   ```bash
   git clone https://github.com/[your-username]/cann-recipes-blog.git
   cd cann-recipes-blog
   ```

2. Open `index.html` in your browser.

   For full functionality (if GitCode raw URLs are blocked by CORS), you can run a local proxy:
   ```bash
   ./start_proxy.sh   # or start_proxy.bat on Windows
   ```
   Then open `index.html`.

## Project Structure

```
├── index.html              # Main website (renamed from recipe_blog.html)
├── assets/                 # CSS, JavaScript, images
├── docs/                   # Documentation
├── proxy/                  # Local proxy server (Node.js/Python)
├── start_proxy.sh          # Shell script to start proxy
├── start_proxy.bat         # Batch script to start proxy
├── .nojekyll               # Disable Jekyll processing
└── README.md               # This file
```

## Content Source

Reports are fetched from the following GitCode repositories:

| Category | Repository |
|----------|------------|
| Infer | https://gitcode.com/cann/cann-recipes-infer |
| Train | https://gitcode.com/cann/cann-recipes-train |
| Spatial Intelligence | https://gitcode.com/cann/cann-recipes-spatial-intelligence |
| Embodied Intelligence | https://gitcode.com/cann/cann-recipes-embodied-intelligence |

## License

MIT
---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- User Manual
- Documentation
title: Deployment
weight: 100
---

[[toc min_headers="4" title="Contents"]]

The big advantage of a static website is that you don't need a special server (no PHP, no database). You can host your site almost anywhere.


## The Output Folder (`site_output`)

When you click **Render**, your entire website is generated in the `site_output` folder. This folder contains everything you need:

```
site_output/
├── index.html
├── 01-introduction/
│   ├── installation.html
│   └── first-steps.html
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── sitemap.xml
```

[[infobox type="warning" title="Important"]]
Always upload the **contents** of <code>site_output</code>, not the folder itself — unless you want your site accessible at <code>yourdomain.com/site_output/</code>.
[[/infobox]]

## Method A: Classic Web Hosting (FTP/SFTP)

If you have web space with a provider (e.g. Strato, Ionos, All-Inkl):

1. Download an FTP program (e.g. **FileZilla** — free and cross-platform).
2. Connect to your server with your login credentials.
3. Navigate to the public directory (often `public_html`, `www`, or `htdocs`).
4. Select all files in your local `site_output` folder.
5. Drag them to the server.

## Method B: Modern Hosting (Netlify / Vercel)

Providers like **Netlify** or **Vercel** specialize in static sites and are often **free** for small projects.

**Netlify Drag & Drop (fastest method):**

1. Go to [app.netlify.com/drop](https://app.netlify.com/drop).
2. Drag your `site_output` folder into the browser window.
3. Your page will be online immediately at a URL like `random-name.netlify.app`.

## Method C: GitHub Pages

If you host your code on GitHub:

1. Create a repository for your project.
2. Upload the contents of `site_output` to the repository (or use a dedicated `gh-pages` branch).
3. In your repository settings, go to **Pages** and activate the appropriate source branch.

Your site will be available at `https://YOUR-USERNAME.github.io/REPO-NAME/`.

## Testing Locally Before Publishing

Always test your page locally before uploading. Click the **"Open in Browser"** button in the editor after rendering, or start a local web server from the `site_output` folder:

```bash
cd site_output
python3 -m http.server
```

Then open `http://localhost:8000` in your browser.

[[infobox type="info" title="Note: Search Function"]]
The search function requires a web server context (<code>http://</code>) to work. It will not function when opening HTML files directly via <code>file://</code> — this is a browser security restriction, not a bug.
[[/infobox]]

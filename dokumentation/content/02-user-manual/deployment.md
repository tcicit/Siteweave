---
author: TCI
breadcrumbs: true
date: '2025-01-08'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Benutzerhandbuch
- Dokumentation
title: Deployment
weight: 100
---

The big advantage of a static website is that you don't need a special server (such as for PHP or databases). You can host your site almost anywhere.

## 1. The output folder (`site_output`)

When you click **“Render”** in the editor, your entire website is generated in the `site_output` folder.

This folder contains everything you need:
*   `index.html` (your home page)
*   All other HTML pages
*   The `assets` folder (images, CSS, JS)

**Important:** You must always upload the **contents** of this folder, not the folder itself (unless you want your site to be accessible at `yourdomain.com/site_output/`).

## 2. Method A: Classic web hosting (FTP/SFTP)

If you already have web space with a provider (such as Strato, Ionos, All-Inkl):

1.  Download an FTP program (e.g., **FileZilla**).
2.  Connect to the server with your login details.
3.  Navigate to the public directory on the server (often `public_html`, `www`, or `htdocs`).
4.  Select all files in the local `site_output` folder.
5.  Drag them to the server.

## 3. Method B: Modern hosting (Netlify / Vercel)

Providers such as **Netlify** or **Vercel** specialize in static pages and are often free for small projects.

**Drag & Drop (Netlify Drop):**
1.  Go to app.netlify.com/drop.
2.  Simply drag your `site_output` folder into the browser window.
3.  Your page will be online immediately (e.g., at `random-name.netlify.app`).

## 4. Method C: GitHub Pages

If you host your code on GitHub, you can use GitHub Pages.

1.  Create a repository for your project.
2.  Upload the contents of `site_output` to the repository (or use a `gh-pages` branch).
3.  Activate the source in the repository settings under “Pages”.

[[infobox type="info" title="Tip"]]
Always test your page locally in your browser (using the “Open in browser” button in the editor) before uploading it.
[[/infobox]]
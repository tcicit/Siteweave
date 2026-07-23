---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- FAQ
- Search
- Troubleshooting
title: Problems with the Search Function (Local)
weight: 20
---

## Why Doesn't the Search Work Locally?

You may have noticed that the search function on your generated website does not work when you open the `index.html` file directly from your hard drive by double-clicking on it.

## The Problem

When you open an HTML file directly, the browser uses the `file://` protocol. The search function relies on a file called `search_index.json`, which must be loaded in the background via JavaScript.

For security reasons (**CORS policies**), modern browsers block a page from loading other local files via JavaScript when using `file://`. In the browser's developer console (F12), you will often see:

> "Access to fetch at '...' from origin 'null' has been blocked by CORS policy."

## The Solution: A Local Web Server

For the search to work, the page must be served via a web server (`http://localhost/...`). This simulates a real web environment.

### Option 1: Python (Simplest)

Since Python is already installed:

1. Open your terminal or command prompt.
2. Navigate to your `site_output` folder:
   ```bash
   cd /path/to/your/project/site_output
   ```
3. Start the server:
   ```bash
   python3 -m http.server
   ```
4. Open `http://localhost:8000` in your browser.

### Option 2: Live Reload (Auto-Refresh)

For automatic page updates while editing, use **livereload**:

`pip install livereload`

Start: 

`livereload`

Open the address displayed (usually `http://localhost:35729`).

## Conclusion

[[infobox type="info" title="Not a Bug"]]
The search not working locally is **not a software error** — it is a browser security feature. As soon as your site is deployed to a real web server, the search will work automatically without any configuration.
[[/infobox]]
---
Test: AAA
author: TCI
breadcrumbs: true
date: '2024-01-20'
draft: false
featured_image: ''
layout: doc
release_date: '2026-02-12'
tags:
- FAQ
- Suche
- Troubleshooting
- Server
test: ''
title: Problems with the search function (local))
weight: 20
---

# Why doesn't the search work locally?

You may have noticed that the search function on your generated website does not work when you open the `index.html` file directly from your hard drive by double-clicking on it.

## The problem

When you open an HTML file directly, the browser uses the `file://` protocol. The search function is based on a file called `search_index.json`, which must be loaded in the background.

For security reasons (CORS policies), modern browsers prevent a file from reloading other local files via JavaScript. In the browser's developer console (F12), you will often see an error such as:

> “Access to fetch at ‘...’ from origin ‘null’ has been blocked by CORS policy.”

## The solution: A local web server

For the search to work, the page must be delivered via a web server (i.e., via `http://localhost...`). This simulates a real web environment.

### Option 1: Python (simple)

Since you already have Python installed, this is the fastest way:

1. Open your terminal/command prompt.
2. Navigate to the folder containing your generated page (e.g., `site_output`).
3. Run the following command:

```bash
python3 -m http.server
```

4. Open `http://localhost:8000` in your browser.

### Option 2: Live Reload (Convenient)

For automatic updates while editing, you can use `livereload`:

1. Install the package once:
```bash
pip install livereload
```
2. Start the server in the `site_output` folder:
```bash
   livereload
   ```
3. Open the address displayed (usually `http://localhost:35729`).

## Conclusion

This behavior is not a software error, but a security feature of the browser. As soon as the page is located on a real web server (on the Internet), the search will work automatically without any further action.
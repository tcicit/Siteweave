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
title: Site Renderer
weight: 60
---

[[toc min_headers="4" title="Contents"]]

The **Site Renderer** (`core.renderer`) is the heart of Siteweave. It is responsible for generating the finished static website from your Markdown content, configuration, and templates.

## The Rendering Pipeline

When you click **Render**, the `SiteRenderer` executes the following steps in order:

### Step 1 — Preparation & Backup

- Creates a timestamped backup of the current `site_output` folder.
- Rotates backups (keeps the last 10 by default).
- Deletes the output directory to ensure a clean build.

### Step 2 — Asset Management

- **Local assets:** Copies `assets` folders located next to Markdown files into the output structure.
- **Global assets:** Copies the global `css`, `js`, and `assets` directories.
- **Plugin assets:** Copies `.css` and `.js` files from active plugins to `css/plugins/` and `js/plugins/`.

### Step 3 — Data Collection & Structure

All Markdown files are scanned and analyzed:

- **Front matter** is read (title, date, tags, layout).
- **Draft pages** (`draft: true`) are skipped.
- **Automatic date management:** If `release_date` is missing, the current date is written back to the file, ensuring stable sort order.
- **Navigation structure** (`site_structure`) is built for menus.
- **Search index** (`search_index.json`) is created for client-side search.
- **Plugin hook:** Plugins that generate virtual pages (e.g. tag overviews) are called.

### Step 4 — HTML Generation

For each Markdown file, the actual HTML is produced:

1. **Code protection:** Code blocks are temporarily removed to prevent plugins or parsers from altering them.
2. **Plugin processing:** All `[[plugin_name args]]` tags are executed and replaced with their HTML output. Supports nesting up to 10 levels.
3. **Code restoration:** Code blocks are reinserted.
4. **Markdown conversion:** Markdown is converted to HTML using these extensions:
   - `tables` — HTML tables
   - `fenced_code` — fenced code blocks
   - `codehilite` — syntax highlighting via Pygments
   - `toc` — table of contents
   - `attr_list` — HTML attributes on elements
5. **Obfuscation:** Email addresses, phone numbers, and physical addresses are automatically replaced with HTML entities to protect against spam bots.

### Step 5 — Special Pages

- **Home page** (`index.html`): Generated from `index.md`. If missing, an empty home page is created.
- **404 page** (`404.html`): Generated from `404.md`.
- **Sitemap** (`sitemap.xml`): Generated at the very end, containing all public pages with modification dates.

## Automatisms Summary

| **Feature** | **Description** |
| :--- | :--- |
| **Release Date Injection** | Automatically writes `release_date` to new Markdown files. |
| **Breadcrumbs** | Automatically inserts breadcrumbs if enabled in front matter. |
| **Backup Rotation** | Keeps the last X backups of the `site_output` folder. |
| **Link Obfuscation** | Automatically protects contact details from bots. |
| **Asset Merging** | Combines global, local, and plugin assets intelligently. |
| **Config Repair** | Automatically corrects common formatting errors in `config.yaml`. |
| **Search Index** | Generates `search_index.json` for client-side full-text search. |

## Configuration

Control the renderer behavior in your project's `config.yaml`:

```yaml
log_level: INFO           # DEBUG, INFO, WARNING, ERROR
backup_on_render: true    # Backup site_output before each render
backup_rotation: 10       # Number of backups to keep

site_output_directory: site_output
content_directory: content
template_directory: templates
assets_directory: assets
plugin_directory: plugins
```

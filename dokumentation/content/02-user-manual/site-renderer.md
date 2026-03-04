---
author: TCI
breadcrumbs: true
date: '2026-01-16'
draft: false
featured_image: ''
layout: doc
release_date: '2026-01-16'
tags:
- Benutzerhandbuch
- Dokumentation
title: Site Renderer
weight: 60
---

The **Site Renderer** (`core.renderer`) is the heart of the application. It is responsible for generating the finished static website from the Markdown content, configuration, and templates.

## Core class: SiteRenderer

The `SiteRenderer` class controls the entire build process. It is initialized with the project directory and automatically loads the `config.yaml`.

### Initialization & configuration

*   **Config normalization:** The `normalize_config` function ensures that the configuration is robust. It automatically fixes common errors in `config.yaml`, such as when lists were incorrectly interpreted as strings or dictionaries (e.g., in `header_links` or `footer_links`).
*   **Path management:** Sets all necessary paths for content, assets, plugins, templates, and output directories relative to the project root.

## The rendering process (`render`)

The `render()` method performs the build process in several steps:

### 1. Preparation & backup

* **Backup:** Before writing new files, the renderer calls `backup_and_clean_output_dir`.
    *   Creates a backup of the current `site_output` folder (with timestamp).
*   Rotates backups (keeps the last 10 by default).
*   Deletes the output directory to ensure a clean build.

### 2. Asset management

*   **Local assets:** Copies `assets` folders located directly next to the Markdown files into the corresponding structure in the output folder (`copy_local_assets`).
*   **Global assets:** Copies the global `css`, `js`, and `assets` directories (`copy_static_directories`).
*   **Plugin Assets:** Searches all active plugins (global and project-specific) for `.css` and `.js` files and copies them centrally to `css/plugins/` or `js/plugins/` (`copy_plugin_assets`).

### 3. Phase 1: Data Collection & Structure

In this phase, all Markdown files are scanned but not yet finally converted to HTML.

* **Front matter analysis:** Reads metadata (title, date, tags, layout) from each file.
* **Draft handling:** Skips files marked with `draft: true` in the front matter.
*   **Automatic date management:**
    *   If `release_date` is missing, the current date is **written back** to the Markdown file.
    *   This guarantees stable sorting of the posts.
*   **Page structure:** Builds the hierarchy for the navigation menu (`site_structure`).
* **Search index:** Creates the `search_index.json` file for client-side search. Contains the title, path, and raw content of all pages.
* **Plugin hook:** Calls `generate_pages` for plugins that want to create their own virtual pages (e.g., tag overviews).

### 4. Phase 2: HTML generation

This is where the actual HTML files are created.

*   **Template selection:** Selects the appropriate Jinja2 template based on the `layout` field in the front matter (default: `layout_full-width.html`).
*   **Content processing:**
1.  **Code protection:** Code blocks (` ```...``` `) are temporarily removed so that plugins or Markdown parsers cannot change them (`_protect_code_blocks`).
2.  **Plugin processing:** Searches for tags such as `[[plugin_name args]]` and executes the corresponding plugin logic (`process_plugins`). Supports nesting up to 10 levels.
3.  **Code restoration:** Reinserts the code blocks.
4.  **Markdown conversion:** Converts Markdown to HTML. Enabled extensions:
* `tables`: Tables.
* `fenced_code`: Code blocks.
* `codehilite`: Syntax highlighting (Pygments).
* `toc`: Table of contents (if configured).
* `attr_list`: Attributes for HTML elements.
    5.  **Obfuscation:** Automatically obscures email addresses and phone numbers with HTML entities to ward off spam bots (`_obfuscate_sensitive_data`).

### 5. Special pages

*   **Home page (`index.html`):** Generated from `index.md`. If this is missing, an empty home page is generated.
* **404 page (`404.html`):** Generated from `404.md`.
* **Sitemap (`sitemap.xml`):** Generated at the very end and contains all public pages including the modification date (`generate_sitemap`).

## Important helper functions

### Plugin system

*   **`load_plugins()`:** Loads Python modules from the `plugins` folder (both globally and in the project). A plugin must have a `handle(content, args, context, env)` function.
*   **`parse_plugin_args(arg_string)`:** Parses arguments such as `key=“value” flag` into a dictionary.

### Navigation

*   **`generate_index_html()`:** Recursively generates the HTML for the navigation menu.
    * Marks the active page and parent folders (`active`, `active-parent`).
* Sorts folders before files.
* Supports dropdowns for subfolders.


### Security & Data Protection

*   **`_obfuscate_sensitive_data(html)`:**
    *   Searches for email patterns.
    *   Searches for phone numbers (international format).
    *   Searches for the address stored in the config.
    *   Replaces these with HTML entities (e.g., `&#64;` instead of `@`).

### Utilities

*   **`slugify(value)`:** Creates URL-friendly slugs (e.g., “Züri Gschnätzlets” -> “zuri-gschnatzlets”).
* **`extract_title(content, filename)`:** Attempts to extract the title from the first H1 heading if it is not in the front matter. The fallback is the file name.

## Automatisms Summary

| Feature | Description |
| :--- | :--- |
| **Release Date Injection** | Automatically writes a `release_date` to new Markdown files. |
| **Breadcrumbs** | Automatically inserts breadcrumbs if enabled in the front matter (default: yes). |
| **Backup Rotation** | Keeps the last X backups of the `site_output` folder. |
| **Link Obfuscation** | Automatically protects contact details from bots. |
| **Asset Merging** | Intelligently combines global and local assets as well as plugin assets. |
| **Config Repair** | Automatically corrects formatting errors in `config.yaml`. |

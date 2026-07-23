---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- Development
- Documentation
title: Architecture & Concepts
weight: 20
---

[[toc min_headers="4" title="Contents"]]

This page provides an overview of the technical structure of Siteweave. It is intended for developers who want to understand or extend the core code.

## 1. Technology Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **GUI Framework** | PyQt6 (Qt Widgets) |
| **Template Engine** | Jinja2 |
| **Markdown Parser** | Python Markdown |
| **Configuration** | YAML (PyYAML) |
| **Metadata** | python-frontmatter |
| **Syntax Highlighting** | Pygments |
| **PDF Generation** | WeasyPrint |
| **Spell Checking** | pyenchant / Hunspell |
| **Markdown Linting** | pymarkdownlnt |

## 2. Folder Structure

```
siteweave/
├── main.py                   ← Entry point; initializes QApplication
├── app_config.yaml           ← Global editor settings
├── requirements.txt
│
├── core/                     ← Business logic (GUI-independent)
│   ├── renderer.py           ← SiteRenderer — the build engine
│   ├── config_manager.py     ← Loads and validates config files
│   └── i18n.py               ← Internationalization support
│
├── gui/                      ← All PyQt6 windows and widgets
│   ├── main_window.py        ← MainWindow
│   ├── editor_widget.py      ← EditorWidget (CodeMirror-style editor)
│   └── project_launcher.py   ← ProjectLauncher (startup dialog)
│
├── plugins/                  ← Global shortcode plugins
├── snippets/                 ← Global text snippet files
├── locales/                  ← Translation files (i18n)
│
└── [your-project]/           ← A Siteweave project
    ├── config.yaml
    ├── content/              ← Markdown content files
    ├── templates/            ← Jinja2 HTML layouts
    ├── assets/               ← Static files (CSS, JS, images)
    │   ├── css/
    │   ├── js/
    │   └── images/
    ├── plugins/              ← Project-specific plugins
    ├── workers/              ← Automation scripts
    ├── themes/               ← Design themes
    ├── backup/               ← Content backups
    └── site_output/          ← Generated HTML website
```

## 3. The "Context" Pattern

A key architectural feature is the use of **context dictionaries** to decouple the GUI from business logic.

### Why Context?

Worker scripts and plugins should not have direct access to GUI objects (`QLineEdit`, `QMainWindow`, etc.). This would cause threading problems and make the code difficult to test.

Instead, the GUI bundles all required data into a "context" dictionary and passes it to the worker or plugin.

### Worker Context

```python
context = {
    'project_root':      '/path/to/project',
    'content_dir':       '/path/to/project/content',
    'current_file_path': '/path/to/file.md',
    'editor_content':    'The current text in the editor...',
    'config':            { ... }
}
```

### Plugin Context (per page)

```python
context = {
    'page_title':         'My Title',
    'date':               '2026-01-01',
    'relative_prefix':    '../',
    'current_output_path':'/blog/article.html',
    'site_structure':     { ... },
    'project_root':       '/path/to/project',
    'config':             { ... }
}
```

## 4. The Rendering Pipeline

| Step | Action |
| :---: | :--- |
| 1 | **Backup & Clean** — backs up old `site_output`, clears directory |
| 2 | **Asset Copying** — local, global, and plugin assets merged into output |
| 3 | **Data Collection** — scans all `.md` files, reads front matter, builds navigation tree, creates `search_index.json` |
| 4 | **Code Protection** — temporarily removes code blocks |
| 5 | **Plugin Processing** — executes `[[shortcodes]]` and replaces with HTML |
| 6 | **Code Restoration** — reinserts code blocks |
| 7 | **Markdown → HTML** — converts with extensions: `tables`, `fenced_code`, `codehilite`, `toc`, `attr_list` |
| 8 | **Obfuscation** — replaces emails, phones, addresses with HTML entities |
| 9 | **Template Rendering** — fills Jinja2 template with content + metadata |
| 10 | **Special Pages** — generates `404.html` and `sitemap.xml` |

## 5. Important Helper Functions

### Navigation

`generate_index_html()` recursively generates the HTML for the navigation menu:
- Marks the active page and parent folders (`active`, `active-parent`)
- Sorts folders before files
- Supports dropdowns for subfolders

### Security & Privacy

`_obfuscate_sensitive_data(html)` replaces:
- Email addresses → HTML entities (`&#64;` for `@`)
- Phone numbers (international format)
- The address stored in `config.yaml`

### Utilities

- `slugify(value)` — creates URL-friendly slugs (e.g. `"Zürich Café"` → `"zurich-cafe"`)
- `extract_title(content, filename)` — extracts title from H1 heading or falls back to filename

## 6. Multilingualism (i18n)

Siteweave uses **Babel** and `.po`/`.mo` translation files for interface localization. The language is set in `app_config.yaml`:

```yaml
language: en   # or: de, fr, es, ...
```

Translation files are located in `locales/[lang]/LC_MESSAGES/`. To add a new language, copy an existing `.po` file, translate the strings, and compile it with `msgfmt`.

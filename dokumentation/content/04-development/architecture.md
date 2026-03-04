---
author: TCI
breadcrumbs: true
date: '2025-01-07'
draft: false
featured_image: ''
layout: doc
release_date: '2026-01-15'
tags:
- Dokumentation
- Entwicklung
title: Architektur & Konzepte
weight: 20
---

This page provides an overview of the technical structure of Sitewave. It is intended for developers who want to understand or extend the core code.

## 1. Technology stack

The editor is based on the following technologies:

*   **Language:** Python 3.8+
*   **GUI framework:** PyQt6 (Qt Widgets)
*   **Template engine:** Jinja2
*   **Markdown parser:** Python Markdown
*   **Configuration:** YAML (PyYAML)
*   **Metadata:** python-frontmatter

## 2. Folder structure

The source code has a modular structure:

*   `run_editor.py`: The entry point. Initializes the QApplication.
* `core/`: Contains the business logic that is independent of the GUI (e.g., `ConfigManager`, `i18n`).
* `gui/`: Contains all PyQt6 windows and widgets (`MainWindow`, `EditorWidget`, `ProjectLauncher`).
*   `workers/`: Contains scripts for background tasks (e.g., link checker, Git sync) that run in separate threads.
*   `plugins/`: (In the project folder) Contains user-defined shortcodes.
* `templates/`: (In the project folder) Contains the HTML layouts.

## 3. The “Context” Pattern

A special feature of the architecture is the use of **context dictionaries** to decouple the GUI and logic.

### Why Context?

Worker scripts (in `workers/`) and plugins should not have direct access to GUI objects (such as `QLineEdit` or `QMainWindow`). This would lead to crashes (threading problems) and make the code difficult to test.

Instead, the GUI bundles a “data package” (the context) and passes it to the worker.

### The worker context

When a tool is started (e.g., “Check links”), the `MainWindow` creates a dictionary with the following content:

```python
context = {
    ‘project_root’: ‘/path/to/project’,
    ‘content_dir’: ‘/path/to/project/content’,
    'current_file_path': ‘/path/to/file.md’,
    ‘editor_content’: ‘The current text in the editor...’,
    ‘config’: { ... } # The project configuration
}
```

The worker reads this data, performs its task, and sends signals (log messages, progress) back to the GUI.

### The plugin context

It works similarly when generating the website. The renderer creates a context for each page:

```python
context = {
    ‘page_title’: ‘My title’,
    ‘date’: ‘2025-01-01’,
    ‘relative_prefix’: ‘../’, # Important for links!
    'site_structure': { ... } # For navigation
}
```

Plugins receive this context in their `handle()` function.

## 4. The Rendering Process

The process from Markdown to HTML file runs in the following steps:

1.  **Scanning:** The `SiteRenderer` recursively scans the `content` directory for `.md` files.
2.  **Reading metadata:** Front matter is parsed (`python-frontmatter`).
3.  **Building structure:** A navigation structure (tree) is created.
4.  **Process plugins:** The Markdown text is searched for shortcodes (`[[...]]`). Any plugins found are executed and replaced with their HTML output.
5.  **Render Markdown:** The remaining text is converted from Markdown to HTML.
6.  **Fill template:** The selected Jinja2 template (e.g., `layout_doc.html`) is loaded and filled with the content (`{{ content }}`) and metadata.
7.  **Save:** The finished HTML file is saved in the `site_output` folder.

---
author: ''
breadcrumbs: true
date: '2026-01-16'
draft: false
featured_image: ''
layout: full-width
release_date: '2026-01-16'
tags:
- Benutzerhandbuch
- Dokumentation
title: Project-tools
weight: 50
---

# Project Tools

The editor provides useful tools under the **“Project Tools”** menu item (or via the Project Launcher) to ensure the quality of the documentation and facilitate maintenance.

## Available Tools

### 1. Check Frontmatter
- **Description:** Checks and corrects the metadata (front matter) of Markdown files.
- **Function:** This tool analyzes the header of each Markdown file (the area between `---`). It ensures that the necessary fields are present and corrects formatting errors so that the static site generator can process the pages correctly.

### 2. Markdown Syntax (PyMarkdown)
- **Description:** Validates all Markdown files in the content folder for syntax errors.
- **Technology:** Based on the linter `pymarkdownlnt`. [Link to documentation](https://pymarkdown.readthedocs.io/en/latest/ )
- **Function:**
- Checks for structural errors such as unclosed code blocks (which lead to `CODE_BLOCK_PLACEHOLDER` errors).
- Checks compliance with Markdown standards.
- **Configuration:**
    The behavior can be controlled via a file named `.pymarkdown.json` in the main directory of the project. There, certain rules (e.g., line length) can be enabled or disabled.

** Example of a rule file `.pymarkdown.json` **

```json
{
    “plugins”: {
        “line-length”: {
            “enabled”: false
        },
        “no-inline-html”: {
            “enabled”: false
        },
        “no-duplicate-header”: {
            “enabled”: false
        },
        “first-line-h1”: {
            “enabled”: false
        },
        “no-trailing-punctuation”: {
            “enabled”: false
        }
    }
}

```

### 3. Content Backup
*   **Description:** Creates a backup copy of the content.
*   **Function:** Archives the current state of the `content` folder in a separate backup directory (often as a ZIP file with a timestamp) to prevent data loss in case of extensive changes.

### 4. Clear Cache
*   **Description:** Cleans up temporary files and caches.
*   **Function:** Deletes the cache of the static site generator and the editor. This is often necessary if changes are not updated in the preview or if rendering errors occur.

### 5. Image Compressor
*   **Description:** Optimizes images in the project.
*   **Function:** Compresses image files (JPG, PNG) in the `assets` folder to reduce file size and improve website loading time without significantly affecting visual quality.

### 6. Check Links
*   **Description:** Checks for broken links.
* **Function:** Scans all documents for internal and external links and reports targets that are not accessible (404 errors).

### 7. Normalize Project
* **Description:** Standardizes the project structure.
*   **Function:** Cleans up file names (e.g., lowercase letters, no special characters) and ensures a consistent folder structure in accordance with project conventions.

### 8. Export PDF
*   **Description:** Generates a PDF document.
*   **Function:** Creates a coherent PDF manual from the Markdown files, including a table of contents.

### 9. Bulk Edit Frontmatter
*   **Description:** Bulk editing of metadata.
*   **Function:** Allows you to change front matter fields in multiple files at the same time (e.g., add/remove tags, change author, set status). Includes preview function and automatic backup.

> **Tip:** Run these tools regularly, especially before publishing a new version of the documentation.

## Automation

The tools can also be automated outside the editor, for example using scripts. This is useful for performing checks before “building” the page.

### Example: Windows batch script

Create a file `run_checks.bat` in the main directory:

```batch
@echo off
echo --- Start quality assurance ---

echo [1] Check front matter...
python lint_frontmatter.py

echo [2] Check Markdown syntax...
python lint_markdown.py

echo Done.
pause
```
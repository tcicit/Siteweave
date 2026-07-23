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
title: Project Tools
weight: 50
---

[[toc min_headers="4" title="Contents"]]

Siteweave provides a comprehensive set of tools under the **"Project Tools"** menu to ensure content quality and simplify maintenance.

## Available Tools

### 1. Check Frontmatter

Analyzes the header of each Markdown file. Ensures required fields are present and corrects formatting errors so the site generator can process all pages correctly.

### 2. Markdown Syntax (PyMarkdown)

Validates all Markdown files for syntax errors using the `pymarkdownlnt` linter. Checks for:

- Unclosed code blocks (which cause `CODE_BLOCK_PLACEHOLDER` errors)
- Compliance with Markdown standards

Configure the linter behavior via a `.pymarkdown.json` file in your project root:

```json
{
    "plugins": {
        "line-length": { "enabled": false },
        "no-inline-html": { "enabled": false },
        "no-duplicate-header": { "enabled": false },
        "first-line-h1": { "enabled": false },
        "no-trailing-punctuation": { "enabled": false }
    }
}
```

### 3. Content Backup

Archives the current state of the `content` folder as a ZIP file with a timestamp in the `backup` directory. Essential before making large-scale changes.

### 4. Clear Cache

Deletes temporary files and caches of the site generator and editor. Use this when changes are not reflected in the preview or when rendering errors occur.

### 5. Image Compressor

Compresses JPG and PNG images in the `assets` folder to reduce file size and improve website loading time. Configure in `config.yaml`:

```yaml
jpeg_quality: 85
png_compression: 6
compressed_suffix: "-compressed"
extensions: ['.jpg', '.jpeg', '.png']
```

### 6. Check Links

Scans all documents for internal and external links and reports any broken targets (404 errors).

### 7. Normalize Project

Standardizes the project structure: cleans up file names (lowercase, no special characters) and ensures a consistent folder layout.

### 8. Export PDF

Generates a coherent PDF manual from the Markdown files, including a table of contents. Configure PDF settings in `config.yaml` under `pdf_export`.

### 9. Bulk Edit Frontmatter

Allows changing front matter fields across multiple files simultaneously — add or remove tags, change the author, update status fields. Includes a **preview function** and **automatic backup** before changes are applied.

[[infobox type="info" title="Best Practice"]]
Run the Frontmatter and Markdown linters regularly — especially before publishing a new version of your site or documentation.
[[/infobox]]

## Automation via Scripts

All tools can also be run from the command line, which is useful for CI/CD pipelines or scheduled tasks.

**Example: Windows batch script (`run_checks.bat`)**

```batch
@echo off
echo --- Starting quality assurance ---

echo [1] Checking front matter...
python lint_frontmatter.py

echo [2] Checking Markdown syntax...
python lint_markdown.py

echo Done.
pause
```

**Example: Running a worker from the command line**

```bash
python run_worker.py --project "/path/to/my-project" --worker "link_checker"
```

---
author: TCI
breadcrumbs: true
date: '2025-01-09'
draft: false
featured_image: ''
layout: full-width
release_date: '2026-01-15'
tags:
- Dokumentation
- konfiguration
title: Configuration (config.yaml)
weight: 50
---

The `config.yaml` file in your project's root directory is the central control center. It not only defines basic website properties, but also controls the behavior of the renderer and various project tools.

Here you will find a detailed explanation of all parameters based on a typical configuration.

## 1. General settings

These parameters define the identity of the website.

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `site_name` | The name of the website. Often displayed in the browser tab (title tag) and in the header. | `My Test Blog` |
| `site_url` | The base URL of the website. Important for generating the sitemap and absolute links. | http://localhost:8000 |
| site_logo | Path to the logo image (relative to the project directory). | assets/logo.png |
| site_favicon | Path to the favicon (icon in the browser tab). | assets/logo.svg |
| `default_template` | The default layout used if no `layout` is specified in the front matter of a page. | `post` |
| `site_theme` | The theme to be used (folder name in `themes_directory`). | `default` |
| `default_author` | Default author name if not specified in the front matter. | `TCI` |

## 2. Directory structure

Here you specify where the editor and renderer search for files and where results are written. All paths are relative to the project directory.

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `content_directory` | Folder containing the Markdown content files. | `content` |
| `site_output_directory` | Target folder for the generated HTML website. **Note:** This folder is cleaned up with every build! | `site_output` |
| `template_directory` | Folder for HTML templates (Jinja2). | `templates` |
| `assets_directory` | Folder for images and documents linked in Markdown. | `assets` |
| `plugin_directory` | Folder for project-specific Python plugins. | `plugins` |
| `css_directory` | Folder for global stylesheets. | `css` |
| `js_directory` | Folder for global JavaScript files. | `js` |
| `backup_directory` | Destination folder for automatic backups. | `backup` |
| `themes_directory` | Folder for themes. | `themes` |

## 3. Content & file types

| Parameter | Description |
| :--- | :--- |
| `markdown_extensions` | A list of file extensions that should be processed as content pages. Usually `.md` and `.markdown`. |

## 4. Navigation

Navigation is defined via lists of links.

### `header_links`
Links for the main menu (top).
```yaml
header_links:
- title: Home
  url: index.html
- title: Articles
  url: blog/index.html
```

### `footer_links`
Links for the footer of the page.
```yaml
footer_links:
- title: Imprint
  url: /imprint.html
```

## 5. Contact & Social Media

This data is used in templates (e.g., in the footer) and by the renderer to protect sensitive data (email, phone number) from spam bots (obfuscation).

```yaml
contact:
  name: Test Tester
  address: 1 Sample Street, 12345 Berlin
  email: info@beispiel.de  # Automatically obfuscated in HTML
  phone: +49 123 4567      # Automatically obfuscated in HTML

social:
  linkedin: https://likedin.com/...
  github: https://github.com/...
```

## 6. Tool configurations

The `config.yaml` also controls the additional tools under “Project Tools”.

### Backup
Controls the behavior of the renderer and the backup tool.
*   `backup_on_render`: (`true`/`false`) Automatically creates a backup of the old output folder before each render.
*   `backup_rotation`: Number of backups to keep (e.g., `5`). Older ones are deleted.

### Image Compression
Settings for the image optimization tool.
* `jpeg_quality`: Quality for JPG images (0-100).
* `png_compression`: Compression level for PNG (0-9).
* `compressed_suffix`: Suffix for compressed files (if originals are to be retained).
* `extensions`: Which file types are processed.

### Normalization
Settings for the “Normalize Project” tool.
*   `excluded_dirs`: Directories to be ignored when cleaning up file names (e.g., `_special`).

### Linter
Settings for the front matter check (`lint_frontmatter.py`).
* `defaults`: Default values that are entered if fields are missing in the front matter (e.g., `author: TCI`).

### PDF Export
Controls the appearance of the generated PDF manual.
* `page_size`: Paper size (e.g., `A4`).
*   `orientation`: Orientation (`portrait` or `landscape`).
*   `margin_...`: Page margins (e.g., `2cm`).
*   `show_cover_page`: Generate cover page?
*   `show_page_numbers`: Display page numbers?
*   `show_print_date`: Display print date?
* `export_path`: Storage location for the PDF files (e.g., `pdf_exports`).
* `custom_css_path`: Path to an additional CSS file for the PDF layout.

### 7. SEO & metadata

| Parameter | Description |
| :--- | :--- |
| `meta_description` | Global description of the website (meta tag). |
| `meta_keywords` | Global keywords (meta tag). |


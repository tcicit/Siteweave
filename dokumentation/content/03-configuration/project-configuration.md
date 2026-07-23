---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- Configuration
- Documentation
title: Project Configuration (config.yaml)
weight: 20
---

[[toc min_headers="4" title="Contents"]]

The `config.yaml` file in your project's root directory is the **central control file**. It defines basic website properties, directory structures, and controls the behavior of the renderer and project tools.

Siteweave uses two types of configuration:

1. **Project settings (`config.yaml`):** Specific to the current project.
2. **Application settings (`app_config.yaml`):** Global editor settings (see separate section).

Edit project settings via **File > Project Settings** or directly in the file.

## 1. General Settings

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `site_name` | Website name — used in `<title>` and header. Available as `{{ site_name }}` in templates. | `My Blog` |
| `site_url` | Final public URL. Important for `sitemap.xml` and absolute links. | `https://example.com` |
| `site_logo` | Path to a logo file (relative to project folder). | `assets/logo.png` |
| `site_favicon` | Path to the favicon (small icon in browser tab). | `assets/favicon.ico` |
| `default_template` | Default layout if no `layout` is specified in front matter. | `post` |
| `site_theme` | Active theme (folder name in `themes_directory`). | `default` |
| `default_author` | Default author name if not specified in front matter. | `TCI` |
| `log_level` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |

## 2. Directory Structure

All paths are relative to the project directory:

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `content_directory` | Folder containing Markdown content files. | `content` |
| `site_output_directory` | Target folder for generated HTML. **Cleaned on each build!** | `site_output` |
| `template_directory` | Folder for Jinja2 HTML templates. | `templates` |
| `assets_directory` | Main folder for static files (images, CSS, JS). | `assets` |
| `plugin_directory` | Folder for custom Python plugins. | `plugins` |
| `css_directory` | Subfolder within `assets_directory` for CSS. | `css` |
| `js_directory` | Subfolder within `assets_directory` for JS. | `js` |
| `backup_directory` | Destination for automatic content backups. | `backup` |
| `themes_directory` | Folder for themes. | `themes` |
| `markdown_extensions` | File extensions recognized as Markdown content. | `['.md', '.markdown']` |

## 3. Navigation

### Header Links (`header_links`)

```yaml
header_links:
  - title: Home
    url: index.html
  - title: Documentation
    url: docs/index.html
    sublinks:
      - title: Getting Started
        url: docs/getting-started.html
      - title: Configuration
        url: docs/configuration.html
  - title: About
    url: about.html
```

### Footer Links (`footer_links`)

```yaml
footer_links:
  - title: Legal Notice
    url: /legal-notice.html
  - title: Privacy Policy
    url: /privacy-policy.html
```

**Using footer links in a template:**

```html
<footer>
    <nav>
        <ul>
        {% if config.footer_links %}
            {% for link in config.footer_links %}
            <li>
                <a href="{{ relative_prefix }}{{ link.url.lstrip('/') }}">
                    {{ link.title }}
                </a>
            </li>
            {% endfor %}
        {% endif %}
        </ul>
    </nav>
    <p>&copy; {{ now.year }} {{ site_name }}</p>
</footer>
```

## 4. Contact & Social Media

```yaml
contact:
  name: John Doe
  email: john@example.com
  address: 12345 Sampletown, Country
  phone: +1 234 567 8900

social:
  twitter: https://twitter.com/yourname
  github: https://github.com/yourname
  linkedin: https://linkedin.com/in/yourname
```

[[infobox type="info" title="Automatic Obfuscation"]]
The renderer automatically replaces email addresses, phone numbers, and the address stored in `config.yaml` with HTML entities in the output (e.g. `&#64;` instead of `@`). This protects your contact details from spam bots without any extra configuration.
[[/infobox]]

## 5. Tool Configurations

### Backup

```yaml
backup_on_render: true    # Backup site_output before each render
backup_rotation: 10       # Number of backups to keep
```

### Image Compression

```yaml
jpeg_quality: 85
png_compression: 6
compressed_suffix: "-compressed"
extensions: ['.jpg', '.jpeg', '.png']
```

### Frontmatter Linter Defaults

```yaml
linter:
  defaults:
    author: TCI
    draft: false
    breadcrumbs: true
```

## 6. PDF Export (`pdf_export`)

```yaml
pdf_export:
  page_size: A4
  orientation: portrait
  margin_top: 2cm
  margin_bottom: 2cm
  margin_left: 2.5cm
  margin_right: 2.5cm
  show_cover_page: true
  show_page_numbers: true
  toc_depth: 3
  export_path: pdf_exports
  cover_logo: assets/pdf_cover_logo.png  # Overrides site_logo for PDF
```

To exclude a specific page from the PDF, add `pdf_exclude: true` to its front matter.

## 7. SEO & Metadata

```yaml
meta_description: "Official documentation for the Siteweave static site editor."
meta_keywords: "static site generator, markdown, python, documentation"
```

## Complete Example: config.yaml

```yaml
site_name: "My Project"
site_url: "https://myproject.example.com"
site_logo: "assets/logo.png"
site_favicon: "assets/favicon.ico"
default_template: post
site_theme: default
default_author: TCI
log_level: INFO

content_directory: content
site_output_directory: site_output
template_directory: templates
assets_directory: assets
plugin_directory: plugins
backup_directory: backup
themes_directory: themes

header_links:
  - title: Home
    url: index.html
  - title: Docs
    url: docs/index.html

footer_links:
  - title: Legal Notice
    url: /legal-notice.html

contact:
  name: John Doe
  email: john@example.com

social:
  github: https://github.com/yourname

backup_on_render: true
backup_rotation: 10

pdf_export:
  page_size: A4
  show_cover_page: true
  toc_depth: 3
```

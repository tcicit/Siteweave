---
author: TCI
breadcrumbs: true
date: '2026-01-09'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Dokumentation
- konfiguration
title: Project Configuration (config.yaml)
weight: 20
---

The `config.yaml` file in your project's root directory is the central control center. It defines basic website properties, directory structures, and controls the behavior of the renderer and various project tools.

Sitewave distinguishes between two types of configurations:
1.  **Project settings (`config.yaml`):** Specific to the current project.
2.  **Application settings (`app_config.yaml`):** Global editor settings (see separate section).

You can edit the project settings via the **File > Project Settings** menu item or edit the `config.yaml` file directly.

## 1. General Settings

These parameters define the identity and basic behavior of the website.

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `site_name` | The name of the website. Used in the title (`<title>`) and header. Accessible via `{{ site_name }}`. | `My Blog` |
| `site_url` | The final URL at which your website will be accessible. Important for creating the `sitemap.xml` and for absolute links. | `https://example.com` |
| `site_logo` | Path to a logo file (relative to the project folder). | `assets/logo.png` |
| `site_favicon` | Path to the favicon (the small icon in the browser tab). | `assets/favicon.ico` |
| `default_template` | The default layout used if no `layout` is specified in the front matter of a page. | `post` |
| `site_theme` | The theme to be used (folder name in `themes_directory`). | `default` |
| `default_author` | Default author name if not specified in the front matter. | `TCI` |
| `log_level` | Controls how detailed the log output is when generating the page (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |

## 2. Directory Structure

Here you specify where the editor and renderer search for files and where results are written. All paths are relative to the project directory.

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `content_directory` | Folder containing the Markdown content files (`.md`). | `content` |
| `site_output_directory` | Target folder for the generated HTML website. **Note:** This folder is cleaned up with every build! | `site_output` |
| `template_directory` | Folder for HTML templates (Jinja2). | `templates` |
| `assets_directory` | Main folder for static files (images, CSS, JS). Contents are copied to output. | `assets` |
| `plugin_directory` | Folder for custom Python plugins (shortcodes). | `plugins` |
| `css_directory` | Specific subfolder within `assets_directory` for CSS. | `css` |
| `js_directory` | Specific subfolder within `assets_directory` for JS. | `js` |
| `backup_directory` | Destination folder for automatic backups of content. | `backup` |
| `themes_directory` | Folder for themes. | `themes` |
| `markdown_extensions` | List of file extensions recognized as Markdown content. | `['.md', '.markdown']` |

## 3. Navigation

Navigation menus are defined via lists of links in the configuration.

### Header Links (`header_links`)
Links for the main menu (top).

```yaml
header_links:
  - title: Home
    url: index.html
  - title: Articles
    url: blog/index.html
    sublinks:
      - title: Tech
        url: blog/tech.html
```

### Footer Links (`footer_links`)
Links for the footer area (e.g., legal notice).

```yaml
footer_links:
  - title: Legal notice
    url: /legal-notice.html
  - title: Privacy policy
    url: /privacy-policy.html
```

**Integration in the template:**
You can access this via `config.footer_links`. Pay attention to `relative_prefix` so that the links work from subpages.

```html
<footer>
    <nav>
        <ul>
        {% if config.footer_links %}
            {% for link in config.footer_links %}
            <li>
                <a href="{{ relative_prefix }}{{ link.url.lstrip(‘/’) }}">
                    {{ link.title }}
                </a>
            </li>
            {% endfor %}
        {% endif %}
        </ul>
    </nav>
    <p>&copy; {{ site_name }}</p>
</footer>
```

## 4. Contact & Social Media

You can store structured contact data and social media profiles.

**Example:**
```yaml
contact:
  name: John Doe
  email: max@beispiel.de
  address: 12345 Musterstadt
  phone: +49 123 4567

social:
  twitter: https://twitter.com/yourname
  github: https://github.com/yourname
```

**Note on Privacy:**
The renderer automatically obfuscates email addresses and phone numbers in the HTML output to protect them from spam bots.

**Integration in the template:**
```html
<div class="contact-info">
    <p>{{ config.contact.name }}</p>
    <p><a href="mailto:{{ config.contact.email }}">{{ config.contact.email }}</a></p>
</div>

<div class="social-links">
    {% for platform, url in config.social.items() %}
        <a href="{{ url }}" class="social-icon {{ platform }}">{{ platform|capitalize }}</a>
    {% endfor %}
</div>
```

## 5. Tool Configurations

The `config.yaml` also controls the additional tools under "Project Tools".

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

### Linter
Settings for the front matter check (`lint_frontmatter.py`).
* `defaults`: Default values that are entered if fields are missing in the front matter (e.g., `author: TCI`).

## 6. PDF Export (`pdf_export`)

Controls the appearance of the generated PDF manual.

### Parameters
* `page_size`: Paper size (e.g., `A4`).
* `orientation`: Orientation (`portrait` or `landscape`).
* `margin_top`, `margin_bottom`, etc.: Page margins (e.g., `2cm`).
* `show_cover_page`: Generate cover page? (`true`/`false`)
* `show_page_numbers`: Display page numbers?
* `toc_depth`: Depth of the table of contents (e.g., `3` for H1-H3).
* `export_path`: Storage location for the PDF files.

### Logo Logic
You can define the logo for the PDF in two ways:

1. **Global Logo:** If `site_logo` is defined, it is used automatically.
2. **Specific PDF Logo:** Use `cover_logo` under `pdf_export` to override the global logo.

```yaml
site_name: “My Project”
site_logo: “assets/logo.png”

pdf_export:
  cover_logo: “assets/pdf_cover_logo.png” # Overrides site_logo for PDF
  toc_depth: 3
```

### Excluding Pages
To exclude a specific page from the PDF, add `pdf_exclude: true` to the front matter of the Markdown file.

```yaml
---
title: My Page
pdf_exclude: true
---
```

## 7. SEO & Metadata

| Parameter | Description |
| :--- | :--- |
| `meta_description` | Global description of the website (meta tag). |
| `meta_keywords` | Global keywords (meta tag). |
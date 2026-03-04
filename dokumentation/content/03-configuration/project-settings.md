---
author: TCI
breadcrumbs: true
date: '2026-01-02'
draft: false
featured_image: None
layout: full-width
release_date: '2026-01-15'
tags:
- Dokumentation
- konfiguration
title: Project settings (config.yaml)
weight: 10
---

Sitewave distinguishes between two types of configurations:

1.  **Project settings (`config.yaml`):** Each project has its own configuration file. It determines how the website is generated (name, folder structure, etc.).
2.  **Application settings (`app_config.yaml`):** This file is stored in the editor's main directory and controls the behavior of the application itself (language, window size, etc.).

## 1. Project settings (`config.yaml`)

This file is the heart of your website project. You can find it directly in the main directory of your project.

```yaml
site_name: “My Website”
site_url: “https://beispiel.de”
content_directory: “content”
site_output_directory: “site_output”
template_directory: “templates”
assets_directory: “assets”
plugin_directory: “plugins”
css_directory: “css”
js_directory: “js”
backup_directory: “backup”
markdown_extensions: [“.md”, “.markdown”]
log_level: “INFO”
```

# Project settings

### Explanation of options

- `site_name`
    The name of your website. Often used in the title (`<title>`) and header.

- `site_url`
    The final URL at which your website will be accessible. Important for creating the `sitemap.xml` and for absolute links.

- `content_directory`
    The folder where your Markdown files (`.md`) are located.

- `site_output_directory`
    The folder where the finished HTML website is generated. The contents of this folder are uploaded to the web server.

- `template_directory`
    The folder containing your Jinja2 layout templates (`.html`).

- `assets_directory`
    The main folder for all static files (images, CSS, JS, etc.). The contents of this folder will be copied to the `site_output_directory`.

- `plugin_directory`
    The folder for your custom Python plugins (shortcodes).

- `css_directory` / `js_directory`
    Specific subfolders within `assets_directory` for CSS and JavaScript files.

- `backup_directory`
    The folder where automatic backups of your `content` directory are stored.

- `markdown_extensions`
    A list of file extensions that should be recognized as Markdown content.

- `log_level`
    Controls how detailed the log output is when generating the page. Possible values: `DEBUG`, `INFO`, `WARNING`, `ERROR`.


The `config.yaml` file in the root directory of your project controls all aspects of website generation. You can conveniently edit these settings via the **File > Project Settings** menu item or edit the file directly.

## 1. Basic settings

*   **`site_name`**: The name of your website (e.g., “My Blog”). It is used as `{{ site_name }}` in templates.
*   **`site_url`**: The full URL at which the site will be published (e.g., `https://mein-blog.de`). Important for SEO and absolute links.
*   **`site_logo`**: Path to a logo file (relative to the project folder).
*   **`site_favicon`**: Path to the favicon (the small icon in the browser tab).

## 2. Directories

The editor uses a default structure that you can customize here:

* **`content_directory`**: Folder for Markdown files (default: `content`).
* **`site_output_directory`**: Folder for the generated HTML page (default: `site_output`).
* **`template_directory`**: Folder for HTML templates (default: `templates`).
*   **`assets_directory`**: Folder for static files (images, CSS, JS).

## 3. Social media (`social`)

You can store links to your social media profiles. This is a dictionary where the key is the platform and the value is the URL.

**Example in `config.yaml`:**
```yaml
social:
  twitter: https://twitter.com/deinname
  github: https://github.com/deinname
  linkedin: https://linkedin.com/in/deinname
```

**Integration in the template:**
You can access it via the variable `config.social`.

```html
<div class="social-links">
    {% if config.social %}
        {% for platform, url in config.social.items() %}
            <a href="{{ url }}" class="social-icon {{ platform }}" target="_blank">
                {{ platform|capitalize }}
            </a>
        {% endfor %}
    {% endif %}
</div>
```

## 4. Footer links (`footer_links`)

This setting allows you to define a list of links for the footer area (e.g., legal notice, privacy policy).

**Example in `config.yaml`:**
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

## 5. Contact information (`contact`)

Here you can store structured contact data.

**Example in `config.yaml`:**
```yaml
contact:
  name: John Doe
  email: max@beispiel.de
  address: 12345 Musterstadt
```

**Integration in the template:**
```html
<div class="contact-info">
    <p>{{ config.contact.name }}</p>
    <p><a href="mailto:{{ config.contact.email }}">{{ config.contact.email }}</a></p>
</div>
```

## 6. Export project as PDF (`pdf_export`)

### Define logo

You can now define the logo in your config.yaml in two ways:

Use global logo: If you have already defined site_logo, it will be used automatically.

```yaml
site_name: “My Project”
site_logo: “assets/logo.png”
```

Use specific PDF logo: If you want to use a different image for the PDF, you can 

specify this under pdf_export:

```yaml
pdf_export:
  cover_logo: “assets/pdf_cover_logo.png”
``` 


You can now control the depth of the table of contents in your config.yaml. To do this, add the pdf_export section (if it doesn't already exist) and set toc_depth.

```yaml
pdf_export:
  # Shows headings up to level 3 (H1, H2, H3) in the table of contents.
  # H1 is the file title, H2 is ‘##’, H3 is ‘###’.
  toc_depth: 3 
```



To exclude a page from the PDF, simply add the following to the front matter section of the corresponding Markdown file:


```yaml
---
title: My Page
pdf_exclude: true
---
```

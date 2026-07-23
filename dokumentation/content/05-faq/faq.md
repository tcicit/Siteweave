---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- FAQ
- Documentation
title: Frequently Asked Questions
weight: 10
---

[[toc min_headers="3" title="Questions"]]

## My changes are not visible online. What am I doing wrong?

After making changes to your Markdown files, two steps are required:

1. **Render:** Click the **"Render"** button in the toolbar. This rebuilds your website in the `site_output` folder.
2. **Upload:** Upload the **contents** of the `site_output` folder to your web server again (e.g. via FTP).

## Can I completely change the appearance of my website?

Yes. The appearance is fully controlled by the files in `templates/` and `assets/css/`.

- **Colors, fonts, spacing:** Edit `style.css`.
- **Basic layout (header, footer):** Edit `templates/base.html`.
- **Page-specific layouts:** Edit `templates/layout_*.html` files.

## How do I create navigation or a menu?

Most included templates generate navigation **automatically** from the folder and file structure of your `content` directory:

- A **folder** in `content` becomes a menu item with a submenu.
- A **file** in `content` becomes a direct link.

Just organize your files logically — the template does the rest. You can also define navigation explicitly via `header_links` in `config.yaml`.

## What is the difference between snippets and plugins?

- **Snippets** are *static* text modules — ideal for quickly inserting recurring content (e.g. a signature or a complex table) via drag & drop. They are plain text files.
- **Plugins (shortcodes)** are *dynamic* — executed by Python code at render time. They can apply logic, access files, or generate content based on parameters (e.g. a gallery from a folder).

## Do I need to be online to use the editor?

No. Siteweave is a pure desktop application that works **completely offline**. You only need an internet connection when uploading your finished website to a server.

## How can I create a backup of my project?

There are several options:

1. **Manually:** Copy the entire project folder to a safe location.
2. **Automatically:** Use **Project Tools → Content Backup** — creates a timestamped ZIP archive.
3. **Professionally (recommended):** Use **Git** for full version control of every change.

## Why doesn't the search work locally?

When opening `index.html` directly by double-clicking, the browser uses the `file://` protocol. For security reasons (CORS policies), browsers block JavaScript from loading local files like `search_index.json`.

**Solution:** Run a local web server from the `site_output` folder:

```bash
python3 -m http.server
```

Then open `http://localhost:8000`. The search will work correctly. This restriction does not apply when the site is deployed to a real web server.

## How do I add a contact form to a static site?

Static sites have no server-side backend, so use an external form service like **Formspree**:

1. Register at [formspree.io](https://formspree.io) and create a form to get your endpoint URL.
2. Insert the form HTML into your Markdown file:

```html
<form action="https://formspree.io/f/YOUR_ID" method="POST" class="contact-form">
  <label>Your email: <input type="email" name="email" required></label>
  <label>Your message: <textarea name="message" required></textarea></label>
  <button type="submit">Send</button>
</form>
```

[[infobox type="info" title="GDPR Note"]]
Since data is sent to an external provider (often in the US), mention this in your privacy policy. Many providers offer GDPR-compliant options or data processing agreements (DPA).
[[/infobox]]

## How do I use multiple languages?

Siteweave's multilingual support works by generating the site multiple times — once per language — and deploying each version to a separate URL path (e.g. `/en/`, `/de/`).

Configure the language switcher in `config.yaml`:

```yaml
language: "en_US"

available_languages:
  - code: "de_DE"
    name: "DE"
    url_prefix: "https://mysite.com"
  - code: "en_US"
    name: "EN"
    url_prefix: "https://mysite.com/en"
```

Then add the switcher to your template:

```html
{% if config.available_languages %}
<div class="language-switcher">
    <ul>
    {% for lang in config.available_languages %}
        <li>
            <a href="{{ lang.url_prefix }}/{{ current_output_path.lstrip('/') }}"
               class="{{ 'active' if lang.code == config.language else '' }}">
                {{ lang.name }}
            </a>
        </li>
    {% endfor %}
    </ul>
</div>
{% endif %}
```

##  Why Files Might Be Missing (Renderer Logic)

Your renderer.py file contains strict rules regarding which files are not included in the sidebar structure:

* **Special Pages:** Files in folders that begin with an underscore (e.g., _entwuerfe/) are ignored.
* **Root index & 404:** The files index.md and 404.md located directly in the root directory are not included in the menu.
* **Folder index:** An index.md file within a subfolder is used as a link for the folder name itself and does not appear as a separate subitem.
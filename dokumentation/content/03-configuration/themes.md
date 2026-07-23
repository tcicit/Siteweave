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
- Design
- Documentation
title: Themes & Layouts
weight: 30
---

[[toc min_headers="4" title="Contents"]]

The design of your website is determined by **themes** and **layouts**.

- **Themes** are complete design packages (CSS, JavaScript, templates).
- **Layouts** are specific structure templates for individual pages (e.g. blog post vs. home page).

## 1. Themes

A theme bundles the appearance of your website. Instead of starting from scratch for each project, activate a theme and get started right away.

### Activating a Theme

Specify the desired theme in your `config.yaml`:

```yaml
themes_directory: "themes"   # Folder where your themes are stored
site_theme: "my-theme"       # Name of the subfolder
```

### Creating Your Own Theme

Create a new folder in the `themes` directory. The folder name becomes the theme name.

```
themes/
└── my-theme/
    ├── templates/
    │   ├── base.html            ← Master layout
    │   ├── layout_doc.html
    │   ├── layout_post.html
    │   └── layout_full-width.html
    └── assets/
        ├── css/
        │   └── style.css
        ├── js/
        │   └── script.js
        └── images/
            └── screenshot.png
```

### The Override Mechanism (Fallback)

When Siteweave needs a file (e.g. `base.html`), it searches in this priority order:

1. **Project folder** (highest priority) — `templates/base.html` in your project.
2. **Theme folder** — `themes/my-theme/templates/base.html`.
3. **App default** — built-in fallback files.

This means you can use a theme and still customize individual parts. Copy any file from the theme to your project's `templates/` folder, edit it there, and your version takes precedence.

## 2. Templates & Layouts (Jinja2)

Siteweave uses **Jinja2** as its template engine. Layout files live in the `templates/` folder.

- **`base.html`** — The master framework. Includes CSS/JS and defines `{% block content %}`.
- **`layout_*.html`** — Specific layouts that inherit from `base.html`.

### Complete Example: `base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} - {{ site_name }}</title>

    <!-- Always use relative_prefix for CSS/JS links to work on all subpages -->
    <link rel="stylesheet" href="{{ relative_prefix }}css/style.css">

    {% if config.site_favicon %}
    <link rel="icon" href="{{ relative_prefix }}{{ config.site_favicon }}">
    {% endif %}
</head>
<body>

    <header>
        <div class="logo">
            <a href="{{ relative_prefix }}index.html">{{ site_name }}</a>
        </div>
        <nav class="main-nav" id="myTopnav">
            <ul>
                {% for link in config.header_links %}
                    {% if link.sublinks %}
                    <li class="dropdown">
                        <a href="{{ relative_prefix }}{{ link.url }}" class="dropbtn">
                            {{ link.title }} <span class="caret">▼</span>
                        </a>
                        <div class="dropdown-content">
                            {% for sublink in link.sublinks %}
                            <a href="{{ relative_prefix }}{{ sublink.url }}">{{ sublink.title }}</a>
                            {% endfor %}
                        </div>
                    </li>
                    {% else %}
                    <li>
                        <a href="{{ relative_prefix }}{{ link.url }}">{{ link.title }}</a>
                    </li>
                    {% endif %}
                {% endfor %}
            </ul>
        </nav>
    </header>

    <main>
        {% block content %}
            {{ content }}
        {% endblock %}
    </main>

    <footer>
        <p>&copy; {{ now.year }} {{ site_name }}</p>
    </footer>

    <script src="{{ relative_prefix }}js/script.js"></script>

</body>
</html>
```

### Creating a New Layout

Create a file in `templates/`, e.g. `layout_special.html`:

```html
{% extends "base.html" %}

{% block content %}
<div class="special-design">
    <h1>{{ page_title }}</h1>
    <p class="date">Published: {{ date }}</p>
    <hr>
    <div class="content">
        {{ content }}
    </div>
</div>
{% endblock %}
```

Select the layout in front matter (omit the `layout_` prefix and `.html` extension):

```yaml
---
title: My Special Page
layout: special
---
```

## 3. Available Template Variables

| Variable | Description |
| :--- | :--- |
| `{{ content }}` | Page content converted from Markdown to HTML. |
| `{{ page_title }}` | Page title (from front matter). |
| `{{ site_name }}` | Website name (from `config.yaml`). |
| `{{ date }}` | Page date (from front matter). |
| `{{ relative_prefix }}` | Relative path to the root (e.g. `../`). **Essential for CSS/JS links!** |
| `{{ current_output_path }}` | Path of the generated HTML file (e.g. `/index.html`). |
| `{{ site_structure }}` | Navigation tree object for menus. |
| `{{ config.* }}` | Access any config.yaml value (e.g. `config.social`). |
| `{{ now.year }}` | Current year — useful in the footer copyright notice. |

All front matter fields are also available as template variables.

**Example:**

```yaml
# In front matter:
author: John Doe
mood: Happy
```

```html
<!-- In template: -->
<p>Written by {{ author }} (mood: {{ mood }})</p>
```

## 4. Jinja2 Basics

Jinja2 is very powerful. Use loops, conditions, and filters to build your pages dynamically:

```html
<!-- Loop -->
{% for link in config.header_links %}
    <a href="{{ link.url }}">{{ link.title }}</a>
{% endfor %}

<!-- Condition -->
{% if current_output_path == '/index.html' %}
    <div class="hero-banner">...</div>
{% endif %}

<!-- Filter -->
{{ platform | capitalize }}
{{ site_name | upper }}
```

For more information, see the [official Jinja2 documentation](https://jinja.palletsprojects.com/en/stable/templates/).

## 5. Responsive Navigation (Hamburger Menu)

### HTML

```html
<a href="javascript:void(0);" class="icon" onclick="toggleMenu()">&#9776;</a>
<nav class="main-nav" id="myTopnav">
    <ul><!-- your links --></ul>
</nav>
```

### CSS

```css
.icon { display: none; font-size: 30px; cursor: pointer; }

@media screen and (max-width: 768px) {
    .icon { display: block; position: absolute; right: 15px; top: 15px; }
    .main-nav ul { display: none; flex-direction: column; }
    .main-nav.responsive ul { display: block; }
    .main-nav ul li { display: block; text-align: left; }
}
```

### JavaScript

```javascript
function toggleMenu() {
    var x = document.getElementById("myTopnav");
    if (x.className === "main-nav") {
        x.className += " responsive";
    } else {
        x.className = "main-nav";
    }
}
```

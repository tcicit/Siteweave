---
author: TCI
breadcrumbs: true
date: '2026-01-18'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-18'
tags:
- Konfiguration
- Design
- Dokumentation
- konfiguration
title: Themes & Layouts
weight: 30
---

The design of your website is determined by **themes** and **layouts**.

* **Themes** are complete design packages (CSS, JavaScript, templates).
* **Layouts** are specific structure templates for individual pages (e.g., blog post vs. home page).

## 1. Themes

A theme bundles the appearance of your website. Instead of starting from scratch for each project, you can activate a theme and get started right away.

### Activating a theme

You can specify the desired theme in your `config.yaml`:

```yaml
# config.yaml
themes_directory: “themes”  # The folder where your themes are located
site_theme: “my-new-theme” # The name of the subfolder
```

### Creating your own theme

To create your own theme, create a new folder in the `themes` directory. The name of this folder is the theme name.

The structure of a theme looks like this:

```text
themes/
└── my-new-theme/
    ├── templates/          # HTML templates (Jinja2)
    │   ├── base.html       # The basic framework (HTML, Head, Body)
    │   ├── layout_post.html
    │   └── ...
    └── assets/             # Static files
        ├── css/
        │   └── style.css
        ├── js/
        │   └── script.js
        └── images/
            └── screenshot.png
```

### The Override Mechanism (Fallback)

The editor uses an intelligent system to find files. For example, if it needs `base.html`, it searches in this order:

1. **Project folder:** Is there `templates/base.html` in your current project? If so, use that (highest priority).
2. **Theme folder:** Is there a `themes/my-theme/templates/base.html`? If so, use this.
3. **Default (fallback):** If nothing is found, the editor uses its built-in default files.

**What this means for you:**
You can use a theme and still customize individual parts. If you don't like the theme's footer, copy `footer.html` from the theme to your project's `templates` folder and edit it there. Your version takes precedence, while the rest continues to come from the theme.

## 2. Templates & Layouts (Jinja2)

The Static Site Editor uses **Jinja2** as its template engine. This allows you to completely customize the look of your website without having to change the content of your Markdown files.

### The template structure

* **`base.html`**: The basic framework. This is where CSS files are included and the `{% block content %}` is defined.
* **`layout_*.html`**: Specific layouts. They usually inherit from `base.html`.

### Example: A complete `base.html`

Here is an example of a solid `base.html` that correctly includes CSS, JavaScript, and navigation. Pay special attention to the use of `{{ relative_prefix }}` so that links work on all subpages.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} - {{ site_name }}</title>
    
    <!-- CSS integration with relative path -->
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
        <nav>
            <ul>
                {% for link in config.header_links %}
                <li>
                    <!-- relative_prefix ensures that the link is always correct -->
                    <a href="{{ relative_prefix }}{{ link.url }}">{{ link.title }}</a>
                </li>
                {% endfor %}
            </ul>
        </nav>
    </header>

    <main>
        <!-- Placeholder for the content of specific layouts -->
        {% block content %}
            {{ content }}
        {% endblock %}
    </main>

    <footer>
        <p>&copy; {{ now.year }} {{ site_name }}</p>
    </footer>

    <!-- JavaScript integration -->
    <script src="{{ relative_prefix }}js/script.js"></script>

</body>
</html>
```

### Create a new layout

Create a file in the `templates/` folder (of your project or theme), e.g. `layout_special.html`.

```html
<!-- templates/layout_special.html -->
{% extends “base.html” %}

{% block content %}
    <div class="special-design">
        <h1>{{ page_title }}</h1>
        <div class="content">
            {{ content }}
        </div>
    </div>
{% endblock %}
```

## 3. Available variables

Your templates provide you with various variables that are automatically filled in by the editor:

| Variable | Description |
| :--- | :--- |
| `{{ content }}` | The content of your Markdown file converted to HTML. |
| `{{ page_title }}` | The title of the page (from the front matter). |
| `{{ site_name }}` | The name of the website (from `config.yaml`). |
| `{{ date }}` | The date of the page (from the front matter). |
| `{{ relative_prefix }}` | The relative path to the main directory (e.g., `../`). Important for links to CSS/JS files. |
| `{{ current_page_path }}` | The file path of the current page. |
| `{{ current_output_path }}` | The path of the generated HTML file (e.g., `/index.html`). |
| `{{ site_structure }}` | An object containing the entire navigation structure (for menus). |

In addition, all fields that you define in the **front matter** of your Markdown file are available as variables.

**Example:**
Markdown:

```yaml
---
author: John Doe
mood: Happy
---
```

Template:

```html
<p>Written by {{ author }} (mood: {{ mood }})</p>
```

## 4. Jinja2 Basics

Jinja2 is very powerful. You can use loops (`{% for %}`), conditions (`{% if %}`) and filters to build your page dynamically. For more information, see the official Jinja2 documentation.

[Official Jinja documentation](https://jinja.palletsprojects.com/en/stable/)


## 5. Examples of header and footer implementation

### Implementing navigation (header)

To display the `header_links` defined in `config.yaml` (including the new dropdowns), the template must iterate through the list and check if `sublinks` are present.

#### Sample code (Jinja2)

Insert this block in your `base.html` or `partials/header.html` where you want the menu to appear:

```html
<nav class="main-nav">
  <ul>
    {% for link in config.header_links %}
      {# Check whether the link leads to the current page #}
      {% set is_active = False %}
      {% if link.url %}
        {% set norm_url = link.url if link.url.startswith(‘/’) else ‘/’ + link.url %}
        {% if norm_url == current_output_path %}{% set is_active = True %}{% endif %}
      {% endif %}

      {# Check whether submenu items (sublinks) exist #}
      {% if link.sublinks %}
        <li class="dropdown {{ ‘active’ if is_active else ‘’ }}">
          <a href="{{ link.url | default(‘#’) }}" class="dropbtn">
            {{ link.title }}
            <span class="caret">▼</span>
          </a>
          <div class="dropdown-content">
            {% for sublink in link.sublinks %}
              <a href="{{ sublink.url }}">{{ sublink.title }}</a>
            {% endfor %}
          </div>
        </li>
      {% else %}
        {# Normal link without submenu #}
        <li class="{{ ‘active’ if is_active else ‘’ }}">
          <a href="{{ link.url }}">{{ link.title }}</a>
        </li>
      {% endif %}
    {% endfor %}
  </ul>
</nav>
```

## Layout CSS (Cascading Style Sheets)

### CSS (example)

To make the dropdown appear when you hover over it with the mouse, you need the appropriate CSS in your `style.css`:

```css
/* Dropdown container */
.dropdown { position: relative; display: inline-block; }

/* Dropdown content (hidden by default) */
.dropdown-content {
  display: none;
  position: absolute;
  background-color: #fff;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 100;
}

/* Links in dropdown */
.dropdown-content a {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
}

/* Display on hover or when active */
.dropdown:hover .dropdown-content { display: block; }

/* Highlight active link */
.main-nav li.active > a { font-weight: bold; color: #007bff; }
```

### Mobile navigation (hamburger menu)

A space-saving “hamburger menu” is standard for mobile devices. Here is a simple implementation.

#### HTML extension

Add a button and an ID to the navigation area:

```html
<!-- Hamburger icon (visible on mobile) -->
<a href="javascript:void(0);" class="icon" onclick="toggleMenu()">&#9776;</a>

<!-- Navigation with ID for JS access -->
<nav class="main-nav" id="myTopnav">
  <ul>
    <!-- ... Your Jinja loop for links ... -->
  </ul>
</nav>
```

#### CSS for mobile (style.css)

```css
/* Hide hamburger icon by default */
.icon { display: none; font-size: 30px; cursor: pointer; }

/* Mobile view (max. 768px) */
@media screen and (max-width: 768px) {
  .icon { display: block; position: absolute; right: 15px; top: 15px; }
  .main-nav ul { display: none; flex-direction: column; }
  .main-nav.responsive ul { display: block; } /* Set via JS */
  .main-nav ul li { display: block; text-align: left; }
}
```

## JavaScript

```javascript
function toggleMenu() {
  var x = document.getElementById(“myTopnav”);
  if (x.className === “main-nav”) { x.className += “ responsive”; } else { x.className = “main-nav”; }
}
```

## Various tips and tricks

### Footer customization (3-column layout)

A classic footer often contains contact information, social media links, and legal links. Here is an example of a 3-column layout that dynamically loads this data from `config.yaml`.

HTML structure (footer.html)

html
<footer class="site-footer">
  <div class="footer-content">
    
    <!-- Column 1: Contact / Address -->
    <div class="footer-column">
      <h3>Contact</h3>
      {% if config.contact %}
        <p><strong>{{ config.contact.name }}</strong></p>
        <p>{{ config.contact.address }}</p>
        <p>Email: {{ config.contact.email }}</p>
        <p>Tel: {{ config.contact.phone }}</p>
      {% endif %}
    </div>

    <!-- Column 2: Social Media -->
    <div class="footer-column">
      <h3>Social Media</h3>
      <ul class="social-links">
        {% for platform, link in config.social.items() %}
          <li><a href="{{ link }}" target="_blank">{{ platform | title }}</a></li>
        {% endfor %}
      </ul>
    </div>

    <!-- Column 3: Links -->
    <div class="footer-column">
      <h3>Links</h3>
      <ul class="footer-links">
        {% for link in config.footer_links %}
          <li><a href="{{ link.url }}">{{ link.title }}</a></li>
        {% endfor %}
      </ul>
    </div>

  </div>
  
  <div class="footer-bottom">
    <p>&copy; {{ now.year }} {{ config.site_name }}. All rights reserved.</p>
  </div>
</footer>
```

#### CSS for the layout (style.css)

```css
.site-footer { background-color: #333; color: #fff; padding: 40px 0; }

/* Flexbox for the columns */
.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-column { flex: 1; min-width: 250px; margin: 10px; }
.footer-column h3 { border-bottom: 2px solid #555; padding-bottom: 10px; margin-bottom: 20px; }
.footer-column ul { list-style: none; padding: 0; }
.footer-column a { color: #ddd; text-decoration: none; }
.footer-column a:hover { color: #fff; text-decoration: underline; }
.footer-bottom { text-align: center; margin-top: 40px; border-top: 1px solid #444; padding-top: 20px; }
```





---
author: TCI
breadcrumbs: true
date: '2026-02-20'
draft: true
featured_image: ''
layout: doc
release_date: '2027-02-20'
tags:
- Konfiguration
- Design
- Dokumentation
- konfiguration
title: Temlates Details
weight: 50
---

The theme system in Sitewave is based on an inheritance mechanism (fallback chain). This means you can use a complete design package (theme) but still overwrite individual files in your project without having to change the original theme.

### How does the mechanism work?

When the editor generates the website and needs a file (e.g., base.html for the layout or style.css for the design), it searches in the following order:

- Project level (highest priority): First, it looks in your current project folder (templates/ or assets/). If the file exists there, it is used.
- Theme level: If it is not found in the project, it looks in the configured theme folder (themes/your-theme/...).
- App default: If nothing is found there either, the editor uses its built-in default files.
- The advantage: You can use a theme and copy and customize just a single file (e.g., footer.html) in your project folder. The rest will still come from the theme.

## Instructions: Creating your own theme

Navigate to the folder specified in your config.yaml under themes_directory (usually themes).
Create a new subfolder for your theme there, e.g., my-new-theme.
Create the subfolders templates and assets inside it.
The structure should look like this:

```text
 Show full code block 
themes/
└── my-new-theme/
    ├── templates/
    │   ├── base.html       <-- The main layout
    │   └── layout_post.html
    └── assets/
        ├── css/
        │   └── style.css   <-- Your design
        └── js/
            └── script.js
```

Activate the theme in your config.yaml:

```yaml
site_theme: my-new-theme
```


### Example with frontmater

```markdown
---
author: TCI
breadcrumbs: true
date: ‘2025-01-04’
date: ‘2026-01-18’
draft: false
featured_image: None
layout: doc
release_date: ‘2026-01-15’
tags: []
release_date: ‘2026-01-18’
tags:
- Configuration
- Design
title: Themes & Layouts
---

# Themes
The design of your website is determined by **themes** and **layouts**.

## Templates
*   **Themes** are complete design packages (CSS, JavaScript, templates).
*   **Layouts** are specific structure templates for individual pages (e.g., blog post vs. home page).

## 1. Themes

A theme bundles the look and feel of your website. Instead of starting from scratch for each project, you can activate a theme and get started right away.

### Activate theme
``` 

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

### The override mechanism (fallback)

The editor uses an intelligent system to find files. For example, if it needs `base.html`, it searches in this order:

1.  **Project folder:** Is there `templates/base.html` in your current project? If so, use that (highest priority).
2.  **Theme folder:** Is there a `themes/my-theme/templates/base.html`? If so, use this one.
3.  **Default (fallback):** If nothing is found, the editor uses its built-in default files.

**What this means for you:**
You can use a theme and still customize individual parts. If you don't like the footer of the theme, copy `footer.html` from the theme to your project's `templates` folder and edit it there. Your version takes precedence, the rest still comes from the theme.



## 2. Templates & Layouts (Jinja2)

The Static Site Editor uses **Jinja2** as its template engine. This allows you to completely customize the look of your website without having to change the content of your Markdown files.


### The Template Structure

All layout files are located in the `templates/` folder of your project.
*   **`base.html`**: The basic framework. This is where CSS files are included and the `{% block content %}` is defined.
*   **`layout_*.html`**: Specific layouts. They usually inherit from `base.html`.

A typical project has the following structure:

### Creating a new layout

- `base.html`: The basic framework of your website. It contains the `<html>`, `<head>`, and `<body>` tags as well as elements that are the same on every page (e.g., navigation, footer).
- `layout_*.html`: Specific layouts that inherit from `base.html` (e.g., `layout_doc.html` for documentation).


### Creating a new layout

- `base.html`: The basic framework of your website. It contains the `<html>`, `<head>`, and `<body>` tags as well as elements that are the same on every page (e.g., navigation, footer).
- `layout_*.html`: Specific layouts that inherit from `base.html` (e.g., `layout_doc.html` for documentation, `layout_blog.html` for blog posts).

### How do I create a new layout?

To create a new layout, create a new file in the `templates/` folder, e.g. `layout_special.html`.

You can then select this layout in your Markdown front matter:

```yaml
----
title: My special page
layout: special
----
```

*(Note: You omit the `layout_` prefix and the `.html` extension in the front matter.)*

#### Example of a layout

Here is a simple example of what `layout_special.html` might look like:
Create a file in the `templates/` folder (of your project or theme), e.g., `layout_special.html`.

```html
{% extends “base.html” %}
<!-- templates/layout_special.html -->
{% extends “base.html” %}

{% block content %}
    <div class="special-container">
    <div class="special-design">
        <h1>{{ page_title }}</h1>
        <p class="date">Published on: {{ date }}</p>
        
        <hr>
        
        <!-- The actual Markdown content is inserted here -->
        {{ content }}
        <div class="content">
            {{ content }}
        </div>
    </div>
{% endblock %}
```

## 3. Available variables +In Markdown front matter, you use it like this (without layout_ and .html):

Various variables are available in your templates, which are automatically filled in by the editor: 

```+yaml 
--- 
title: My special page +layout: special 
--- 

```

| Variable | Description | 
| :--- | :--- | 
| {{ content }} | The content of your Markdown file converted to HTML. | 
| {{ page_title }} | The title of the page (from the front matter). | 
| {{ site_name }} | The name of the website (from config.yaml). | 
| {{ date }} | The date of the page (from the front matter). | 
| {{ relative_prefix }} | The relative path to the main directory (e.g., ../). Important for links to CSS/JS files. | 
| {{ current_page_path }} | The file path of the current page. | 
| {{ site_structure }} | An object containing the entire navigation structure (for menus). |

### Available variables


In addition, all fields that you define in the front matter of your Markdown file are available as variables. 

You can use these variables in your templates:

Example: Markdown: 

```yaml
author: John Doe -mood: Happy
``` 

| Variable | Description |
| :--- | :--- | 
| {{ content }} | The rendered HTML content from Markdown. | 
| {{ page_title }} | Title of the page. | +| {{ site_name }} | Name of the website (from Config). |
| {{ date }} | Date of the page. | 
| {{ relative_prefix }} | Path to the root (e.g., ../), important for links! | 
| {{ config.social }} | Access to config values (e.g., social media). | 
| {{ site_structure }} | Navigation tree. |

Template: -html -<p>Written by {{ author }} (mood: {{ mood }})</p> 

### Integrate navigation & footer

## 4. Jinja2 basics +In base.html, you can integrate navigation and footer modularly or define them directly.

Jinja2 is very powerful. You can use loops ({% for %}), conditions ({% if %}), and filters to build your page dynamically. For more information, see the official Jinja2 documentation.

## 5. Examples of header and footer implementation

### Implementing navigation (Header)

To display the header_links defined in config.yaml (including the new dropdowns), the template must iterate through the list and check whether sublinks are present.

#### Sample code (Jinja2)
Insert this block in your base.html or partials/header.html where you want the menu to appear:

Example of CSS integration in the head:




```html
 Show full code block 
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


## CSS

#### CSS (example)
To make the dropdown appear when you hover over it with the mouse, you need the appropriate CSS in your style.css:


```css 
/* Dropdown container */ -.dropdown { position: relative; display: inline-block; }
/* Dropdown content (hidden by default) */ -.dropdown-content {

display: none;
position: absolute;
background-color: #fff;
min-width: 160px;
box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
z-index: 100; -}

/* Links in the dropdown */ -.dropdown-content a {
color: black;
padding: 12px 16px;
text-decoration: none;
display: block; -}
/* Display on hover or when active */ -.dropdown:hover .dropdown-content { display: block; }
/* Highlight active link */ -.main-nav li.active > a { font-weight: bold; color: #007bff; } 
```

### Mobile navigation (hamburger menu)

A space-saving “hamburger menu” is standard for mobile devices. Here is a simple implementation.

#### HTML extension

Add a button and an ID to the navigation area:

```html 
☰
```

#### CSS for mobile (style.css)

```css 
/* Hide hamburger icon by default */ -.icon { display: none; font-size: 30px; cursor: pointer; }
/* Mobile view (max. 768px) */ -@media screen and (max-width: 768px) {

.icon { display: block; position: absolute; right: 15px; top: 15px; }
.main-nav ul { display: none; flex-direction: column; }
.main-nav.responsive ul { display: block; } /* Set via JS */
.main-nav ul li { display: block; text-align: left; } -} 
```

## JavaScript

```javascript 

function toggleMenu() {

var x = document.getElementById(“myTopnav”);
if (x.className === “main-nav”) { x.className += “ responsive”; } else { x.className = “main-nav”; } -} 
```

## Various tips and tricks

### Footer customization (3-column layout)

A classic footer often contains contact information, social media links, and legal links. Here is an example of a 3-column layout that dynamically loads this data from config.yaml.

#### HTML structure (footer.html)

```html 

plaintext
 <h3>Contact</h3>
plaintext
 {% if config.contact %}
plaintext
   <p><strong>{{ config.contact.name }}</strong></p>
plaintext
   <p>{{ config.contact.address }}</p>
plaintext
   <p>Email: {{ config.contact.email }}</p>
plaintext
   <p>Tel: {{ config.contact.phone }}</p>
plaintext
 {% endif %}
plaintext
 <h3>Social Media</h3>
plaintext
 <ul class="social-links">
plaintext
   {% for platform, link in config.social.items() %}
plaintext
     <li><a href="{{ link }}" target="_blank">{{ platform | title }}</a></li>
plaintext
   {% endfor %}
plaintext
 </ul>
plaintext
 <h3>Links</h3>
plaintext
 <ul class="footer-links">
plaintext
   {% for link in config.footer_links %}
plaintext
     <li><a href="{{ link.url }}">{{ link.title }}</a></li>
plaintext
   {% endfor %}
plaintext
 </ul>
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
margin: 0 auto; -}
.footer-column { flex: 1; min-width: 250px; margin: 10px; } 
.footer-column h3 { border-bottom: 2px solid #555; padding-bottom: 10px; margin-bottom: 20px; } 
.footer-column ul { list-style: none; padding: 0; } 
.footer-column a { color: #ddd; text-decoration: none; } 
.footer-column a:hover { color: #fff; text-decoration: underline; } 
.footer-bottom { text-align: center; margin-top: 40px; border-top: 1px solid #444; padding-top: 20px; } 

``` 

*(The renderer automatically copies style.css from your theme assets folder to the finished site_output.)*

## Here is a complete example of a base.html file.

The most important thing here is the variable {{ relative_prefix }}. Since your website is static and may have subfolders (e.g., blog/article.html), links to CSS, JS, and images must always be set relative to the main directory. The editor automatically calculates this prefix for each page (e.g., ../ or ../../).

* **`base.html`**: The basic framework. CSS files are integrated here and the `{% block content %}` is defined.
* **`layout_*.html`**: Specific layouts. They usually inherit from `base.html`.

### Example: A complete `base.html`

Here is an example of a solid `base.html` that correctly integrates CSS, JavaScript, and navigation. Pay particular attention to the use of `{{ relative_prefix }}` so that links work on all subpages.

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

### Creating a new layout

Create a file in the `templates/` folder (of your project or theme), e.g. `layout_special.html`.
Explanation of the most important parts:
CSS & JS integration:

```html
<link rel="stylesheet" href="{{ relative_prefix }}css/style.css">
<script src="{{ relative_prefix }}js/script.js"></script>
```

If you are on the home page, relative_prefix is empty. If you are in a subfolder, it is ../. This ensures that the browser always finds the files.

The content block:

```html
{% block content %}
    {{ content }}
{% endblock %}
```

This is the placeholder. When you create a layout such as layout_post.html that uses `{% extends “base.html” %}`, this block is replaced with the content of the post.

Navigation: The loop `{% for link in config.header_links %}` dynamically generates the menu based on your config.yaml.


This is a very common requirement in theme development. Since we use Jinja2 as our template engine, you can use the `{% if %}` logic.

There are two main ways to achieve this:

Method 1: Via the file path (recommended for the home page)
The editor provides the variable current_output_path. For the home page, this path is always /index.html.

Insert this block into your base.html (e.g., directly after the <header>):

html
 Show full code block 
{% if current_output_path == ‘/index.html’ %}
    <div class="hero-banner">
        <!-- relative_prefix ensures that the image is always found -->
        <img src="{{ relative_prefix }}assets/hero-image.jpg" alt="Welcome">
        <h1>Welcome to my website</h1>
    </div>
{% endif %}
```

Method 2: Using front matter variables (More flexible)
If you want to display the image on other pages as well (e.g., a landing page), you can define your own variable in the front matter of the Markdown file.

In the Markdown file (index.md):

```yaml
---
title: Home
show_hero: true
---
```

In base.html:

```html
{% if show_hero %}
    <div class="hero-banner">...</div>
{% endif %}
```


| `{{ date }}` | The date of the page (from the front matter). |
| `{{ relative_prefix }}` | The relative path to the main directory (e.g., `../`). Important for links to CSS/JS files. |
| `{{ current_page_path }}` | The file path of the current page. |
| `{{ current_output_path }}` | The path of the generated HTML file (e.g., `/index.html`). |
| `{{ site_structure }}` | An object containing the entire navigation structure (for menus). |

In addition, all fields that you define in the **front matter** of your Markdown file are available as variables.

```css
.footer-column a:hover { color: #fff; text-decoration: underline; }
.footer-bottom { text-align: center; margin-top: 40px; border-top: 1px solid #444; padding-top: 20px; }
```

### Display elements only on the home page

Often, you want to display certain elements, such as a large header image (hero image), only on the home page. To do this, you can use the variable current_output_path.

#### Example for base.html

html
{% if current_output_path == ‘/index.html’ %}

   <!-- relative_prefix is important if the page is moved later -->

   <img src="{{ relative_prefix }}assets/header.jpg" alt="Welcome">

   <div class="hero-text">

       <h1>Welcome to my website</h1>

   </div>
{% endif %} 

```
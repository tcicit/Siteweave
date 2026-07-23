import os
'''
Worker-Skript, das ein neues Projekt mit einem Standard-Blog-Template erstellt.
Es erstellt eine vorgefertigte Verzeichnisstruktur mit Beispiel-Templates, CSS, JavaScript und Content, die als Ausgangspunkt für die Entwicklung eines neuen Blogs dienen kann.
Das Skript ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für die Erstellung des Templates befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen wird, sondern eher als "Projekt-Template" dient, das
beim Erstellen eines neuen Projekts ausgewählt werden kann.


'''

name = "Template: Standard-Blog erstellen"
description = "Erstellt ein neues Projekt mit dem Standard-Blog-Template."
category = "template"
hidden = False

# Basis-Verzeichnis für das Template
BASE_DIR = os.path.join(os.path.dirname(__file__), "project_templates", "Standard-Blog")

def create_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Erstellt: {rel_path}")

print(f"Erstelle Template in: {BASE_DIR}")

# 1. Konfiguration
create_file("config.yaml", """site_name: "__PROJECT_NAME__"
site_logo: "assets/logo.png
site_url: "http://localhost:8000"
content_directory: "content"
site_output_directory: "site_output"
template_directory: "templates"
assets_directory: "assets"
plugin_directory: "plugins"
backup_directory: "backup"
markdown_extensions: [".md", ".markdown"]
log_level: "INFO"
header_links:
  - title: "Home"
    url: "index.html"
  - title: "Artikel"
    url: "blog/index.html"
  - title: "Über mich"
    url: "ueber.html"
""")

# 2. CSS
create_file("css/style.css", """/* Standard Blog Styles */
:root {
    --primary-color: #2ecc71; /* Angepasst: Grün statt Blau */
    --text-color: #333;
    --bg-color: #f4f4f4;
    --header-bg: #fff;
    --link-color: #2980b9;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
    margin: 0;
    padding: 0;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

/* Header & Navigation */
header {
    background: var(--header-bg);
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
}

header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header h1 { margin: 0; font-size: 1.5rem; }
header h1 a { color: #333; text-decoration: none; }

nav ul { list-style: none; padding: 0; margin: 0; display: flex; }
nav li { position: relative; margin-left: 20px; }
nav a {
    text-decoration: none;
    color: #666;
    font-weight: 500;
    transition: color 0.2s;
    display: block;
}
nav a:hover { color: var(--primary-color); }

/* Dropdown */
nav .dropdown {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    background: #fff;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    min-width: 180px;
    z-index: 100;
    border-radius: 4px;
    padding: 5px 0;
}
nav li:hover .dropdown { display: block; }
nav .dropdown li { margin: 0; display: block; }
nav .dropdown a { padding: 8px 15px; font-size: 0.95rem; color: #555; }
nav .dropdown a:hover { background: #f9f9f9; color: var(--primary-color); }

/* Content */
article {
    background: #fff;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    margin-bottom: 30px;
}

h1, h2, h3 { color: #2c3e50; margin-top: 1.5em; }
h1 { margin-top: 0; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }

a { color: var(--link-color); text-decoration: none; }
a:hover { text-decoration: underline; }

img { max-width: 100%; height: auto; border-radius: 4px; }

/* Blog Post Meta */
.post-header { margin-bottom: 2rem; }
.meta { color: #888; font-size: 0.9rem; margin-top: 0.5rem; }
.post-tags { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee; }
.tag { 
    background: #eee; color: #555; 
    padding: 3px 8px; border-radius: 3px; 
    font-size: 0.85rem; margin-right: 5px; 
}

/* Footer */
footer {
    text-align: center;
    padding: 40px 0;
    color: #888;
    font-size: 0.9rem;
    margin-top: 40px;
    border-top: 1px solid #e0e0e0;
}
""")

# 3. JavaScript
create_file("js/main.js", """// Main JavaScript file
console.log('Blog Template geladen.');
""")

# 4. Templates
# Base Template
create_file("templates/base.html", """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} | Mein Blog</title>
    
    <link rel="stylesheet" href="{{ relative_prefix }}css/style.css">
    
    {# Plugin CSS Dateien laden #}
    {% for css_file in plugin_css_files %}
    <link rel="stylesheet" href="{{ relative_prefix }}{{ css_file }}">
    {% endfor %}
</head>
<body>

    {% include 'partials/header.html' %}

    <div class="container">
        {% block content %}
            {{ content }}
        {% endblock %}
    </div>

    {% include 'partials/footer.html' %}

    <script src="{{ relative_prefix }}js/main.js"></script>
</body>
</html>
""")

# Partials
create_file("templates/partials/header.html", """<header>
    <div class="container">
        <h1><a href="{{ relative_prefix }}index.html">{{ config.site_name }}</a></h1>
        <nav>
            <ul>
            {% for link in config.header_links %}
            <li>
                <a href="{{ relative_prefix }}{{ link.url }}">{{ link.title }}</a>
                {% if link.children %}
                <ul class="dropdown">
                    {% for sublink in link.children %}
                    <li><a href="{{ relative_prefix }}{{ sublink.url }}">{{ sublink.title }}</a></li>
                    {% endfor %}
                </ul>
                {% endif %}
            </li>
            {% endfor %}
            </ul>
        </nav>
    </div>
</header>
""")

create_file("templates/partials/footer.html", """<footer>
    <p>&copy; 2025 {{ config.site_name }}. Design angepasst.</p>
</footer>
""")

# Layouts
create_file("templates/layout_full-width.html", """{% extends "base.html" %}

{% block content %}
    <article>
        {% if title %}
        <h1>{{ title }}</h1>
        {% endif %}
        
        {{ content }}
    </article>
{% endblock %}
""")

create_file("templates/layout_post.html", """{% extends "base.html" %}

{% block content %}
    <article class="blog-post">
        <header class="post-header">
            <h1>{{ title }}</h1>
            <div class="meta">
                <span>Veröffentlicht am {{ date }}</span>
                {% if author %} | <span>von {{ author }}</span>{% endif %}
            </div>
        </header>
        
        <div class="post-content">
            {{ content }}
        </div>
        
        {% if tags %}
        <div class="post-tags">
            Tags: 
            {% for tag in tags %}
            <span class="tag">#{{ tag }}</span>
            {% endfor %}
        </div>
        {% endif %}
    </article>
{% endblock %}
""")

# 5. Content
# Index
create_file("content/index.md", """---
title: Willkommen
date: 2025-01-01
layout: full-width
---

Willkommen auf meinem neuen Blog! Dies ist die Startseite.

## Neueste Artikel

[[latest_posts count="3" show_excerpt="true"]]

[Alle Artikel ansehen](blog/index.html)
""")

# Über mich
create_file("content/ueber.md", """---
title: Über mich
date: 2025-01-01
layout: full-width
---

Hallo! Ich bin der Autor dieses Blogs.

Ich schreibe über Technik, Programmierung und das Leben.
""")

# Blog Index
create_file("content/blog/index.md", """---
title: Alle Artikel
date: 2025-01-01
layout: full-width
---

Hier finden Sie eine Übersicht aller meiner Blog-Artikel.

[[list_dir path="blog" sort="date"]]
""")

# Beispiel Post
create_file("content/blog/hallo-welt.md", """---
title: Hallo Welt
date: 2025-01-02
author: Admin
layout: post
tags: [Allgemein, Intro]
---

Dies ist mein erster Blog-Eintrag.

Ich freue mich darauf, hier meine Gedanken zu teilen.

## Was euch erwartet

* Spannende Tutorials
* Interessante Einblicke
* Und vieles mehr...

Bleibt dran!
""")

print("\\nFertig! Das Template 'Standard-Blog' wurde erstellt.")
print("Starte nun den Editor neu und wähle 'Neues Projekt erstellen...', um es zu nutzen.")

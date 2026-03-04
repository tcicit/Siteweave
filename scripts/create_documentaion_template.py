import os

'''
Worker-Skript, das ein neues Projekt mit einem Dokumentations-Template erstellt.
Es erstellt eine vorgefertigte Verzeichnisstruktur mit Beispiel-Templates, CSS, JavaScript und Content, die als Ausgangspunkt für die Entwicklung einer technischen Dokumentation, eines Wikis oder einerWissensdatenbank dienen kann.
Das Skript ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für die Erstellung des Templates befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen wird, sondern eher als "Projekt-Template" dient, das
beim Erstellen eines neuen Projekts ausgewählt werden kann.


'''

name = "Template: Dokumentation erstellen"
description = "Erstellt ein neues Projekt mit dem Dokumentations-Template."
category = "template"
hidden = False

# Basis-Verzeichnis für das Template
BASE_DIR = os.path.join(os.path.dirname(__file__), "project_templates", "Dokumentation")

def create_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Erstellt: {rel_path}")

print(f"Erstelle Template in: {BASE_DIR}")

# 1. Konfiguration
create_file("config.yaml", """site_name: "{{ config.site_name }}"
site_logo: "assets/logo.png"
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
footer_links:
  - title: "Impressum"
    url: "impressum.html"
  - title: "Datenschutz"
    url: "datenschutz.html"
            
""")

# 2. CSS
create_file("css/style.css", """/* Documentation Template Styles */
:root {
    --primary-color: #2980b9;
    --text-color: #333;
    --bg-color: #fff;
    --sidebar-bg: #f7f9fa;
    --sidebar-width: 280px;
    --header-height: 60px;
    --link-color: #2980b9;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    color: var(--text-color);
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

a { color: var(--link-color); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Header */
header {
    background: var(--primary-color);
    color: white;
    height: var(--header-height);
    display: flex;
    align-items: center;
    padding: 0 20px;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.logo-link { display: flex; align-items: center; }
.header-logo { height: 40px; margin-right: 15px; }

header h1 { margin: 0; font-size: 1.2rem; }
header h1 a { color: white; text-decoration: none; }
header nav { margin-left: auto; }
header nav ul { list-style: none; padding: 0; margin: 0; display: flex; }
header nav li { position: relative; }
header nav a { color: white; margin-left: 15px; text-decoration: none; font-size: 0.9rem; display: block; }

/* Dropdown Menu */
header nav .dropdown {
    display: none;
    position: absolute;
    top: 100%;
    right: 0;
    background: #fff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    min-width: 160px;
    z-index: 1000;
    border-radius: 4px;
}
header nav li:hover .dropdown { display: block; }
header nav .dropdown li { display: block; margin: 0; }
header nav .dropdown a { color: #333; padding: 10px 15px; margin: 0; display: block; }
header nav .dropdown a:hover { background: #f4f4f4; color: var(--primary-color); }

/* Layout Container */
.doc-container {
    display: flex;
    margin-top: var(--header-height);
    min-height: calc(100vh - var(--header-height));
}

/* Sidebar Navigation */
.sidebar {
    width: var(--sidebar-width);
    background: var(--sidebar-bg);
    border-right: 1px solid #e1e4e8;
    padding: 20px;
    position: fixed;
    top: var(--header-height);
    bottom: 0;
    overflow-y: auto;
}

.sidebar h3 { font-size: 0.9rem; text-transform: uppercase; color: #666; margin-top: 0; margin-bottom: 15px; }

/* Styles für das generierte Menü */
.sidebar ul { list-style: none; padding: 0; margin: 0; }
.sidebar li { margin-bottom: 2px; }
.sidebar a, .sidebar .dropbtn { 
    text-decoration: none; 
    color: #444; 
    font-size: 0.95rem; 
    display: block; 
    padding: 6px 10px; 
    border-radius: 4px;
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    cursor: pointer;
}
.sidebar a:hover, .sidebar .dropbtn:hover { background-color: #e1e4e8; color: var(--primary-color); }
.sidebar a.active { background-color: #e1e4e8; color: var(--primary-color); font-weight: bold; }

/* Dropdown/Submenu Styles */
.sidebar .dropdown-content { display: none; padding-left: 15px; }
.sidebar .active-parent > .dropdown-content, 
.sidebar .dropdown:hover > .dropdown-content { display: block; }
.sidebar .dropbtn::after { content: ' ▼'; font-size: 0.7em; float: right; }

/* Main Content */
.content {
    margin-left: calc(var(--sidebar-width) + 20px);
    padding: 40px;
    max-width: 800px;
    flex: 1;
}

h1 { border-bottom: 1px solid #eee; padding-bottom: 10px; margin-top: 0; }
h2 { margin-top: 2em; }
code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; color: #c7254e; }
pre { background: #f6f8fa; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #e1e4e8; }
pre code { background: none; color: inherit; padding: 0; }
blockquote { border-left: 4px solid var(--primary-color); margin: 1.5em 0; padding-left: 15px; color: #666; background: #f9f9f9; padding: 10px 15px; }
img { max-width: 100%; height: auto; border-radius: 4px; border: 1px solid #eee; }

/* Footer */
footer {
    margin-left: calc(var(--sidebar-width) + 20px);
    padding: 20px 40px;
    border-top: 1px solid #eee;
    font-size: 0.85rem;
    color: #888;
    text-align: center;
    background: #fff;
}

.footer-links {
    margin-left: 1em;
}

.footer-links a {
    margin: 0 5px;
    color: #666;
}

@media (max-width: 768px) {
    .sidebar { display: none; } /* Mobile: Hide sidebar for simplicity */
    .content { margin-left: 0; }
    footer { margin-left: 0; }
}
""")

# 3. JavaScript
create_file("js/main.js", """console.log('Documentation Template loaded.');""")

# 4. Templates
# Base
create_file("templates/base.html", """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} | __PROJECT_NAME__</title>
    <link rel="stylesheet" href="{{ relative_prefix }}css/style.css">
    {% for css_file in plugin_css_files %}
    <link rel="stylesheet" href="{{ relative_prefix }}{{ css_file }}">
    {% endfor %}
</head>
<body>
    {% include 'partials/header.html' %}

    <div class="doc-container">
        <aside class="sidebar">
            <h3>Inhalt</h3>
            <!-- Automatische Navigation basierend auf der Ordnerstruktur -->
            {{ generate_index_html(site_structure, relative_prefix, current_output_path) | safe }}
        </aside>

        <main class="content">
            {% block content %}
                {{ content }}
            {% endblock %}
        </main>
    </div>

    {% include 'partials/footer.html' %}
    <script src="{{ relative_prefix }}js/main.js"></script>
</body>
</html>
""")

# Partials
create_file("templates/partials/header.html", """<header>
    {% if config.site_logo %}
    <a href="{{ relative_prefix }}index.html" class="logo-link">
        <img src="{{ relative_prefix }}{{ config.site_logo }}" alt="Logo" class="header-logo">
    </a>
    {% endif %}
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
</header>
""")

create_file("templates/partials/footer.html", """<footer>
    <span>&copy; {{ now.year }} {{ config.site_name }}. Erstellt mit Sitewave.</span>
    {% if config.footer_links %}
    <span class="footer-links">
        {% for link in config.footer_links %}
        <a href="{{ relative_prefix }}{{ link.url }}">{{ link.title }}</a>{% if not loop.last %} |{% endif %}
        {% endfor %}
    </span>
    {% endif %}
</footer>
""")

# Layouts
create_file("templates/layout_doc.html", """{% extends "base.html" %}

{% block content %}
    <h1>{{ title }}</h1>
    
    {% if date %}
    <p style="color: #888; font-size: 0.9em;">Zuletzt aktualisiert: {{ date }}</p>
    {% endif %}

    {{ content }}
{% endblock %}
""")

create_file("templates/layout_full-width.html", """{% extends "base.html" %}
{% block content %}
    {{ content }}
{% endblock %}
""")

# 5. Content
create_file("content/index.md", """---
title: Einführung
layout: doc
---

Willkommen zur Dokumentation für **{{ config.site_name }}**.

Dies ist ein Template, das speziell für technische Dokumentationen, Wikis oder Wissensdatenbanken entwickelt wurde.

## Features dieses Templates

* **Sidebar-Navigation:** Automatisch generiert aus der Ordnerstruktur.
* **Sauberes Design:** Fokus auf Lesbarkeit.
* **Responsive:** Passt sich (teilweise) an mobile Geräte an.

## Wie geht es weiter?

1. Bearbeite diese Seite in `content/index.md`.
2. Füge neue Seiten im `content`-Ordner hinzu.
3. Erstelle Unterordner für Kapitel (z.B. `content/anleitung/`).

[[infobox type="info" title="Tipp"]]
Nutze die **Gliederung** im Editor, um schnell durch lange Dokumente zu navigieren.
[[/infobox]]
""")

create_file("content/installation.md","""

---
title: Installation
layout: doc
---

## Voraussetzungen

Bevor du beginnst, stelle sicher, dass du folgende Software installiert hast:

* Python 3.8 oder neuer
* pip (Python Package Installer)

## Installationsschritte

1. Klone das Repository:
   ```bash
   git clone https://github.com/dein-user/{{ config.site_name }}.git
``` 

""")

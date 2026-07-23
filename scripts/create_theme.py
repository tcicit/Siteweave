import os
import sys

def create_theme(theme_name, base_dir="themes"):
    """
    Erstellt eine neue Theme-Struktur.
    - theme_name: Name des neuen Themes (z.B. "mein-neues-theme")
    - base_dir: Basisverzeichnis, in dem das Theme erstellt wird (standardmäßig "themes")   
    Das Skript erstellt folgende Struktur:
    themes/
    └── mein-neues-theme/
        ├── templates/
        │   ├── base.html
        │   └── layout_full-width.html
        ├── css/
        │   └── style.css
        ├── js/
        │   └── main.js
        └── assets/     
        Es werden einfache Standarddateien erstellt, die als Ausgangspunkt für die Entwicklung eines neuen Themes dienen können.
        
    """
    # Pfad zum Theme-Ordner (standardmäßig im 'themes' Ordner des aktuellen Verzeichnisses)
    theme_path = os.path.join(base_dir, theme_name)

    if os.path.exists(theme_path):
        print(f"Fehler: Das Theme '{theme_name}' existiert bereits in '{base_dir}'.")
        return

    print(f"Erstelle Theme '{theme_name}' in '{theme_path}'...")

    # 1. Verzeichnisstruktur erstellen
    subdirs = ["templates", "css", "js", "assets"]
    for d in subdirs:
        os.makedirs(os.path.join(theme_path, d), exist_ok=True)

    # 2. base.html erstellen (Das Grundgerüst)
    base_html = """<!DOCTYPE html>
<html lang="{{ config.language | default('de') }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} | {{ config.site_name }}</title>
    
    <!-- Theme CSS -->
    <link rel="stylesheet" href="{{ relative_prefix }}css/style.css">
    
    <!-- Plugin CSS (automatisch eingebunden) -->
    {% for css_file in plugin_css_files %}
    <link rel="stylesheet" href="{{ relative_prefix }}{{ css_file }}">
    {% endfor %}
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <a href="{{ relative_prefix }}index.html">{{ config.site_name }}</a>
            </div>
            <nav>
                <ul>
                {% for link in config.header_links %}
                    <li><a href="{{ relative_prefix }}{{ link.url }}">{{ link.title }}</a></li>
                {% endfor %}
                </ul>
            </nav>
        </div>
    </header>

    <main class="container">
        {% block content %}
            {{ content }}
        {% endblock %}
    </main>

    <footer>
        <div class="container">
            <p>&copy; {{ now.year }} {{ config.site_name }}</p>
            <nav>
                {% for link in config.footer_links %}
                    <a href="{{ relative_prefix }}{{ link.url }}">{{ link.title }}</a>
                {% endfor %}
            </nav>
        </div>
    </footer>

    <!-- Theme JS -->
    <script src="{{ relative_prefix }}js/main.js"></script>
</body>
</html>"""

    with open(os.path.join(theme_path, "templates", "base.html"), "w", encoding="utf-8") as f:
        f.write(base_html)

    # 3. Ein Standard-Layout erstellen (layout_full-width.html)
    layout_html = """{% extends "base.html" %}

{% block content %}
    <article>
        {% if title %}
        <h1>{{ title }}</h1>
        {% endif %}
        
        <div class="content">
            {{ content }}
        </div>
    </article>
{% endblock %}"""

    with open(os.path.join(theme_path, "templates", "layout_full-width.html"), "w", encoding="utf-8") as f:
        f.write(layout_html)

    # 4. CSS erstellen
    css_content = """/* Basis Styles für Theme: """ + theme_name + """ */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
    background-color: #f9f9f9;
}

.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 20px;
}

header {
    background: #ffffff;
    border-bottom: 1px solid #eaeaea;
    padding: 1rem 0;
    margin-bottom: 2rem;
}

header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header .logo a {
    font-size: 1.5rem;
    font-weight: bold;
    text-decoration: none;
    color: #333;
}

nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    gap: 20px;
}

nav a {
    text-decoration: none;
    color: #555;
}

nav a:hover {
    color: #000;
}

main {
    background: #fff;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    min-height: 50vh;
}

footer {
    text-align: center;
    padding: 40px 0;
    color: #888;
    font-size: 0.9rem;
}

img {
    max-width: 100%;
    height: auto;
}
"""
    with open(os.path.join(theme_path, "css", "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

    # 5. JS erstellen
    js_content = """console.log('Theme """ + theme_name + """ loaded.');"""
    with open(os.path.join(theme_path, "js", "main.js"), "w", encoding="utf-8") as f:
        f.write(js_content)

    print("Fertig!")
    print(f"Um das Theme zu nutzen, setze in deiner config.yaml: site_theme: \"{theme_name}\"")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python create_theme.py [THEME_NAME]")
        print("Beispiel:   python create_theme.py mein-neues-theme")
    else:
        create_theme(sys.argv[1])

import os
import shutil

name = "Template: One Pager"
description = "Erstellt ein neues Projekt mit einem One-Pager-Layout."
category = "template" # This category is for the dialog, not for worker menu
hidden = False # This script is a template generator, not a regular worker

# Basis-Verzeichnis für das Template
# This will be copied to the new project location
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "project_templates", "One-Pager")

def create_file(rel_path, content):
    full_path = os.path.join(TEMPLATE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    # print(f"Erstellt: {rel_path}") # Suppress print for template creation

# Ensure the template directory is clean before creating files
if os.path.exists(TEMPLATE_DIR):
    shutil.rmtree(TEMPLATE_DIR)
os.makedirs(TEMPLATE_DIR)

# 1. Konfiguration
create_file("config.yaml", """site_name: "{{ config.site_name }}"
site_logo: "assets/logo.png"
site_url: "{{ config.site_url }}"
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
    url: "#home"
  - title: "About"
    url: "#about"
  - title: "Services"
    url: "#services"
  - title: "Contact"
    url: "#contact"
""")

# 2. CSS
create_file("assets/css/style.css", """/* One-Pager Template Styles */
:root {
    --primary-color: #3498db;
    --text-color: #333;
    --bg-color: #f8f8f8;
    --header-bg: #fff;
    --link-color: #3498db;
    --section-padding: 80px 0;
}

html {
    scroll-behavior: smooth;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
    margin: 0;
    padding: 0;
}

a { color: var(--link-color); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Header & Navigation */
header {
    background: var(--header-bg);
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    position: fixed;
    width: 100%;
    top: 0;
    left: 0;
    z-index: 1000;
}

header .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header h1 { margin: 0; font-size: 1.8rem; }
header h1 a { color: #333; text-decoration: none; }

nav ul { list-style: none; padding: 0; margin: 0; display: flex; }
nav li { margin-left: 30px; }
nav a {
    text-decoration: none;
    color: #666;
    font-weight: 500;
    transition: color 0.2s;
    display: block;
    padding: 5px 0;
}
nav a:hover, nav a.active { color: var(--primary-color); }

/* Sections */
section {
    padding: var(--section-padding);
    text-align: center;
    min-height: 100vh; /* Ensure sections take full viewport height */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

section:nth-of-type(even) {
    background-color: #f0f0f0;
}

section:nth-of-type(odd) {
    background-color: #fff;
}

/* Custom Backgrounds */
.bg-primary { background-color: var(--primary-color) !important; color: white; }
.bg-dark { background-color: #2c3e50 !important; color: white; }
.bg-light { background-color: #ecf0f1 !important; }
.bg-image-hero { background-image: url('../assets/hero-bg.jpg'); }
.bg-image-services { background-image: url('../assets/services-bg.jpg'); }

/* Content within sections */
section .content-wrapper {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    background-color: rgba(255, 255, 255, 0.9); /* Semi-transparent background for text on images */
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

section.bg-primary .content-wrapper,
section.bg-dark .content-wrapper {
    background-color: rgba(0, 0, 0, 0.4);
    color: white;
}

section h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: inherit; /* Inherit color from section */
}

section p {
    font-size: 1.1rem;
    line-height: 1.8;
    color: inherit;
}

/* Footer */
footer {
    text-align: center;
    padding: 40px 0;
    color: #888;
    font-size: 0.9rem;
    border-top: 1px solid #e0e0e0;
    background-color: var(--header-bg);
}

@media (max-width: 768px) {
    header .container { flex-direction: column; }
    nav ul { margin-top: 10px; }
    nav li { margin: 0 10px; }
    section { padding: 60px 0; }
    section h2 { font-size: 2rem; }
    section .content-wrapper { padding: 15px; }
}
""")

# 3. JavaScript
create_file("assets/js/main.js", """// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Highlight active nav link on scroll (optional)
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('nav a');

    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - sectionHeight / 3) { // Adjust offset as needed
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').substring(1) === current) {
            link.classList.add('active');
        }
    });
});

console.log('One-Pager Template loaded.');
""")

# 4. Templates
# Base
create_file("templates/base.html", """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} | {{ config.site_name }}</title>
    
    <link rel="stylesheet" href="{{ relative_prefix }}assets/css/style.css">
    {% for css_file in plugin_css_files %}
    <link rel="stylesheet" href="{{ relative_prefix }}{{ css_file }}">
    {% endfor %}
</head>
<body>

    {% include 'partials/header.html' %}

    <main>
        {% block content %}
            {{ content }}
        {% endblock %}
    </main>

    {% include 'partials/footer.html' %}
    <script src="{{ relative_prefix }}assets/js/main.js"></script>
</body>
</html>
""")

# Partials
create_file("templates/partials/header.html", """<header>
    <div class="container">
        <h1><a href="#home">{{ config.site_name }}</a></h1>
        <nav>
            <ul>
            {% for link in config.header_links %}
            <li>
                <a href="{{ link.url }}">{{ link.title }}</a>
            </li>
            {% endfor %}
            </ul>
        </nav>
    </div>
</header>
""")

create_file("templates/partials/footer.html", """<footer>
    <p>&copy; {{ now.year }} {{ config.site_name }}. All rights reserved.</p>
</footer>
""")

# Layouts
create_file("templates/layout_onepager_main.html", """{% extends "base.html" %}

{% block content %}
    {{ content }}
{% endblock %}
""")

create_file("templates/layout_onepager_section.html", """{% extends "base.html" %}

{% block content %}
    <section id="{{ section_id }}" class="{{ section_class }}" {% if background_image %}style="background-image: url('{{ relative_prefix }}{{ background_image }}');"{% endif %}>
        <div class="content-wrapper">
            <h2>{{ title }}</h2>
            {{ content }}
        </div>
    </section>
{% endblock %}
""")

# 5. Assets (dummy images)
create_file("assets/logo.png", "") # Placeholder
create_file("assets/hero-bg.jpg", "") # Placeholder
create_file("assets/services-bg.jpg", "") # Placeholder

# 6. Content
create_file("content/index.md", """---
title: Willkommen
layout: onepager_main
---

[[include src="section-home.md"]]
[[include src="section-about.md"]]
[[include src="section-services.md"]]
[[include src="section-contact.md"]]
""")

create_file("content/section-home.md", """---
title: Your Awesome One-Pager
layout: onepager_section
section_id: home
section_class: bg-image-hero text-white
background_image: assets/hero-bg.jpg
weight: 10
---

<p>Welcome to our modern and responsive one-page website template.</p>
<p>Scroll down to discover more about us!</p>
""")

create_file("content/section-about.md", """---
title: About Us
layout: onepager_section
section_id: about
section_class: bg-light
weight: 20
---

<p>We are a team of passionate individuals dedicated to creating amazing things.</p>
<p>Our mission is to deliver high-quality solutions that exceed your expectations.</p>
""")

create_file("content/section-services.md", """---
title: Our Services
layout: onepager_section
section_id: services
section_class: bg-image-services text-white
background_image: assets/services-bg.jpg
weight: 30
---

<p>We offer a wide range of services to meet your needs.</p>
<ul>
    <li>Web Design & Development</li>
    <li>Digital Marketing</li>
    <li>Content Creation</li>
    <li>Consulting</li>
</ul>
""")

create_file("content/section-contact.md", """---
title: Contact Us
layout: onepager_section
section_id: contact
section_class: bg-dark text-white
weight: 40
---

<p>Have a question or want to work with us? Get in touch!</p>
<p>Email: info@example.com</p>
<p>Phone: +1 (123) 456-7890</p>
""")

print("\\nFertig! Das Template 'One-Pager' wurde erstellt.")
print("Starte nun den Editor neu und wähle 'Neues Projekt erstellen...', um es zu nutzen.")

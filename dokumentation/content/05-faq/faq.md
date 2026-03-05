---
Test: AAA
author: TCI
breadcrumbs: true
date: '2025-01-09'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags: []
test: ''
title: Häufig gestellte Fragen (FAQ)
weight: 10
---

Here you will find answers to some of the most frequently asked questions about using the TCI Static Site Editor.

### My changes are not visible online. What am I doing wrong?

After you have made changes to your Markdown files, you need to perform two steps:

1.  **Render:** Click on the **“Render”** button in the toolbar. This will rebuild your website in the `site_output` folder.
2.  **Upload:** Upload the **contents** of the `site_output` folder to your web server again (e.g., via FTP).

### Can I completely change the appearance of my website?

Yes. The appearance is controlled by the files in the `templates/` and `assets/css/` folders.

*   **Colors, fonts, spacing:** Change the `style.css` file.
*   **Basic layout (header, footer):** Edit the `templates/base.html` file.
*   **Page-specific layouts:** Edit the `templates/layout_*.html` files.

### How do I create navigation or a menu?

Most of the included templates (such as the documentation template) generate navigation **automatically** from the folder and file structure of your `content` directory.

* A folder in `content` becomes a menu item with a submenu.
* A file in `content` becomes a direct link.

So all you have to do is organize your files logically, and the template takes care of the rest.

### What is the difference between snippets and plugins?

Translated with DeepL.com (free version)

* **Snippets** are static text modules. They are ideal for quickly inserting recurring but unchangeable content (such as a signature or a complex table) using drag & drop.
* **Plugins (shortcodes)** are dynamic. They are executed by Python code and can contain logic, access other files, or generate content based on parameters (e.g., create a gallery from a folder).

### Do I need to be online to use the editor?

No. The editor is a pure desktop application and works completely **offline**. You only need an internet connection if you want to upload your finished website to a server.

### How can I create a backup of my project?

There are several easy ways:

1.  **Manually:** Simply copy the entire project folder to a safe location.
2.  **Automatically:** The editor has a built-in backup feature that regularly creates copies of your `content` folder in the `backup` directory.
3.  **Professionally (recommended):** Use a version control system such as **Git**. This allows you to track and restore every change.
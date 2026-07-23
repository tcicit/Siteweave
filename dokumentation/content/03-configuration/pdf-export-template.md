---
author: TCI
breadcrumbs: true
date: '2028-04-09'
draft: false
featured_image: ''
layout: doc
release_date: '2026-04-09'
tags:
- Configuration
- Documentation
title: PDF Export Templates
weight: 40
---

To create a custom PDF theme and have it appear in the Project Configuration dialog (under the "PDF Export" tab), follow a standard folder structure. The system automatically scans these locations.

## Step-by-Step Guide

### 1. Choose Location

You can store PDF themes in two locations:
* **Global (all projects):** Create a `pdf_themes` folder in the app root directory (alongside `main.py`).
* **Project-specific:** Create a `pdf_themes` folder directly inside your project folder.

### 2. Create the Theme Directory

Create a subfolder inside `pdf_themes/`. The folder name will be displayed in the theme selector dropdown.

Example: `pdf_themes/my-manual-theme/`

### 3. Add Required Files

Inside your theme folder (e.g. `my-manual-theme/`), add at least:

#### a) `style.css` (Required)

Defines the visual design of your PDF output. Siteweave uses WeasyPrint, supporting standard CSS for paged media.

```css
/* Example style.css */
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Helvetica', sans-serif;
    color: #333;
}

h1 {
    color: #2c3e50;
    border-bottom: 2px solid #2c3e50;
}

.cover-page {
    text-align: center;
    page-break-after: always;
}
```

#### b) `config.yaml` (Optional)
Specify default settings for the theme that load when selected.

```yaml
# Example config.yaml
features:
  toc_depth: 3
  show_cover_page: true
  include_index_files: false
```

### 4. Activation
1. Open the Project Configuration dialog in Siteweave.
2. Go to the **PDF Export** tab.
3. Select your new theme from the **Theme** dropdown. A live preview will render immediately.

[[infobox type="tip" title="Development Tip"]]
If you edit `style.css` while the settings dialog is open, switch themes back and forth to refresh the live preview, or click the folder icon (📁) to open the theme directory on disk.
[[/infobox]]

---

## Professional CSS Example for PDF Themes

Below is an example utilizing CSS Paged Media (`@page`) margin boxes for headers, footers, and page numbers:

```css
@page {
    size: A4;
    margin-top: 3cm;
    margin-bottom: 2.5cm;
    margin-left: 2cm;
    margin-right: 2cm;

    @top-right {
        content: string(chapter-title);
        font-family: sans-serif;
        font-size: 9pt;
        color: #666;
    }

    @bottom-left {
        content: "Siteweave Documentation";
        font-family: sans-serif;
        font-size: 9pt;
        color: #666;
    }

    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-family: sans-serif;
        font-size: 9pt;
        color: #666;
    }
}

h1 {
    string-set: chapter-title content();
    break-before: page;
}

.toc a::after {
    content: target-counter(attr(href), page);
    float: right;
}
```

### Key Features Explained
- **`@top-left`, `@bottom-right`**: Page margin boxes where headers and footers are placed.
- **`string-set` & `string()`**: Captures header titles (e.g. `h1`) and renders them dynamically in top margins.
- **`counter(page)` & `counter(pages)`**: Page numbers and total count.
- **`target-counter`**: Automatically fills page numbers for TOC links.
- **`break-before: page`**: Forces major chapters to start on fresh pages.

---

## Using Local Custom Fonts

Include `.ttf` or `.woff` fonts in your theme folder:

```text
pdf_themes/
  my-theme/
    style.css
    fonts/
      MyFont-Regular.ttf
      MyFont-Bold.ttf
```

Reference them inside `style.css`:

```css
@font-face {
    font-family: 'MyFont';
    src: url('fonts/MyFont-Regular.ttf');
    font-weight: normal;
    font-style: normal;
}

@font-face {
    font-family: 'MyFont';
    src: url('fonts/MyFont-Bold.ttf');
    font-weight: bold;
    font-style: normal;
}

body {
    font-family: 'MyFont', sans-serif;
}
```
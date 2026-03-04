---
author: TCI
breadcrumbs: true
date: '2025-01-06'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Benutzerhandbuch
- Dokumentation
title: Medien & Bilder
weight: 30
---

Images and graphics break up text and make complex topics easier to understand. The Sitewave offers simple ways to integrate media into your content.

## 1. Inserting images

### Using the toolbar

1.  Place the cursor where you want the image to appear.
2.  Click on the **Insert Image** icon (usually a landscape image icon) in the toolbar.
3.  Select the image file from your computer.
4.  The editor automatically inserts the corresponding Markdown code.

### Drag & drop

You can often drag image files directly from your file manager into the editor window. The editor will then attempt to resolve the path and generate the Markdown code.

### Manually with Markdown

The syntax for images is simple:

```markdown
!Description of the image
```

*   **The exclamation mark `!`** at the beginning identifies it as an image.
*   **The alternative text (alt text) is enclosed in square brackets `[]`**. This is displayed if the image cannot be loaded and is important for accessibility.
*   **The path to the image file is enclosed in parentheses `()`**.

**Example:**
```markdown
![A beautiful sunset](../assets/images/sun.jpg)
```

### Setting the image size

1. When you click on “Insert image,” select the file as usual.
2. A small input window for the width will then appear.
3. Enter, for example, 300px or 50% and confirm with OK.
4. The editor will then insert the Markdown code with the corresponding attribute: !Alt Text{: width="300px" }.
5. If you leave the field blank, the image will be inserted in its original size as before.

**Example:**
```markdown
![App Config](assets/app_config-01.png){: width="50%" }
```

## 2. Image galleries

For collections of images (e.g., vacation photos or screenshots), the editor comes with an integrated **gallery plugin**. Instead of inserting each image individually, you can display an entire folder as a gallery.

To do this, use the shortcode `[[gallery]]`.

### Syntax

```markdown
[[gallery folder="assets/images/my-album"]]
```

### Parameters

*   `folder`: The path to the folder containing the images (relative to the project directory).
*   `title`: (Optional) A headline for the gallery.

The plugin automatically generates a grid view of all images in this folder.

## 3. Managing files (assets)

To keep your website tidy, you should store all media in the `assets` folder.

* **Structure:** Create subfolders in `assets` to keep track of everything (e.g., `assets/images`, `assets/downloads`).
* **Publishing:** Everything in the `assets` folder is automatically copied to the output folder when the website is generated.

[[infobox type="info" title="Tip on file size"]]
Make sure your images are not too large (e.g., photos taken directly from a camera). Scale them to a web-friendly size beforehand (e.g., max. 1920px wide) and use formats such as JPG or WebP to keep your website's loading time short.
[[/infobox]]

### Image compression (project tool)

The editor has a built-in tool to automatically optimize images. You can find it in the menu under **Project Tools > Image Compressor**.

This tool helps you:
* Reduce the size of images (e.g., to a maximum width of 1920px).
* Reduce the file size (compression).
* Convert images to modern formats such as WebP.

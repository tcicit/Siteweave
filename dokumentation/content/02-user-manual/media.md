---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- User Manual
- Documentation
title: Media & Images
weight: 30
---

[[toc min_headers="4" title="Contents"]]

Images and graphics break up text and make complex topics easier to understand. Siteweave offers several ways to integrate media into your content.

## 1. Inserting Images

### Using the Toolbar

1. Place the cursor where you want the image to appear.
2. Click the **Insert Image** icon in the toolbar.
3. Select the image file from your computer.
4. The editor automatically inserts the corresponding Markdown code.

Optionally, a dialog will ask for a width value — enter e.g. `300px` or `50%` to set the display size.

### Drag & Drop

Drag image files directly from your file manager into the editor window. The editor will generate the Markdown code automatically.

### Manually with Markdown

```markdown
![A beautiful sunset](../assets/images/sun.jpg)
```

- The **exclamation mark `!`** identifies it as an image.
- The **alt text** in `[]` is shown when the image cannot load and is important for accessibility.
- The **path** in `()` points to the file.

### Setting the Image Size

```markdown
![App Screenshot](assets/screenshot.png){: width="50%" }
```

### Using the Image Plugin

The `[[image]]` plugin provides advanced options not available in standard Markdown:

```markdown
[[image path="assets/photo.jpg" shadow="true" border="true"]]

[[image path="assets/photo.jpg" align="right" width="300px" caption="Caption text" lightbox="true"]]

[[image path="assets/banner.jpg" radius="15px" overlay="rgba(0,0,0,0.3)"]]

[[image path="assets/logo.png" href="https://example.com" target="_blank"]]
```

| Parameter | Description |
| :--- | :--- |
| `path` | Path to the image file (required) |
| `align` | `left`, `right`, or `center` |
| `width` | e.g. `300px` or `50%` |
| `caption` | Caption text shown below the image |
| `shadow` | `true` adds a drop shadow |
| `border` | `true` adds a border |
| `radius` | Rounded corners, e.g. `15px` |
| `lightbox` | `true` opens image full-size on click |
| `href` | Wraps the image in a link |
| `target` | Link target, e.g. `_blank` |
| `class` | Custom CSS class(es) |

## 2. Image Galleries

For collections of images (e.g. vacation photos or screenshots), use the **gallery plugin** to display an entire folder as a grid:

```markdown
[[gallery folder="assets/images/my-album"]]

[[gallery folder="assets/images/my-album" title="My Photos"]]
```

The plugin automatically generates a responsive grid view of all images in the specified folder.

## 3. Managing Files (Assets)

Store all media in the `assets` folder. Create subfolders for organization:

```
assets/
├── images/
│   ├── screenshots/
│   └── photos/
├── downloads/
└── videos/
```

Everything in the `assets` folder is automatically copied to `site_output` when the website is rendered.

[[infobox type="info" title="Tip: Image File Size"]]
Scale images to a web-friendly size (max. 1920px wide) before adding them to your project. Use the **JPG** or **WebP** format to keep file sizes small and loading times fast.
[[/infobox]]

## 4. Image Compressor (Project Tool)

The editor has a built-in tool to automatically optimize images. Find it under **Project Tools > Image Compressor**.

This tool can:

- Reduce image dimensions (e.g. to a maximum width)
- Reduce file size (compression)
- Convert images to modern formats such as **WebP**

Configure it in your `config.yaml`:

```yaml
jpeg_quality: 85
png_compression: 6
extensions: ['.jpg', '.jpeg', '.png']
```
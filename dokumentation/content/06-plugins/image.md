---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: full-width
pdf_exclude: true
release_date: '2026-03-08'
tags:
- Plugin
- Documentation
title: Plugin — Image
weight: 30
---

[[toc min_headers="4" title="Contents"]]

The `image` plugin extends standard Markdown images with advanced layout options: alignment, captions, lightboxes, shadows, borders, overlays, and more.

## Syntax

```markdown
[[image path="path/to/image.jpg" param="value" ...]]
```

## Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| **src** | String | **(Required)** Path to the image file |
| **align** | `left` / `right` / `center` | Float the image left or right, or center it |
| **width** | e.g. `300px` / `50%` | Display width |
| **caption** | String | Caption text shown below the image |
| **shadow** | `true` / `false` | Add a drop shadow |
| **border** | `true` / `false` | Add a border |
| **radius** | e.g. `15px` | Rounded corners |
| **lightbox** | `true` / `false` | Opens image full-size on click |
| **overlay** | e.g. `rgba(0,0,0,0.3)` | Color overlay on hover |
| **href** | URL | Wraps the image in a link |
| **target** | `_blank` / `_self` | Link target |
| **class** | String | Custom CSS class(es) |
| **alt** | String | Alt text for accessibility |

## Examples

### Basic Image

```markdown
[[image src="_assets/bild-5-compressed.jpg"]]
```

[[image src="_assets/bild-5-compressed.jpg"]]


### Image with Shadow and Border

```markdown
[[image src="_assets/photo.jpg" shadow="true" border="true"]]
```

[[image src="_assets/bild-6-compressed.jpg" shadow="true" border="true"]]


### Right-Aligned with Caption and Lightbox

```markdown
[[image path="assets/photo.jpg" align="right" width="300px" caption="A beautiful photo" lightbox="true"]]
```

### Centered with Rounded Corners

```markdown
[[image path="assets/banner.jpg" width="100%" radius="12px"]]
```

### Image as Link (Opens in New Tab)

```markdown
[[image path="assets/logo.png" href="https://example.com" target="_blank"]]
```

### Image with Color Overlay on Hover

```markdown
[[image path="assets/hero.jpg" width="100%" overlay="rgba(0,0,0,0.4)"]]
```

### Image with Custom CSS Class

```markdown
[[image path="assets/screenshot.png" class="my-frame shadow-effect"]]
```

## When to Use `[[image]]` vs Standard Markdown

| Use Case | Recommendation |
| :--- | :--- |
| Simple inline image | `![alt](path)` — standard Markdown is fine |
| Need alignment, caption, or lightbox | Use `[[image]]` plugin |
| Need shadow, border, or overlay | Use `[[image]]` plugin |
| Image wrapped in a link | Use `[[image href="..."]]` |

[[infobox type="info" title="Tip: Image Compression"]]
Use the **Image Compressor** under Project Tools to optimize your images before adding them. This reduces file size and improves your website's loading speed.
[[/infobox]]
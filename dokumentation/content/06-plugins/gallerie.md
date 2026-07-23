---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
pdf_exclude: true
release_date: '2026-03-08'
tags:
- Plugin
- Documentation
title: Plugin — Gallery
weight: 40
---

The `gallery` plugin generates a responsive image grid from all images in a specified folder. No manual listing of individual files required.

## Syntax

```markdown
[[gallery folder="assets/images/my-album"]]
```

## Parameters

| Parameter | Description | Default |
| :--- | :--- | :--- |
| **path or folder** | Path to the directory containing images (relative to markdown file). ||
| **layout** | "grid" (Default) or "masonry". ||
| **cols** | Number of columns in grid layout. Default: "3". ||
| **ratio** | Aspect ratio for grid layout. Options: "original", "1:1", "4:3" (Default), "3:2", "16:9". ||
| **gap** | Gap between images. Default: "1rem". ||

## Examples

### Basic Gallery

```markdown
[[gallery layout="grid" cols="3""]]

![Bild 1 Compressed.](_assets/galleries/gallery_2026-03-12_101741/bild-1-compressed..jpg)
![Bild 2 Compressed.](_assets/galleries/gallery_2026-03-12_101741/bild-2-compressed..jpg)
[[/gallery]]
```


[[gallery layout="grid" cols="3"]]
![Bild 1 Compressed.](_assets/bild-1-compressed.jpg)
![Bild 2 Compressed.](_assets/bild-2-compressed.jpg)
![Bild 3 Compressed.](_assets/bild-3-compressed.jpg)
![Bild 4 Compressed.](_assets//bild-4-compressed.jpg)
![Bild 5 Compressed.](_assets/bild-5-compressed.jpg)
![Bild 6 Compressed.](_assets/bild-6-compressed.jpg)
![Bild 7 Compressed.](_assets/bild-7-compressed.jpg)
![Bild 8 Compressed.](_assets/bild-8-compressed.jpg)
![Bild 9 Compressed.](_assets//bild-9-compressed.jpg)
![Bild 10 Compressed](_assets//bild-10-compressed.jpg)
![Bild 11 Compressed](_assets//bild-11-compressed.jpg)
![Bild 12 Compressed](_assets//bild-12-compressed.jpg)
![Bild 13 Compressed](_assets//bild-13-compressed.jpg)
[[/gallery]]

### Gallery from Folder and with Lightbox

```markdown
[[gallery layout="masonry" folder="_assets/blumen" cols="4"]]

```
[[gallery layout="masonry" folder="_assets/blumen" cols="4"]]
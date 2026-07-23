---
author: TCI
breadcrumbs: true
date: '2025-12-18'
draft: false
featured_image: None
layout: doc
pdf_exclude: true
release_date: '2025-12-18'
tags:
- Dokumentation
- Plugins
title: Plugin —  Box
weight: 160
---

Erzeugt eine einzelne Box innerhalb eines Grids.

`[[box title="Wichtiger Hinweis"]]`
Dies ist der Inhalt der Box.
`[[/box]]`

    
## Parameters:

| Parameter | Description | Default |
|:--- | :--- | :--- |
| **title** | Der Titel der Box. | |
| **bgcolor** | Eine CSS-Hintergrundfarbe (z.B. '#eaf7ff' oder 'lightyellow'). ||


## Beispiel

[[box title="Wichtiger Hinweis" bgcolor="#eaf7ff"]]
Dies ist der Inhalt der Box.
[[/box]]

 
### Noch ein  Beispiel mit Bild


[[box title="Mit Bild und Text" bgcolor="#ccd4e0"]]

[[image src="_assets/bild-3-compressed.jpg" width="300px" height="200px" align="center" border="true" shadow="true" radius="10px" caption="Mein Bild" lightbox="true"  alt="Alternativtext" class="custom-class" href="https://example.com" target="_blank" zoom="true" opacity="0.8"]]

Dies ist der Inhalt der Box. Und hier noch **Fetter** Text.

[[/box]]
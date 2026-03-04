---
author: TCI
breadcrumbs: true
date: '2025-08-09'
draft: false
featured_image: None
layout: full-width
pdf_exclude: true
release_date: '2025-08-09'
tags:
- Galerie
- Test
- Plugin
- Dokumentation
- Plugins
title: Galerie Test
---

## Beschreibung

Erzeugt eine Bildergalerie mit Lightbox. Verwendet komprimierte Bilder für die Vorschau und verlinkt auf die Originalbilder in der Lightbox.

### Zwei Modi:

#### 1. Aus einem Verzeichnis:

```

[[gallery path="relativer/pfad/zum/ordner" layout="grid" cols="3" ...]]

```

#### 2. Aus Markdown-Bildern im Inhalt:

```

[[gallery layout="grid" cols="3" ...]]
  ![Alt-Text 1](pfad/zum/bild1.jpg)
  ![Alt-Text 2](pfad/zum/bild2.jpg)
[[/gallery]]

```

### Parameter:

- layout (str): 'grid' (Standard) oder 'masonry'.
- cols (int): Anzahl der Spalten. Standard: 3.
- ratio (str): Seitenverhältnis der Vorschaubilder. 
    - Mögliche Werte: 'original', '1:1', '4:3', '3:2', '16:9', **Standard: '4:3'**
- gap (str): Abstand zwischen den Bildern (z.B. '1rem', '10px'). Standard: '1rem'.


## Beispiele:

### Galerie mit Standard-Seitenverhältnis

`[[gallery]]`

[[gallery]]
![Bild 1](assets/bild-1-compressed.jpg)
![Bild 2](assets/bild-2-compressed.jpg)
![](assets/bild-3-compressed.jpg)
![](assets/bild-4-compressed.jpg)
![](assets/bild-5-compressed.jpg)
![](assets/bild-6-compressed.jpg)
![](assets/bild-7-compressed.jpg)
![](assets/bild-8-compressed.jpg)
![](assets/bild-9-compressed.jpg)
![](assets/bild-10-compressed.jpg)
![](assets/bild-11-compressed.jpg)
![](assets/bild-12-compressed.jpg)
![](assets/bild-13-compressed.jpg)
![](assets/bild-14-compressed.jpg)
![](assets/bild-15-compressed.jpg)
![](assets/bild-16-compressed.jpg)
[[/gallery]]


### Zwischentitel
Hier kommt noch etwas Text.

### Galerie mit Quadrat-Seitenverhältnis
`[[gallery ratio="1:1"]]`

[[gallery ratio="1:1"]]
![Bild 1](assets/bild-1-compressed.jpg)
![Bild 2](assets/bild-2-compressed.jpg)
![](assets/bild-3-compressed.jpg)
![](assets/bild-4-compressed.jpg)
![](assets/bild-5-compressed.jpg)
![](assets/bild-6-compressed.jpg)
![](assets/bild-7-compressed.jpg)
![](assets/bild-8-compressed.jpg)
![](assets/bild-9-compressed.jpg)
![](assets/bild-10-compressed.jpg)
![](assets/bild-11-compressed.jpg)
![](assets/bild-12-compressed.jpg)
![](assets/bild-13-compressed.jpg)
![](assets/bild-14-compressed.jpg)
![](assets/bild-15-compressed.jpg)
![](assets/bild-16-compressed.jpg)
[[/gallery]]


### Galerie mit Masonry-Layout
`[[gallery layout="masonry"]]`

[[gallery layout="masonry"]]
![Bild 1](assets/bild-1-compressed.jpg)
![Bild 2](assets/bild-2-compressed.jpg)
![](assets/bild-3-compressed.jpg)
![](assets/bild-4-compressed.jpg)
![](assets/bild-5-compressed.jpg)
![](assets/bild-6-compressed.jpg)
![](assets/bild-7-compressed.jpg)
![](assets/bild-8-compressed.jpg)
![](assets/bild-9-compressed.jpg)
![](assets/bild-10-compressed.jpg)
![](assets/bild-11-compressed.jpg)
![](assets/bild-12-compressed.jpg)
![](assets/bild-13-compressed.jpg)
![](assets/bild-14-compressed.jpg)
![](assets/bild-15-compressed.jpg)
![](assets/bild-16-compressed.jpg)
[[/gallery]]



### Blumen Galerie (Directory Listing)

`[[gallery path="assets/blumen" layout="masonry" cols="4"]]`


[[gallery path="assets/blumen" layout="masonry" cols="4"]]
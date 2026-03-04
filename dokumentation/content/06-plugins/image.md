---
author: TCI
breadcrumbs: true
date: '2026-01-15'
draft: false
featured_image: ''
layout: doc
pdf_exclude: true
release_date: '2026-01-15'
tags:
- Plugin
- Test
- Dokumentation
- Plugins
title: Image Plugin Test
---

### Pluginname: Image

### Beschreibung:

    Erweitertes Image-Plugin mit vielen Gestaltungsoptionen.


### Syntax: 
    
    `[[image src="bild.jpg" width="300px" height="200px" align="center" border="true" shadow="true" radius="10px" caption="Mein Bild" lightbox="true" overlay="rgba(0,0,0,0.3)" alt="Alternativtext" class="custom-class" 
    href="https://example.com" target="_blank" zoom="true" opacity="0.8"]]`

### Parameter:

      - src: Pfad zum Bild (relativ zur Markdown-Datei). (Pflicht)
      - width: Breite des Bildes (z.B. "300px", "50%").
      - height: Höhe des Bildes (z.B. "200px", "auto").
      - align: Bildausrichtung: "left", "center", "right". Standard: "center".
      - border: Rahmen um das Bild. "true" für Standardrahmen,      oder CSS-Wert (z.B. "2px solid #000").
      - shadow: Schatteneffekt. "true" für Standard-Schatten, oder CSS-Wert (z.B. "0 4px 8px rgba(0,0,0,0.15)").
      - radius: Runden der Bild-Ränder. CSS-Wert (z.B. "10px").
      - caption: Bildbeschreibung.
      - lightbox: "true" für Lightbox-Funktionalität. Standard: "false".
      - overlay: Hintergrundfarbe für den Overlay. CSS-Wert (z.B. "rgba(0,0,0,0.3)").
      - alt: Alternativtext für das Bild. Standard: "Bild".
      - class: Zusätzliche CSS-Klasse für das Bild.
      - href: Link für das Bild.
      - target: Target-Attribut für das Link (z.B. "_blank").
      - zoom: "true" für Zoom-Effekt. Standard: "false".
      - opacity: Opacität des Bildes (z.B. "0.8"). 


### Beispiele:


[[image src="assets/bild-8-compressed.jpg" width="300px" ]]

---

Erstellt ein zentriertes Bild mit den angegebenen Stilen, einer Bildunterschrift, Lightbox-Funktionalität und einem Link.

[[image src="assets/bild-8-compressed.jpg" width="300px" height="200px" align="center" border="true" shadow="true" radius="10px" caption="Mein Bild" lightbox="true" overlay="rgba(0,0,0,0.3)" alt="Alternativtext" class="custom-class" href="https://example.com" target="_blank" zoom="true" opacity="0.8"]]



    
### Ergebnis:

       - HTML-Code für das Bild mit den angegebenen Attributen und Stilen. 
       - Wenn das Bild ein Overlay enthält, wird ein Wrapper erstellt. 
       - Wenn das Bild ein Lightbox enthält, wird ein Link erstellt. 
       - Wenn das Bild ein Overlay und ein Lightbox enthält, wird ein Wrapper erstellt.
       - Wenn das Bild ein Overlay und kein Lightbox enthält, wird ein Wrapper erstellt.
       - Wenn kein Overlay und kein Lightbox, wird das Bild ohne Wrapper erstellt.         
       - Wenn kein Bild übergeben wird, wird eine Warnung angezeigt.
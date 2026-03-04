---
author: TCI
breadcrumbs: true
date: '2025-12-19'
draft: false
featured_image: None
layout: full-width
pdf_exclude: true
release_date: '2025-12-19'
tags:
- Plugin
- Test
- Dokumentation
- Plugins
title: CSV Import Test
---

## Beschreibung

Liest eine CSV-Datei und stellt sie als HTML-Tabelle dar.
    
Syntax: `[[csv_table src="daten.csv" delimiter=";" header="true" class="my-table"]]`

    
### Argumente:

* src: Pfad zur CSV-Datei (relativ zur Markdown-Datei).
* delimiter: Trennzeichen (Standard: ","). Für Tabulator nutze "\\t".
* header: "true" (Standard) oder "false". Ob die erste Zeile Überschriften enthält.
* class: CSS-Klasse für das <table> Element (Standard: "csv-table").
* caption: Optionaler Titel der Tabelle.

## Beispiele

[[csv_table src="preise.csv" delimiter=";" caption="Unsere aktuelle Preisliste"]]
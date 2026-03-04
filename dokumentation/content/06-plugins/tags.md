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
- Plugin
- Test
- Dokumentation
- Plugins
title: Tags Plugin
---

## Beschreibung

Verarbeitet die `[[tags]]` Shortcodes im Markdown-Inhalt.
Unterstützt `[[tags type="cloud"]]` und `[[tags type="list"]]`.
Parameter:
- type (str): 'cloud' für Tag-Cloud, 'list' für einfache Liste. Standard: 'list'.
Rückgabe:
Gerenderter HTML-Code für die Tags.


## Beispiel
### Tag-Cloud

Die Größe eines Tags in der Cloud entspricht der Anzahl der zugeordneten Artikel.

[[tags type="cloud"]]

### Alphabetische Liste

[[tags type="list"]]
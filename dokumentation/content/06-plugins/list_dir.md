---
author: TCI
breadcrumbs: true
date: '2025-12-14'
draft: false
featured_image: None
layout: full-width
pdf_exclude: true
release_date: '2025-12-14'
tags:
- Plugin
- Test
- Dokumentation
- Plugins
template: base.html
title: List Dir Plugin
---

## Beschreibung
Listet alle Seiten in einem Verzeichnis als HTML-Liste auf.

Syntax:

``` 

[[list_dir]]                      -> listet Seiten im aktuellen Verzeichnis
[[list_dir path="/kategorie/"]]   -> listet Seiten im angegebenen Verzeichnis
[[list_dir sort="title|path"]]    -> Sortierreihenfolge (default: title)
[[list_dir recursive="true"]]     -> schließt auch Unterverzeichnisse mit ein

```

## Beispiel

[[list_dir]]
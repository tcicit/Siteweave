---
author: TCI
breadcrumbs: true
date: '2025-12-14'
draft: false
featured_image: None
layout: full-width
pdf_exclude: true
release_date: '2025-08-09'
tags:
- Bilder
- Latest Posts
- Test
- Plugin
- Dokumentation
- Plugins
template: base.html
title: Latest Post Test
---

## Beschreibung

Generiert eine Liste der letzten Beiträge, gefiltert und sortiert.
Verwendung:

`[[latest_posts count="5" sort="desc" tags="tag1,tag2" tag_mode="all" show_excerpt="true" excerpt_length="30" show_image="true"]]`

### Parameter:
- count (int): Anzahl der anzuzeigenden Beiträge. Standard: 5.
- sort (str): 'asc' für aufsteigend, 'desc' für absteigend (Standard).
- tags (str): Kommagetrennte Liste von Tags zum Filtern der Beiträge.
- tag_mode (str): 'all' (Standard) für Beiträge mit allen Tags, 'any' für Beiträge mit mindestens einem Tag.
- show_excerpt (str): 'true' oder 'false' (Standard). Ob ein Auszug angezeigt werden soll.
- excerpt_length (int): Anzahl der Wörter im Auszug. Standard: 30.
- show_image (str): 'true' oder 'false' (Standard). Ob das Vorschaubild angezeigt werden soll. Der Kontext muss eine Liste `all_pages` enthalten, wobei jede Seite ein Dictionary mit mindestens den folgenden Schlüsseln ist:
- title: Titel der Seite
- path: Pfad zur Seite
- metadata: Dictionary mit Metadaten, einschließlich 'date' (ISO-Format) und 'tags' (Liste von Tags)
- content: Der Markdown-Inhalt der Seite
- featured_image: (optional) Pfad zum Vorschaubild der Seite

### Rückgabe:
HTML-Liste der letzten Beiträge entsprechend den angegebenen Kriterien.



## Beispiele für den Einsatz vom Latest Post Plugins

- Beispiel (AND-Modus): `tags="Wandern, Test"` - Muss BEIDE Tags haben (tag_mode="all" (Standard): Eine Seite muss alle angegebenen Tags haben.)
[[latest_posts count="5" sort="desc" tags="Wandern"]]

- Beispiel (OR-Modus): `tags="Wandern, Natur" tag_mode="any"` - tag_mode="any": Eine Seite muss nur einen beliebigen der angegebenen Tags haben.
[[latest_posts count="5" sort="desc" tags="Wandern, Natur" tag_mode="any"]]

- Beispiel: `tags="Wandern"`
[[latest_posts count="5" sort="asc" tags="Wandern,Natur"]]

- Beispiel: `latest_posts count="5" sort="desc"`
[[latest_posts count="5" sort="desc"]]

- Beispiel: `latest_posts count="5" sort="asc"`
[[latest_posts count="5" sort="asc"]]

- Beispiel: `latest_posts count="5"  show_excerpt="true" excerpt_length="30"`
[[latest_posts count="5"  show_excerpt="true" excerpt_length="30"]]

- Beispiel: `latest_posts`
[[latest_posts]]
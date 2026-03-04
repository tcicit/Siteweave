---
author: TCI
breadcrumbs: true
date: '2024'
draft: false
featured_image: null
layout: full-width
pdf_exclude: true
release_date: '2025-12-10'
tags:
- Plugin
- Test
- Dokumentation
- Plugins
title: Details Plugins
---

## Beschreibung

Dieses Plugin ist ideal für FAQs oder um zusätzliche Informationen zu verstecken, die nicht jeder sofort sehen muss.

Erstellt einen ausklappbaren Inhaltsblock (<details>).

Syntax: `[[details summary="Titel für die Zusammenfassung"]]Inhalt...[[/details]]`


## Beispiele

[[details summary="Klick mich, um mehr zu erfahren!"]]
Hier steht der versteckte Inhalt. Man kann hier auch ganz normal **Markdown** verwenden, um den Text zu formatieren.

*   Listen
*   sind
*   möglich

[[/details]]

Man kann es auch ohne Titel verwenden. Dann wird ein Standardtext angezeigt.

[[details]]
Dies ist ein weiterer versteckter Block.
[[/details]]
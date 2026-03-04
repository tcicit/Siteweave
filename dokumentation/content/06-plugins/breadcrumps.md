---
author: TCI
breadcrumbs: true
date: '2025-12-18'
draft: false
featured_image: null
layout: full-width
pdf_exclude: true
release_date: '2025-12-18'
tags:
- Dokumentation
- Plugins
title: Breadcrumbs Plugin Test
---

## Beschreibung

Generiert die Datenstruktur für die Breadcrumbs basierend auf dem aktuellen Pfad
und der gesamten Seitenstruktur.
Format der zurückgegebenen Daten:
breadcrumbs = [] # Liste von Dictionaries mit 'title' und 'url' Feldern

Die erste Breadcrumb ist immer "Home" und zeigt auf die Startseite.

Es ist auch möglich `[[breadcrumbs]]` Shortcode in der Startseite zu verwenden,
in diesem Fall wird nur "Home" zurückgegeben.

## Beispiel

[[breadcrumbs]]
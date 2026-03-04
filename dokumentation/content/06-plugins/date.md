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
- Datum
- Test
- Plugin
- Dokumentation
- Plugins
title: Aktuelles Datum
---

## Beschreibung

Gibt das aktuelle Datum im angegebenen Format zurück.

### Verwendung:
```
[[date format="%Y-%m-%d"]]

[[date format="%A, %d. %B %Y"]]
[[date]]

```

### Parameter

format : str, optional
Ein Python strftime-Formatstring. 
Standard: '%d.%m.%Y'. 

### Beispiele:

- %Y-%m-%d -> 2024-08-09
- %A, %d. %B %Y -> Freitag, 09. August 2024 



## Beispiele

Diese Seite wurde zuletzt aktualisiert am: **[[date]]**.

Das komplette Datum lautet: **[[date format="%A, %d. %B %Y"]]**.

Das Jahr für den Copyright-Hinweis: **[[date format="%Y"]]**.
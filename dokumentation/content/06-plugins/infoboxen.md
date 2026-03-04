---
author: TCI
breadcrumbs: true
date: '2024'
draft: false
featured_image: null
layout: full-width
pdf_exclude: true
release_date: '2025-08-09'
tags:
- Infobox
- Test
- Plugin
- Dokumentation
- Plugins
template: base.html
title: Infobox Test
---

## Beschreibung


Verarbeitet das `[[infobox]]`-Plugin.

Syntax: `[[infobox type="warning" title="Optionaler Titel"]]Inhalt...[[/infobox]]`

Typen: info, success, warning, danger

Der Inhalt der Infobox wird ebenfalls als Markdown verarbeitet.


## Beispiele
### Standard-Infobox

Dies ist eine einfache Informationsbox ohne spezifischen Typ.

[[infobox]]
Dies ist eine ganz normale Information. Sie können hier **Markdown** verwenden, um den Text zu formatieren.
[[/infobox]]

### Infoboxen mit Typen

Man kann verschiedene Typen für die Boxen angeben, um ihre Bedeutung hervorzuheben.

[[infobox type="info" title="Optionaler Titel"]]Dies ist eine informative Meldung[[/infobox]]

[[infobox type="success"]]
**Erfolg!** Die Operation wurde erfolgreich abgeschlossen.
[[/infobox]]

[[infobox type="warning"]]
**Achtung:** Bitte überprüfen Sie Ihre Eingaben. Etwas könnte falsch sein.
[[/infobox]]

[[infobox type="danger"]]
**Gefahr!** Dies ist eine kritische Warnung. Seien Sie vorsichtig.
[[/infobox]]
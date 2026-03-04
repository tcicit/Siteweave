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
- Infobox
- Test
- Plugin
- Dokumentation
- Plugins
template: base.html
title: Grid und Box
---

## Beschreibung

Erzeugt einen Grid-Container. Die inneren Plugins (z.B. 'box') werden durch den rekursiven Plugin-Prozessor des Generators verarbeitet.

### Parameter: 

- cols (str): Anzahl der Spalten im Grid. Standard: '3'.Erzeugt eine einzelne Box innerhalb eines Grids.
- title (str, optional): Der Titel der Box.
- bgcolor (str, optional): Eine CSS-Hintergrundfarbe (z.B. '#eaf7ff' oder 'lightyellow').

```

[[grid cols="3"]] 
   [[box title="Box 1" bgcolor="#eaf7ff"]]
     Text 
   [[/box]]
   [[box title="Box 2" ]]
     TexT 
   [[/box]]
   [[box title="Box 3" bgcolor="red"]]
     TexT 
   [[/box]]

[[/grid]]

```

## Beispiel

### Was unsere Kunden sagen

[[grid cols="3"]]

[[box title="Anna S." bgcolor="#eaf7ff"]]
Ich bin absolut begeistert! Der Service war schnell und das Ergebnis übertrifft meine Erwartungen. Ich kann es nur **jedem empfehlen**.

- Schnelle Lieferung
- Tolle Qualität
- Super Kundenservice
[[/box]]

[[box title="Markus T."]]
Ein wirklich durchdachtes Produkt. Man merkt, dass hier Profis am Werk waren. Die Einarbeitung war dank der guten Dokumentation ein Kinderspiel.
[[/box]]


[[box title="Markus T." bgcolor="#4A5359]]
![Wald](assets/wald-01-compressed.jpg)

Ein wirklich durchdachtes Produkt. Man merkt, dass hier Profis am Werk waren. Die Einarbeitung war dank der guten Dokumentation ein Kinderspiel.
[[/box]]


[[/grid]]


### Und hier Box ohne Grid

```

[[box title="Markus T." bgcolor="#594A58]]
![Wald](assets/wald-01-compressed.jpg)

Ein wirklich durchdachtes Produkt. Man merkt, dass hier Profis am Werk waren. Die Einarbeitung war dank der guten Dokumentation ein Kinderspiel.
[[/box]]

```



[[box title="Markus T." bgcolor="#594A58]]
![Wald](assets/wald-01-compressed.jpg)

Ein wirklich durchdachtes Produkt. Man merkt, dass hier Profis am Werk waren. Die Einarbeitung war dank der guten Dokumentation ein Kinderspiel.
[[/box]]
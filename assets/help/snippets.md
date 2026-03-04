---
title: Snippet Documentation
---

# Available Snippets

This documentation was automatically generated from the snippet files.

## Allgemein
### Breadcrumbs
```
[[breadcrumbs]]
```

### Datum (Heute)
```
[[date format="%d.%m.%Y"]]
```

### Hinweis Box
```
!!! note "Titel"
    Inhalt
```

### Inhaltsverzeichnis
```
[TOC]
```

### Seite einbinden
```
[[include page="pfad/zur/seite.md"]]
```

### Test Snippet Yaml
```
Dies ist ein Test Mit mehreren Zeilen 
```

### Verzeichnis-Liste
```
[[list_dir]]
```

## Allgemein, Text
### Lorem ipsum
```
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
```

## Formatierung
### Box (Farbig)
```
[[box title="Titel" bgcolor="#eaf7ff"]]
Inhalt der Box
[[/box]]

```

### Code Block (Python)
```
[[code lang="python"]]
print("Hello World")
[[/code]]

```

### Infobox (Warnung)
```
[[infobox type="warning" title="Achtung"]]
Wichtiger Hinweis!
[[/infobox]]

```

### Text Farbe
```
[[color text="red"]]Roter Text[[/color]]
```

## Galerie
### Bilder-Galerie alle Bilder im Path
```
[[gallery  path="assets/images"]]
```

## Layout
### Details (Aufklappbar)
```
[[details summary="Mehr anzeigen"]]
Versteckter Inhalt
[[/details]]

```

### Grid Layout (3 Spalten)
```
[[grid cols="3"]]
[[box title="Spalte 1"]]Inhalt 1[[/box]]
[[box title="Spalte 2"]]Inhalt 2[[/box]]
[[box title="Spalte 3"]]Inhalt 3[[/box]]
[[/grid]]

```

## Medien
### Bilder-Galerie
```
[[gallery dir="assets/images"]]
```

### CSV Tabelle einbinden
```
[[csv_table src="daten.csv" delimiter=";" header="true" class="table"]]
```

### Galerie (Ordner)
```
[[gallery path="assets/images" layout="grid" cols="3"]]
```

### YouTube Video
```
[[youtube id="VIDEO_ID"]]
```

## Navigation
### Archiv Liste
```
[[archive]]
```

### Breadcrumbs Navigation
```
[[breadcrumbs]]
```

### Inhaltsverzeichnis (TOC)
```
[[toc title="Inhalt" depth="3"]]
```

### Letzte Beiträge
```
[[latest_posts count="5" show_image="true" show_excerpt="true"]]
```

### Tag Cloud
```
[[tags type="cloud"]]
```

### Verzeichnis auflisten
```
[[list_dir recursive="false"]]
```

## Sicherheit
### E-Mail Link (Geschützt)
```
[[obfuscate email="info@example.com" label="Schreiben Sie uns"]]
```

## Struktur
### Datei einbinden
```
[[include src="pfad/zur/datei.md"]]
```

## Tabellen
### Tabelle 2 Spaltig
```
First Header | Second Header  
 ------------- | ------------- 
 Content Cell | Content Cell  
 Content Cell | Content Cell  
```

### Tabelle 3 Spalten
```
First Header | Second Header | Third Header ------------- | ------------- | ------------- Content Cell | Content Cell | Content Cell Content Cell | Content Cell | Content Cell
```

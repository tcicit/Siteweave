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
- plugin
- test
- Dokumentation
- Plugins
title: Adresse Verschleierung (obfuscate)
---

## Beschreibung
Plugin zum Verschleiern von sensiblen Daten wie E-Mails, Telefonnummern und Adressen.

Die effektivste Methode, die gleichzeitig benutzerfreundlich ist und keine externen Skripte erfordert, ist das HTML Entity Encoding.

Dabei werden die Zeichen in ihre numerischen HTML-Codes umgewandelt (z. B. wird @ zu &#64;). Browser stellen dies für Menschen ganz normal dar, aber einfache Bots und Scraper sehen nur einen "Buchstabensalat" und können die Adressen oft nicht extrahieren.

Es unterstützt E-Mails (inkl. mailto:-Link), Telefonnummern (inkl. tel:-Link) und normale Adressen.

    
Argumente:
- email: E-Mail-Adresse (erzeugt mailto-Link)
- phone: Telefonnummer (erzeugt tel-Link)
- address: Adresse oder Text (wird nur kodiert)
- text: Alias für address
- label: Optionaler Link-Text (für email/phone)
- subject: Optionaler Betreff (für email)
    
Verwendung:
```
    [[obfuscate email="info@example.com"]]
    [[obfuscate phone="+49 123 456"]]
    [[obfuscate address="Musterstraße 1"]]
    [[obfuscate]]Beliebiger Text[[/obfuscate]]
```

## Beispiele

1. E-Mail-Adresse (erstellt automatisch einen mailto: Link):

markdown
Kontaktieren Sie uns unter: [[obfuscate email="info@example.com"]]


Optional mit anderem Link-Text:

markdown
[[obfuscate email="info@example.com" label="Schreiben Sie uns eine E-Mail"]]

2. Telefonnummer (erstellt automatisch einen tel: Link für Smartphones):

markdown

Rufen Sie an: [[obfuscate phone="+49 123 456 789"]]

3. Adresse oder beliebiger Text (nur Text-Verschleierung):

markdown
Unser Büro: [[obfuscate address="Musterstraße 1, 12345 Berlin"]]

Oder als Block:

markdown
[[obfuscate]]
Musterstraße 1
12345 Berlin
[[/obfuscate]]


Das Plugin mischt zufällig dezimale (&#64;) und hexadezimale (&#x40;) Kodierungen, was es für Bots noch schwieriger macht, Muster zu erkennen.
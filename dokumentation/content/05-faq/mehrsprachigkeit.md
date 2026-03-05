---
title: "Mehrsprachige Websites (i18n)"
author: "TCI"
date: "2024-05-22"
layout: doc
tags:
- Templates
- Internationalisierung
- i18n
- Anleitung
draft: false
---

Siteweave bietet integrierte Unterstützung für die Erstellung mehrsprachiger Websites. Dies wird als Internationalisierung (kurz: i18n) bezeichnet. Anstatt für jede Sprache separate Inhalte zu pflegen, können Sie Textbausteine in Ihren Templates zentral verwalten und übersetzen.

## Das Konzept

Das Prinzip basiert auf Schlüssel-Wert-Paaren. Anstatt einen Text direkt in Ihr HTML-Template zu schreiben, verwenden Sie einen eindeutigen **Schlüssel**.

**Ohne i18n:**
```html
<h1>Willkommen auf unserer Webseite</h1>
```

**Mit i18n:**
```html
<h1>{{ _('welcome_title') }}</h1>
```

Der Generator von Siteweave ersetzt den Schlüssel `welcome_title` zur Laufzeit durch den passenden Text aus einer Übersetzungsdatei, die zur aktuell ausgewählten Sprache gehört.

## Schritt-für-Schritt-Anleitung

Folgen Sie diesen Schritten, um Ihre Website mehrsprachig zu machen.

### 1. Sprachen in `config.yaml` definieren

Zuerst müssen Sie die Standardsprache und alle verfügbaren Sprachen in Ihrer `config.yaml`-Datei festlegen.

```yaml
# config.yaml

site_name: "Meine mehrsprachige Seite"
language: "de"  # Die Standardsprache

# Optional: Eine Liste aller unterstützten Sprachen
# Dies kann z.B. für einen Sprachumschalter genutzt werden
available_languages:
  - code: "de"
    name: "Deutsch"
    url_prefix: "/"
  - code: "en"
    name: "English"
    url_prefix: "/en/"
```

### 2. Übersetzungsdateien erstellen

Erstellen Sie im Hauptverzeichnis Ihres Projekts einen neuen Ordner namens `i18n`. In diesem Ordner legen Sie für jede Sprache eine JSON-Datei an. Der Dateiname muss dem Sprachcode aus der Konfiguration entsprechen (z.B. `de.json`, `en.json`).

**Projektstruktur:**
```
.
├── config.yaml
├── content/
├── templates/
└── i18n/
    ├── de.json
    └── en.json
```

**Inhalt von `i18n/de.json`:**
```json
{
  "welcome_title": "Willkommen auf unserer Webseite!",
  "about_us": "Über uns",
  "contact": "Kontakt"
}
```

**Inhalt von `i18n/en.json`:**
```json
{
  "welcome_title": "Welcome to our Website!",
  "about_us": "About us",
  "contact": "Contact"
}
```

### 3. Übersetzungen im Template verwenden

Jetzt können Sie die Schlüssel in Ihren Jinja2-Templates (z.B. in `templates/base.html` oder Partials) verwenden. Siteweave stellt dafür die Funktion `_()` zur Verfügung.

**Beispiel für `templates/partials/header.html`:**
```html
<nav>
    <ul>
        <li><a href="{{ relative_prefix }}index.html">{{ _('home') }}</a></li>
        <li><a href="{{ relative_prefix }}about.html">{{ _('about_us') }}</a></li>
        <li><a href="{{ relative_prefix }}contact.html">{{ _('contact') }}</a></li>
    </ul>
</nav>
```

Damit dies funktioniert, müssen Sie die entsprechenden Schlüssel (`home`, `about_us`, `contact`) natürlich in Ihren JSON-Dateien definieren.

[[infobox type="info" title="Hinweis"]]
Die `_()` Funktion ist ein gängiger Standard für Übersetzungen und ist eine Kurzform für "gettext".
[[/infobox]]

## Wie es funktioniert (Hinter den Kulissen)

Wenn Sie den Generator starten, passiert Folgendes:
1.  Siteweave liest die `config.yaml` und erkennt die konfigurierten Sprachen.
2.  Für jede Sprache lädt der Generator die entsprechende `.json`-Datei aus dem `i18n`-Ordner.
3.  Beim Rendern der Templates wird die `_()`-Funktion bereitgestellt, die jeden Schlüssel mit dem passenden Wert aus der geladenen Sprachdatei ersetzt.

So können Sie Ihre Templates sauber und frei von hartcodierten Texten halten und Ihre Website einfach um neue Sprachen erweitern.

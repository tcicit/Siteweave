---
author: TCI
breadcrumbs: true
date: '2000-01-01'
draft: false
featured_image: None
layout: full-width
pdf_exclude: true
release_date: '2025-08-09'
tags:
- Test
- Plugin
- Code
- Dokumentation
- Plugins
title: Syntax Highlighting Test
---

## Beschreibung
Erstellt einen Code-Block mit Syntax-Highlighting.
Es kann die Standart Markdown Syntax verwendet werden. 


Syntax: `[[code lang="python"]]print("Hello")[[/code]]`

Argumente:
- lang: Die Programmiersprache (z.B. python, javascript, html). 
        Wenn weggelassen, wird versucht, die Sprache zu erraten.

## Beispiele


### Python-Code

Hier ist ein Beispiel für einen Python-Codeblock. Die Sprache wird explizit angegeben.

```python
import os

def list_files(directory):
    """Lists all files in a given directory."""
    print(f"Files in '{directory}':")
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            print(f"  - {filename}")

list_files('.')
```

### JSON-Code

Hier ist ein JSON-Beispiel.

```json
{
  "project": "tci-static-site",
  "feature": "syntax-highlighting",
  "status": "implemented",
  "awesome": true
}
```

### Code mit Zeilennummern und Hervorhebung

Man kann auch Zeilennummern hinzufügen (`linenums="1"`) und bestimmte Zeilen hervorheben (`hl_lines`).

```{.python linenums="1" hl_lines="7 10"}
class Greeter:
    """A simple class to greet."""

    def __init__(self, name):
        self.name = name

    def greet(self):
        # This line will be highlighted
        print(f"Hello, {self.name}!")

greeter = Greeter("World")
# And this line will be highlighted too
greeter.greet()
```

### Ungespezifizierte Sprache

Wenn keine Sprache angegeben ist, versucht das System, sie zu erraten.

```
# This looks like a shell script
echo "Guessing the language..."
ls -la
```


**2. Die neue Plugin-Methode (mit expliziter Sprache

```
[[code lang="python"]]
def hallo():
    print("Welt")
[[/code]]
```
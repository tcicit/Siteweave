---
author: TCI
breadcrumbs: true
date: '2026-01-16'
draft: false
featured_image: ''
layout: doc
release_date: '2026-01-16'
tags:
- Entwicklung
title: Mehrsprachigkeit (i18n)
---


Sitewave is designed for multilingualism (internationalization / i18n). It uses the standard **GNU gettext** system and the Python library **Babel**.

## 1. Prerequisites

Ensure that the development environment is set up and `Babel` is installed:

```bash
pip install Babel
```


## 2. Marking text in the code
In order for text to be translated, it must be marked in the Python code. We use the function _() for this.


```
from core.i18n import _

# ...

# Simple string
button = QPushButton(_(“Save File”))

# String with placeholders (Important: use .format()!)
message = _(“The file {filename} was saved.”).format(filename=“test.md”)
``` 

Important:

Import _ from core.i18n.
Use .format() with named arguments for placeholders, as the word order may change in other languages. F-strings (f“Text {var}”) cannot be translated!

## 3. Translation workflow
We have a helper script manage_translations.py in the main directory that controls the entire process.

### Step 1: Extract & update texts
If you have added or changed new texts in the code, run the script:

```bash
python manage_translations.py
``` 
What happens during this process?

Babel searches the entire source code (gui/, core/, etc.) for calls to _(“...”).
It creates or updates the locales/tci-editor.pot template.
It updates the existing translation files (e.g., locales/en/LC_MESSAGES/tci-editor.po) without deleting existing translations.

### Step 2: Translate texts

Open the .po file for the desired language (e.g., locales/en/LC_MESSAGES/tci-editor.po).

We recommend using an editor such as Poedit (available free of charge).

Open the .po file in Poedit.
New texts appear in the list (often marked in bold or at the top).
Enter the translation in the field below.
Save the file.
Alternatively, you can also edit the file with a text editor:

```po

#: gui/main_window.py:123
msgid “Save File”
msgstr “Save File”
```

### Step 3: Compile
In order for the application to load the translations quickly, they must be compiled into binary .mo files.

The manage_translations.py script does this automatically at the end of the run. So all you have to do is run the script again.

You can also do this manually using the command:

```bash
pybabel compile -d locales -D tci-editor
```

## 4. Add a new language
To add a new language (e.g., French fr):

Create the directory and the initial file:

```bash
pybabel init -i locales/tci-editor.pot -d locales -l fr -D tci-editor
``` 

This creates locales/fr/LC_MESSAGES/tci-editor.po.

Edit the file and add the translations (see step 2).

Run python manage_translations.py to create the .mo file.

To allow the user to select the language, add it to the combo box in gui/dialogs/app_config_dialog.py:

```python
 Show full code block 
# gui/dialogs/app_config_dialog.py
elif key == “language”:
    widget = QComboBox()
    widget.addItem(“English”, “en”)
    widget.addItem(“Deutsch”, “de”)
    widget.addItem(“Français”, “fr”) # Add new
```

## 5. Switch language
The language is set in app_config.yaml:

```yaml
language: “de”
``` 

Or via the App Tools > App Settings dialog. The application must be restarted for the change to take effect.

## 6. The script 

```bash
python3 manage_translations.py
```

--- 1. Extract texts ---
Run: pybabel extract -F babel.cfg -o locales/tci-editor.pot .
extracting messages from __init__.py (encoding=“utf-8”)

--- 2. Update catalogs ---
Run: pybabel update -i locales/tci-editor.pot -d locales -D tci-editor
updating catalog locales/de/LC_MESSAGES/tci-editor.po based on locales/tci-editor.pot

--- 3. Compile catalogs ---
Run: pybabel compile -d locales -D tci-editor
compiling catalog locales/de/LC_MESSAGES/tci-editor.po to locales/de/LC_MESSAGES/tci-editor.mo

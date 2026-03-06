---
author: TCI
breadcrumbs: true
date: '2025-01-01'
draft: false
featured_image: None
layout: full-width
release_date: '2026-01-15'
tags:
- introduction
- Dokumentation
title: Installation & Requirements
weight: 10
---

# Static Site Editor – Installation Guide

The Static Site Editor is a Python application that runs locally on your computer. Here you will learn how to set it up.

## 1. Requirements

Before you begin, make sure the following software is installed on your system:

- **Operating System:** Windows 10/11, macOS, or Linux  
- **Python:** Version 3.8 or newer  

You can check whether Python is installed by running the following command in your terminal (or command prompt):

```bash

python --version

# or on Linux/macOS often:
python3 --version

```

## 2. Installation

### Step 1: Download the Source Code

Download the project or clone the repository into a folder of your choice:

```bash

git clone https://github.com/your-user/sitewave.git
cd sitewave

```

### Step 2: Create a Virtual Environment (Recommended)

It is recommended to use a virtual environment to install dependencies in isolation.

**Windows:**

```bash

python -m venv venv
venv\Scripts\activate

```

**macOS / Linux:**

```bash

python3 -m venv venv
source venv/bin/activate

```

### Step 3: Install Dependencies

The application requires several Python libraries (e.g., for the graphical user interface and Markdown rendering). Install them using `pip`:

```bash

pip install PyQt6 PyQt6-WebEngine python-frontmatter Markdown PyYAML Jinja2 Babel Pillow Pygments weasyprint requests

```

or by using the `requirements.txt` file:

```bash

pip install -r requirements.txt

```

The **requirements.txt** file:

```txt

markdown
Jinja2
python-frontmatter
Pillow
Pygments
PyQt6
PyQt6-WebEngine
weasyprint
Babel
requests
pymarkdownlnt
pyenchant

```

#### Spellchecker 

Abhängigkeiten installieren Zuerst muss pyenchant zum Projekt hinzugefügt werden.

Python-Paket installieren:

```bash
pip install pyenchant
```

Füge pyenchant auch zu deiner requirements.txt-Datei hinzu.

Backend-Wörterbücher installieren: pyenchant benötigt System-Wörterbücher. Die Installation hängt vom Betriebssystem ab. Dies ist ein wichtiger Hinweis für die spätere Distribution der App.

**Linux (Debian/Ubuntu):**

```bash
sudo apt-get install hunspell hunspell-de-de hunspell-en-us
```

**macOS (via Homebrew):**

```bash
brew install hunspell
```

Wörterbücher müssen evtl. manuell in /Library/Spelling  oder ~/Library/Spelling abgelegt werden.

**Windows:** Hier ist es am einfachsten, die Hunspell-Wörterbuchdateien (.dic, .aff) direkt mit deiner Anwendung auszuliefern und pyenchant den Pfad dorthin mitzuteilen.


## 3. Start the Application

Once all dependencies are installed, you can start the editor:

```bash

python run.py

```

The main window of the editor should now open.

> **Note for Linux users:** If you experience display issues (e.g., a black window), the app will automatically attempt to disable GPU acceleration. Make sure that `libxcb-cursor0` or similar system libraries are installed if PyQt6 does not start properly.

Here are the additional packages that must be installed on Ubuntu/Debian:

```bash

sudo apt install libpangocairo-1.0-0
sudo apt install libcairo2
sudo apt install libgdk-pixbuf2.0-0
sudo apt install libffi-dev
sudo apt install libxcb-cursor0

```
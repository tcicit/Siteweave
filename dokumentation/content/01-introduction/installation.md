---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- Installation
- Documentation
title: Installation & Requirements
weight: 10
---

[[toc min_headers="4" title="Contents"]]

Siteweave is a Python application that runs locally on your computer. Here you will learn how to set it up.

## System Requirements

Before you begin, make sure the following software is installed on your system:

| **Requirement** | **Detail** |
| :--- | :--- |
| **Operating System** | Linux, macOS, or Windows |
| **Python Version** | 3.10 or higher |
| **Package Manager** | pip (comes with Python) |
| **Optional** | Hunspell (for spellchecking) |

You can check whether Python is installed by running the following command in your terminal:

```bash
python --version

# or on Linux/macOS:
python3 --version
```

## Installation Steps

### Step 1 — Clone the Repository

Download the project or clone the repository into a folder of your choice:

```bash
git clone https://github.com/YOUR-USERNAME/siteweave.git
cd siteweave

# Copy the default configuration
cp app_config_default.yaml app_config.yaml
```

### Step 2 — Create a Virtual Environment

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

### Step 3 — Install Dependencies

Install all required Python libraries using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file includes:

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

### Step 4 — Install Hunspell (Optional, for Spellchecking)

**Linux (Debian/Ubuntu):**

```bash
sudo apt-get install hunspell hunspell-de-de hunspell-en-us
```

**macOS (via Homebrew):**

```bash
brew install hunspell
```

**Windows:** The easiest way is to deliver the Hunspell dictionary files (`.dic`, `.aff`) directly with your application and configure `pyenchant` to use their path.

### Step 5 — Additional System Libraries (Linux only)

On Ubuntu/Debian, install these additional packages:

```bash
sudo apt install libpangocairo-1.0-0
sudo apt install libcairo2
sudo apt install libgdk-pixbuf2.0-0
sudo apt install libffi-dev
sudo apt install libxcb-cursor0
```

### Step 6 — Launch Siteweave

Once all dependencies are installed, start the editor:

```bash
python main.py
```

The main window of the editor should now open.

[[infobox type="info" title="Tip: First Launch"]]
On first launch, Siteweave will use the settings from `app_config.yaml`.
You can immediately open or create a project via the project manager.
[[/infobox]]

[[infobox type="warning" title="Linux Display Issues"]]
If you experience display issues on Linux (e.g., a black window), the app will automatically attempt to disable GPU acceleration. Make sure `libxcb-cursor0` or similar system libraries are installed if PyQt6 does not start properly.
[[/infobox]]

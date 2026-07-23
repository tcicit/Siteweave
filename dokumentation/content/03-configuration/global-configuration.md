---
author: TCI
breadcrumbs: true
date: '2026-07-23'
draft: false
featured_image: ''
layout: doc
release_date: '2026-07-23'
tags:
- Configuration
- Global Settings
title: Global Configuration
weight: 15
---

[[toc min_headers="3" title="Contents"]]

Siteweave uses a central configuration file named `app_config.yaml` located in the application root folder to manage editor settings, UI preferences, keybindings, external tool integrations, and default behaviors across all projects.

---

## 1. UI & Visual Settings

| Property | Default | Description |
| :--- | :--- | :--- |
| `view_show_preview` | `true` | Show or hide the HTML live preview pane on launch. |
| `view_show_toolbar` | `true` | Toggle visibility of the main action toolbar. |
| `view_show_line_numbers` | `true` | Display line numbers in the Markdown editor. |
| `view_dark_mode` | `false` | Enable dark theme UI for the editor and preview. |
| `editor_font_size` | `12` | Font size (in points) for the code editor. |
| `editor_font_family` | `Monospace` | Monospaced font family for Markdown editing. |
| `preview_font_family` | `Sans Serif` | Font family used inside the live preview pane. |
| `preview_font_size` | `14` | Base font size (pt) in the live preview. |
| `language` | `en_US` | GUI language (`en_US`, `de_DE`, etc.). |

---

## 2. Editor & Autosave Behavior

```yaml
autosave_interval: 300    # Automatic save interval in seconds
autosave_on_close: false  # Auto-save active file when closing window
autosave_on_switch: false # Auto-save when switching between tabs/documents
auto_open_last_project: true # Automatically reopen the last opened project
```

---

## 3. Toolbar & Icon Customization

### Action Icons Mapping (`action_icons`)
Maps internal action IDs to theme icon names:
```yaml
action_icons:
  new_act: add
  save_act: save
  insert_img_act: image
  insert_file_act: link
  toggle_preview_act: preview
  dark_mode_act: dark_mode
  config_act: info
  project_config_act: settings
```

### Toolbar Layout (`toolbar_layout`)
Defines the sequence and order of items in the top toolbar:
```yaml
toolbar_layout:
- new_act
- save_act
- separator
- undo_act
- redo_act
- search_act
- separator
- toggle_preview_act
- switch_project_act
- project_config_act
- spacer
- gallery_act
- insert_img_act
- insert_file_act
- bold_act
- italic_act
```

---

## 4. External Applications & Media Editors

Integrate external graphics software (e.g. GIMP, Inkscape) or document viewers (e.g. Xreader) to edit or open media files directly from the Media Manager.

```yaml
external_editors:
- name: GIMP
  extensions: [.jpg, .jpeg, .png, .webp, .gif, .xcf]
  command: [flatpak, run, org.gimp.GIMP]
  icon: applications-other
- name: Inkscape
  extensions: [.svg]
  command: [flatpak, run, org.inkscape.Inkscape]
  icon: applications-other
- name: xreader
  extensions: [.pdf]
  command: [xreader, '%U']
  icon: applications-other
```

---

## 5. Application Paths

Specifies subdirectories relative to the application root for global assets and extension resources:

```yaml
paths:
  snippets: snippets
  themes: themes
  locales: locales
  pdf_themes: pdf_themes
  plugins: plugins
  scripts: scripts
```

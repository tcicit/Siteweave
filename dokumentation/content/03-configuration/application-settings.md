---
author: TCI
breadcrumbs: true
date: '2026-01-17'
draft: false
featured_image: ''
layout: doc
release_date: '2026-01-17'
tags:
- Konfiguration
- Dokumentation
- konfiguration
title: App Settings
weight: 10
---

# App Settings (app_config.yaml)

The `app_config.yaml` file in the application's root directory controls the editor's global settings, which apply across projects. You can edit this file manually or change many of the settings via the **App Tools -> App Settings** dialog.

## 1. Editor Behavior

### Auto Save

These settings control when and how the editor saves your work to prevent data loss.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `autosave_interval` | Number | `60` | Time interval in seconds at which automatic saving occurs. Set the value to `0` to disable time-based saving. |
| `autosave_on_close` | Boolean | `true` | If `true`, unsaved changes are saved immediately when the window is closed, without a confirmation dialog appearing. |
| `autosave_on_switch` | Boolean | `true` | If `true`, saving occurs automatically when switching files (in the file tree) or projects. |

### Startup behavior & language

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `auto_open_last_project` | Boolean | Automatically opens the last used project at startup. If `false`, the Project Launcher always appears. |
| `language` | String | Language of the user interface (e.g., `en` for English, `de` for German). Requires a restart. |
| `recent_projects` | List | List of paths to recently opened projects (managed automatically). |

## 2. Display & Font

These settings affect the appearance of the editor and preview.

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `editor_font_family` | The font in the editor area. It is recommended to use a monospace font. | `Monospace`, `Consolas`, `Fira Code` |
| `editor_font_size` | Font size in the editor in pixels. | `12` |
| `preview_font_family` | The font for the live preview. | `Sans Serif`, `Arial` |
| `preview_font_size` | Font size in the preview. | `14` |
| `view_show_line_numbers` | Display line numbers on the left margin (`true`/`false`). | `true` |
| `view_dark_mode` | Start the editor in dark mode. | `false` |
| `view_show_preview` | Display the live preview at startup. | `false` |
| `view_show_toolbar` | Display the toolbar. | `true` |

## 3. Customize toolbar (`toolbar_layout`)

You can completely configure the toolbar by editing the `toolbar_layout` list. This allows you to hide rarely used functions or change the order.

### Available elements:

* **Actions:** `new_act`, `save_act`, `undo_act`, `redo_act`, `bold_act`, `italic_act`, `code_act`, `h1_act`, `h2_act`, `h3_act`, `ul_act`, `ol_act`, `table_act`, `insert_img_act`, `insert_file_act`, `gallery_act`, `emoji_act`, `search_act`, `replace_act`, `render_act`, `open_browser_act`, `config_act`, `switch_project_act`, `toggle_preview_act`, `select_all_act`.

* **Separators:** `separator` (vertical line).
* **Spacers:** `spacer` (moves subsequent elements to the right).

## 4. Customize icons (`action_icons`)

You can assign a separate icon to each command. The icons are searched for in the `assets/icons` folder (as `.svg` files) or can be specified as an absolute path.

**Syntax:** `action_name: icon_filename_without_extension`

```yaml
action_icons:
  save_act: save          # Uses assets/icons/save.svg
  emoji_act: emoji        # Uses assets/icons/emoji.svg
  exit_act: cancel
```

## 5. Paths

System paths for resources are defined here.

```yaml
paths:
  snippets: snippets  # Folder for text snippets
  themes: themes      # Folder for editor themes
```

## 6. Window position

The following parameters are automatically updated by the editor to restore the window position and size.

* window_width, window_height
* window_x, window_y

**Note:** The color settings (editor_colors) have been removed from this file and are now managed separately via the App Tools > Color Settings dialog.
---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- Configuration
- Documentation
title: App Settings (app_config.yaml)
weight: 10
---

[[toc min_headers="4" title="Contents"]]

The `app_config.yaml` file in the application's root directory controls the editor's **global settings**, which apply across all projects. You can edit this file manually or change many settings via the **App Tools → App Settings** dialog.

## 1. Editor Behavior

### Auto Save

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `autosave_interval` | Number | `60` | Seconds between automatic saves. Set to `0` to disable. |
| `autosave_on_close` | Boolean | `true` | Save automatically when the window is closed. |
| `autosave_on_switch` | Boolean | `true` | Save when switching files or projects. |

### Startup Behavior & Language

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `auto_open_last_project` | Boolean | Automatically opens the last used project at startup. If `false`, the Project Launcher always appears. |
| `language` | String | UI language (e.g. `en` for English, `de` for German). Requires a restart. |
| `recent_projects` | List | List of recently opened project paths (managed automatically). |

## 2. Display & Font

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `editor_font_family` | Font in the editor. Use a monospace font for best results. | `Consolas`, `Fira Code` |
| `editor_font_size` | Font size in the editor (pixels). | `12` |
| `preview_font_family` | Font for the live preview. | `Arial`, `Sans Serif` |
| `preview_font_size` | Font size in the preview (pixels). | `14` |
| `view_show_line_numbers` | Show line numbers in the editor. | `true` |
| `view_dark_mode` | Start the editor in dark mode. | `false` |
| `view_show_preview` | Show live preview at startup. | `false` |
| `view_show_toolbar` | Show the toolbar. | `true` |

## 3. Customize Toolbar (`toolbar_layout`)

You can fully configure the toolbar by editing the `toolbar_layout` list. This allows you to hide rarely used functions or reorder buttons.

### Available Elements

**Actions:**

```
new_act, save_act, undo_act, redo_act, bold_act, italic_act, code_act,
h1_act, h2_act, h3_act, ul_act, ol_act, table_act, insert_img_act,
insert_file_act, gallery_act, emoji_act, search_act, replace_act,
render_act, open_browser_act, config_act, switch_project_act,
toggle_preview_act, select_all_act
```

**Separators and spacers:**

- `separator` — vertical line between button groups
- `spacer` — moves subsequent elements to the right

**Example configuration:**

```yaml
toolbar_layout:
  - new_act
  - save_act
  - separator
  - bold_act
  - italic_act
  - code_act
  - separator
  - render_act
  - open_browser_act
  - spacer
  - toggle_preview_act
```

## 4. Customize Icons (`action_icons`)

Assign a custom icon to each command. Icons are searched for in the `assets/icons` folder (as `.svg` files).

```yaml
action_icons:
  save_act: save        # Uses assets/icons/save.svg
  render_act: render    # Uses assets/icons/render.svg
  emoji_act: emoji
```

## 5. Paths

```yaml
paths:
  snippets: snippets    # Folder for text snippets
  themes: themes        # Folder for editor themes
```

## 6. Window Position

The following parameters are updated automatically by the editor to restore window position and size on next launch:

- `window_width`, `window_height`
- `window_x`, `window_y`

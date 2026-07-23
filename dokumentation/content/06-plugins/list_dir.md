---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
pdf_exclude: true
release_date: '2026-03-08'
tags:
- Plugin
- Documentation
title: Plugin — List Directory
weight: 70
---

The `list_dir` plugin generates an automatic list of links to all pages in a folder. It is the core of Siteweave's automatic navigation and index generation.

## Syntax

```markdown
[[list_dir]]

[[list_dir path="02-user-manual" exclude="index.md" sort="weight"]]
```

## Parameters

| Parameter | Description | Default |
| :--- | :--- | :--- |
| **path** | Subfolder to list (relative to current page). If omitted, lists the current folder. | current folder |
| **xclude** | Comma-separated filenames to exclude (e.g. `"index.md"`). | none |
| **sort** | Sort order: `weight`, `date`, `title`, `filename` | `filename` |
| **depth** | Maximum folder depth to list | `1` |
| **show_date** | Show publication date next to each link | `false` |

## Examples

### List Current Folder

```markdown
[[list_dir exclude="index.md" sort="weight"]]
```
[[list_dir exclude="index.md" sort="weight"]]


### List a Specific Subfolder

```markdown
## Getting Started

[[list_dir path="01-introduction" exclude="index.md" sort="weight"]]

## User Manual

[[list_dir path="02-user-manual" exclude="index.md" sort="weight"]]
```

### List with Dates

```markdown
[[list_dir sort="date" show_date="true"]]
```

## How the Index Pages Work

Every section index in this documentation uses `list_dir`. The `index.md` file of each section contains only a front matter block and the plugin call:

```markdown
---
title: Getting Started
layout: full-width
pdf_exclude: true
weight: 0
---

This index was created automatically.

[[list_dir exclude="index.md" sort="weight"]]
```

This means you never have to manually maintain navigation lists — just add or remove `.md` files and the index updates itself on the next render.

[[infobox type="info" title="Sort by Weight"]]
Use the **weight** field in your front matter to control the order of pages in **list_dir** outputs. Pages with lower weight values appear first. This is the recommended approach for documentation sections where logical order matters more than alphabetical or chronological order.
[[/infobox]]
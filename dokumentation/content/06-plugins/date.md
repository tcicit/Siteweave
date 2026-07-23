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
title: Plugin — Date
weight: 90
---

The `date` plugin inserts a dynamically formatted date or time value at render time. Use it for "last updated" notices, copyright years, or timestamps anywhere in your content.

## Syntax

```markdown
[[date]]

[[date format="%B %d, %Y"]]

[[date format="%Y"]]
```

## Parameters

| Parameter | Description | Default |
| :--- | :--- | :--- |
| `format` | Python `strftime` format string | `%Y-%m-%d` |
| `source` | `now` (render time) or `page` (from front matter `date`) | `now` |

## Format Reference

| Code | Meaning | Example |
| :--- | :--- | :--- |
| `%Y` | 4-digit year | `2026` |
| `%y` | 2-digit year | `26` |
| `%m` | Month (zero-padded) | `03` |
| `%B` | Full month name | `March` |
| `%b` | Abbreviated month | `Mar` |
| `%d` | Day (zero-padded) | `08` |
| `%A` | Full weekday name | `Sunday` |
| `%a` | Abbreviated weekday | `Sun` |
| `%H:%M` | Hour:Minute (24h) | `14:30` |

## Examples

Current date (default format): [[date]]

Current year only: [[date format="%Y"]]

Long format: [[date format="%B %d, %Y"]]

European format: [[date format="%d.%m.%Y"]]

## Typical Use Cases

**Footer copyright notice:**

```markdown
© [[date format="%Y"]] My Company. All rights reserved.
```

**Last updated notice:**

```markdown
*This page was last rendered on [[date format="%B %d, %Y"]].*
```

**Page date from front matter:**

```markdown
Published: [[date source="page" format="%B %d, %Y"]]
```
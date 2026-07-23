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
title: Plugin — Tables
weight: 60
---

[[toc min_headers="4" title="Contents"]]

Tables are supported natively via the Python Markdown `tables` extension — no plugin shortcode required. The `csv` plugin allows you to import tabular data directly from `.csv` files.

## Standard Markdown Tables

### Basic Table

```markdown
| Name | Role | Location |
| :--- | :--- | :------- |
| Alice | Developer | Zurich |
| Bob | Designer | Berlin |
| Carol | Manager | London |
```

Rendered:

| Name | Role | Location |
| :--- | :--- | :------- |
| Alice | Developer | Zurich |
| Bob | Designer | Berlin |
| Carol | Manager | London |

### Column Alignment

```markdown
| Left aligned | Centered | Right aligned |
| :----------- | :------: | ------------: |
| Text | Text | Text |
| 1234 | 5678 | 9012 |
```

| Left aligned | Centered | Right aligned |
| :----------- | :------: | ------------: |
| Text | Text | Text |
| 1234 | 5678 | 9012 |

### Table with Formatted Content

Tables can contain **bold**, *italic*, `code`, and [links](https://example.com):
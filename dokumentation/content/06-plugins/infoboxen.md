---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: full-width
pdf_exclude: true
release_date: '2026-03-08'
tags:
- Plugin
- Documentation
title: Plugin — Infobox
weight: 10
---


Description: Creates an infobox with different styles and an optional title.

## Syntax

`[[infobox type="warning" title="Attention!"]]Content...[[/infobox]]`

## Parameters

| Parameter | Values | Description |
| :--- | :--- | :--- |
| **type** | `info`, `warning`, `success`, `error` | Visual style of the box |
| **title** | Any string | Optional title displayed at the top |


## Examples

### Default (no type)
```
[[infobox]]
This is a default infobox without a type or title. Plain and simple.
[[/infobox]]
```

[[infobox]]
This is a default infobox without a type or title. Plain and simple.
[[/infobox]]

### Type: info

[[infobox type="info" title="Information"]]
This is an **informational** message. Use it for tips, hints, and general notes that are helpful but not critical.
[[/infobox]]

### Type: success

[[infobox type="success" title="Success"]]
**Operation completed successfully.** Use this to confirm completed steps or positive outcomes.
[[/infobox]]

### Type: warning

[[infobox type="warning" title="Warning"]]
**Please double-check your input.** Use this to highlight important cautions before a potentially destructive action.
[[/infobox]]

### Type: error

[[infobox type="error" title="Error"]]
**Critical warning!** This is irreversible. Use sparingly for serious errors or data-loss situations.
[[/infobox]]
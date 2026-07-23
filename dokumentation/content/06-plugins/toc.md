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
title: Plugin — Table of Contents
weight: 20
---

The `toc` plugin inserts an automatic table of contents based on the headings in your page. It can be set to only appear when the page has enough headings to justify it.

## Syntax

```markdown
[[toc title="Contents" depth="3" min_headers="4"]]
```

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **title** | String | `"Contents"` | Heading shown above the TOC |
| **depth* | Int | `6` | Maximum heading depth included |
| **min_headers** | Int | `1` | Minimum number of headings required to show the TOC |

## Live Example

The TOC shown at the top of this page (if visible) was inserted with:

```markdown
[[toc min_headers="4" title="Contents"]]
```

The `min_headers="4"` setting means the TOC is only rendered if the page contains at least 4 headings — keeping short pages clean.

## How It Works

The plugin inserts the `[TOC]` marker used by the Python Markdown `toc` extension. When the renderer processes the page, this marker is replaced with a generated list of all headings at or above the specified `depth`.

[[infobox type="info" title="Tip"]]
Place the `[[toc]]` shortcode at the very top of your page content (after the front matter) for best results. It works well on long documentation pages but adds little value on short pages — use `min_headers` to control when it appears.
[[/infobox]]

## Example

```markdown
[[toc min_headers="4" title="Contents"]]
```

[[toc min_headers="4" title="Contents"]]
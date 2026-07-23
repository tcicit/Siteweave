---
author: TCI
breadcrumbs: true
date: '2026-07-23'
draft: false
featured_image: ''
layout: doc
release_date: '2026-07-23'
tags:
- Plugins
- Tags
title: Tags Plugin
weight: 35
---

The `tags` plugin generates tag clouds, tag listings, and tagged content summaries across your project.

## Syntax

### Tag Cloud
```markdown
[[tags mode="cloud"]]
```

### Tag List for Current Page
```markdown
[[tags mode="list"]]
```

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mode` | string | `cloud` | Display mode: `cloud`, `list`, or `summary`. |
| `sort` | string | `count` | Sort tags by `count` (frequency) or `name` (alphabetical). |
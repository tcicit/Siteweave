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
- Code
title: Code Plugin
weight: 30
---

The `code` plugin provides syntax-highlighted code blocks with line numbers and custom styling using Pygments.

## Syntax

```markdown
[[code lang="python" filename="example.py"]]
def greet(name):
    return f"Hello, {name}!"
[[/code]]
```

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `lang` | string | `text` | Programming or markup language (e.g. `python`, `html`, `css`, `bash`, `yaml`). |
| `filename` | string | `""` | Optional file header label displayed above the code block. |
| `linenos` | boolean | `true` | Show or hide line numbers. |

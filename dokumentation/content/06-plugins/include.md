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
title: Plugin — Include
weight: 80
---

Description: Reads a file and returns its content.

## Syntax: 

`[[include src="file.md"]]`


## Parameters:
- **src**: Path to the file (relative to the markdown file).
- **class**: Optional CSS class to apply to the included content.

>CSS classes must be defined in the template's styles.css file. 

## Examples

### Include a Markdown File

```markdown
[[include src="_assets/_notice.md"]]
```

[[include src="_assets/_notice.md" class="include-warnings"]]

## Benefits

- **Single source of truth** — update content in one place and it propagates everywhere.
- **Clean Markdown files** — keep repeated boilerplate out of your content files.
- **No duplication** — reduces the chance of inconsistencies across pages.

[[infobox type="warning" title="Circular Includes"]]
Avoid circular includes (file A includes file B, which includes file A). Siteweave has a depth limit to prevent infinite loops, but it is still best practice to avoid them.
[[/infobox]]
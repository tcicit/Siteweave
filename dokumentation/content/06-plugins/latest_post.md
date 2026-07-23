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
title: Plugin — Latest Posts
weight: 120
---

The `latest_posts` plugin generates a list of the most recently published pages, sorted by `release_date`. Ideal for blog home pages and sidebars.

## Syntax

```markdown
[[latest_posts count="5"]]
```

## Parameters

| Parameter | Description | Default |
| :--- | :--- | :--- |
| **count** | Number of posts to display | `5` |
| **folder** | Restrict to a specific content subfolder | all content |
| **show_date** | `true` — show publication date | `true` |
| **show_summary** | `true` — show the `summary` front matter field | `false` |
| **exclude_drafts** | `true` — skip draft pages | `true` |

## Examples

### Latest 5 Posts (Default)

```markdown
[[latest_posts]]
```

[[latest_posts]]



### Latest 3 Posts from a Specific Folder

```markdown
[[latest_posts count="3" folder="blog"]]
```

### With Summary

```markdown
[[latest_posts count="5" show_summary="true"]]
```

## Front Matter Integration

For best results with the `show_summary` parameter, add a `summary` field to your pages:

```yaml
---
title: My Tutorial on Python Decorators
date: 2026-02-15
release_date: 2026-02-15
tags:
- Python
- Tutorial
summary: A practical introduction to Python decorators — what they are, how they work, and when to use them.
---
```

## Typical Placement

**Blog home page (`index.md` in the blog folder):**

```markdown
# Blog

Welcome to the blog. Here are the latest posts:

[[latest_posts count="10" folder="blog" show_summary="true"]]
```

**Home page sidebar:**

```markdown
## Recent Posts

[[latest_posts count="5"]]
```
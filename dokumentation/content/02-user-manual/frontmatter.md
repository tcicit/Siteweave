---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- User Manual
- Documentation
title: Front Matter
weight: 40
---

[[toc min_headers="4" title="Contents"]]

Every page in your project contains a special block at the very beginning called **front matter**. This area stores metadata about the page — information that is not directly visible in the text but is essential for generating the website correctly.

## 1. What is Front Matter?

Front matter is a **YAML block** at the very top of your Markdown file, enclosed by two lines of three dashes (`---`):

```yaml
---
title: My Page
date: 2025-01-01
layout: doc
draft: false
tags:
- Tutorial
- Documentation
---

Page content starts here...
```

The **Metadata Panel** below the editor lets you edit these fields conveniently via a form — no manual YAML editing required. Changes in the form are automatically written to the YAML block and vice versa.

## 2. Standard Fields

Siteweave automatically recognizes and uses the following fields:

| **Field** | **Type** | **Description** |
| :--- | :--- | :--- |
| `title` | String | **(Required)** Page title — shown in the browser tab and as the main H1 heading. |
| `date` | Date | Display date of the page (format: `YYYY-MM-DD`). |
| `release_date` | Date | Automatically set on first render; ensures stable chronological sorting. |
| `layout` | String | Template to use (without `.html`), e.g. `doc` → `layout_doc.html`. |
| `draft` | Boolean | If `true`, this page is skipped during rendering. |
| `tags` | List | Keywords for categorization, e.g. `[News, Update]`. |
| `author` | String | Author name. |
| `featured_image` | String | Path to a preview image for the page. |
| `breadcrumbs` | Boolean | Controls whether breadcrumb navigation is displayed. |
| `pdf_exclude` | Boolean | If `true`, this page is excluded from PDF exports. |
| `weight` | Integer | Controls the sort order in navigation and `[[list_dir]]` outputs. Lower = earlier. |

## 3. Custom Fields

One of the strengths of front matter is that you can define **any additional fields you want**. They become available as variables in your Jinja2 templates automatically.

**Example — adding a summary and a hero image:**

```yaml
---
title: My Vacation in Italy
date: 2025-06-15
featured_image: /assets/images/italy.jpg
summary: A short report about my trip through Tuscany.
show_hero: true
---
```

### Using Custom Fields in Templates

```html
<!-- templates/layout_blog.html -->
<article>
    <h1>{{ page_title }}</h1>

    {% if featured_image %}
        <img src="{{ relative_prefix }}{{ featured_image }}" alt="Preview image" class="featured-image">
    {% endif %}

    {% if summary %}
        <p class="intro">{{ summary }}</p>
    {% endif %}

    <div class="content">
        {{ content }}
    </div>
</article>
```

## 4. Controlling Page Rendering with Front Matter

### Draft Pages

Set `draft: true` to exclude a page from the rendered output while keeping it in the project:

```yaml
---
title: Work in Progress
draft: true
---
```

### Excluding Pages from PDF Export

Add `pdf_exclude: true` to pages like index files or navigation pages that should not appear in the PDF manual:

```yaml
---
title: Section Index
pdf_exclude: true
---
```

### Controlling Sort Order

The `weight` field determines the order in which pages appear in navigation menus and `[[list_dir]]` outputs. Pages with a lower weight value appear first:

```yaml
---
title: Installation
weight: 10
---
```

```yaml
---
title: First Steps
weight: 20
---
```

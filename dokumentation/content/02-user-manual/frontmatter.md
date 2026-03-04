---
author: TCI
breadcrumbs: true
date: '2025-01-11'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Benutzerhandbuch
- Dokumentation
title: Frontmatter
weight: 40
---

Every page in your project contains a special block at the beginning called **front matter**. This area is used to store metadata about the page that is not directly visible in the text but is important for generating the web page.

## 1. What is front matter?

Front matter is a YAML block located at the very top of your Markdown file. It is enclosed by two lines of three dashes `---`.

```yaml
---
title: My Page
date: 2025-01-01
layout: doc
---
```

Below the text field, the editor provides a form (“metadata panel”) that allows you to conveniently edit the most important fields without having to write the YAML code manually. Changes made in the form are automatically written to the YAML block and vice versa.

## 2. Standard fields

The Sitewave automatically recognizes and uses the following fields:

*   **`title`**: (Required field) The title of the page. This is displayed in the browser tab (`<title>`) and usually as the main heading (`<h1>`) on the page.
*   **`date`**: The date displayed on the page (format: YYYY-MM-DD).
*   **`release_date`**: A technical date that is automatically set by the system during the first render to ensure stable chronological sorting.
*   **`layout`**: The template to be used (without `.html`), e.g. `post` for `templates/layout_post.html`.
*   **`draft`**: (`true`/`false`) If enabled, this page is ignored during rendering (draft).
*   **`tags`**: A list of keywords (e.g., `[News, Update]`).
*   **`author`**: The name of the author.
* **`image`**: Path to a preview image for the page.
* **`breadcrumbs`**: (`true`/`false`) Controls whether breadcrumb navigation should be displayed.

## 3. Custom fields

One of the strengths of front matter is that you can define **any fields you want**.

**Example:**
You want to define a preview image and a short summary for blog articles. Simply add the fields `image` and `summary`:

```yaml
---
title: My Vacation
date: 2025-06-15
image: /assets/images/vacation.jpg
summary: A short report about my trip to Italy.
---
```

### Use in Templates

These custom fields are then automatically available in your Jinja2 templates.

```html
<!-- templates/layout_blog.html -->
<article>
    <h1>{{ title }}</h1>
    
    {% if image %}
        <img src="{{ relative_prefix }}{{ image }}" alt="Preview image" class="featured-image">
    {% endif %}

    {% if summary %}
        <p class="intro">{{ summary }}</p>
    {% endif %}

    <div class="content">
        {{ content }}
    </div>
</article>
```

This allows you to design your website with extreme flexibility without having to change the editor's program code.
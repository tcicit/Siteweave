---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- Development
- Documentation
title: Developing Your Own Plugins
weight: 10
---

[[toc min_headers="4" title="Contents"]]

Plugins (also called **shortcodes**) are Python files in the `plugins/` folder that generate HTML from simple Markdown shortcode tags. Basic Python knowledge is required.

## 1. Why Plugins?

Instead of copying complex HTML every time:

```html
<div class="infobox infobox-warning">
    <div class="infobox-title">Attention</div>
    <p>This is important information.</p>
</div>
```

...you simply write in Markdown:

```markdown
[[infobox type="warning" title="Attention"]]
This is important information.
[[/infobox]]
```

Plugins keep your content clean, prevent errors, and make maintenance much easier.

## 2. Your First Plugin

### Step 1: Create the File

Create `plugins/greeting.py`. The file name (`greeting`) becomes the plugin name.

### Step 2: Write the `handle` Function

```python
# plugins/greeting.py

def handle(content, args, context, env):
    """
    A simple greeting plugin.
    Syntax: [[greeting name="World"]]
    """
    name = args.get('name', 'Unknown')
    return f"<strong>Hello, {name}!</strong>"
```

### Step 3: Use the Plugin

In any `.md` file:

```markdown
This is a test: [[greeting name="Reader"]].
And here without a name: [[greeting]].
```

Rendered output:

```html
This is a test: <strong>Hello, Reader!</strong>.
And here without a name: <strong>Hello, Unknown!</strong>.
```

## 3. The `handle` Function in Detail

```python
def handle(content, args, context, env):
    return "..."
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `content` | `str` or `None` | Text between opening and closing tags. `None` for self-closing tags. |
| `args` | `dict` | Parameters from the shortcode (e.g. `{"type": "warning", "title": "Note"}`). |
| `context` | `dict` | Page context — `page_title`, `date`, `relative_prefix`, `site_structure`, etc. |
| `env` | `object` | The Jinja2 environment — for advanced template rendering. |

## 4. Practical Example: Info Box

```python
# plugins/infobox.py
import markdown as md

def handle(content, args, context, env):
    box_type = args.get('type', 'info')   # info, warning, success, danger
    title    = args.get('title', '')

    html_content = md.markdown(content) if content else ''
    title_html   = f'<div class="infobox-title">{title}</div>' if title else ''

    return f'<div class="infobox infobox-{box_type}">{title_html}{html_content}</div>'
```

Usage:

```markdown
[[infobox type="warning" title="Important"]]
This content will be **formatted** with Markdown.
[[/infobox]]
```

## 5. Practical Example: Latest Posts

```python
# plugins/latest_posts.py
import os
import frontmatter

def handle(content, args, context, env):
    count = int(args.get('count', 5))
    content_dir = context.get('project_root', '') + '/content'

    posts = []
    for root, dirs, files in os.walk(content_dir):
        for f in files:
            if f.endswith('.md') and f != 'index.md':
                post = frontmatter.load(os.path.join(root, f))
                if not post.get('draft', False):
                    posts.append({
                        'title': post.get('title', f),
                        'date':  str(post.get('release_date', '')),
                        'path':  os.path.join(root, f).replace(content_dir, '').replace('.md', '.html')
                    })

    posts = sorted(posts, key=lambda x: x['date'], reverse=True)[:count]

    items = ''.join(
        f'<li><a href="{p["path"]}">{p["title"]}</a> <span class="date">{p["date"]}</span></li>'
        for p in posts
    )
    return f'<ul class="latest-posts">{items}</ul>'
```

Usage:

```markdown
[[latest_posts count="5"]]
```

## 6. Using the Context

The `context` dictionary gives you access to page and site data:

```python
def handle(content, args, context, env):
    relative_prefix = context.get('relative_prefix', '')
    page_title      = context.get('page_title', '')
    site_name       = context.get('site_name', '')
    config          = context.get('config', {})

    # Access social links from config
    github_url = config.get('social', {}).get('github', '#')

    return f'<a href="{github_url}" class="github-link">View on GitHub</a>'
```

## 7. Plugin Location

Plugins can be placed in two locations:

- **Global plugins** — `plugins/` in the Siteweave application folder. Available to all projects.
- **Project plugins** — `plugins/` in your project folder. Overrides global plugins with the same name.

## 8. Tips & Best Practices

- Always use `args.get('key', 'default')` — never assume a parameter exists.
- Return valid HTML strings. Empty string `""` is a valid return value.
- Use `content` for block-style content between opening/closing tags.
- Process `content` through `markdown.markdown()` to support Markdown formatting inside plugins.
- Keep plugins focused — one responsibility per plugin.

---
author: TCI
breadcrumbs: true
date: '2025-01-05'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Dokumentation
- Entwicklung
title: Develop your own plugins
weight: 10
---

This article explains how you can create your own plugins for Sitewaver. Plugins, also known as “shortcodes,” are a powerful way to use reusable and complex HTML components directly in your Markdown files.

You will need basic Python knowledge to follow this guide.

## 1. What is a plugin and why do I need it?

Imagine you want to display a special info box with a warning triangle and a yellow background on several pages. Instead of copying the complex HTML code every time:

```html
<div class="infobox infobox-warning">
    <div class="infobox-title">Attention</div>
    <p>This is important information.</p>
</div>
```

...you could simply write this in your Markdown:

```markdown
[[infobox type="warning" title="Attention"]]
This is important information.
[[/infobox]]
```

That's the purpose of a plugin: it takes a simple instruction (the “shortcode”) and converts it into more complex HTML at runtime. This keeps your content clean, avoids errors, and makes maintaining your website much easier.

## 2. The basics: Your first plugin

A plugin is essentially a simple Python file located in the `plugins/` directory of your project. Each plugin must contain a special function called `handle`.

### Step 1: Create the file

Create a new file in the `plugins/` directory. Let's call it `greeting.py`. The file name (`greeting`) becomes the name of your plugin.

### Step 2: Write the `handle` function

Open `plugins/greeting.py` and paste the following code:

```python
# plugins/greeting.py

def handle(content, args, context, env):
    “”"
    A simple greeting plugin.
    Syntax: [[greeting name="World"]]
    “”"
    # Get the value of the ‘name’ parameter from the shortcode.
    # If it doesn't exist, use “Unknown” as the default.
    name = args.get(‘name’, ‘Unknown’)

    # Return the HTML code as a string.
    return f“<strong>Hello, {name}!</strong>”
```

### Step 3: Use the plugin

Open any `.md` file in your `content/` directory and add the shortcode:

```markdown
This is my first test: [[greeting name="Reader"]].

And here without a name: [[greeting]].
```

If you now regenerate the page with `python site_renderer.py`, the following HTML code will be generated at these points:

```html
This is my first test: <strong>Hello, Reader!</strong>.

And here without a name: <strong>Hello, Unknown!</strong>.
```

Congratulations, you've written your first plugin!

## 3. The `handle` function in detail

The `handle` function is the heart of every plugin. It receives four arguments that provide you with all the information you need to process the shortcode.

```python
def handle(content, args, context, env):
    # Your code here...
    return “...”
```

Let's take a closer look at the arguments:

### `content` (string or `None`)

This parameter contains all the text that is *between* the opening and closing plugin tags.

**Example:** For the shortcode `[[box]]This is the content[[/box]]`, `content` would be the string `“This is the content”`.

For “self-closing” tags such as `[[greeting name="World"]]`, `content` has the value `None`.

### `args` (Dictionary)

This is a Python dictionary that contains all parameters (attributes) from the opening tag.

**Example:** For the shortcode `[[infobox type="warning" title="Attention"]]`, the `args` dictionary looks like this:
```python
{
    “type”: “warning”,
    “title”: “Attention”
}
```
You can safely access these values with `args.get(‘parameter_name’, ‘default_value’)`.

### `context` (Dictionary)

This is a very powerful dictionary. It gives you access to metadata for the current page and the entire website. Here are some of the most important keys:

*   `context[‘page_title’]`: The title of the page where the plugin is used.
* `context[‘author’]`, `context[‘date’]`, `context[‘tags’]`: All variables from the front matter of the current page.
* `context[‘relative_prefix’]`: The relative path to the root directory (e.g., `./` or `../`). Extremely important for creating links to assets or other pages correctly!
* `context[‘site_structure’]`: The entire page structure of the website as a nested dictionary. Useful for building navigation elements.
* `context[‘current_page_path’]`: The file path of the Markdown file currently being processed (e.g., `content/Test/my-page.md`).

### `env` (Jinja2 Environment)

This is the Jinja2 template engine object. You only need it for advanced use cases, e.g. if your plugin itself needs to render a Jinja2 template file to generate very complex HTML.




## 4. Plugins that process content

Many plugins enclose a block of content. The `infobox` plugin is a perfect example. It takes the Markdown text inside and wraps it in a styled `<div>`.

To do this, you need to import and use the `markdown` library in your plugin.

**Example: A simple `quote.py` plugin**

```python
# plugins/quote.py
import markdown

def handle(content, args, context, env):
    “”"
    Formats text as a block quote.
    Syntax: [[quote author="Albert Einstein"]]Quote text...[[/quote]]
    “”"
    author = args.get(‘author’)

    # Convert the Markdown content to HTML
    html_content = markdown.markdown(content.strip() if content else ‘’)

    author_html = f“<footer>— {author}</footer>” if author else ‘’

    return f“<blockquote>{html_content}{author_html}</blockquote>”
```

**Important:** The generator processes the plugins first and *then* the rest of the Markdown on the page. So if you want Markdown to work *within* your plugin (such as lists or bold text), you must explicitly convert it in your `handle` function with `markdown.markdown()`.

## 5. Advanced technique: Generating pages

Some plugins need to generate not only HTML snippets, but entire, standalone pages (e.g., tag overviews). For this, there is the optional function `generate_pages`.

```python
def generate_pages(tags_collection, env, output_dir, site_structure, all_site_pages):
    # Logic for creating new HTML files
    pass
```

This function is called once per build. It allows you to write files directly to the `output_dir`.

## 6. Plugin-specific CSS

If your plugin requires special CSS rules, place a CSS file with the same name as your plugin in the `css/plugins/` directory (e.g., `css/plugins/quote.css`).

The generator automatically finds these files and embeds them on every page.


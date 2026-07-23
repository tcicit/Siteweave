---
author: TCI
breadcrumbs: true
date: '2000-01-01'
draft: false
featured_image: None
layout: doc
pdf_exclude: true
release_date: '2025-08-09'
tags:
- Plugin
- Documentation
title: Plugin --Syntax Highlighting
weight: 140
---

Creates a code block with syntax highlighting. Standard Markdown syntax can be used. 

Syntax: `[[code lang="python"]]print(“Hello”)[[/code]]`

## Arguments:

- **lang**: The programming language (e.g., python, javascript, html). If omitted, the function will attempt to guess the language.
- **line_numbers**: Display line numbers **true**

## Examples

### Python Code

Here is an example of a Python code block. The language is explicitly specified.

```python
import os

def list_files(directory):
    “”“Lists all files in a given directory.”‘’
    print(f“Files in ‘{directory}’:”)
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            print(f“  - {filename}”)

list_files(‘.’)
```

### JSON Code

Here is a JSON example.

```json
{
  “project”: “tci-static-site”,
  “feature”: “syntax-highlighting”,
  “status”: “implemented”,
  “awesome”: true
}
```

### Example with line_numbers:

```
[[code lang="python" line_numbers="true"]]
    def greet(name):
    print(f“Hello, {name}!”)
[[/code]]
```

[[code lang="python" line_numbers="true"]]
    def greet(name):
    print(f“Hello, {name}!”)
[[/code]]
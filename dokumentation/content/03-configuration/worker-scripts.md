---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- Configuration
- Documentation
title: Worker Scripts & Automation
weight: 50
---

[[toc min_headers="4" title="Contents"]]

Worker scripts are Python scripts located in the `workers/` directory of your project. They are designed for project-wide background tasks that are independent of editing a single file.

## Typical Use Cases

- Check all links in the project for validity (`link_checker`)
- Create a backup of the `content` folder (`backup_tool`)
- Synchronize the project with a Git repository (`git_sync`)
- Upload the finished website to a server (deployment script)

## 1. The `run(context)` Function

Each worker must have a function called `run` that accepts a `context` dictionary:

```python
# workers/my_worker.py

def run(context):
    # Extract required data from the context
    project_path = context.get('project_root')
    config = context.get('config')

    print(f"Worker running in: {project_path}")
    # ... your logic here ...
```

### The Context Dictionary

The `context` is provided by the GUI and contains:

```python
context = {
    'project_root':    '/path/to/project',
    'content_dir':     '/path/to/project/content',
    'assets_dir':      '/path/to/project/assets',
    'current_file_path': '/path/to/current/file.md',
    'editor_content':  'The current text in the editor...',
    'config':          { ... },   # The project configuration
    'source':          'gui'      # 'gui' or 'command_line'
}
```

## 2. Running Workers via Command Line

Create a `run_worker.py` file in the application root to run workers outside the GUI:

```python
# run_worker.py
import os
import sys
import argparse
import importlib.util

def main():
    parser = argparse.ArgumentParser(description="Siteweave Worker Runner")
    parser.add_argument("--project", required=True, help="Absolute path to the project directory.")
    parser.add_argument("--worker", required=True, help="Worker name (without .py), e.g. 'link_checker'.")
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f"Error: Project directory not found: {args.project}")
        sys.exit(1)

    context = {
        'project_root': args.project,
        'content_dir':  os.path.join(args.project, 'content'),
        'assets_dir':   os.path.join(args.project, 'assets'),
        'config':       {},
        'source':       'command_line'
    }

    worker_path = os.path.join(args.project, 'workers', f"{args.worker}.py")
    if not os.path.exists(worker_path):
        print(f"Error: Worker not found: {worker_path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location(args.worker, worker_path)
    worker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker_module)

    if hasattr(worker_module, 'run'):
        print(f"--- Running worker '{args.worker}' ---")
        worker_module.run(context)
        print("--- Done ---")
    else:
        print(f"Error: No 'run(context)' function found in worker '{args.worker}'.")

if __name__ == "__main__":
    main()
```

### Example Call

```bash
python run_worker.py --project "/path/to/my-project" --worker "link_checker"
```

## 3. Example: A Link Checker Worker

```python
# workers/link_checker.py
import os
import re
import requests

def run(context):
    content_dir = context.get('content_dir')
    broken_links = []

    for root, dirs, files in os.walk(content_dir):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                urls = re.findall(r'https?://[^\s\)\]\"]+', content)
                for url in urls:
                    try:
                        resp = requests.head(url, timeout=5, allow_redirects=True)
                        if resp.status_code >= 400:
                            broken_links.append((filename, url, resp.status_code))
                    except Exception as e:
                        broken_links.append((filename, url, str(e)))

    if broken_links:
        print(f"\nFound {len(broken_links)} broken link(s):")
        for filename, url, status in broken_links:
            print(f"  [{status}] {filename}: {url}")
    else:
        print("All links are valid.")
```

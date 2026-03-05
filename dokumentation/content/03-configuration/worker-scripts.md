---
author: TCI
breadcrumbs: true
date: '2025-01-10'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Dokumentation
- konfiguration
title: Worker Scripts & Automatisierung
weight: 50
---

Worker scripts are Python scripts located in the `workers` directory of your project. They are designed for project-wide tasks that are independent of editing a single file.

**Typical use cases:**
* Check all links in the project for validity (`link_checker`).
* Create a backup of the `content` folder (`backup_tool`).
* Synchronize the project with a Git repository (`git_sync`).
* Upload the finished website to a server (deployment script).

## 1. The `run(context)` function

Each worker must have a function called `run` that accepts a `context` dictionary as an argument.

```python
# workers/my_worker.py

def run(context):
    # Extract required data from the context
    project_path = context.get(‘project_root’)
    print(f“Worker is running in project {project_path}!”)
    # ... your logic goes here ...
```

This `context` is usually provided by the GUI and contains information such as project paths and configurations. However, to run the worker outside of the GUI (e.g., in an automation script), we need to create this context manually.

## 2. Run worker via command line

To call a worker directly, we need a small “runner” script. This script is responsible for loading the project configuration, creating the `context`, and running the desired worker.

Create a new file called `run_worker.py` in the root directory of your editor with the following content:

```python
# run_worker.py
import os
import sys
import argparse
import importlib.util

def main():
    parser = argparse.ArgumentParser(description=“TCI Static Site Worker Runner”)
    parser.add_argument(“--project”, required=True, help="Absolute path to the project directory.")
    parser.add_argument(“--worker”, required=True, help="Name of the worker (without .py), e.g., ‘link_checker’.")
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f“Error: Project directory not found: {args.project}”)
        sys.exit(1)

    # Load the project configuration (simplified)
    # In a real implementation, you would load config.yaml here
    project_config = {‘site_name’: ‘My Project’} 

    # Create the context
    context = {
        'project_root': args.project,
        ‘content_dir’: os.path.join(args.project, ‘content’),
        ‘assets_dir’: os.path.join(args.project, ‘assets’),
        ‘config’: project_config,
        ‘source’: ‘command_line’ # Useful to know where the call came from
    }

    worker_name = args.worker
    worker_path = os.path.join(args.project, ‘workers’, f“{worker_name}.py”)

    if not os.path.exists(worker_path):
        print(f“Error: Worker script not found: {worker_path}”)
        sys.exit(1)

    # Load and execute the worker
    try:
        spec = importlib.util.spec_from_file_location(worker_name, worker_path)
        worker_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(worker_module)

        if hasattr(worker_module, ‘run’):
            print(f“--- Running worker ‘{worker_name}’ for project ‘{os.path.basename(args.project)}’ ---”)
            worker_module.run(context)
            print(“--- Worker execution completed ---”)
        else:
    print(f“Error: No ‘run(context)’ function found in worker ‘{worker_name}’.”)

except Exception as e:
    print(f“An error occurred: {e}”)

if __name__ == “__main__”:
    main()
```

### Example 3: Automating a link checker

With the `run_worker.py` script, you can now start each worker from the command line. This is perfect for CI/CD pipelines (e.g., with GitHub Actions) or simple cron jobs.

**Example call in the terminal:**
```bash
python run_worker.py --project “/path/to/my/blog-project” --worker “link_checker”
```

This command runs the link checker for your blog project and outputs the results directly in the terminal without you having to open the GUI.
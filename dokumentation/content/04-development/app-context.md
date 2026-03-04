---
author: TCI
breadcrumbs: true
date: '2025-01-03'
draft: false
featured_image: ''
layout: full-width
release_date: '2026-01-15'
tags:
- Dokumentation
- Entwicklung
title: App Context
weight: 70
---

In this application, the “context” is not a special Qt6 object (such as a QOpenGLContext), but rather a design pattern used to exchange data between the graphical user interface (GUI) and the logic (workers/plugins).

Technically speaking, it is a simple Python dictionary (dict) that serves as a container for all necessary information.

Here is an explanation of how this context works in your app:

1. The purpose of the context
Since the worker scripts (in the workers/ folder) and plugins are standalone modules, they do not have direct access to the MainWindow or the Qt widgets (such as text fields or settings). To ensure that they still know what to work on, they are given a “package” containing all the necessary data – this is the context.

2. Where is it created? (gui/main_window.py)
When you start a tool in the menu (e.g., “Check links”), this dictionary is compiled in the run_generic_worker method:

python
# Excerpt from gui/main_window.py
context = {
    ‘content_dir’: self.content_dir,          # Where are the Markdown files located?
    ‘project_root’: self.project_root,        # Where is the main directory?
    ‘snippets_dir’: os.path.join(...),        # Where are the snippets?
    'current_file_path': self.current_file_path, # Which file is open?
    ‘editor_content’: self.editor.toPlainText(), # What is currently in the editor?
    ‘metadata’: metadata,                     # Front matter data (title, date...)
    ‘config’: self.project_config             # The config.yaml data
}
```

3. How is it transferred? (gui/workers.py)
The WorkerThread (a Qt QThread class) receives this context and stores it. Since threads run parallel to the GUI, it is important that they have a copy of the data and do not access the GUI directly (which would cause crashes).

```python
# Excerpt from gui/workers.py
class WorkerThread(QThread):
    def __init__(self, worker_path, context=None):
        # ...
        self.context = context or {}

    def run(self):
        # ...
        # The worker script is loaded and executed here.
        result = module.run(self.context)
```

4. How is it used? (e.g., workers/link_checker.py)
In the worker script itself, the context arrives as an argument in the run function. The script then fetches the data it needs:

```python
# Excerpt from workers/link_checker.py
def run(context):
    # Extract data from the context
    project_root = context.get(‘project_root’)
    content_dir = context.get(‘content_dir’)
    
    # ... Execute logic ...
```

### Summary
The “context” in your app is therefore the interface between the Qt6 interface and the pure Python logic.

Advantage: Your worker scripts remain clean and independent of Qt. Theoretically, you could also execute them via the command line, as long as you pass them the correct dictionary.
Content: It contains paths, configurations, and the current editor content.

## Explanation: Context for workers vs. plugins
In both cases, the context is a Python dictionary that serves as a “data package.” The key difference is when it is created and what information it contains.

### Context for workers (e.g., link checker)
When? It is created in the GUI (MainWindow) the moment you click on a menu item under “Project Tools” or “App Tools.”

Purpose: It serves to provide tools that access the current state of the editor or project with the necessary information.

Content (GUI-centric):

project_root, content_dir: Basic project paths.
current_file_path: The file currently open in the editor.
editor_content: The raw, unformatted text currently in the editor.
metadata: The front matter data from the panel as it is currently displayed.
config: The loaded config.yaml of the project.
Analogy: The worker context is a snapshot of the editor window in real time. It is intended for “live tools.”

### Context for plugins (in the renderer)
When? It is recreated in the SiteRenderer during the build process for each individual page that is rendered.

Purpose: It gives a plugin (e.g., [[latest_posts]]) information about the specific page it is on and about the entire website structure.

Content (page- and website-centric):


All front matter variables of the current page (e.g., title, date, tags).
page_title: The title of the current page.
current_output_path: The final URL path of the page (e.g., /blog/my-article.html).
relative_prefix: An extremely important path (./, ../, ../../), so that the plugin can create correct relative links to CSS or images, no matter how deeply nested the page is.
site_structure: The complete navigation structure of the entire website.
all_pages: A list of all pages in the project, often sorted by date.
tags_collection: A collection of all tags and the associated pages.
Analogy: The plugin context is like the building instructions for a single page, but it also contains the complete blueprint for the entire website. It is intended for content generation tools.

In summary, the worker context is for tools that interact with the editor, while the plugin context is for tools that generate content for the finished website.



#How can I add a new variable to the worker context?


Hello! That's a very good question that goes to the heart of communication between the GUI and the workers.

To add a new variable to the worker context, you need to perform two steps:

Add the variable to the context dictionary in gui/main_window.py. This is where the “data package” for the worker is put together.
Read the variable from the context dictionary in the worker script.
I'll show you an example where we add the app version (app_version) to the context.

## Step 1: Extend context in MainWindow
First, we define the version number in the __init__ method and then add it to the context in run_generic_worker.

main_window.py

```
        # Paths
        self.app_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.app_version = “1.1.0” # Example of a new variable
        if project_path:
            self.project_root = project_path
        else:
            'current_file_path': self.current_file_path,
            ‘editor_content’: self.editor.toPlainText() if self.current_file_path else None,
            ‘metadata’: metadata,
            ‘config’: self.project_config
            ‘config’: self.project_config,
            ‘app_version’: self.app_version # Add the new variable here
        }
        
        self.worker = WorkerThread(worker_path, context)
```

## Step 2: Use variable in worker

Now every worker can access this new variable. As an example, we will adapt link_checker.py so that it writes the app version to the log file.

link_checker.py

```
    “”"
    project_root = context.get(‘project_root’)
    content_dir = context.get(‘content_dir’)
    app_version = context.get(‘app_version’, ‘unknown’) # Read new variable here

    if not project_root or not content_dir:
        return _(“Error: Project context not found.”)

    log_message(_(“\n--- Starting Link Check ---”))
    log_message(_(“\n--- Starting Link Check (App Version: {version}) ---”).format(version=app_version))

    if not REQUESTS_AVAILABLE:
        log_message(_(“Warning: The ‘requests’ library is not installed. External HTTP links will be skipped.”))
```

## Summary

You can follow this pattern to pass any data from the main window to your workers. The context is the central bridge that connects the decoupled parts of your application.







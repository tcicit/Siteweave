---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
release_date: '2026-03-08'
tags:
- Getting Started
- Documentation
title: First Steps
weight: 20
---

[[toc min_headers="4" title="Contents"]]

After installing the editor, this guide walks you through creating your first website project and publishing your first page.

## 1. Create a New Project

When you start the editor for the first time (and no previous project is open), the **Project Launcher** appears.

1. Click the **"Create New Project"** button.
2. A dialog window opens — fill in the following:
   - **Project Name:** Give your project a name (e.g., "My Blog").
   - **Location:** Choose a folder on your hard drive.
   - **Template:** Select a template. For beginners, "Empty Project" or "Blog" is recommended.
3. Click **"Create"**.

The editor will automatically create the necessary folder structure (`content`, `templates`, `assets`, `config.yaml`) and open the project.

## 2. Create Your First Page

Once the main window is open, you will see the file tree on the left.

1. **Right-click** on the `content` folder (or a subfolder).
2. Select **"New File"** from the context menu.
3. Enter a file name — use lowercase letters and hyphens, e.g. `my-first-post.md`. The `.md` extension is often added automatically.
4. The new file will be created and opened directly in the editor.

## 3. Write Content

Each page consists of two parts: the **front matter** (header metadata) and the actual **content**.

### Adjust Metadata (Front Matter)

In the panel to the right of the text editor, you will see form fields for the front matter. At minimum, fill in:

- **Title:** The page heading, e.g. "Hello World".
- **Date:** Today's date is usually pre-filled.
- **Layout:** Leave at the default value for now.

### Write Text

Write your content in the large editor field using Markdown:

```markdown
This is my first post.

## A Subheading

Here is some text. I can make words **bold** or *italic*.

- List item one
- List item two
```

## 4. Preview & Generate

### Live Preview

Click the **eye icon (👁)** in the toolbar to activate the live preview. The right panel shows how your page will look in real time.

### Build Website (Render)

To turn your Markdown files into a finished HTML website:

1. Click the **"Render"** button in the toolbar.
2. The editor processes all files. Follow the progress in the log window at the bottom.
3. After completion, click **"Open in Browser"** to view your finished page.

[[infobox type="success" title="Congratulations!"]]
You have created your first static website with Siteweave. From here, explore the User Manual to learn about plugins, themes, and advanced configuration.
[[/infobox]]

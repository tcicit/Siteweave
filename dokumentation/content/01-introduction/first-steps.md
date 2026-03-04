---
author: TCI
breadcrumbs: true
date: '2025-01-01'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Einstieg
- Dokumentation
title: First Steps
weight: 20
---

After installing the editor, we will now guide you through creating your first website project and publishing your first post.

## 1. Create a New Project

When you start the editor for the first time (and no previous project is opened), you will see the **Project Launcher**.

1. Click the **"Create New Project"** button.
2. A dialog window will open:
   - **Project Name:** Give your project a name (e.g., "My Blog").
   - **Location:** Choose a folder on your hard drive where the project should be saved.
   - **Template:** Select a template. For beginners, "Empty Project" or "Blog" is recommended.
3. Click **"Create"**.

The editor will now automatically create the necessary folder structure (`content`, `templates`, `assets`, `config.yaml`) and open the project.

## 2. Create Your First Page

Once the main window is open, you will see the file tree on the left.

1. **Right-click** on the `content` folder (or a subfolder).
2. Select **"New File"** from the context menu.
3. Enter a file name.
   - **Tip:** Use lowercase letters and hyphens instead of spaces (e.g., `my-first-post.md`). The `.md` file extension is often added automatically.
4. The new file will be created and opened directly in the editor.

## 3. Write Content

Each page consists of two parts: the header section (front matter) and the actual content.

### Adjust Metadata (Front Matter)

In the panel to the right of the text editor, you will see form fields. These represent the "front matter".

- **Title:** Enter a heading here, e.g., "Hello World".
- **Date:** Today’s date is usually preselected.
- **Layout:** Leave this at the default value for now.

### Write Text

Now write your text in the large editor field. You can use Markdown:

```markdown
This is my first post.

## A Subheading
Here is some text. I can make words **bold** or *italic*.
```


## 4. Preview & Generate

### Live Preview

Click the **eye icon** (👁️) in the toolbar to activate the live preview. You will now see on the right side how your page will roughly look.

### Build Website (Render)

To turn your Markdown files into a finished HTML website:

1. Click the "Render" button or the icon in the toolbar in the toolbar.
2. The editor will now process all files. You can follow the progress in the log window (at the bottom).
3. After completion, click "Open in Browser" to view your finished page.

Congratulations! You have created your first static website.
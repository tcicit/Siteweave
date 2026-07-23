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
title: Editor & Markdown
weight: 20
---

[[toc min_headers="4" title="Contents"]]

The Siteweave editor is designed to make writing content as easy as possible. It uses **Markdown**, an easy-to-learn markup language that is converted to HTML when generating the web page. Most formatting can also be inserted directly via the **toolbar**.

## 1. Markdown Basics


```markdown
# Heading h1
## Heading h2
### Heading h3

**Bold**   
*Italic*   
`Inline code`

- Unordered item
- Unordered item
  - Nested item

1. Ordered item
2. Ordered item

[Link text](https://example.com)
![Image alt text](path/to/image.jpg)

> Blockquote text

| Header 1 | Header 2 | Header 3 |
| :------- | :------: | -------: |
| Left     | Center   | Right    |
| Content  | Content  | Content  |


---   (horizontal rule)
```


### Setting Image Size

When inserting an image via the toolbar, you can specify a width. The result:

```markdown
![App Screenshot](assets/screenshot.png){: width="50%" }
```

## 2. Using Snippets

The **Snippets** tab on the right side contains reusable text modules.

### Inserting Snippets

1. Open the **Snippets** tab on the right-hand side.
2. Find the desired snippet in the list.
3. **Drag & drop** it directly to the desired position in your text.

### Creating Your Own Snippets

1. Click the **"Open snippet folder"** icon in the toolbar.
2. Your file manager opens in the snippet directory.
3. Create a new text file, e.g. `my-signature.txt`.
4. Write the Markdown code you want to reuse and save the file.
5. The new snippet will appear in the list immediately.

## 3. Using Plugins (Shortcodes)

In addition to standard Markdown, the editor supports **plugins** (shortcodes) to insert advanced features like info boxes, galleries, and dynamic content. The syntax uses double square brackets `[[...]]`.

### Simple Plugin

```markdown
[[date]]
```

### Plugin with Parameters

```markdown
[[infobox type="warning" title="Attention"]]
```

### Block Plugin (with Content)

Some plugins wrap a content area — they have an opening and a closing tag:

```markdown
[[infobox type="warning" title="Important Note"]]
This is the content of the box. You can use **Markdown** here.
[[/infobox]]
```

#### Live Example — Infobox Plugin

[[infobox type="warning" title="Warning"]]
This is a **warning box**. Use it to highlight important cautions for your readers.
[[/infobox]]


### Image Plugin Examples

The `[[image]]` plugin offers far more control than standard Markdown images:

```markdown
# Image with shadow and border
[[image path="assets/photo.jpg" shadow="true" border="true"]]

# Image aligned right with caption and lightbox
[[image path="assets/photo.jpg" align="right" width="300px" caption="A caption" lightbox="true"]]

# Image with rounded corners
[[image path="assets/banner.jpg" radius="15px"]]

# Image with a link
[[image path="assets/logo.png" href="https://example.com" target="_blank"]]
```
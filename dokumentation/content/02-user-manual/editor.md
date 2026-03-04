---
author: TCI
breadcrumbs: true
date: '2025-01-04'
draft: false
featured_image: None
layout: doc
release_date: '2026-01-15'
tags:
- Benutzerhandbuch
- Dokumentation
title: Editor & Markdown
weight: 20
---

The Sitewave is designed to make writing content as easy as possible. It uses **Markdown**, an easy-to-learn markup language that is converted to HTML when generating the web page.

## 1. Markdown Basics

You don't need to be a programmer to use Markdown. Here are the most important commands. Many of them can also be inserted directly via the **toolbar** at the top of the editor.

### Text Formatting

- **Bold:** Enclose the text with two asterisks: `**Bold text**`
- *Italics:* Enclose the text with an asterisk: `*Italic text*`
- Code: Enclose code snippets with backticks (grave accents) see the cheat sheet below. 

### Headings

Use hash symbols (`#`) at the beginning of a line to create headings. The number of hash symbols determines the level.

```markdown

# Heading 1 (page title - only once per page!)
## Heading 2 (main chapter)
### Heading 3 (subchapter)

```

### Lists

**Unordered list:**
Use hyphens `-` or asterisks `*`.

```
 - Point 1
 - Point 2
   - Indented subpoint
   - Indented subpoint
```

**Ordered list:**
Use numbers followed by a period.

```markdown
1. First step
2. Second step
```

### Links

A link consists of the displayed text in square brackets and the URL in parentheses.

`Click me`

### Tables

Tables are created using vertical bars `|` and hyphens `-`.

```markdown
| Header 1 | Header 2 |
| ------ | ------ |
| Content | Content |
```

## 2. Using snippets

On the right side of the editor, you will find the **“Snippets”** tab. Snippets are reusable text modules that can save you a lot of typing (e.g., for complex tables or recurring layout elements).

### Inserting snippets

1.  Open the **Snippets** tab on the right-hand side (if hidden).
2.  Find the desired snippet in the list.
3.  Drag it with the mouse (**drag & drop**) directly to the desired location in your text in the editor.

### Creating your own snippets

You can create your own snippets:

1.  Click on the **“Open snippet folder”** icon in the toolbar (usually a folder symbol).
2.  Your operating system's file manager will open in the snippet directory.
3.  Create a new text file there (e.g., `my-signature.txt`).
4.  Write the Markdown code you want to reuse and save the file.
5.  The new snippet will now appear in the list in the editor.

## 3. Using plugins (shortcodes)

In addition to standard Markdown, the editor also supports **plugins** (also called shortcodes) to insert advanced features such as info boxes, galleries, or dynamic content.

The syntax always uses double square brackets `[[...]]`.

### Simple plugins

A simple plugin looks like this:

`[[date]]` (Inserts the current date, for example)

### Plugins with parameters

Many plugins accept settings (parameters):

`[[infobox type="warning" title="Attention"]]`

### Plugins with content

Some plugins enclose a text area. They have an opening and a closing tag (with `/`):

```markdown
[[infobox type="warning" title="Warning"]]
This is the content of the box.
[[/infobox]]
```

#### This is an example of the “infobox” plugin
[[infobox type="warning" title="Note"]]
This is the content of the box.
[[/infobox]]

#### Example of the image plugin

Simple image with shadow and frame:

```markdown
[[image src="assets/bild.jpg" shadow="true" border="true"]]
```

Image aligned to the right with caption and lightbox:

```markdown
[[image src="assets/foto.jpg" align="right" width="300px" caption="A beautiful photo" lightbox="true"]]
```

Image with rounded corners and overlay:

```markdown
[[image src="assets/banner.jpg" radius="15px" overlay="rgba(0,0,0,0.3)"]]
```

Image with its own CSS class

```markdown
[[image src="assets/screenshot.png" class="my-special-frame shadow-effect"]]
```

Image with link to Google (opens in a new tab):

```markdown
[[image src="assets/logo.png" href="https://google.com" target="_blank"]]

```

Image as internal link:

```markdown
[[image src="assets/button.png" href="/contact.html"]]
```

## Markdown cheat sheet

```
## Headers

# This is a Heading h1
## This is a Heading h2
###### This is a Heading h6

## Emphasis

*This text will be italic*  
_This will also be italic_

**This text will be bold**  
__This will also be bold__

_You **can** combine them_

## Lists

### Unordered

* Item 1
* Item 2
* Item 2a
* Item 2b
    * Item 3a
    * Item 3b

### Ordered

1. Item 1
2. Item 2
3. Item 3
    1. Item 3a
    2. Item 3b

## Images

![This is an alt text.](/image/sample.webp “This is a sample image.”)

## Links

You may be using [Markdown Live Preview](https://markdownlivepreview.com/).

## Blockquotes

> Markdown is a lightweight markup language with plain-text-formatting syntax, created in 2004 by John Gruber with Aaron Swartz.
>
>> Markdown is often used to format readme files, for writing messages in online discussion forums, and to create rich text using a plain text editor.

## Tables

| Left columns  | Right columns |
| ------------- |:------------ -:|
| left foo      | right foo     |
| left bar      | right bar     |
| left baz      | right baz     |

## Blocks of code

 ```
 let message = ‘Hello world’;
 alert(message);
 ```

## Inline code

`This web site is using `markedjs/marked`.

```

---
title: Plugin Documentation
---

# Available Plugins

This documentation was automatically generated from the plugin source codes.

## Table of Contents

<div style="column-count: 2; column-gap: 2rem; -webkit-column-count: 2; -moz-column-count: 2;">
<ul style="margin-top: 0; padding-left: 20px;">
<li><a href="#box">box</a></li>
<li><a href="#breadcrumbs">breadcrumbs</a></li>
<li><a href="#code">code</a></li>
<li><a href="#color">color</a></li>
<li><a href="#csv_table">csv_table</a></li>
<li><a href="#date">date</a></li>
<li><a href="#details">details</a></li>
<li><a href="#gallery">gallery</a></li>
<li><a href="#grid">grid</a></li>
<li><a href="#image">image</a></li>
<li><a href="#include">include</a></li>
<li><a href="#infobox">infobox</a></li>
<li><a href="#latest_posts">latest_posts</a></li>
<li><a href="#list_dir">list_dir</a></li>
<li><a href="#obfuscate">obfuscate</a></li>
<li><a href="#search">search</a></li>
<li><a href="#tags">tags</a></li>
<li><a href="#toc">toc</a></li>
</ul>
</div>

---

## box {: id='box'}
Creates a box with an optional title and background color.

**Syntax:**

```
[[box title="Title" bgcolor="#f0f0f0"]]Content...[[/box]]
Parameters:
  - title: Optional title of the box.
  - bgcolor: Optional background color of the box (e.g. "#f0f0f" or "lightblue").
```

**Parameters:**

- `bgcolor` (automatically detected)
- `title` (automatically detected)

**Examples:**

```markdown
[[box title="Important Information" bgcolor="#FF0000"]]
  This is important information in a red box.
  [[/box]]
    Creates a box with the title "Important Information" and a red background.
  [[box bgcolor="lightgreen"]]
  This is a box with a green background without a title.
  [[/box]]
    Creates a box with a green background without a title.
Result:
    HTML code for the box with the specified content and styles.
```

---

## breadcrumbs {: id='breadcrumbs'}
Generates breadcrumb navigation based on the site structure.

**Syntax:**

```
[[breadcrumbs]]
Parameters: None
```

**Examples:**

```markdown
[[breadcrumbs]]
    Inserts breadcrumb navigation at this position.
Result:
    HTML code for the breadcrumb navigation.
```

---

## code {: id='code'}
Generates code blocks with Pygments highlighting.

**Syntax:**

```
[[code lang="python"]]Content...[[/code]]

Parameters:
  - lang: The language of the code (e.g. "python", "javascript").
```

**Parameters:**

- `lang` (automatically detected)

**Examples:**

```markdown
[[code lang="python"]]
     print("Hallo Welt!")
  [[/code]]
    Generates a code block with Pygments highlighting for "python".
    
Result:
    <div class="codehilite"><pre><code>print("Hallo Welt!")</code></pre></div>
```

---

## color {: id='color'}
Highlights the enclosed text with the specified text and background colors.

**Syntax:**

```
[[color text="red" bg="#f0f0f0"]]Text[[/color]]

Parameters:
  - text: Text color (e.g. "red", "#ff0000", "rgb(255,0,0)").
  - bg: Background color (e.g. "#f0f0f0", "lightblue", "rgba(255,255,255,0.5)").
```

**Parameters:**

- `bg` (automatically detected)
- `text` (automatically detected)

**Examples:**

```markdown
[[color text="blue" bg="#e0e0ff"]]Blue text on light blue background.[[/color]]
    Highlights the text with blue font color and light blue background.
  [[color text="#ffffff" bg="black"]]White text on black background.[[/color]]
    Highlights the text with white font color and black background.
    
Result:
    <span style="color: blue; background-color: #e0e0ff;">Blue text on light blue background.</span>
```

---

## csv_table {: id='csv_table'}
Reads a CSV file and renders it as an HTML table.

**Syntax:**

```
[[csv_table src="daten.csv" delimiter=";" header="true" class="my-table"]]
Parameters:
  - src: Path to the CSV file (relative to the markdown file).
  - delimiter: Delimiter character (Default: ","). Use "\t" for tab.
  - header: "true" (Default) or "false". Whether the first row contains headers.
  - class: CSS class for the `<table>` element (Default: "csv-table").
  - caption: Optional title for the table.
```

**Parameters:**

- `caption` (automatically detected)
- `class` (automatically detected)
- `delimiter` (automatically detected)
- `header` (automatically detected)
- `src` (automatically detected)

**Examples:**

```markdown
[[csv_table src="data.csv" delimiter=";" header="true" class="my-table" caption="My Data"]]
    Reads "data.csv" using ";" as a delimiter, treats the first row as headers, applies the CSS class "my-table", and adds a caption "My Data".
Result:
    HTML code for the table displaying the CSV data.
```

---

## date {: id='date'}
Returns the current date in the specified format.

**Syntax:**

```
[[date format="%d.%m.%Y"]]
Parameters:
  - format: The format for the date. Default: "%d.%m.%Y".
```

**Parameters:**

- `format` (automatically detected)

**Examples:**

```markdown
[[date format="%A, %d. %B %Y"]] 
    Returns the current date in the format "Monday, 24. December 2024".
  [[date]]
    Returns the current date in the default format "24.12.2024".  
Result:
    24.12.2024
```

---

## details {: id='details'}
Creates a collapsible content block (`<details>`).

**Syntax:**

```
[[details summary="Summary Title"]]Content...[[/details]]
Parameters:
  - summary: The text displayed in the summary. Default: "Details".
```

**Parameters:**

- `summary` (automatically detected)

**Examples:**

```markdown
[[details summary="More Information"]]
  Here is more information that can be expanded.
  [[/details]]
    Creates a collapsible area with the summary "More Information".

Result:
    HTML code for the `<details>` block with the specified content.
```

---

## gallery {: id='gallery'}
Creates an image gallery with lightbox. Uses compressed images for thumbnails and links to originals.

**Syntax:**

```
1. Directory: [[gallery path="path/to/dir" layout="grid" cols="3" ratio="4:3" gap="1rem"]]
  2. Markdown Images: [[gallery layout="masonry" cols="4" ratio="original"]] !Alt [[/gallery]]
Parameters:
  - path: Path to the directory containing images (relative to markdown file).
  - layout: "grid" (Default) or "masonry".
  - cols: Number of columns in grid layout. Default: "3".
  - ratio: Aspect ratio for grid layout. Options: "original", "1:1", "4:3" (Default), "3:2", "16:9".
  - gap: Gap between images. Default: "1rem".
```

**Parameters:**

- `cols` (automatically detected)
- `gap` (automatically detected)
- `layout` (automatically detected)
- `path` (automatically detected)
- `ratio` (automatically detected)

**Examples:**

```markdown
[[gallery path="images/gallery1" layout="grid" cols="3" ratio="4:3" gap="1rem"]]
    Creates a gallery from the directory "images/gallery1" with a 3-column grid in 4:3 ratio.

  [[gallery layout="masonry" cols="4" ratio="original"]]
      ![Image 1](images/pic1-compressed.jpg)
      ![Image 2](images/pic2-compressed.jpg)
      ![Image 3](images/pic3-compressed.jpg)
      ![Image 4](images/pic4-compressed.jpg)
  [[/gallery]]
    Creates a gallery from the images specified in the content in masonry layout.
    
Result:
    HTML code for the gallery with lightbox functionality.
```

---

## grid {: id='grid'}
Creates a grid layout with a configurable number of columns.

**Syntax:**

```
[[grid cols="3"]]Content...[[/grid]]
Parameters:
  - cols: Number of columns in the grid. Default: "3".
```

**Parameters:**

- `cols` (automatically detected)

**Examples:**

```markdown
[[grid cols="4"]]
  Content for the first column.
  Content for the second column.
  Content for the third column.
  Content for the fourth column.
  [[/grid]]
    Creates a 4-column grid with the specified content.
Result:
    <div class="plugin-grid" style="grid-template-columns: repeat(4, 1fr);">
        Content for the first column.
        ...
    </div>
```

---

## image {: id='image'}
Advanced image plugin with many styling options.

**Syntax:**

```
[[image src="bild.jpg" width="300px" height="200px" align="center" border="true" shadow="true" radius="10px" caption="Mein Bild" lightbox="true" overlay="rgba(0,0,0,0.3)" alt="Alternativtext" class="custom-class" href="https://example.com" target="_blank" zoom="true" opacity="0.8"]]
Parameters:
  - src: Path to the image (relative to the markdown file). (Required)
  - width: Width of the image (e.g. "300px", "50%").
  - height: Height of the image (e.g. "200px", "auto").
  - align: Image alignment: "left", "center", "right". Default: "center".
  - border: Border around the image. "true" for default border, or CSS value (e.g. "2px solid #000").
  - shadow: Shadow effect. "true" for default shadow, or CSS value.
  - radius: Border radius. CSS value (e.g. "10px").
  - caption: Image caption.
  - lightbox: "true" for lightbox functionality. Default: "false".
  - overlay: Background color for the overlay. CSS value.
  - alt: Alternative text for the image. Default: "Image".
  - class: Additional CSS class for the image.
  - href: Link for the image.
  - target: Target attribute for the link (e.g. "_blank").
  - zoom: "true" for zoom effect. Default: "false".
  - opacity: Opacity of the image (e.g. "0.8").
```

**Parameters:**

- `align` (automatically detected)
- `alt` (automatically detected)
- `border` (automatically detected)
- `caption` (automatically detected)
- `class` (automatically detected)
- `height` (automatically detected)
- `href` (automatically detected)
- `lightbox` (automatically detected)
- `opacity` (automatically detected)
- `overlay` (automatically detected)
- `radius` (automatically detected)
- `shadow` (automatically detected)
- `src` (automatically detected)
- `target` (automatically detected)
- `width` (automatically detected)
- `zoom` (automatically detected)

**Examples:**

```markdown
[[image src="images/pic1.jpg" width="300px" height="200px" align="center" border="true" shadow="true" radius="10px" caption="Mein Bild" lightbox="true" overlay="rgba(0,0,0,0.3)" alt="Alternativtext" class="custom-class" href="https://example.com" target="_blank" zoom="true" opacity="0.8"]]
    Creates a centered image with the specified styles, a caption, lightbox functionality, and a link.
Result:
   - HTML code for the image with the specified attributes and styles.
```

---

## include {: id='include'}
Reads a file and returns its content.

**Syntax:**

```
[[include src="file.md"]]
Parameters:
  - src: Path to the file (relative to the markdown file).
```

**Parameters:**

- `src` (automatically detected)

**Examples:**

```markdown
[[include src="chapter1/intro.md"]]
    Reads the content of "intro.md" in the subdirectory "chapter1" relative to the current file.
Result:
    The content of the specified file is inserted at this position.
    <!-- Include Plugin: 'src' attribute missing or invalid. Must be a path string (e.g. src="file.md"). -->
    <!-- Include Plugin: 'current_page_path' could not be determined in context. -->
    <!-- Include Plugin: File not found at './chapter1/intro.md'. -->
    <!-- Include Plugin: Error reading file: ... -->
```

---

## infobox {: id='infobox'}
Creates an infobox with different styles and an optional title.

**Syntax:**

```
[[infobox type="warning" title="Attention!"]]Content...[[/infobox]]
Parameters:
  - type: The type of the infobox. Possible values: "info", "warning", "error", "success". Default: "info".
  - title: Optional title of the infobox.
```

**Parameters:**

- `title` (automatically detected)
- `type` (automatically detected)

**Examples:**

```markdown
[[infobox type="warning" title="Attention!"]]
  This is a warning.
  [[/infobox]]
    Creates a yellow warning infobox with the title "Attention!".
  [[infobox type="success"]]
  This is a success message.
  [[/infobox]]
    Creates a green success infobox without a title.
    
Result:
    <div class="infobox infobox-warning">
        <div class="infobox-title">Attention!</div>
        <div class="infobox-content">
    
                    <p>This is a warning.</p>
        </div>
    </div>
```

---

## latest_posts {: id='latest_posts'}
Zeigt eine Liste der neuesten Blog-Beiträge an, mit verschiedenen Filter- und Anzeigeoptionen.

**Syntax:**

```
[[latest_posts count="5" sort="desc" tags="tag1,tag2" tag_mode="all" show_excerpt="true" excerpt_length="30" show_image="true"]]
```

**Parameters:**

- count: Anzahl der anzuzeigenden Beiträge. Standard: 5
  - sort: Sortierreihenfolge der Beiträge. Mögliche Werte: "asc" oder "desc". Standard: "desc"
  - tags: Kommagetrennte Liste von Tags zum Filtern der Beiträge. Standard: keine Filterung
  - tag_mode: Modus für die Tag-Filterung. Mögliche Werte: "all" (alle Tags müssen übereinstimmen) oder "any" (mindestens ein Tag muss übereinstimmen). Standard: "all"
  - show_excerpt: Ob ein Auszug des Beitragsinhalts angezeigt werden soll. Mögliche Werte: "true" oder "false". Standard: "false"
  - excerpt_length: Anzahl der Wörter im Auszug, falls show_excerpt auf "true" gesetzt ist. Standard: 30
  - show_image: Ob das Beitragsbild angezeigt werden soll, falls vorhanden. Mögliche Werte: "true" oder "false". Standard: "false"

**Examples:**

```markdown
[[latest_posts count="3" sort="desc" tags="python,programmierung" tag_mode="any" show_excerpt="true" excerpt_length="20" show_image="true"]]
    Zeigt die 3 neuesten Beiträge an, die entweder das Tag "python" oder "programmierung" haben, mit einem 20-Wörter-Auszug und dem Beitragsbild.
  [[latest_posts count="5" sort="asc" show_excerpt="false" show_image="false"]]
    Zeigt die 5 ältesten Beiträge ohne Auszug und ohne Bild an.
Ergebnis:
    HTML-Liste der neuesten Beiträge entsprechend den angegebenen Parametern.
```

---

## list_dir {: id='list_dir'}
Lists all Markdown files in a directory.

**Syntax:**

```
[[list_dir path="subdir" layout="table" sort="date" show_date="true" date_format="%d.%m.%Y" exclude="file1.md,file2.md" recursive="false" class="custom-class"]]

Parameters:
  - path: Path to the directory (relative to the Markdown file).
    - If not specified, the directory of the current file is used.
  - layout: "list" (default) or "table". Determines the layout of the listing.
  - sort: "title" (default), "date", "path" or "weight". Determines the sorting of pages.
  - show_date: "true" or "false". Determines whether the date of the pages should be displayed.
  - date_format: Format for the date if show_date is "true". Default: Raw format from frontmatter.
  - exclude: Comma-separated list of filenames to exclude.
  - recursive: "true" or "false" (default). Whether to search subdirectories.
  - class: Additional CSS classes for the list or table.
```

**Parameters:**

- `class` (automatically detected)
- `date_format` (automatically detected)
- `exclude` (automatically detected)
- `layout` (automatically detected)
- `path` (automatically detected)
- `recursive` (automatically detected)
- `show_date` (automatically detected)
- `sort` (automatically detected)

**Examples:**

```markdown
[[list_dir path="blog" layout="table" sort="date" show_date="true" date_format="%d.%m.%Y" exclude="draft.md" recursive="false" class="my-list"]]
    Lists all Markdown files in the "blog" directory as a table sorted by date, shows the date in Day.Month.Year format,
    excludes the file "draft.md", and does not search subdirectories.

  [[list_dir layout="list" sort="title" show_date="false"]]
    Lists all Markdown files in the current directory as a simple list sorted by title, without showing the date.

Result:
    HTML code for the list or table of Markdown files in the specified directory.
```

---

## obfuscate {: id='obfuscate'}
Obfuscates sensitive data like emails, phone numbers, and addresses to protect against bots.

**Syntax:**

```
[[obfuscate email="info@example.com"]]
  [[obfuscate phone="+49 123 456"]]
  [[obfuscate address="Sample Street 1"]]
  [[obfuscate]]Any text[[/obfuscate]]

Parameters:
  - email: Email address (creates a mailto link).
  - phone: Phone number (creates a tel link).
  - address: Address or text (only encoded).
  - text: Alias for address.
  - label: Optional link text (for email/phone).
  - subject: Optional subject (for email).
```

**Parameters:**

- `address` (automatically detected)
- `email` (automatically detected)
- `label` (automatically detected)
- `phone` (automatically detected)
- `subject` (automatically detected)
- `text` (automatically detected)

**Examples:**

```markdown
[[obfuscate email="info@example.com"]]
  [[obfuscate phone="+49 123 456"]]
  [[obfuscate address="Sample Street 1"]]
  [[obfuscate]]This is some sensitive text.[[/obfuscate]]
     Obfuscates the provided email, phone number, address, or any text between the tags to make it less accessible to bots.  

Result:
    HTML entities encoded string or link.
```

---

## search {: id='search'}
Adds a client-side search function. The plugin renders a search input and the necessary JavaScript to search the website.

**Syntax:**

```
[[search]]
[[search placeholder="Suchen..." show_excerpt="true" excerpt_length="150" show_filter="false" paginate="false" per_page="10" pagination_window="2"]]


Parameters:    

- placeholder (optional): The placeholder text for the search input. Default: "Search..."
- show_excerpt (optional): "true" or "false", whether to show a short excerpt of the content. Default: "true"
- excerpt_length (optional): The length of the excerpt in characters. Default: 150
- show_filter (optional): "true" or "false", whether to show a dropdown menu for the search scope (Title, Tags, Content). Default: "false"
- paginate (optional): "true" or "false", whether to paginate results. Default: "false"
- per_page (optional): Number of results per page if pagination is active. Default: 10
- pagination_window (optional): Number of page links shown around the current page. Default: 2
    

Example:
    [[search placeholder="Search site..." show_excerpt="false"]]
```

**Parameters:**

- `excerpt_length` (automatically detected)
- `paginate` (automatically detected)
- `pagination_window` (automatically detected)
- `per_page` (automatically detected)
- `placeholder` (automatically detected)
- `show_excerpt` (automatically detected)
- `show_filter` (automatically detected)

---

## tags {: id='tags'}
Generates a tag cloud or a list.

**Syntax:**

```
[[tags type="list"]] 
    [[tags type="cloud"]]

Parameters:
  - type: 'list' (default) or 'cloud'
  - exclude: Comma-separated list of tags to exclude (e.g. "draft,entwurf")
  - min_count: Only show tags with at least this number of posts (e.g. min_count=3)
  - limit: Only show the top N tags (e.g. limit=10)
  - random: "true" for random order (e.g. random=true)
  - sort_by: "count" for sorting by count (e.g. sort_by=count)
  - group: "true" for grouping by initial letter (e.g. group=true)
  - cols: Number of columns for the list view (e.g. cols=3)
  - show_count: "true" to show the number of posts next to the tag (e.g. show_count=true)
  - color: "random" for random colors in the tag cloud (e.g. color=random)
```

**Parameters:**

- `color` (automatically detected)
- `cols` (automatically detected)
- `exclude` (automatically detected)
- `group` (automatically detected)
- `limit` (automatically detected)
- `min_count` (automatically detected)
- `random` (automatically detected)
- `show_count` (automatically detected)
- `sort_by` (automatically detected)
- `type` (automatically detected)

**Examples:**

```markdown
[[tags type="cloud" min_count=2 limit=20 random=true color=random]]
  [[tags type="list" exclude="draft,entwurf" sort_by="count" show_count=true cols=2]]

Result:
  - For the cloud: A visual tag cloud where font size and optionally color reflect the number of posts.
  - For the list: An alphabetically sorted list of tags, optionally with columns and the number of posts next to each tag.
```

---

## toc {: id='toc'}
Inserts the [TOC] marker for the Python-Markdown 'toc' extension.

Extended Functionality:
Can automatically hide the table of contents based on the number of headers
(for short articles).

**Syntax:**

```
[[toc title="Inhalt" depth="3" min_headers="4"]]

Parameters:
- title (str): Title of the table of contents.
- depth (int): Maximum depth of headers. Default: 6.
- min_headers (int): Minimum number of headers required to show the TOC.
```

**Parameters:**

- `min_headers` (automatically detected)

**Examples:**

```markdown
- [[toc title="Inhalt" depth="3"]]
  Inserts a table of contents with the title "Inhalt" and includes headers up to level 3.
- [[toc min_headers="5"]]
  Inserts a table of contents only if there are at least 5 headers in the article.  
 

Result:
The [TOC] marker or an empty string.
```

---

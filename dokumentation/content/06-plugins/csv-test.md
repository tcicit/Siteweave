---
author: TCI
breadcrumbs: true
date: '2025-12-19'
draft: false
featured_image: None
layout: doc
pdf_exclude: true
release_date: '2025-12-19'
tags:
- Plugin
- Documentation
title: Pluggin — CSV Import
weight: 150
---

Import tabular data from a `.csv` file directly into a Markdown page:

```markdown
[[csv_table file="assets/data/products.csv" header="true"]]
```

### Parameters

| Parameter | Description |
| :--- | :--- |
| **src** | Path to the CSV file (relative to project root) |
| **header** | `true` / `false` — treat first row as table header |
| **delimiter** | Column delimiter character (default: `,`) |
| **class** | Custom CSS class for the generated table |
| **caption** | Optional table title. |

### Example CSV File

```csv

Product,Version,Status,Notes
Siteweave,0.2,Active,Desktop editor
PyQt6,6.6,Stable,GUI framework
Jinja2,3.1,Stable,Template engine
WeasyPrint,60,Stable,PDF generation

```

```markdown
[[csv file="assets/data/dependencies.csv" header="true" class="dependencies-table"]]
```

[[csv_table src="_assets/preise.csv"  delimiter=";" caption="Our current price list" header="true" class="dependencies-table"]]


[[infobox type="info" title="Tip: Table Readability"]]
For tables with many columns, consider splitting data into multiple smaller tables with clear headings, or using the CSV plugin to keep large datasets in a separate file outside your Markdown content.
[[/infobox]]
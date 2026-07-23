---
author: TCI
breadcrumbs: true
date: '2025-12-18'
draft: false
featured_image: None
layout: doc
pdf_exclude: true
release_date: '2025-12-18'
tags:
- Dokumentation
- Plugins
title: Plugin —  Breadcrumbs
weight: 170
---


Generates the data structure for the breadcrumbs based on the current path and the entire site structure.
Format of the returned data:

The first breadcrumb is always “Home” and points to the homepage.

It is also possible to use the `[[breadcrumbs]]` shortcode on the homepage;
in this case, only “Home” is returned.

## Example

`[[breadcrumbs]]`

[[breadcrumbs]]
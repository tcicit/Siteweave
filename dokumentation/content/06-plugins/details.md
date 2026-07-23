---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
pdf_exclude: true
release_date: '2026-03-08'
tags:
- Plugin
- Documentation
title: Plugin — Details (Accordion)
weight: 100
---

Description: Creates a collapsible content block (`<details>`).

## Syntax: `[[details summary="Summary Title"]]Content...[[/details]]`

## Parameters:
- **summary**: The text displayed in the summary. Default: "Details".

## Example

[[details summary="Lorem ipsum Title"]]

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.

[[/details]]



## Use Cases

- **FAQ pages** — list questions as collapsed sections
- **Long reference pages** — hide advanced details behind accordions
- **Step-by-step guides** — reveal steps one at a time
- **Spoilers** — hide solutions or answers until the reader is ready
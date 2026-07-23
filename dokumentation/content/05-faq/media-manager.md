---
author: TCI
breadcrumbs: true
date: '2026-06-03'
draft: false
featured_image: ../../assets/images/media-manager.jpg
layout: doc
release_date: '2026-06-03'
tags:
- FAQ
- Media Manager
title: Media Manager
weight: 40
---

## Media Manager Screen

![media-manager.jpg](../../assets/images/media-manager.jpg)

## Media Manager Configuration

![konfiguration-media-manager.jpg](../../assets/konfiguration-media-manager.jpg)

To open files in external applications (such as Flatpak applications like GIMP or Inkscape on Linux) directly from Siteweave, configure external editors in your settings.

Flatpak applications run in a sandbox, so launching them with a file argument uses `flatpak run <App-ID>`.

Ensure Flatpaks are installed with their default IDs. If you want to add other custom editors, find their application IDs by running `flatpak list` in your terminal.

| Name                           | Application ID        |
| ------------------------------ | --------------------- |
| GNU Image Manipulation Program | `org.gimp.GIMP`       | 
| Inkscape                       | `org.inkscape.Inkscape` |
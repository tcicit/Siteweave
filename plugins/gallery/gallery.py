import re
import uuid
import os
import html


IMAGE_MD_RE = re.compile(r'^\s*!\[(.*?)\]\((.*?)\)\s*$', re.MULTILINE) # Regex zum Finden von Markdown-Bildern im Inhalt

COMPRESSED_SUFFIX = "-compressed" # Muss mit dem Suffix im Kompressionsskript übereinstimmen

def handle(content, args, context, env):
    """
    Plugin Name: Gallery
    Description: Creates an image gallery with lightbox. Uses compressed images for thumbnails and links to originals.
    Syntax:
      1. Directory: [[gallery path="path/to/dir" layout="grid" cols="3" ratio="4:3" gap="1rem"]]
      2. Markdown Images: [[gallery layout="masonry" cols="4" ratio="original"]] !Alt [[/gallery]]
    Parameters:
      - path: Path to the directory containing images (relative to markdown file).
      - layout: "grid" (Default) or "masonry".
      - cols: Number of columns in grid layout. Default: "3".
      - ratio: Aspect ratio for grid layout. Options: "original", "1:1", "4:3" (Default), "3:2", "16:9".
      - gap: Gap between images. Default: "1rem".
    Examples:
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
    """
    gallery_path_arg = args.get('path')
    image_data = [] # Wird eine Liste von Dictionaries: {'alt': ..., 'thumb': ..., 'original': ...}


    if gallery_path_arg:
        # --- Modus 1: Galerie aus Verzeichnis erstellen ---
        base_dir = os.path.dirname(context.get('current_page_path', ''))
        full_gallery_path = os.path.join(base_dir, gallery_path_arg)

        if not os.path.isdir(full_gallery_path):
            return f'<p style="color: red;"><b>Fehler im gallery Plugin:</b> Das Verzeichnis <code>{gallery_path_arg}</code> wurde nicht gefunden.</p>'

        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        try:
            for filename in sorted(os.listdir(full_gallery_path)):
                if not filename.lower().endswith(image_extensions) or COMPRESSED_SUFFIX in filename:
                    continue

                original_rel_path = os.path.join(gallery_path_arg, filename).replace(os.path.sep, '/')
                base, ext = os.path.splitext(filename)
                
                # Prüfe, ob eine komprimierte Version für die Vorschau existiert
                compressed_filename = f"{base}{COMPRESSED_SUFFIX}{ext}"
                compressed_full_path = os.path.join(full_gallery_path, compressed_filename)
                
                thumb_rel_path = original_rel_path
                if os.path.exists(compressed_full_path):
                    thumb_rel_path = os.path.join(gallery_path_arg, compressed_filename).replace(os.path.sep, '/')

                alt_text = html.escape(base.replace('-', ' ').replace('_', ' ').capitalize())

                image_data.append({
                    'alt': alt_text,
                    'thumb': thumb_rel_path,
                    'original': original_rel_path
                })


        except Exception as e:
            return f'<p style="color: red;"><b>Fehler im gallery Plugin:</b> Ein Fehler ist aufgetreten: {e}</p>'

    elif content:
        # --- Modus 2: Galerie aus Markdown-Inhalt erstellen ---
        md_images = IMAGE_MD_RE.findall(content)
        for alt, thumb_src in md_images:
            base, ext = os.path.splitext(thumb_src)
            original_src = thumb_src
            if base.endswith(COMPRESSED_SUFFIX):
                original_src = base[:-len(COMPRESSED_SUFFIX)] + ext
            image_data.append({'alt': alt, 'thumb': thumb_src, 'original': original_src})

    if not image_data:
        return f'<p style="color: orange;"><b>Info im gallery Plugin:</b> Keine Bilder zum Anzeigen gefunden. {gallery_path_arg} / {content} </p>'

    # Parameter auslesen mit Standardwerten
    layout = str(args.get('layout', 'grid')).lower()
    cols = str(args.get('cols', '3'))
    ratio = str(args.get('ratio', '4:3')).lower()
    gap = str(args.get('gap', '1rem'))

    # Validierung der Parameter
    if layout not in ['grid', 'masonry']:
        layout = 'grid'
    
    valid_ratios = ['original', '1:1', '4:3', '3:2', '16:9']
    if ratio not in valid_ratios:
        ratio = '4:3' # Fallback auf einen sicheren Wert

    # Eindeutige ID für diese Galerie-Instanz
    gallery_id = str(uuid.uuid4())[:8]

    # CSS-Klassen und Style-Attribute für den Container
    container_classes = [f"gallery-layout-{layout}"]
    if layout == 'grid':
        container_classes.append(f"gallery-ratio-{ratio.replace(':', '-')}")
    
    container_style = f"--gallery-cols: {cols}; --gallery-gap: {gap};"

    grid_html = []
    overlays_html = []

    for i, img in enumerate(image_data):
        unique_id = f"lightbox-{gallery_id}-{i}"
        alt_text = img['alt']
        thumb_src = img['thumb']
        original_src = img['original']

        # Vorschaubild im Raster/Masonry
        if layout == 'grid' and ratio != 'original':
            thumb_html = (
                f'<a href="#{unique_id}" class="gallery-thumb">'
                f'  <img src="{thumb_src}" alt="{alt_text}" loading="lazy">'
                f'</a>'
            )
        else: # Masonry oder 'original' ratio
            thumb_html = (
                f'<a href="#{unique_id}">'
                f'  <img class="gallery-item" src="{thumb_src}" alt="{alt_text}" loading="lazy">'
                f'</a>'
            )
        
        grid_html.append(thumb_html)

        # Lightbox-Overlay (standardmässig versteckt)
        overlays_html.append(f'<div class="lightbox-target" id="{unique_id}">')
        
        # Navigation zum vorigen/nächsten Bild
        prev_id = f"lightbox-{gallery_id}-{i-1}" if i > 0 else None
        next_id = f"lightbox-{gallery_id}-{i+1}" if i < len(image_data) - 1 else None
        
        if prev_id:
            overlays_html.append(f'    <a href="#{prev_id}" class="lightbox-nav prev" aria-label="Voriges Bild">&#10094;</a>')
        if next_id:
            overlays_html.append(f'    <a href="#{next_id}" class="lightbox-nav next" aria-label="Nächstes Bild">&#10095;</a>')

        overlays_html.append(f'    <a href="#_" class="lightbox-close" aria-label="Schliessen">&times;</a>')
        overlays_html.append(f'    <img class="lightbox-image" src="{original_src}" alt="{alt_text}">')
        if alt_text:
            overlays_html.append(f'    <figcaption class="lightbox-caption">{alt_text}</figcaption>')
        overlays_html.append('</div>')

    final_grid_html = (
        f'<div class="{" ".join(container_classes)}" style="{container_style}">\n'
        + '\n'.join(grid_html) 
        + '\n</div>'
    )
    final_overlays_html = '<div class="lightbox-container">\n' + '\n'.join(overlays_html) + '\n</div>'

    return final_grid_html + final_overlays_html
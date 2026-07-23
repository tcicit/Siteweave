def handle(content, args, context, env):
    """
    Plugin Name: Image
    Description: Advanced image plugin with many styling options.
    Syntax: [[image src="bild.jpg" width="300px" height="200px" align="center" border="true" shadow="true" radius="10px" caption="Mein Bild" lightbox="true" overlay="rgba(0,0,0,0.3)" alt="Alternativtext" class="custom-class" href="https://example.com" target="_blank" zoom="true" opacity="0.8"]]
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
    Examples:
      [[image src="images/pic1.jpg" width="300px" height="200px" align="center" border="true" shadow="true" radius="10px" caption="Mein Bild" lightbox="true" overlay="rgba(0,0,0,0.3)" alt="Alternativtext" class="custom-class" href="https://example.com" target="_blank" zoom="true" opacity="0.8"]]
        Creates a centered image with the specified styles, a caption, lightbox functionality, and a link.
    Result:
       - HTML code for the image with the specified attributes and styles.
    """
    
    # 1. Quelle ist Pflicht
    src = args.get('src')
    if not src:
        return '<div style="color:red; border:1px solid red; padding:10px;">Image Plugin Error: "src" attribute is missing.</div>'

    # 2. Argumente auslesen
    width = args.get('width')
    height = args.get('height')
    align = args.get('align', 'center')
    border = args.get('border')
    shadow = args.get('shadow')
    radius = args.get('radius')
    caption = args.get('caption')
    lightbox = str(args.get('lightbox', 'false')).lower() == 'true'
    overlay = args.get('overlay')
    alt = args.get('alt', caption if caption else 'Image')
    css_class = args.get('class')
    href = args.get('href')
    target = args.get('target')
    zoom = str(args.get('zoom', 'false')).lower() == 'true'
    opacity = args.get('opacity')

    # 3. Styles zusammenbauen
    style_list = []
    
    if width:
        style_list.append(f"width: {width}")
    if height:
        style_list.append(f"height: {height}")
    if radius:
        style_list.append(f"border-radius: {radius}")
    if opacity:
        style_list.append(f"opacity: {opacity}")
        
    # Rahmen
    if border:
        if str(border).lower() == 'true':
            style_list.append("border: 1px solid #ddd")
        elif str(border).lower() != 'false':
            style_list.append(f"border: {border}")
            
    # Schatten
    if shadow:
        if str(shadow).lower() == 'true':
            style_list.append("box-shadow: 0 4px 8px rgba(0,0,0,0.15)")
        elif str(shadow).lower() != 'false':
            style_list.append(f"box-shadow: {shadow}")

    style_attr = f' style="{"; ".join(style_list)}"' if style_list else ''

    # 4. Container Klassen
    classes = ["plugin-image"]
    if align in ['left', 'center', 'right']:
        classes.append(f"align-{align}")
    if css_class:
        classes.append(css_class)
    if zoom:
        classes.append("zoom-effect")
    if overlay:
        classes.append("has-overlay")
    
    # 5. HTML generieren
    html = f'<figure class="{" ".join(classes)}">'
    
    # Bild-Tag
    img_html = f'<img src="{src}" alt="{alt}"{style_attr}>'
    
    # Overlay Logik (benötigt Wrapper)
    if overlay:
        # Radius auch auf Overlay anwenden, damit es nicht übersteht
        overlay_radius = radius if radius else "0"
        img_html = f'<div class="img-wrapper" style="position: relative; display: inline-block;">{img_html}<div class="overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: {overlay}; pointer-events: none; border-radius: {overlay_radius};"></div></div>'

    # Lightbox Wrapper
    if lightbox:
        html += f'<a href="{src}" class="glightbox" data-description="{alt}">{img_html}</a>'
    elif href:
        target_attr = f' target="{target}"' if target else ''
        html += f'<a href="{href}"{target_attr}>{img_html}</a>'
    else:
        html += img_html

    # Caption
    if caption:
        html += f'<figcaption>{caption}</figcaption>'

    html += '</figure>'
    
    return html
import os
import html
import frontmatter


def handle(content, args, context, env):
    """
    Plugin Name: List Dir

    Description: Lists all Markdown files in a directory.

    Syntax: [[list_dir path="subdir" layout="table" sort="date" order="desc" show_date="true" date_format="%d.%m.%Y" exclude="file1.md,file2.md" recursive="false" class="custom-class"]]

    Parameters:
      - path: Path to the directory (relative to the Markdown file).
        - If not specified, the directory of the current file is used.
      - layout: "list" (default) or "table". Determines the layout of the listing.
      - sort: "title" (default), "date", "path" or "weight". Determines the sorting of pages.
      - order: "asc" or "desc". Determines the sort order. Default is "asc" for most modes, but "desc" (newest first) for "date".
      - show_date: "true" or "false". Determines whether the date of the pages should be displayed.
      - date_format: Format for the date if show_date is "true". Default: Raw format from frontmatter.
      - exclude: Comma-separated list of filenames to exclude.
      - recursive: "true" or "false" (default). Whether to search subdirectories.
      - class: Additional CSS classes for the list or table.
    
    Examples:
      [[list_dir path="blog" sort="title" order="desc"]]
        Lists all pages in the "blog" directory, sorted by title from Z to A.
    
      [[list_dir sort="date" order="asc"]]
        Lists pages sorted by date, oldest first.
    
    Result:
        HTML code for the list or table of Markdown files in the specified directory.

    """
    
    # 1. Pfade aus dem Kontext holen
    content_dir = context.get('content_dir')
    # Fallback falls content_dir nicht im Context ist
    if not content_dir and context.get('project_root'):
        content_dir = os.path.join(context.get('project_root'), 'content')

    current_page_path = context.get('current_page_path')
    relative_prefix = context.get('relative_prefix', './')

    if not content_dir:
        return '<div style="color:red; border:1px solid red; padding:5px;">Error: content_dir missing in context</div>'

    # 2. Zielverzeichnis bestimmen
    target_arg = args.get('path', '')
    if not isinstance(target_arg, str):
        target_arg = ''
    target_arg = target_arg.strip()
    
    if target_arg:
        # Pfad ist relativ zum Content-Verzeichnis
        # Entferne führende Slashes um os.path.join nicht zu verwirren
        target_arg = target_arg.lstrip('/')
        target_dir = os.path.join(content_dir, target_arg)
    elif current_page_path:
        # Kein Pfad angegeben -> Verzeichnis der aktuellen Datei
        if os.path.isfile(current_page_path):
            target_dir = os.path.dirname(current_page_path)
        else:
            target_dir = current_page_path
    else:
        return '<div style="color:red; border:1px solid red; padding:5px;">Error: Cannot determine target directory</div>'

    if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        return f'<div style="color:orange; border:1px solid orange; padding:5px;">Directory not found: {html.escape(target_arg or "current")}</div>'

    # 3. Dateien sammeln
    recursive_arg = args.get('recursive', 'false')
    if isinstance(recursive_arg, bool):
        recursive = recursive_arg
    else:
        recursive = str(recursive_arg).lower() in ('true', 'yes', '1')
    md_files = []

    # show_date Argument verarbeiten
    show_date_arg = args.get('show_date', 'false')
    if isinstance(show_date_arg, bool):
        show_date = show_date_arg
    else:
        show_date = str(show_date_arg).lower() in ('true', 'yes', '1')

    # date_format Argument verarbeiten
    date_format = args.get('date_format')
    if not isinstance(date_format, str):
        date_format = None

    # exclude Argument verarbeiten
    exclude_arg = args.get('exclude', '')
    if not isinstance(exclude_arg, str):
        exclude_arg = ''
    excludes = [x.strip() for x in exclude_arg.split(',') if x.strip()]

    if recursive:
        for root, dirs, files in os.walk(target_dir):
            for f in files:
                if f.lower().endswith(('.md', '.markdown')):
                    md_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(target_dir):
            full_path = os.path.join(target_dir, f)
            if os.path.isfile(full_path) and f.lower().endswith(('.md', '.markdown')):
                md_files.append(full_path)

    # 4. Metadaten extrahieren
    pages = []
    for file_path in md_files:
        # Aktuelle Seite überspringen
        if current_page_path and os.path.abspath(file_path) == os.path.abspath(current_page_path):
            continue

        # Exclude check
        if os.path.basename(file_path) in excludes:
            continue

        try:
            post = frontmatter.load(file_path)
            title = post.metadata.get('title', os.path.basename(file_path))
            date_obj = post.metadata.get('date')
            try:
                weight = int(post.metadata.get('weight', 0))
            except (ValueError, TypeError):
                weight = 0
            
            # Datum verarbeiten (Sortierung vs Anzeige)
            sort_date = str(date_obj) if date_obj else ''
            display_date = sort_date
            
            if date_obj and date_format and hasattr(date_obj, 'strftime'):
                try:
                    display_date = date_obj.strftime(date_format)
                except Exception:
                    pass # Fallback auf Standard-String
            
            # Relativen Pfad für Link berechnen
            # Wir berechnen den Pfad relativ zum content_dir und setzen .html an
            rel_path = os.path.relpath(file_path, content_dir)
            base, _ = os.path.splitext(rel_path)
            html_path = base + ".html"
            
            # Windows Backslashes korrigieren
            html_path = html_path.replace(os.path.sep, '/')
            
            # Link zusammenbauen: relative_prefix führt zum Root, dann Pfad zur Datei
            href = f"{relative_prefix}{html_path}"
            
            pages.append({
                'title': title,
                'date': sort_date,
                'display_date': display_date,
                'path': file_path,
                'href': href,
                'weight': weight
            })
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # 5. Sortieren
    sort_mode = str(args.get('sort', 'title')).lower()
    order_arg = str(args.get('order', 'default')).lower()

    if sort_mode == 'date':
        # Default for date is descending (newest first)
        reverse = not (order_arg == 'asc')
        pages.sort(key=lambda x: x['date'], reverse=reverse)
    elif sort_mode == 'path':
        reverse = (order_arg == 'desc')
        pages.sort(key=lambda x: x['path'], reverse=reverse)
    elif sort_mode == 'weight':
        reverse = (order_arg == 'desc')
        pages.sort(key=lambda x: (x['weight'], x['title']), reverse=reverse)
    elif sort_mode == 'title':
        reverse = (order_arg == 'desc')
        pages.sort(key=lambda x: x['title'], reverse=reverse)
    else:
        return f'<div style="color:red; border:1px solid red; padding:5px;">Error: Invalid sort mode "{html.escape(sort_mode)}". Valid modes: title, date, path, weight</div>'

    if not pages:
        return '<p><em>No pages found.</em></p>'

    # 6. HTML generieren
    layout = args.get('layout', 'list')
    if not isinstance(layout, str):
        layout = 'list'
    
    # Zusätzliche CSS-Klassen verarbeiten
    custom_class = args.get('class', '')
    if not isinstance(custom_class, str):
        custom_class = ''
    custom_class = html.escape(custom_class.strip())
    
    # show_date ist bereits als Boolean verarbeitet, aber wir müssen sicherstellen, dass es nur in der Tabelle oder Liste angezeigt wird, wenn es tatsächlich aktiviert ist.
    if layout.lower() == 'table':
        table_classes = f'list-dir-table {custom_class}'.strip()
        output = [f'<table class="{table_classes}">']
        output.append('<thead><tr><th>Title</th>')
        if show_date:
            output.append('<th>Date</th>')
        output.append('</tr></thead><tbody>')
                
        for page in pages:
            output.append('<tr>')
            output.append(f'<td><a href="{page["href"]}">{html.escape(page["title"])}</a></td>')
            if show_date:
                output.append(f'<td>{html.escape(page["display_date"])}</td>')
            output.append('</tr>')
        output.append('</tbody></table>')
    else:
        ul_classes = f'list-dir {custom_class}'.strip()
        output = [f'<ul class="{ul_classes}">']
        for page in pages:
            date_html = ""
            if show_date and page['display_date']:
                date_html = f' <span class="list-dir-date">({html.escape(page["display_date"])})</span>'
            output.append(f'<li><a href="{page["href"]}">{html.escape(page["title"])}</a>{date_html}</li>')
        output.append('</ul>')

    return '\n'.join(output)


def generate_pages(tags_collection, env, output_dir, site_structure, all_site_pages):
    pass

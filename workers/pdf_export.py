import os
import markdown
from datetime import datetime
from core.i18n import _

'''
Worker-Skript, das die aktuell geöffnete Markdown-Datei als PDF exportiert.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für die PDF-Generierung befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen werden kann, sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.

'''


name = _("Export as PDF")
description = _("Exports the currently open file as PDF.")
category = "project"
hidden = False

def run(context):
    content = context.get('editor_content')
    file_path = context.get('current_file_path')
    metadata = context.get('metadata', {})
    config = context.get('config', {})
    project_root = context.get('project_root')
    pdf_config = config.get('pdf_export', {})

    if not content or not file_path:
        return _("Error: No file opened.")

    try:
        from weasyprint import HTML, CSS
    except ImportError:
        return _("Error: 'weasyprint' not installed. Please run 'pip install weasyprint'.")

    # --- Get settings with defaults ---
    page_size = pdf_config.get('page_size', 'A4')
    orientation = pdf_config.get('orientation', 'portrait')
    margin_top = pdf_config.get('margin_top', '2cm')
    margin_right = pdf_config.get('margin_right', '2cm')
    margin_bottom = pdf_config.get('margin_bottom', '2cm')
    margin_left = pdf_config.get('margin_left', '2cm')
    show_cover = pdf_config.get('show_cover_page', True)
    show_page_numbers = pdf_config.get('show_page_numbers', True)
    show_print_date = pdf_config.get('show_print_date', True)
    custom_css_path = pdf_config.get('custom_css_path', '')

    # 1. Deckblatt generieren (optional)
    cover_html = ""
    if show_cover:
        title = metadata.get('title', _('Untitled'))
        author = metadata.get('author', '')
        date = metadata.get('date', '')
        
        cover_html = f"""
        <div class="cover-page">
            <h1>{title}</h1>
            <p class="author">{author}</p>
            <p class="date">{date}</p>
        </div>
        """

    # 2. Inhalt konvertieren
    html_body = markdown.markdown(content, extensions=['tables', 'fenced_code', 'attr_list'])
    
    full_html = cover_html + html_body
    
    # 3. Dynamisches CSS für ein ansprechendes PDF-Layout
    css_parts = [f'''
        @page {{
            size: {page_size} {orientation};
            margin-top: {margin_top};
            margin-right: {margin_right};
            margin-bottom: {margin_bottom};
            margin-left: {margin_left};
    ''']

    # Footer für Seitenzahlen und Datum
    if show_page_numbers or show_print_date:
        css_parts.append('''
            @bottom-center {
                content: "";
                display: block;
                border-top: 1px solid #ccc;
                width: 100%;
                vertical-align: top;
            }
        ''')
        if show_page_numbers:
            css_parts.append('''
            @bottom-right {
                content: "''' + _('Page') + ''' " counter(page);
                font-size: 9pt;
                color: #666;
            }
            ''')
        if show_print_date:
            print_date = datetime.now().strftime('%d.%m.%Y')
            css_parts.append(f'''
            @bottom-left {{
                content: "''' + _('Printed on') + f''' {print_date}";
                font-size: 9pt;
                color: #666;
            }}
            ''')
    
    css_parts.append("}") # close @page

    # Allgemeine Body-Styles
    css_parts.append('''
        body { font-family: sans-serif; line-height: 1.6; font-size: 11pt; color: #333; }
        h1, h2, h3 { color: #000; margin-top: 1.5em; }
        h1 { font-size: 24pt; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
        code { background: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 0.9em; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; margin: 1em 0; }
        img { max-width: 100%; height: auto; margin: 1em 0; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        blockquote { border-left: 4px solid #ccc; margin-left: 0; padding-left: 16px; color: #666; font-style: italic; }
        a { color: #0066cc; text-decoration: none; }
    ''')

    # Deckblatt-Styles (optional)
    if show_cover:
        css_parts.append('''
        .cover-page { page-break-after: always; text-align: center; padding-top: 30%; }
        .cover-page h1 { font-size: 36pt; border: none; margin-bottom: 1em; color: #000; }
        .cover-page .author { font-size: 18pt; margin-bottom: 0.5em; }
        .cover-page .date { font-size: 14pt; color: #666; }
        ''')

    # Custom CSS laden
    if custom_css_path:
        # Pfad auflösen (relativ zum Projekt-Root)
        if not os.path.isabs(custom_css_path) and project_root:
            full_css_path = os.path.join(project_root, custom_css_path)
        else:
            full_css_path = custom_css_path
            
        if os.path.exists(full_css_path):
            try:
                with open(full_css_path, 'r', encoding='utf-8') as f:
                    css_parts.append(f"\n/* Custom CSS from {os.path.basename(full_css_path)} */\n")
                    css_parts.append(f.read())
            except Exception as e:
                return _("Error loading custom CSS: {e}").format(e=e)

    css = CSS(string="".join(css_parts))

    # 4. Ausgabepfad bestimmen
    export_dir = pdf_config.get('export_path')
    
    if export_dir:
        # Wenn Pfad relativ ist, auf Projekt-Root beziehen
        if not os.path.isabs(export_dir) and project_root:
            export_dir = os.path.join(project_root, export_dir)
        
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except OSError as e:
                return _("Error: Could not create export directory: {e}").format(e=e)
        
        filename = os.path.basename(file_path)
        output_path = os.path.join(export_dir, os.path.splitext(filename)[0] + ".pdf")
    else:
        # Standard: Gleicher Ordner wie Quelldatei
        output_path = os.path.splitext(file_path)[0] + ".pdf"

    # Base URL ist wichtig, damit relative Bilder gefunden werden
    base_url = os.path.dirname(file_path)

    try:
        # PDF generieren
        HTML(string=full_html, base_url=base_url).write_pdf(output_path, stylesheets=[css])
        return _("PDF successfully created: {filename}").format(filename=os.path.basename(output_path))
    except Exception as e:
        return _("Error creating PDF: {e}").format(e=e)
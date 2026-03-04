import os
import markdown
import re
import frontmatter
from datetime import datetime
import unicodedata
from core.i18n import _

'''
Worker-Skript, das alle Markdown-Dateien im Content-Ordner zusammenführt und als ein PDF-Handbuch exportiert.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für die PDF-Generierung befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen werden kann, sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.
'''

# --- Worker Metadata ---
name = _("Export Project PDF")
description = _("Merges all Markdown files into a single PDF handbook.")
category = "project"
hidden = False

def slugify(value):
    """
    Converts a string into a URL-friendly slug.
    :param value: The string to slugify.
    :return: The slugified string.
    """
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

def run(context):
    project_root = context.get('project_root')
    content_dir = context.get('content_dir')
    config = context.get('config', {})
    pdf_config = config.get('pdf_export', {})
    # Lese die gewünschte Tiefe aus der Konfiguration, Standard ist 3 (H1, H2, H3)
    toc_depth = int(pdf_config.get('toc_depth', 3))
    
    if not project_root or not content_dir:
        return _("Error: Project context missing.")

    try:
        from weasyprint import HTML, CSS
    except ImportError:
        return _("Error: 'weasyprint' not installed. Please run 'pip install weasyprint'.")

    # 1. Alle Markdown-Dateien sammeln und sortieren
    md_files = []
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith(('.md', '.markdown')):
                full_path = os.path.join(root, file)
                # Relativer Pfad für Sortierung (damit Ordnerstruktur beachtet wird)
                rel_path = os.path.relpath(full_path, content_dir)
                md_files.append((rel_path, full_path))
    
    # Sortieren: index.md immer zuerst im Ordner, dann alphabetisch
    def sort_key(item):
        path = item[0].replace('\\', '/')
        parts = path.split('/')
        # Trick: index.md bekommt ein Leerzeichen vorangestellt, damit es oben sortiert wird
        if parts[-1].lower() in ['index.md', 'index.markdown']:
            parts[-1] = ' ' + parts[-1]
        return parts

    md_files.sort(key=sort_key)

    # 2. Inhalte zusammenfügen
    full_markdown = ""
    
    # Deckblatt-Daten
    site_name = config.get('site_name', 'Documentation')
    site_logo = config.get('site_logo')
    # Erlaube Override durch pdf_export Konfiguration
    if pdf_config.get('cover_logo'):
        site_logo = pdf_config.get('cover_logo')

    date_str = datetime.now().strftime('%d.%m.%Y')

    full_html_content = []

    # Deckblatt HTML
    if pdf_config.get('show_cover_page', True):
        logo_html = ""
        if site_logo:
            logo_path = os.path.join(project_root, site_logo)
            if os.path.exists(logo_path):
                import urllib.parse
                logo_url = 'file://' + urllib.parse.quote(logo_path)
                logo_html = f'<img src="{logo_url}" class="cover-logo" alt="Logo">'

        full_html_content.append(f"""
        <div class="cover-page">
            {logo_html}
            <h1 class="cover-title">{site_name}</h1>
            <p class="cover-subtitle">{_('Handbuch / Dokumentation')}</p>
            <p class="cover-date">{date_str}</p>
        </div>
        <div style="page-break-after: always;"></div>
        """)

    # Temporäre Speicher für Kapitel und TOC
    chapters_content = []
    toc_entries = []
    # Regex, um Überschriften von Level 2 bis 6 zu finden
    HEADING_RE = re.compile(r'^(#{2,6})\s+(.*)')
    
    for rel_path, full_path in md_files:
        try:
            post = frontmatter.load(full_path)
            
            # Seite überspringen, wenn pdf_exclude: true im Frontmatter gesetzt ist
            if post.metadata.get('pdf_exclude', False):
                continue
            
            # Titel ermitteln (Frontmatter > H1 > Dateiname)
            title = post.metadata.get('title')
            if not title:
                for line in post.content.splitlines():
                    if line.strip().startswith('# '):
                        title = line.strip()[2:]
                        break
            if not title:
                title = os.path.splitext(os.path.basename(full_path))[0].replace('-', ' ').replace('_', ' ').title()
            
            # Anker für die Datei selbst (Kapitel-Start)
            file_anchor = slugify(rel_path)
            
            # Überschriften im Inhalt für das Inhaltsverzeichnis extrahieren und Anker hinzufügen
            sub_headings = []
            new_content_lines = []
            for line in post.content.splitlines():
                match = HEADING_RE.match(line.strip())
                if match:
                    level = len(match.group(1))
                    if level <= toc_depth:
                        heading_title = match.group(2).strip()
                        anchor = slugify(f"{rel_path}-{heading_title}")
                        sub_headings.append({'level': level, 'title': heading_title, 'anchor': anchor})
                        # Markdown-Zeile mit ID für den Anker neu schreiben
                        new_content_lines.append(f"{match.group(1)} {heading_title} {{id=\"{anchor}\"}}")
                        continue
                new_content_lines.append(line)
            
            toc_entries.append({'title': title, 'anchor': file_anchor, 'sub_headings': sub_headings})
                
            text = "\n".join(new_content_lines)
            # Bilder-Pfade korrigieren (müssen absolut sein für WeasyPrint)
            def replace_img_path(match):
                alt = match.group(1)
                url = match.group(2)
                if not url.startswith(('http', 'https', 'data:')):
                    # Absoluten Pfad berechnen
                    abs_img_path = os.path.abspath(os.path.join(os.path.dirname(full_path), url))
                    # Für WeasyPrint als file:// URL formatieren
                    import urllib.parse
                    url = 'file://' + urllib.parse.quote(abs_img_path)
                return f'![{alt}]({url})'
            
            text = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img_path, text)

            # Markdown zu HTML
            html = markdown.markdown(text, extensions=['tables', 'fenced_code', 'attr_list'])
            
            # Container für Kapitel mit Hauptüberschrift
            chapters_content.append(f'<div class="chapter">')
            chapters_content.append(f'<h1 id="{file_anchor}">{title}</h1>')
            chapters_content.append(html)
            chapters_content.append('</div>')
            # Seitenumbruch nach jedem Kapitel
            chapters_content.append('<div style="page-break-after: always;"></div>')

        except Exception as e:
            print(f"Fehler bei {rel_path}: {e}")

    # Inhaltsverzeichnis (TOC) generieren und einfügen
    if toc_entries:
        full_html_content.append(f'<div class="toc">')
        full_html_content.append(f'<h1>{_("Table of Contents")}</h1>')
        full_html_content.append('<ul>')
        for entry in toc_entries:
            full_html_content.append(f'<li><a href="#{entry["anchor"]}">{entry["title"]}</a></li>')
            if entry['sub_headings']:
                for sub in entry['sub_headings']:
                    # Einrückung basierend auf der Überschriftenebene (H2, H3, ...)
                    padding = (sub['level'] - 1) * 20  # 20px pro Ebene
                    full_html_content.append(f'<li class="toc-sub-item" style="padding-left: {padding}px;"><a href="#{sub["anchor"]}">{sub["title"]}</a></li>')
        full_html_content.append('</ul>')
        full_html_content.append('</div>')
        full_html_content.append('<div style="page-break-after: always;"></div>')

    # Kapitel hinzufügen
    full_html_content.extend(chapters_content)

    final_html = "\n".join(full_html_content)

    # 3. PDF Generieren
    css_string = """
    @page {
        size: A4;
        margin: 2cm;
        @bottom-center {
            content: counter(page);
            font-size: 10pt;
            color: #666;
        }
    }
    @page :first {
        @bottom-center {
            content: none;
        }
    }
    body { font-family: sans-serif; line-height: 1.5; font-size: 11pt; }
    img { max-width: 100%; height: auto; }
    pre { background: #f5f5f5; padding: 10px; border-radius: 5px; white-space: pre-wrap; }
    code { font-family: monospace; background: #f5f5f5; padding: 2px 4px; }
    h1, h2, h3 { color: #333; page-break-after: avoid; }
    h1 { border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 0; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #eee; }
    
    /* Deckblatt Styles */
    .cover-page { text-align: center; padding-top: 20%; }
    .cover-title { font-size: 36pt; border: none; margin-bottom: 0.5em; }
    .cover-subtitle { font-size: 18pt; color: #666; }
    .cover-date { margin-top: 2em; color: #999; }
    .cover-logo { max-height: 150px; margin-bottom: 2em; }
    
    /* TOC Styles */
    .toc ul { list-style-type: none; padding-left: 0; }
    .toc li { margin-bottom: 0.5em; border-bottom: 1px dotted #ccc; }
    .toc li.toc-sub-item { border-bottom: none; margin-bottom: 0.2em; font-size: 0.9em; }
    .toc a { text-decoration: none; color: #000; display: flex; justify-content: space-between; padding: 4px 0; }
    .toc a::after { content: target-counter(attr(href), page); }
    """

    # Export Pfad
    export_path = pdf_config.get('export_path', 'pdf_export')
    if not os.path.isabs(export_path):
        export_path = os.path.join(project_root, export_path)
    os.makedirs(export_path, exist_ok=True)

    filename = f"{site_name.replace(' ', '_')}_Manual.pdf"
    output_file = os.path.join(export_path, filename)

    try:
        html_obj = HTML(string=final_html, base_url=project_root)
        css_obj = CSS(string=css_string)
        html_obj.write_pdf(output_file, stylesheets=[css_obj])
        return _("PDF Manual created: {path}").format(path=output_file)
    except Exception as e:
        return _("Error creating PDF: {e}").format(e=e)
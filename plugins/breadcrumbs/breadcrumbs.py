import os
from jinja2 import TemplateNotFound

def _generate_breadcrumbs_data(current_output_path, site_structure, relative_prefix):
    """
    Generiert die Datenstruktur für die Breadcrumbs basierend auf dem aktuellen Pfad
    und der gesamten Seitenstruktur.
    :param current_output_path: Der aktuelle Ausgabepfad der Seite (z.B. 'kategorie/unterkategorie/seite.html')
    :param site_structure: Die gesamte Seitenstruktur als verschachteltes Diktat.
    :param relative_prefix: Der relative Prefix für URLs (z.B. '', 'subdirect/')
    :return: Liste im Format [{'title': 'Titel', 'url': 'URL'}, ...]    
    :
    Format der zurückgegebenen Daten:
    breadcrumbs = [] # Liste von Diktaten mit 'title' und 'url' Feldern 

    Die erste Breadcrumb ist immer "Home" und zeigt auf die Startseite.

    Es ist auch möglich [[breadcrumbs]] Shortcode. in der Startseite zu verwenden,
    in diesem Fall wird nur "Home" zurückgegeben.   

    """
    # Erzeuge Home-URL (zeigt explizit auf die Index-Datei, damit Klicks
    # auch bei file://-Ansicht die HTML-Datei öffnen und nicht den Dateimanager)
    def _join_url(prefix, path):
        if not prefix:
            return path
        p = prefix.rstrip('/')
        return f"{p}/{path}"

    home_url = _join_url(relative_prefix, 'index.html')
    breadcrumbs = [{'title': 'Home', 'url': home_url}]

    clean_path = current_output_path.strip('/')
    if not clean_path or clean_path == 'index.html':
        return breadcrumbs  # Nur "Home" für die Startseite

    path_segments = clean_path.split('/')
    current_structure_level = site_structure

    for i, segment in enumerate(path_segments):
        is_last_segment = (i == len(path_segments) - 1)
        # Baut den relativen Pfad für die URL schrittweise auf
        # z.B. 'kategorie', dann 'kategorie/unterkategorie', etc.
        current_relative_path = '/'.join(path_segments[:i+1])

        if is_last_segment and segment.endswith('.html'):
            # Letztes Segment ist die HTML-Datei (die aktuelle Seite)
            page_title = segment.replace('.html', '').replace('-', ' ').replace('_', ' ').title()  # Fallback-Titel

            # Finde den echten Titel aus der Seitenstruktur
            if '__files' in current_structure_level:
                for page_info in current_structure_level['__files']:
                    if page_info['path'] == current_output_path:
                        page_title = page_info['title']
                        break

            # Die URL für die letzte Seite ist der Pfad zur Datei selbst
            url = _join_url(relative_prefix, current_relative_path)
            breadcrumbs.append({'title': page_title, 'url': url})
        else:
            # Dies ist ein Verzeichnispfad-Segment
            dir_title = segment.replace('-', ' ').replace('_', ' ').title()  # Fallback-Titel

            # Versuche, einen besseren Titel für das Verzeichnis zu finden (z.B. aus _index.md)
            if segment in current_structure_level:
                # Prüfe, ob es eine Index-Datei mit Titel in diesem Verzeichnis gibt
                if '__files' in current_structure_level[segment]:
                    for page_info in current_structure_level[segment]['__files']:
                        if page_info['path'].endswith(f'{segment}/index.html'):
                            dir_title = page_info.get('title', dir_title)
                            break
                # Gehe eine Ebene tiefer in der Struktur für die nächste Iteration
                current_structure_level = current_structure_level[segment]
            else:
                # Wenn der Pfad in der Struktur nicht existiert, brechen wir ab.
                # Die bisherigen Breadcrumbs werden trotzdem zurückgegeben.
                break

            # Verzeichnispfade zeigen auf die jeweilige Index-Datei, damit
            # sie beim Anklicken die erwartete HTML-Seite öffnen.
            url = _join_url(relative_prefix, f"{current_relative_path}/index.html")
            breadcrumbs.append({'title': dir_title, 'url': url})

    return breadcrumbs

def handle(content, args, context, env):
    """
    Plugin Name: Breadcrumbs
    Description: Generates breadcrumb navigation based on the site structure.
    Syntax: [[breadcrumbs]]
    Parameters: None
    Examples:
      [[breadcrumbs]]
        Inserts breadcrumb navigation at this position.
    Result:
        HTML code for the breadcrumb navigation.
    """
    # Prüfe, ob Breadcrumbs im Frontmatter explizit deaktiviert wurden
    if context.get('breadcrumbs') is False:
        return ""

    current_output_path = context.get('current_output_path')
    site_structure = context.get('site_structure')
    # Hole den relativen Prefix. Wenn er './' ist, ersetze ihn durch einen leeren String,
    # um saubere, relative Pfade von der Wurzel aus zu gewährleisten.
    relative_prefix_raw = context.get('relative_prefix', './')
    relative_prefix = '' if relative_prefix_raw == './' else relative_prefix_raw

    if not current_output_path or not site_structure:
        return ""

    breadcrumbs_data = _generate_breadcrumbs_data(current_output_path, site_structure, relative_prefix)

    try:
        template = env.get_template('breadcrumbs.html')
        return template.render(breadcrumbs=breadcrumbs_data, relative_prefix=relative_prefix)
    except TemplateNotFound:
        return f'<p><em>[Breadcrumbs-Plugin: Template "breadcrumbs.html" nicht gefunden]</em></p>'
    except Exception as e:
        print(f"FEHLER im Breadcrumbs-Plugin (handle): {e}")
        return f'<p><em>[Fehler beim Rendern der Breadcrumbs]</em></p>'

def generate_pages(tags_collection, env, output_dir, site_structure, all_site_pages):
    """
    Das Breadcrumbs-Plugin generiert keine eigenen Seiten, daher ist diese Funktion leer.
    """
    pass
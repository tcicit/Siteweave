import os
import urllib.parse

def resolve_image_url(url, current_file_path, project_root, mode='absolute'):
    """
    Zentrale Logik zur Auflösung von Bildpfaden für verschiedene Export-Modi.
    
    Modes:
    - 'absolute': Rückgabe des absoluten Pfads im Dateisystem.
    - 'weasyprint': Rückgabe einer file:// URL für WeasyPrint.
    - 'markdown_relative': Rückgabe eines Pfads relativ zum Projekt-Root (für MD-Export).
    """
    if url.startswith(('http://', 'https://', 'data:', 'mailto:')):
        return url

    # Absoluten Pfad auf der Festplatte ermitteln
    if url.startswith('/'):
        abs_path = os.path.normpath(os.path.join(project_root, url.lstrip('/')))
    else:
        # current_file_path ist der absolute Pfad zur .md Quelldatei
        abs_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), url))

    if mode == 'weasyprint':
        return 'file://' + urllib.parse.quote(abs_path)
    
    if mode == 'markdown_relative':
        try:
            rel_to_root = os.path.relpath(abs_path, project_root)
            # Wir nehmen an, dass der Export in einem Unterordner liegt (z.B. markdown_exports/)
            # Daher gehen wir eine Ebene nach oben um den Pfad wieder korrekt aufzulösen.
            return os.path.join("..", rel_to_root).replace(os.path.sep, '/')
        except ValueError:
            return url
            
    return abs_path

def get_image_replacer(current_file_path, project_root, mode='absolute'):
    """Gibt eine Callback-Funktion für re.sub zurück."""
    def replacer(match):
        return f'![{match.group(1)}]({resolve_image_url(match.group(2), current_file_path, project_root, mode)})'
    return replacer
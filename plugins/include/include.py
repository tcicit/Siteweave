import os
import frontmatter

def handle(content, args, context, env):
    """
    Plugin Name: Include
    Description: Reads a file and returns its content.
    Syntax: [[include src="file.md"]]
    Parameters:
      - src: Path to the file (relative to the markdown file).
    Examples:
      [[include src="chapter1/intro.md"]]
        Reads the content of "intro.md" in the subdirectory "chapter1" relative to the current file.
    Result:
        The content of the specified file is inserted at this position.
        <!-- Include Plugin: 'src' attribute missing or invalid. Must be a path string (e.g. src="file.md"). -->
        <!-- Include Plugin: 'current_page_path' could not be determined in context. -->
        <!-- Include Plugin: File not found at './chapter1/intro.md'. -->
        <!-- Include Plugin: Error reading file: ... -->
    """
    include_rel_path = args.get('src')
    # Prüfe explizit, ob der Wert ein String ist, um Fehler bei Flags wie [[include src]] zu vermeiden.
    if not isinstance(include_rel_path, str) or not include_rel_path:
        return "<!-- Include Plugin: 'src'-Attribut fehlt oder ist ungültig. Es muss ein Pfad als String sein (z.B. src=\"datei.md\"). -->"

    current_page_path = context.get('current_page_path')
    if not current_page_path:
        return "<!-- Include Plugin: 'current_page_path' konnte nicht im Kontext ermittelt werden. -->"

    # Löst den Pfad relativ zum Verzeichnis der aktuellen Datei auf
    base_dir = os.path.dirname(current_page_path)
    full_include_path = os.path.normpath(os.path.join(base_dir, include_rel_path))

    if not os.path.exists(full_include_path):
        return f"<!-- Include Plugin: Datei nicht gefunden unter '{full_include_path}'. -->"

    try:
        post = frontmatter.load(full_include_path)
        return post.content
    except Exception as e:
        return f"<!-- Include Plugin: Fehler beim Lesen der Datei '{full_include_path}': {e} -->"
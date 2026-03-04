import os
import re
import unicodedata
import logging
from workers.logger_config import configure_logger

'''
Normalizer for handling file and path normalization in the content directory.
This module provides functions to:
- Check for broken image links in markdown files.
- Check for broken internal links to other markdown files and their anchors.
- Find unused asset files that are not linked in any markdown file.
- Normalize file and folder names to be URL-friendly (slugified).
The main entry point is the `run(context)` function, which takes a context dictionary with keys like 'content_dir' and 'config'.
'''

DEFAULT_EXCLUDED_DIRS = {
    '_spezial', 
    # Füge hier weitere Ordnernamen hinzu, die nicht umbenannt werden sollen.
    # z.B. 'assets' (obwohl es bereits ignoriert wird, wenn es so heisst)
}

# Regex zum Finden von Markdown-Bild-Links
IMAGE_LINK_RE = re.compile(r'!\[.*?\]\((.*?)\)')
# Regex zum Finden von normalen Markdown-Links (ignoriert Bilder)
MARKDOWN_LINK_RE = re.compile(r'\[[^!].*?\]\((.*?)\)')
# Regex für explizite ID in markdown attr_list, e.g. {#my-id}
ATTR_ID_RE = re.compile(r'\{[^\}]*#([a-zA-Z0-9_-]+)[^\}]*\}')
# Regex for id attribute in HTML tags
HTML_ID_RE = re.compile(r'id\s*=\s*["\']([a-zA-Z0-9_-]+)["\']')
# Regex for headings
HEADING_RE = re.compile(r'^(#+)\s+(.*)', re.MULTILINE)

logger = logging.getLogger("normalize")
 
def slugify(value):
    """
    Konvertiert einen String in einen URL-freundlichen Slug.
    Beispiel: "Mein Schöner Ordner" -> "mein-schoener-ordner"
    """
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

def _normalize_path_components(path, base_dir, content_root):
    """Normalisiert alle Teile eines relativen Pfades."""
    # Mache den Pfad absolut, um `..` aufzulösen, dann wieder relativ zum Basis-Verzeichnis
    abs_path = os.path.abspath(os.path.join(base_dir, path))
    rel_path = os.path.relpath(abs_path, content_root)
    
    parts = rel_path.split(os.path.sep)
    filename, ext = os.path.splitext(parts[-1])
    normalized_parts = [slugify(part) for part in parts[:-1]] + [slugify(filename) + ext]
    return os.path.join(*normalized_parts)

def _get_anchors_from_file(file_abs_path):
    """
    Parses a markdown file and extracts all possible anchor IDs.
    This includes slugified headings and explicit HTML/attr_list IDs.
    """
    anchors = set()
    try:
        with open(file_abs_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Find explicit HTML IDs: id="..."
        for html_id in HTML_ID_RE.findall(content):
            anchors.add(html_id)

        # 2. Find headings and their potential IDs
        for match in HEADING_RE.finditer(content):
            heading_line = match.group(2).strip()
            
            # Check for explicit ID from attr_list: {#my-id}
            explicit_id_match = ATTR_ID_RE.search(heading_line)
            if explicit_id_match:
                anchors.add(explicit_id_match.group(1))
            else:
                # If no explicit ID, create one by slugifying the heading text
                # Remove any potential leftover markdown formatting like links
                clean_heading = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', heading_line)
                anchors.add(slugify(clean_heading))

    except Exception:
        pass # If file can't be read, it will be caught by the caller.
    return anchors

def check_broken_links(directory, excluded_dirs):
    """
    Durchläuft das Verzeichnis und prüft alle Markdown-Dateien auf defekte Bild-Links.
    """
    logger.info("Phase 1: Prüfe auf defekte BILD-Links...")
    found_broken_links = False
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]

        for filename in files:
            if not filename.endswith(('.md', '.markdown')):
                continue

            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for image_path in IMAGE_LINK_RE.findall(content):
                    # Ignoriere Web-URLs und absolute Pfade
                    if image_path.startswith(('http://', 'https://', '/')):
                        continue
                    
                    # Baue den absoluten Pfad zum Bild, relativ zur Markdown-Datei
                    absolute_image_path = os.path.abspath(os.path.join(os.path.dirname(file_path), image_path))

                    if not os.path.exists(absolute_image_path):
                        found_broken_links = True
                        logger.error(f"[DEFEKT] Link '{image_path}' in Datei: '{os.path.relpath(file_path, directory)}'")

            except Exception as e:
                logger.warning(f"Konnte Datei nicht lesen: '{file_path}': {e}")
    
    if not found_broken_links:
        logger.info("  -> Keine defekten Bild-Links gefunden. Sehr gut!")

def check_internal_links(directory, excluded_dirs):
    """
    Prüft alle Markdown-Dateien auf defekte interne Links zu anderen Markdown-Seiten und deren Anker.
    """
    logger.info("Phase 2: Prüfe auf defekte INTERNE SEITEN-Links & Anker...")
    valid_targets = set()
    all_md_files = []
    anchor_cache = {} # Cache for anchor IDs: { 'abs/path/to/file.md': {'anchor1', 'anchor2'} }

    # Pass 1: Sammle alle möglichen validen, normalisierten Ziele.
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
        for filename in files:
            if filename.endswith(('.md', '.markdown')):
                relative_path = os.path.relpath(os.path.join(root, filename), directory)
                all_md_files.append(relative_path)
                
                # Normalisiere den Pfad, wie er nach der Umbenennung aussehen wird
                normalized_target = _normalize_path_components(relative_path, directory, directory)
                valid_targets.add(normalized_target.replace(os.path.sep, '/'))

    # Pass 2: Überprüfe die Links in jeder Datei.
    found_broken_links = False
    for file_rel_path in all_md_files:
        file_abs_path = os.path.join(directory, file_rel_path)
        try:
            with open(file_abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for link_target in MARKDOWN_LINK_RE.findall(content):
                # Ignoriere Web-URLs und Links zu Nicht-Markdown-Dateien (ausser sie enthalten einen Anker)
                if link_target.startswith(('http://', 'https://', '/')) or (not link_target.endswith(('.md', '.markdown')) and '#' not in link_target):
                    continue
                
                # Pfad und Anker trennen
                path_part = link_target
                anchor_part = None
                if '#' in link_target:
                    path_part, anchor_part = link_target.split('#', 1)

                # Wenn path_part leer ist, ist es ein Link auf der gleichen Seite
                if not path_part:
                    target_file_abs_path = file_abs_path
                else:
                    # Normalisiere den Link-Pfad relativ zur aktuellen Datei, um die Existenz zu prüfen
                    link_dir = os.path.dirname(file_rel_path)
                    normalized_link = _normalize_path_components(path_part, os.path.join(directory, link_dir), directory)

                    if normalized_link.replace(os.path.sep, '/') not in valid_targets:
                        found_broken_links = True
                        logger.error(f"[DEFEKTE SEITE] Link '{link_target}' in Datei: '{file_rel_path}'")
                        continue # Anker nicht prüfen, wenn die Seite defekt ist
                    
                    # Wir brauchen den originalen, nicht-normalisierten absoluten Pfad zum Lesen
                    target_file_abs_path = os.path.abspath(os.path.join(os.path.dirname(file_abs_path), path_part))

                # --- Anker-Validierung ---
                if anchor_part is not None:
                    if target_file_abs_path not in anchor_cache:
                        # Anker der Zieldatei parsen und cachen
                        anchor_cache[target_file_abs_path] = _get_anchors_from_file(target_file_abs_path)
                    
                    if anchor_part not in anchor_cache.get(target_file_abs_path, set()):
                        found_broken_links = True
                        logger.error(f"[DEFEKTER ANKER] Link '{link_target}' in Datei: '{file_rel_path}' (Anker '#{anchor_part}' nicht gefunden)")
        except Exception as e:
            logger.warning(f"Konnte Datei nicht lesen: '{file_rel_path}': {e}")

    if not found_broken_links:
        logger.info("  -> Keine defekten internen Links oder Anker gefunden. Sehr gut!")

def find_unused_assets(directory, excluded_dirs):
    """
    Findet Asset-Dateien (Bilder, PDFs etc.), die in keiner Markdown-Datei verlinkt sind.
    """
    logger.info("Phase 3: Prüfe auf ungenutzte Asset-Dateien...")
    all_assets = set()
    used_assets = set()

    # Walk through the entire content directory
    for root, dirs, files in os.walk(directory, topdown=True):
        # Respect excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]

        for filename in files:
            file_path = os.path.join(root, filename)
            
            if not filename.endswith(('.md', '.markdown')):
                # This is a potential asset file
                if not filename.startswith('.'):
                    all_assets.add(os.path.abspath(file_path))
            else:
                # This is a markdown file, parse it for links
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Combine finders for all links (images and others)
                    links = IMAGE_LINK_RE.findall(content) + MARKDOWN_LINK_RE.findall(content)
                    
                    for link_target in links:
                        if link_target.startswith(('http://', 'https://', '#', '/')):
                            continue
                        
                        absolute_link_path = os.path.abspath(os.path.join(os.path.dirname(file_path), link_target))
                        used_assets.add(absolute_link_path)
                except Exception as e:
                    logger.warning(f"Konnte Datei nicht lesen: '{file_path}': {e}")

    unused = all_assets - used_assets
    if unused:
        logger.warning(f"Folgende {len(unused)} Asset-Dateien scheinen ungenutzt zu sein:")
        for asset_path in sorted(list(unused)):
            logger.warning(f"    - {os.path.relpath(asset_path, directory)}")
    else:
        logger.info("  -> Keine ungenutzten Asset-Dateien gefunden. Sehr gut!")

def normalize_structure(directory, excluded_dirs):
    """
    Durchläuft das angegebene Verzeichnis und normalisiert Datei- und Ordnernamen.
    Wichtig: Verarbeitet von unten nach oben, um Pfadprobleme zu vermeiden.
    """
    logger.info(f"Phase 4: Starte Normalisierung der Datei- und Ordnernamen in '{directory}'...")
    
    # os.walk mit topdown=False ist entscheidend.
    # Es stellt sicher, dass wir zuerst die Inhalte eines Ordners umbenennen,
    # bevor wir den Ordner selbst umbenennen.
    for root, dirs, files in os.walk(directory, topdown=False):
        # 1. Dateien normalisieren
        for filename in files:
            # Ignoriere versteckte Dateien (z.B. .DS_Store)
            if filename.startswith('.'):
                continue

            base, ext = os.path.splitext(filename)
            normalized_base = slugify(base)
            
            if base != normalized_base:
                old_path = os.path.join(root, filename)
                new_filename = normalized_base + ext
                new_path = os.path.join(root, new_filename)
                logger.info(f"  - Datei umbenennen: '{os.path.relpath(old_path, directory)}' -> '{os.path.relpath(new_path, directory)}'")
                os.rename(old_path, new_path)

        # 2. Verzeichnisse normalisieren
        for dirname in dirs:
            # Ignoriere ausgeschlossene und versteckte Verzeichnisse
            if dirname in excluded_dirs or dirname.startswith('.'):
                continue

            normalized_dirname = slugify(dirname)

            if dirname != normalized_dirname:
                old_path = os.path.join(root, dirname)
                new_path = os.path.join(root, normalized_dirname)
                logger.info(f"  - Ordner umbenennen: '{os.path.relpath(old_path, directory)}' -> '{os.path.relpath(new_path, directory)}'")
                os.rename(old_path, new_path)

    logger.info("Normalisierung abgeschlossen.")
    logger.info("Es wird empfohlen, den Cache deines Browsers zu leeren, da sich die URLs geändert haben könnten.")

def run(context):
    content_dir = context.get('content_dir', 'content')
    project_root = context.get('project_root', '.')
    config = context.get('config', {})
    configure_logger("normalize", project_root)
    
    # Konfiguration laden
    excluded_dirs = set(DEFAULT_EXCLUDED_DIRS)
    excluded_dirs.update(config.get('normalization', {}).get('excluded_dirs', []))

    if os.path.isdir(content_dir):
        # Finde Probleme, bevor etwas geändert wird.
        check_broken_links(content_dir, excluded_dirs)
        check_internal_links(content_dir, excluded_dirs)
        find_unused_assets(content_dir, excluded_dirs)
        # Benenne Dateien und Ordner um.
        normalize_structure(content_dir, excluded_dirs)
        return "Normalisierung abgeschlossen."
    else:
        raise FileNotFoundError(f"Das Verzeichnis '{content_dir}' wurde nicht gefunden.")
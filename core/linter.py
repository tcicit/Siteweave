import os
import re
import logging
from datetime import datetime
from workers.logger_config import configure_logger

try:
    import frontmatter
except ImportError:
    print("Erforderliches Paket 'python-frontmatter' nicht gefunden.")
    print("Bitte installiere es mit: pip install python-frontmatter")
    exit(1)

MARKDOWN_EXTENSIONS = [".md", ".markdown"]

# Definiert, welche Felder vorhanden sein sollten und was ihre Standardwerte sind.
FRONTMATTER_SCHEMA = {
    'title': {'type': str, 'required': True},
    'author': {'type': str, 'default': ''},
    'date': {'type': str, 'required': True}, # Wird mit release_date synchronisiert
    'tags': {'type': list, 'default': []},
    'draft': {'type': bool, 'default': False},
    'release_date': {'type': str, 'required': True, 'default': lambda: datetime.now().strftime('%Y-%m-%d')},
    'featured_image': {'type': str, 'default': None},
    'breadcrumbs': {'type': bool, 'default': True},
    'layout': {'type': str, 'default': 'full-width'},
    'weight': {'type': int, 'default': 0},
}

logger = logging.getLogger("lint_frontmatter")

def extract_title_from_content(markdown_content, fallback_filename):
    """Extrahiert den ersten H1-Titel aus dem Markdown-Inhalt."""
    for line in markdown_content.splitlines():
        if line.strip().startswith('# '):
            return line.strip()[2:]
    # Fallback: Dateinamen bereinigen
    return os.path.splitext(fallback_filename)[0].replace('_', ' ').replace('-', ' ').title()

def is_markdown_file(filename):
    """Prüft, ob eine Datei eine Markdown-Datei ist."""
    return any(filename.endswith(ext) for ext in MARKDOWN_EXTENSIONS)

def check_and_update_frontmatter(content_dir, config=None):
    """Durchläuft das Inhaltsverzeichnis und prüft/aktualisiert das Frontmatter."""
    logger.info(f"Überprüfe und aktualisiere Frontmatter im Verzeichnis '{content_dir}'...")
    updated_files_count = 0
    warning_count = 0

    # Schema aus Config laden/überschreiben
    schema = FRONTMATTER_SCHEMA.copy()
    if config:
        linter_config = config.get('linter', {})
        defaults = linter_config.get('defaults', {})
        for key, value in defaults.items():
            if key in schema:
                schema[key]['default'] = value
            else:
                schema[key] = {'type': type(value), 'default': value}

    # Stelle sicher, dass in jedem Verzeichnis eine index.md vorhanden ist
    created_index_count = 0
    for root, dirs, files in os.walk(content_dir):
        # Skip hidden directories
        dir_name = os.path.basename(root)
        if dir_name.startswith('.'):
            continue

        has_index = any(f.lower() in ('index.md', 'index.markdown') for f in files)
        # Only create index if directory contains markdown files or subdirectories
        contains_content = any(is_markdown_file(f) for f in files) or bool(dirs)
        if not has_index and contains_content:
            index_path = os.path.join(root, 'index.md')
            title = 'Index'
            # Der Titel stammt vom Verzeichnisnamen, außer im Content-Root
            if os.path.normpath(root) != os.path.normpath(content_dir):
                title = os.path.basename(root).replace('_', ' ').replace('-', ' ').title()
            fm = {
                'title': title,
                'release_date': schema['release_date']['default']() if callable(schema['release_date']['default']) else schema['release_date']['default'],
                'date': schema['release_date']['default']() if callable(schema['release_date']['default']) else schema['release_date']['default'],
                'tags': [],
                'draft': False,
                'layout': schema['layout']['default'],
                'breadcrumbs': schema['breadcrumbs']['default']
            }
            post_obj = frontmatter.Post(f"\n\nDieser Index wurde automatisch erstellt.\n\n[[list_dir]]", **fm)
            try:
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(frontmatter.dumps(post_obj))
                created_index_count += 1
                logger.info(f"  - [ERSTELLT] '{os.path.relpath(index_path, content_dir)}' wurde angelegt.")
            except Exception as e:
                logger.error(f"Konnte '{index_path}' nicht erstellen: {e}")

    if created_index_count > 0:
        logger.info(f"{created_index_count} fehlende index.md-Datei(en) wurden erstellt.")

    for root, _, files in os.walk(content_dir):
        for filename in files:
            if not is_markdown_file(filename):
                continue

            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, content_dir)

            try:
                post = frontmatter.load(file_path)
                metadata = post.metadata
                made_change = False

                # --- Felder hinzufügen und korrigieren ---

                # 1. `release_date` sicherstellen (wichtig für Sortierung)
                if 'release_date' not in metadata:
                    default_release_date = schema['release_date']['default']
                    metadata['release_date'] = default_release_date() if callable(default_release_date) else default_release_date
                    logger.info(f"  - [HINZUGEFÜGT] '{relative_path}': 'release_date' auf '{metadata['release_date']}' gesetzt.")
                    made_change = True

                # 2. `date` mit `release_date` synchronisieren, falls fehlend
                if 'date' not in metadata:
                    metadata['date'] = metadata['release_date']
                    logger.info(f"  - [HINZUGEFÜGT] '{relative_path}': 'date' auf '{metadata['date']}' gesetzt.")
                    made_change = True

                # 3. `title` prüfen und ggf. aus Inhalt extrahieren
                if 'title' not in metadata:
                    extracted_title = extract_title_from_content(post.content, filename)
                    metadata['title'] = extracted_title
                    logger.info(f"  - [HINZUGEFÜGT] '{relative_path}': 'title' aus Inhalt extrahiert -> '{extracted_title}'.")
                    made_change = True

                # 4. Restliche Felder aus dem Schema prüfen
                for key, rules in schema.items():
                    if key not in metadata and 'default' in rules:
                        metadata[key] = rules['default']() if callable(rules['default']) else rules['default']
                        logger.info(f"  - [HINZUGEFÜGT] '{relative_path}': Fehlendes Feld '{key}' auf '{metadata[key]}' gesetzt.")
                        made_change = True

                # 5. Typ von 'tags' korrigieren (häufiger Fehler)
                if 'tags' in metadata and not isinstance(metadata['tags'], list):
                    logger.warning(f"'{relative_path}': 'tags' ist keine Liste. Versuche zu korrigieren.")
                    warning_count += 1
                    if isinstance(metadata['tags'], str) and metadata['tags']:
                        metadata['tags'] = [tag.strip() for tag in re.split(r'[,\s]+', metadata['tags']) if tag.strip()]
                        logger.info(f"    -> Korrigiert zu: {metadata['tags']}")
                        made_change = True
                    else:
                        metadata['tags'] = schema['tags']['default']
                        logger.info(f"    -> Zurückgesetzt auf Standard: {metadata['tags']}")
                        made_change = True

                # 6. Tags in der Liste prüfen (müssen Strings sein)
                if 'tags' in metadata and isinstance(metadata['tags'], list):
                    new_tags = []
                    tags_changed = False
                    for tag in metadata['tags']:
                        if not isinstance(tag, str):
                            new_tags.append(str(tag))
                            tags_changed = True
                            logger.warning(f"'{relative_path}': Tag '{tag}' (Typ: {type(tag).__name__}) zu String konvertiert.")
                        else:
                            new_tags.append(tag)
                    if tags_changed:
                        metadata['tags'] = new_tags
                        made_change = True

                # --- Datei zurückschreiben, wenn Änderungen vorgenommen wurden ---
                if made_change:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(frontmatter.dumps(post))
                    updated_files_count += 1

            except Exception as e:
                logger.error(f"Konnte Datei nicht verarbeiten '{relative_path}': {e}")
                warning_count += 1

    logger.info("Prüfung abgeschlossen.")
    if updated_files_count > 0:
        logger.info(f"{updated_files_count} Datei(en) wurden erfolgreich aktualisiert.")
    else:
        logger.info("Alle Dateien scheinen auf dem neuesten Stand zu sein.")

    if warning_count > 0:
        logger.warning(f"Es gab {warning_count} Warnung(en). Bitte überprüfe die Ausgabe oben.")

def run(context):
    """
    Einstiegspunkt für den WorkerThread.
    """
    content_dir = context.get('content_dir', 'content')
    project_root = context.get('project_root', '.')
    config = context.get('config', {})
    
    # Logger konfigurieren
    configure_logger("lint_frontmatter", project_root)
    
    check_and_update_frontmatter(content_dir, config)
    return "Frontmatter-Check abgeschlossen."
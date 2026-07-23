import os
import re
import frontmatter
import importlib.util
from datetime import datetime
from core.path_utils import get_image_replacer
from core.i18n import _
from core.plugin_manager import PluginManager
from core.renderer import process_plugins, _protect_code_blocks, _restore_code_blocks

'''
Worker-Skript, das alle Markdown-Dateien im Content-Ordner zusammenführt und als eine einzige Markdown-Datei exportiert.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
'''

# --- Worker Metadata ---
name = _("Export Project as Markdown")
description = _("Merges all Markdown files into a single Markdown file.")
category = "export"
hidden = False


def _sort_key_for_paths(item):
    """Create sort key that places index files first in directories, then sorts alphabetically."""
    path = item[0].replace('\\', '/')
    parts = path.split('/')
    if parts[-1].lower() in ['index.md', 'index.markdown']:
        parts[-1] = ' ' + parts[-1]
    return parts


def _extract_title(post, full_path):
    """Extract title from post metadata, first heading, or filename (in order of preference)."""
    title = post.metadata.get('title')
    if title:
        return title

    for line in post.content.splitlines():
        if line.strip().startswith('# '):
            return line.strip()[2:]

    return os.path.splitext(os.path.basename(full_path))[0].replace('-', ' ').replace('_', ' ').title()


def _build_plugin_context(project_root, content_dir, full_path, config):
    """Build context dict for plugin processing."""
    return {
        'project_root': project_root,
        'content_dir': content_dir,
        'current_page_path': full_path,
        'relative_prefix': '',
        'config': config,
        'is_pdf': True
    }


def _process_content_with_plugins(content_text, plugin_context, plugins):
    """Process content through plugin pipeline: protect code → process → restore."""
    protected_content, code_protections = _protect_code_blocks(content_text)
    processed_content = process_plugins(protected_content, plugin_context, None, plugins)
    return _restore_code_blocks(processed_content, code_protections)

def run(context):
    project_root = context.get('project_root')
    app_root = context.get('app_root')

    # Fallback für app_root ermitteln
    if not app_root:
        worker_dir = os.path.dirname(os.path.abspath(__file__))
        app_root = os.path.dirname(worker_dir)

    content_dir = context.get('content_dir')
    config = context.get('config', {})
    pdf_config = config.get('pdf_export', {})
    
    if not project_root or not content_dir:
        return _("Error: Project context missing.")

    include_index = bool(pdf_config.get('include_index_files', False))

    # Plugins laden und PDF/Export-irrelevante Plugins deaktivieren
    plugin_manager = PluginManager(app_root, project_root)
    plugins = plugin_manager.load_plugins()
    def dummy_handle(content, args, context, env): return ""
    excluded = ['list_dir', 'latest_posts', 'toc', 'breadcrumbs', 'search', 'navigation']
    for p_name in excluded:
        plugins[p_name] = type('MockPlugin', (), {'handle': dummy_handle})

    # 1. Alle Markdown-Dateien sammeln und sortieren
    md_files = []
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                filename_low = file.lower().strip()
                is_index = filename_low in ['index.md', 'index.markdown', '_index.md', '_index.markdown']
                if is_index and not include_index:
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, content_dir)
                md_files.append((rel_path, full_path))
    
    # Sortieren: index.md immer zuerst im Ordner, dann alphabetisch
    def sort_key(item):
        path = item[0].replace('\\', '/')
        parts = path.split('/')
        if parts[-1].lower() in ['index.md', 'index.markdown']:
            parts[-1] = ' ' + parts[-1]
        return parts

    md_files.sort(key=sort_key)

    # 2. Inhalte zusammenfügen
    site_name = config.get('site_name', 'Project Export')
    date_str = datetime.now().strftime('%d.%m.%Y')
    
    full_content = []
    
    # Header
    full_content.append(f"# {site_name}")
    full_content.append(f"**{_('Date')}:** {date_str}\n")
    full_content.append("---\n")
    
    # Inhaltsverzeichnis (Platzhalter)
    full_content.append(f"## {_('Table of Contents')}\n")
    
    body_content = []
    toc_lines = []

    for rel_path, full_path in md_files:
        try:
            post = frontmatter.load(full_path)
            
            # Seite überspringen, wenn pdf_exclude: true (wir nutzen das gleiche Flag wie beim PDF Export)
            if post.metadata.get('pdf_exclude', False):
                continue
            
            # Titel ermitteln
            title = post.metadata.get('title')
            if not title:
                for line in post.content.splitlines():
                    if line.strip().startswith('# '):
                        title = line.strip()[2:]
                        break
            if not title:
                title = os.path.splitext(os.path.basename(full_path))[0].replace('-', ' ').replace('_', ' ').title()
            
            # Anker für TOC (eindeutig machen durch Pfad)
            anchor = rel_path.replace(os.path.sep, '-').replace('.', '-').lower()
            anchor = re.sub(r'[^a-z0-9-]', '', anchor)
            
            toc_lines.append(f"- [{title}](#{anchor})")
            
            # Inhalt aufbereiten
            body_content.append(f"\n<div id='{anchor}'></div>\n") # HTML Anker für Navigation innerhalb der MD Datei
            body_content.append(f"# {title}\n")
            
            # Plugins auflösen
            plugin_context = {
                'project_root': project_root,
                'content_dir': content_dir,
                'current_page_path': full_path,
                'relative_prefix': '', 
                'config': config,
                'is_pdf': True # Wir setzen dies auch hier, um Plugins zu signalisieren, dass kein Web-Kontext vorliegt
            }
            
            content_text = post.content
            protected_content, code_protections = _protect_code_blocks(content_text)
            processed_content = process_plugins(protected_content, plugin_context, None, plugins)
            content_text = _restore_code_blocks(processed_content, code_protections)
            
            # Bilder-Pfade korrigieren
            # Wir gehen davon aus, dass der Export in 'markdown_exports' landet.
            replacer = get_image_replacer(full_path, project_root, mode='markdown_relative')
            text = re.sub(r'!\[(.*?)\]\((.*?)\)', replacer, content_text)
            
            body_content.append(text)
            body_content.append("\n\n---\n")

        except Exception as e:
            body_content.append(_("\n> Error processing {rel_path}: {e}\n").format(rel_path=rel_path, e=e))

    full_content.extend(toc_lines)
    full_content.append("\n---\n")
    full_content.extend(body_content)

    # 3. Datei schreiben
    export_dir = os.path.join(project_root, "markdown_exports")
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f"{site_name.replace(' ', '_')}_Complete.md"
    output_file = os.path.join(export_dir, filename)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(full_content))
        return _("Markdown export created: {path}").format(path=output_file)
    except Exception as e:
        return _("Error creating Markdown export: {e}").format(e=e)
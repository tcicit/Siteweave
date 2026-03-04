import os
import re
import frontmatter
import importlib.util
from datetime import datetime
from core.i18n import _
from core.renderer import process_plugins, _protect_code_blocks, _restore_code_blocks

'''
Worker-Skript, das alle Markdown-Dateien im Content-Ordner zusammenführt und als eine einzige Markdown-Datei exportiert.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
'''

# --- Worker Metadata ---
name = _("Export Project as Markdown")
description = _("Merges all Markdown files into a single Markdown file.")
category = "project"
hidden = False

def load_plugins(project_root):
    plugins = {}
    # App-Root ermitteln (Elternverzeichnis von workers/)
    worker_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.dirname(worker_dir)
    
    plugin_dirs = [
        os.path.join(app_root, "plugins"),
        os.path.join(project_root, "plugins")
    ]

    for directory in plugin_dirs:
        if not os.path.isdir(directory):
            continue
        
        for item in sorted(os.listdir(directory)):
            path = os.path.join(directory, item)
            module_path = None
            plugin_name = None
            
            if os.path.isfile(path) and item.endswith('.py') and not item.startswith('__'):
                plugin_name = os.path.splitext(item)[0]
                module_path = path
            elif os.path.isdir(path) and not item.startswith('__') and not item.startswith('.'):
                init_file = os.path.join(path, "__init__.py")
                named_file = os.path.join(path, f"{item}.py")
                if os.path.isfile(named_file):
                    plugin_name = item
                    module_path = named_file
                elif os.path.isfile(init_file):
                    plugin_name = item
                    module_path = init_file
            
            if plugin_name and module_path:
                try:
                    spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", module_path)
                    plugin_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(plugin_module)
                    if hasattr(plugin_module, 'handle'):
                        plugins[plugin_name.lower()] = plugin_module
                except Exception as e:
                    print(f"Error loading plugin {plugin_name}: {e}")
    return plugins

def run(context):
    project_root = context.get('project_root')
    content_dir = context.get('content_dir')
    config = context.get('config', {})
    
    if not project_root or not content_dir:
        return _("Error: Project context missing.")

    # 1. Alle Markdown-Dateien sammeln und sortieren
    md_files = []
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith(('.md', '.markdown')):
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

    # Plugins laden
    plugins = load_plugins(project_root)

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
                'config': config
            }
            
            content_text = post.content
            protected_content, code_protections = _protect_code_blocks(content_text)
            processed_content = process_plugins(protected_content, plugin_context, None, plugins)
            content_text = _restore_code_blocks(processed_content, code_protections)
            
            # Bilder-Pfade korrigieren
            # Wir gehen davon aus, dass der Export in 'markdown_exports' landet.
            # Bilder in 'assets' sind dann via '../assets' erreichbar.
            def replace_img_path(match):
                alt = match.group(1)
                url = match.group(2)
                if not url.startswith(('http', 'https', 'data:', 'mailto:')):
                    if url.startswith('/'):
                        abs_img_path = os.path.join(project_root, url.lstrip('/'))
                    else:
                        abs_img_path = os.path.normpath(os.path.join(os.path.dirname(full_path), url))
                    
                    try:
                        rel_to_root = os.path.relpath(abs_img_path, project_root)
                        # Pfad für den Export (wir gehen eins hoch aus markdown_exports)
                        new_url = os.path.join("..", rel_to_root).replace(os.path.sep, '/')
                        return f'![{alt}]({new_url})'
                    except ValueError:
                        pass 
                return match.group(0)
            
            text = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img_path, content_text)
            
            body_content.append(text)
            body_content.append("\n\n---\n")

        except Exception as e:
            body_content.append(f"\n> Error processing {rel_path}: {e}\n")

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
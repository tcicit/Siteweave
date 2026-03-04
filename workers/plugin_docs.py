import os
import ast
import re
from workers.logger_config import configure_logger
from core.i18n import _

'''
Worker-Skript, das die Docstrings aller Plugins im plugins-Ordner analysiert und eine strukturierte Markdown-Dokumentation (plugins.md) im assets/help-Ordner erstellt. 
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
Die Logik für die Analyse der Docstrings und die Generierung der Markdown-Dokumentation befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen werden kann, sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann. 
'''

name = _("Generate Plugin Documentation")
hidden = False
category = "app"
description = _("Creates a help file (plugins.md) from the plugin docstrings.")

def slugify(value):
    """Converts a string into a URL-friendly slug."""
    import unicodedata
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

def parse_docstring(docstring):
    """Parst den Docstring und extrahiert strukturierte Daten."""
    data = {
        'name': _('Unknown'),
        'description': '',
        'syntax': '',
        'parameters': '',
        'examples': ''
    }
    
    if not docstring:
        return data
    
    # Regex to find all sections at once
    section_pattern = re.compile(r'^\s*(Syntax|Verwendung|Usage|Argumente|Arguments|Parameter|Args|Beispiele|Examples)\s*:', re.IGNORECASE | re.MULTILINE)
    
    # Find the start of the first section
    first_section_match = section_pattern.search(docstring)
    
    if first_section_match:
        # Everything before the first section is the description
        desc_end = first_section_match.start()
        raw_desc = docstring[:desc_end].strip()
        
        # Clean up description (remove Pluginname/Beschreibung prefixes)
        desc_lines = []
        for line in raw_desc.splitlines():
            if re.match(r'^\s*(Pluginname|Plugin Name|Name)\s*:', line, re.IGNORECASE):
                continue
            if re.match(r'^\s*(Beschreibung|Description)\s*:', line, re.IGNORECASE):
                line = re.sub(r'^\s*(Beschreibung|Description)\s*:\s*', '', line, flags=re.IGNORECASE)
            desc_lines.append(line)
        data['description'] = "\n".join(desc_lines).strip()
        
        # Process all sections
        for match in section_pattern.finditer(docstring):
            section_name = match.group(1).lower().strip()
            
            # Find the content of this section (between this match and the next, or to the end)
            start = match.end()
            next_match = section_pattern.search(docstring, start)
            end = next_match.start() if next_match else len(docstring)
            content = docstring[start:end].strip()
            
            if section_name in ['syntax', 'verwendung', 'usage']:
                data['syntax'] = content
            elif section_name in ['argumente', 'arguments', 'parameter', 'args']:
                data['parameters'] = content
            elif section_name in ['beispiele', 'examples']:
                data['examples'] = content
    else:
        # No sections found, the whole thing is a description
        raw_desc = docstring.strip()
        desc_lines = []
        for line in raw_desc.splitlines():
            if re.match(r'^\s*(Pluginname|Plugin Name|Name)\s*:', line, re.IGNORECASE):
                continue
            if re.match(r'^\s*(Beschreibung|Description)\s*:', line, re.IGNORECASE):
                line = re.sub(r'^\s*(Beschreibung|Description)\s*:\s*', '', line, flags=re.IGNORECASE)
            desc_lines.append(line)
        data['description'] = "\n".join(desc_lines).strip()
    
    return data

def run(context):
    project_root = context.get('project_root')
    if not project_root:
        return _("Error: Project root not found.")

    # App-Root ermitteln (Elternverzeichnis von workers/)
    worker_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.dirname(worker_dir)

    # Plugins und Hilfe liegen im App-Root
    plugins_dir = os.path.join(app_root, "plugins")
    help_dir = os.path.join(app_root, "assets", "help")
    output_file = os.path.join(help_dir, "plugins.md")

    if not os.path.exists(plugins_dir):
        return _("Error: Plugin directory not found: {plugins_dir}").format(plugins_dir=plugins_dir)

    # Logging konfigurieren
    logger = configure_logger("plugin_docs", project_root)

    os.makedirs(help_dir, exist_ok=True)

    markdown_lines = [
        "---",
        f"title: {_('Plugin Documentation')}",
        "---",
        "",
        f"# {_('Available Plugins')}",
        "",
        _("This documentation was automatically generated from the plugin source codes."),
        ""
    ]

    count = 0
    valid_plugins = []
    for item in sorted(os.listdir(plugins_dir)):
        item_path = os.path.join(plugins_dir, item)
        plugin_filepath = None

        if os.path.isfile(item_path) and item.endswith(".py") and not item.startswith("__"):
            plugin_filepath = item_path
        elif os.path.isdir(item_path) and not item.startswith("__") and not item.startswith("."):
            named_file = os.path.join(item_path, f"{item}.py")
            init_file = os.path.join(item_path, "__init__.py")
            if os.path.isfile(named_file):
                plugin_filepath = named_file
            elif os.path.isfile(init_file):
                plugin_filepath = init_file

        if not plugin_filepath:
            continue

        try:
            with open(plugin_filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            
            docstring = None
            detected_args = set()

            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == "handle":
                    docstring = ast.get_docstring(node)
                    
                    # Code-Analyse: Suche nach args.get('name') oder args['name']
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call):
                            # args.get('key')
                            if (isinstance(subnode.func, ast.Attribute) and 
                                subnode.func.attr == 'get' and
                                isinstance(subnode.func.value, ast.Name) and 
                                subnode.func.value.id == 'args'):
                                if subnode.args and isinstance(subnode.args[0], ast.Constant):
                                    detected_args.add(subnode.args[0].value)
                        elif isinstance(subnode, ast.Subscript):
                            # args['key']
                            if (isinstance(subnode.value, ast.Name) and 
                                subnode.value.id == 'args' and 
                                isinstance(subnode.slice, ast.Constant)):
                                detected_args.add(subnode.slice.value)
                    break
            
            info = parse_docstring(docstring)
            
            # Fallback für Name, falls nicht im Docstring
            if info['name'] == _('Unknown'):
                info['name'] = os.path.splitext(item)[0]

            # Automatisch erkannte Argumente hinzufügen
            existing_params = info['parameters'].lower()
            for arg in sorted(detected_args):
                if arg.lower() not in existing_params:
                    # Append to parameters string
                    if info['parameters']:
                        info['parameters'] += "\n"
                    info['parameters'] += f"- `{arg}` ({_('automatically detected')})"

            # Nur anzeigen, wenn Informationen vorhanden sind
            if info['description'] or info['parameters'] or info['syntax'] or info['examples']:
                valid_plugins.append(info)
                count += 1

        except Exception as e:
            logger.error(_("Error parsing {filename}: {e}").format(filename=os.path.basename(plugin_filepath), e=e))

    # Inhaltsverzeichnis (TOC) generieren
    if valid_plugins:
        markdown_lines.append(f"## {_('Table of Contents')}")
        markdown_lines.append("")
        markdown_lines.append('<div style="column-count: 2; column-gap: 2rem; -webkit-column-count: 2; -moz-column-count: 2;">')
        markdown_lines.append('<ul style="margin-top: 0; padding-left: 20px;">')
        for info in valid_plugins:
            name = _(info['name'])
            # Einfacher Slugify für Anker (Kleinbuchstaben, Leerzeichen zu Bindestrichen)
            anchor = slugify(name)
            markdown_lines.append(f'<li><a href="#{anchor}">{name}</a></li>')
        markdown_lines.append("</ul>")
        markdown_lines.append("</div>")
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

    # Plugin-Details generieren
    for info in valid_plugins:
        name = _(info['name'])
        anchor = slugify(name)
        # Explizite ID für den Header setzen, damit Links funktionieren
        markdown_lines.append(f"## {name} {{: id='{anchor}'}}")
        
        if info['description']:
            markdown_lines.append(info['description'])
            markdown_lines.append("")
        
        if info['syntax']:
            markdown_lines.append(f"**{_('Syntax')}:**")
            markdown_lines.append("")
            markdown_lines.append("```")
            markdown_lines.append(info['syntax'])
            markdown_lines.append("```")
            markdown_lines.append("")
        
        if info['parameters']:
            markdown_lines.append(f"**{_('Parameters')}:**")
            markdown_lines.append("")
            markdown_lines.append(info['parameters'])
            markdown_lines.append("")

        if info['examples']:
            markdown_lines.append(f"**{_('Examples')}:**")
            markdown_lines.append("")
            markdown_lines.append("```markdown")
            markdown_lines.append(info['examples'])
            markdown_lines.append("```")
            markdown_lines.append("")
        
        markdown_lines.append("---")
        markdown_lines.append("")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_lines))
        
        msg = _("Documentation for {count} plugins created: assets/help/plugins_dokumentaion.md").format(count=count)
        logger.info(msg)
        return msg
    except Exception as e:
        logger.error(_("Error writing file: {e}").format(e=e))
        return _("Error writing file: {e}").format(e=e)
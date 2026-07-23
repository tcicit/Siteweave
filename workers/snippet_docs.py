import os
import yaml
from core.i18n import _

'''
Worker-Skript, das die Snippet-Dokumente generiert und eine strukturierte Markdown-Dokumentation (snippets.md) im assets/help-Ordner erstellt.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
Die Logik für die Generierung der Dokumentation befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen werden kann,
sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.
'''

# --- Worker Metadata ---
name = _("Generate Snippet Documentation")
category = "app"
hidden = False
description = _("Creates a help file (snippets.md) from the existing snippets.")

def run(context):
    project_root = context.get('project_root')
    if not project_root:
        return _("Error: Project root not found.")

    # App-Root ermitteln (Elternverzeichnis von workers/)
    worker_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.dirname(worker_dir)

    snippets_dir = context.get('snippets_dir')
    if not snippets_dir:
        # Fallback: Versuche das Verzeichnis relativ zum Worker-Skript zu finden
        # Annahme: Struktur ist app_root/workers/snippet_docs.py und app_root/snippets/
        snippets_dir = os.path.join(app_root, "snippets")

    help_dir = os.path.join(app_root, "assets", "help")
    output_file = os.path.join(help_dir, "snippets.md")

    if not os.path.isdir(snippets_dir):
        return _("Error: Snippet directory '{snippets_dir}' not found or is not a directory.").format(snippets_dir=snippets_dir)

    os.makedirs(help_dir, exist_ok=True)

    snippets = []
    for filename in os.listdir(snippets_dir):
        if filename.endswith(('.yaml', '.yml')):
            try:
                with open(os.path.join(snippets_dir, filename), 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        snippets.append(data)
            except Exception as e:
                print(_("Error loading {filename}: {e}").format(filename=filename, e=e))

    markdown_lines = [
        "---",
        f"title: {_('Snippet Documentation')}",
        "---",
        "",
        f"# {_('Available Snippets')}",
        "",
        _("This documentation was automatically generated from the snippet files."),
        ""
    ]

    # Alle Kategorien sammeln
    all_categories = set()
    for s in snippets:
        c = s.get('category', _('General'))
        if isinstance(c, list):
            all_categories.update(c)
        else:
            all_categories.add(c)

    for category in sorted(list(all_categories)):
        markdown_lines.append(f"## {category}")
        
        # Snippets für diese Kategorie finden
        cat_snippets = [s for s in snippets if category in (s.get('category', _('General')) if isinstance(s.get('category'), list) else [s.get('category', _('General'))])]
        cat_snippets.sort(key=lambda x: x.get('name', ''))

        for snippet in cat_snippets:
            name = snippet.get('name', _('Untitled'))
            code = snippet.get('code', '')
            
            markdown_lines.append(f"### {name}")
            markdown_lines.append("```")
            markdown_lines.append(code)
            markdown_lines.append("```")
            markdown_lines.append("")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_lines))
        return _("Documentation for {count} snippets created: assets/help/snippets.md").format(count=len(snippets))
    except Exception as e:
        return _("Error writing file: {e}").format(e=e)
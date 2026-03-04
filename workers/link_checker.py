import os
import re
from core.i18n import _

from core import APP_NAME, APP_VERSION

'''
Worker-Skript, das alle Links im Content-Ordner überprüft und fehlerhafte Links meldet.
Es prüft sowohl interne Links (zu anderen Dateien im Projekt) als auch externe HTTP-Links. 
Das Skript ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für das Überprüfen der Links befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen wird, sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.   

'''


# --- Worker Metadata ---
name = _("Check Links")
description = _("Checks for broken links in the content directory.")    
hidden = False
category = "project"
# -----------------------


# Versuche, 'requests' zu importieren, aber scheitere nicht, wenn es nicht installiert ist.
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def log_message(message):
    """Hängt eine Nachricht an die worker.log im Projektstamm an."""
    with open("worker.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")

def run(context):
    """
    Durchsucht alle Markdown-Dateien im content-Verzeichnis nach fehlerhaften Links.
    Prüft sowohl interne Dateilinks als auch externe HTTP-Links.
    """
    project_root = context.get('project_root')
    content_dir = context.get('content_dir')
    app_version = context.get('app_version', 'unbekannt') # Neue Variable hier auslesen

    if not project_root or not content_dir:
        return _("Error: Project context not found.")

    log_message(_("\n--- Starting Link Check (App Version: {version}) ---").format(version=app_version))

    if not REQUESTS_AVAILABLE:
        log_message(_("Warning: The 'requests' library is not installed. External HTTP links will be skipped."))
        log_message(_("         Install it with: pip install requests"))

    broken_links = []
    # Regex für Markdown Links und Bilder: [text](url) oder ![alt](url)
    md_regex = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')
    # Regex für HTML Images: <img src="...">
    html_img_regex = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)

    for root, unused_dirs, files in os.walk(content_dir):
        for filename in files:
            if not filename.lower().endswith(('.md', '.markdown')):
                continue

            file_path = os.path.join(root, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                log_message(_("Could not read file {file_path}: {e}").format(file_path=file_path, e=e))
                continue

            # Code-Bereiche identifizieren, um Links darin zu ignorieren
            ignore_ranges = []
            # Fenced Code Blocks (``` ... ```)
            for m in re.finditer(r'```[\s\S]*?```', content):
                ignore_ranges.append((m.start(), m.end()))
            # Inline Code (` ... `)
            for m in re.finditer(r'`[^`\n]+`', content):
                ignore_ranges.append((m.start(), m.end()))

            def is_ignored(match_start):
                return any(start <= match_start < end for start, end in ignore_ranges)

            def check_url(link_target, line_number, is_image=False):
                # Das Ziel kann einen Titel haben wie "url 'title'". Wir wollen nur die URL.
                if ' ' in link_target:
                    link_target = link_target.split(' ')[0].strip('<>')

                if not link_target or link_target.startswith(('#', 'mailto:')):
                    return

                type_label = _("Image") if is_image else _("Link")

                # --- Externe Links prüfen ---
                if link_target.startswith(('http:', 'https://')):
                    if not REQUESTS_AVAILABLE:
                        return
                    try:
                        response = requests.head(link_target, timeout=10, allow_redirects=True, headers={'User-Agent': '{APP_NAME}-Link-Checker/{APP_VERSION}'})
                        if response.status_code >= 400:
                            broken_links.append((file_path, link_target, f"{type_label}: HTTP {response.status_code}", line_number))
                            log_message(_("Broken external {type_label} in {rel_path} -> {link_target} (HTTP {status_code})").format(type_label=type_label, rel_path=os.path.relpath(file_path, project_root), link_target=link_target, status_code=response.status_code))
                    except requests.RequestException:
                        broken_links.append((file_path, link_target, f"{type_label}: Request Error", line_number))
                        log_message(_("Broken external {type_label} in {rel_path} -> {link_target} (Connection Error)").format(type_label=type_label, rel_path=os.path.relpath(file_path, project_root), link_target=link_target))
                
                # --- Interne Links prüfen ---
                else:
                    target_path_part = link_target.split('#')[0]
                    if not target_path_part: return

                    target_abs_path = os.path.normpath(os.path.join(os.path.dirname(file_path), target_path_part))

                    if target_abs_path.lower().endswith('.html'):
                        md_path = os.path.splitext(target_abs_path)[0] + '.md'
                        markdown_path = os.path.splitext(target_abs_path)[0] + '.markdown'
                        if not (os.path.exists(md_path) or os.path.exists(markdown_path)):
                            broken_links.append((file_path, link_target, f"{type_label}: " + _("Source file not found"), line_number))
                            log_message(_("Broken internal {type_label} in {rel_path} -> {link_target} (Source file .md/.markdown not found)").format(type_label=type_label, rel_path=os.path.relpath(file_path, project_root), link_target=link_target))
                    elif not os.path.exists(target_abs_path):
                        broken_links.append((file_path, link_target, f"{type_label}: " + _("File not found"), line_number))
                        log_message(_("Broken internal {type_label} in {rel_path} -> {link_target} (Target file not found)").format(type_label=type_label, rel_path=os.path.relpath(file_path, project_root), link_target=link_target))

            # Markdown Links und Bilder prüfen
            for match in md_regex.finditer(content):
                if is_ignored(match.start()):
                    continue
                line_number = content.count('\n', 0, match.start()) + 1
                is_image = match.group(1).startswith('!')
                check_url(match.group(2).strip(), line_number, is_image)

            # HTML Bilder prüfen
            for match in html_img_regex.finditer(content):
                if is_ignored(match.start()):
                    continue
                line_number = content.count('\n', 0, match.start()) + 1
                check_url(match.group(1).strip(), line_number, is_image=True)

    log_message(_("--- Link Check Finished ---"))

    if not broken_links:
        return _("Link check finished. No broken links found.")
    else:
        results = []
        for file_path, link, error, line in broken_links:
            rel_path = os.path.relpath(file_path, project_root)
            display_text = _("File: {rel_path} (Line {line})\nLink: {link}\nError: {error}").format(rel_path=rel_path, line=line, link=link, error=error)
            results.append({
                'file_path': file_path,
                'line': line,
                'display_text': display_text
            })
            
        log_message(_("Summary: {count} broken links found.").format(count=len(broken_links)))
        return results
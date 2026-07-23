import os
import shutil
import subprocess
import re
from core.i18n import _
from core.logging import configure_logger

# Metadaten für den Project Launcher / Worker
name = _("Check Markdown Syntax (Current File)")
description = _("Validates the currently open Markdown file with pymarkdownlnt.")
category = "project"
hidden = False

def parse_linter_output(output, file_path):
    errors = []
    lines = output.splitlines()
    for line in lines:
        # Regex für PyMarkdown Ausgabe: file:line:col: rule: msg
        # Beispiel: content/index.md:1:1: MD041: ...
        match = re.search(r':(\d+):(\d+): (.*)', line)
        if match:
            line_num = int(match.group(1))
            msg = match.group(3)
            item = {
                'file_path': file_path,
                'line': line_num,
                'display_text': f"Line {line_num}: {msg}"
            }
            errors.append(item)
    return errors

def check_markdown_file(project_root, file_path, logger=None):
    '''
    Prüft eine spezifische Markdown-Datei mit PyMarkdown.
    '''
    # 1. Prüfen, ob pymarkdownlnt installiert ist
    if not shutil.which("pymarkdown"):
        return _("Error: The package 'pymarkdownlnt' is not installed.\nPlease run 'pip install pymarkdownlnt'.")

    if not os.path.exists(file_path):
        return _("Error: File not found: {path}").format(path=file_path)

    if logger:
        logger.info(_("Starting PyMarkdown scan for: {file_path}").format(file_path=file_path))

    try:
        # 2. Befehl zusammenbauen
        cmd = ["pymarkdown"]
        
        # Explizit Konfigurationsdatei angeben, falls vorhanden
        config_file = os.path.join(project_root, ".pymarkdown.json")
        if os.path.exists(config_file):
            cmd.extend(["-c", config_file])
            
        # Scan-Befehl und Pfad
        cmd.extend(["scan", file_path])
        
        # Prozess starten und Ausgabe abfangen
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=project_root
        )

        if result.returncode == 0:
            return []
        else:
            # PyMarkdown gibt Fehler auf stdout (und manchmal stderr) aus
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            
            return parse_linter_output(output, file_path)

    except Exception as e:
        return _("Critical error during execution: {e}").format(e=e)

def run(context):
    """ Einstiegspunkt für den WorkerThread.
     :param context: Ein Dictionary mit Informationen über das aktuelle Projekt und die geöffnete Datei.
     :return: Eine Liste von Problemen oder eine Erfolgs- bzw. Fehlermeldung als String.
    """
    project_root = context.get("project_root", ".")
    current_file_path = context.get("current_file_path")
    
    if not current_file_path:
        return _("No file is currently open in the editor.")
        
    if not current_file_path.lower().endswith(('.md', '.markdown')):
        return _("The currently open file is not a Markdown file.")
        
    logger = configure_logger("markdown_linter", project_root)
    res = check_markdown_file(project_root, current_file_path, logger=logger)
    
    if isinstance(res, list) and not res:
        return _("No syntax errors found. Everything looks good!")
    return res
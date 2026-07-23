'''
Docstring für workers.clear_cache
Löscht das Ausgabeverzeichnis, Backups und den Plugin-Cache.
Das Skript ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für die Löschung befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen wird, 
sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.   
Die Funktion `run(context)` führt die Löschoperationen durch und gibt eine Zusammenfassung der Ergebnisse zurück.  

'''
import os
import shutil
from core.i18n import _

# --- Worker Metadata ---
name = _("Clear Cache")
description = _("Deletes the output directory, backups, and plugin cache.")
category = "project"
hidden = False

def run(context):
    project_root = context.get('project_root')
    config = context.get('config', {})
    
    if not project_root:
        return _("Error: Project root not found.")

    # App-Root ermitteln
    worker_dir = os.path.dirname(os.path.abspath(__file__))
    app_root = os.path.dirname(worker_dir)

    messages = []

    # 1. Output-Verzeichnis leeren
    output_dir_name = config.get("site_output_directory", "site_output")
    output_dir = os.path.join(project_root, output_dir_name)
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            messages.append(_("Successfully cleared output directory: {dir}").format(dir=output_dir_name))
        except Exception as e:
            messages.append(_("Error clearing output directory: {e}").format(e=e))
    
    # 2. Backup-Verzeichnis leeren
    backup_dir_name = config.get("backup_directory", "backups")
    backup_dir = os.path.join(project_root, backup_dir_name)
    if os.path.exists(backup_dir):
        try:
            shutil.rmtree(backup_dir)
            os.makedirs(backup_dir, exist_ok=True)
            messages.append(_("Successfully cleared backup directory: {dir}").format(dir=backup_dir_name))
        except Exception as e:
            messages.append(_("Error clearing backup directory: {e}").format(e=e))

    # 3. Plugin-Cache (__pycache__) leeren
    dirs_to_scan = [
        os.path.join(project_root, config.get("plugin_directory", "plugins")),
        os.path.join(app_root, "plugins")
    ]
    
    cleared_pycache = False
    for scan_dir in dirs_to_scan:
        if not os.path.isdir(scan_dir): continue
        for root, dirs, unused_files in os.walk(scan_dir):
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                try:
                    shutil.rmtree(pycache_path)
                    cleared_pycache = True
                except Exception as e:
                    messages.append(_("Error clearing pycache {path}: {e}").format(path=pycache_path, e=e))
    
    if cleared_pycache:
        messages.append(_("Successfully cleared plugin caches (__pycache__)."))

    if not messages:
        return _("Nothing to clear.")
        
    return "\n".join(messages)
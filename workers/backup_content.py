from datetime import datetime
import os
import shutil
import zipfile
from core.i18n import _

'''
Worker-Skript, das ein Backup des gesamten Content-Ordners als ZIP-Archiv erstellt.
Es unterstützt eine Backup-Rotation, bei der nur die letzten N Backups behalten werden (konfigurierbar über die Projektkonfiguration).
Das Skript ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für die Erstellung des Backups befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen wird, sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.   

'''

# --- Worker Metadata ---
name = _("Content Backup (ZIP)")
description = _("Creates a ZIP archive of the entire content folder with versioning.")
hidden = False
category = "project"

def run(context):
    content_dir = context.get('content_dir')
    project_root = context.get('project_root')
    config = context.get('config', {})
    progress_callback = context.get('progress_callback')

    if not content_dir or not os.path.exists(content_dir):
        return _("Error: Content directory not found.")

    if not project_root:
        return _("Error: Project root not in context.")

    # Zielverzeichnis für Backups erstellen
    backup_dir_name = config.get("backup_directory", "backups")
    backup_dir = os.path.join(project_root, backup_dir_name)
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_name = f"content_backup_{timestamp}"
    output_filename_base = os.path.join(backup_dir, archive_name)
    output_zip_file = output_filename_base + ".zip"

    try:
        if progress_callback:
            files_to_zip = []
            for root, dirs, files in os.walk(content_dir):
                for file in files:
                    files_to_zip.append(os.path.join(root, file))
            
            total_files = len(files_to_zip)
            progress_callback(0, total_files, _("Starting backup..."))
            
            with zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, file_path in enumerate(files_to_zip):
                    arcname = os.path.relpath(file_path, content_dir)
                    zipf.write(file_path, arcname)
                    if i % 5 == 0 or i == total_files - 1:
                        progress_callback(i + 1, total_files, _("Backing up: {file}").format(file=arcname))
        else:
            # Fallback auf shutil, falls kein Callback (z.B. CLI)
            shutil.make_archive(output_filename_base, 'zip', root_dir=content_dir)

        # --- ROTATION LOGIC ---
        rotation_count = config.get("backup_rotation", 10)
        if rotation_count > 0:
            all_backups = sorted(
                [f for f in os.listdir(backup_dir) if f.startswith("content_backup_") and f.endswith(".zip")],
                key=lambda f: os.path.getmtime(os.path.join(backup_dir, f))
            )
            
            if len(all_backups) > rotation_count:
                backups_to_delete = all_backups[:-rotation_count]
                for backup_file in backups_to_delete:
                    try:
                        os.remove(os.path.join(backup_dir, backup_file))
                    except OSError:
                        pass # Ignore errors during deletion
        
        return _("Backup successfully created: {output_filename}").format(output_filename=os.path.basename(output_zip_file))
    except Exception as e:
        return _("Error creating backup: {e}").format(e=e)
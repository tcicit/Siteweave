import os
import shutil
import subprocess
import shlex
from core.i18n import _
import logging

# Diese Datei sollte keine PyQt6-Imports enthalten, um sie UI-agnostisch zu halten.
# Fehlerbehandlung (z.B. QMessageBox) wird in den aufrufenden UI-Komponenten durchgeführt.

def is_editor_available(command):
    """
    Prüft, ob der angegebene Editor (Binärdatei oder Flatpak) auf dem System existiert.
    Gibt True zurück, wenn der Editor gefunden wird, sonst False.
    """
    if not command:
        return False
    
    cmd_parts = command if isinstance(command, list) else shlex.split(command)
    if not cmd_parts: return False
    executable = cmd_parts[0]
    
    # Spezialfall Flatpak: Prüfen ob die App-ID registriert ist
    if executable == "flatpak" and "run" in cmd_parts:
        try:
            # Wir suchen die App-ID (das Element nach 'run')
            app_id = cmd_parts[cmd_parts.index("run") + 1]
            # Wenn Flatpak-Check fehlschlägt, prüfe Binär-Fallbacks (GIMP/Inkscape)
            if subprocess.run(["flatpak", "info", app_id], capture_output=True, check=False).returncode == 0:
                return True
            
            if "org.gimp.GIMP" in app_id and shutil.which("gimp"):
                return True
            if "org.inkscape.Inkscape" in app_id and shutil.which("inkscape"):
                return True
        except Exception:
            logging.getLogger("utils").error(_("Error while checking Flatpak app '{app_id}': {e}").format(app_id=app_id, e=e))
        return False

    return shutil.which(executable) is not None

def open_external_editor(command, file_path):
    """
    Startet einen externen Editor mit der angegebenen Datei.
    Passt Flatpak-Befehle bei Bedarf an.
    Wirft eine Exception, wenn der Editor nicht gestartet werden kann.
    """
    cmd_parts = command if isinstance(command, list) else shlex.split(command)
    # Die Logik für Flatpak-Fallback ist identisch und kann hier zentralisiert werden
    if cmd_parts and cmd_parts[0] == "flatpak" and "run" in cmd_parts:
        try:
            app_id = cmd_parts[cmd_parts.index("run") + 1]
            if subprocess.run(["flatpak", "info", app_id], capture_output=True, check=False).returncode != 0:
                if "org.gimp.GIMP" in app_id and shutil.which("gimp"):
                    cmd_parts = ["gimp"]
                elif "org.inkscape.Inkscape" in app_id and shutil.which("inkscape"):
                    cmd_parts = ["inkscape"]
        except Exception:
            pass

    full_cmd = cmd_parts + [file_path]
    subprocess.Popen(full_cmd) # Startet den Prozess im Hintergrund
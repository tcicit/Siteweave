from core.normalizer import run as run_normalizer
from core.i18n import _

'''
Worker-Skript, das Dateinamen bereinigt (z.B. Leerzeichen durch Bindestriche ersetzt) und Links überprüft.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik für die Bereinigung der Dateinamen und die Überprüfung der Links befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen werden kann, sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.          

'''

# --- Worker Metadata ---
name = _("Normalize Project")
description = _("Cleans up file names and checks links.")
hidden = False
category = "project"

def run(context):
    return run_normalizer(context)
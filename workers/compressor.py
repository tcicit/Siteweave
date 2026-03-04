from core.image_tools import run as run_compressor
from core.i18n import _

'''
Worker-Skript, das dien Bilder im Content-Ordner komprimiert, um die Seitengröße zu reduzieren und die Ladezeiten zu verbessern.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.       
Die Logik       
für die Komprimierung befindet sich in diesem Skript, da es sich um eine einmalige Aktion handelt, die nicht von der GUI aus direkt aufgerufen wird, sondern eher als "Projekt-Wartungs-Tool" dient, das bei Bedarf manuell gestartet werden kann.   

'''

# --- Worker Metadata ---
name = _("Image Compressor")
description = _("Compresses images in the content folder.")
hidden = False
category = "project"


def run(context):
    return run_compressor(context)

from core.image_tools import run

'''
Dieses Skript komprimiert Bilder im Content-Ordner eines Projekts. Es nutzt die zentrale Logik aus core/image_tools.py, um die Bilder zu komprimieren.  
Die Metadaten am Anfang des Skripts geben an, dass es sich um eine Funktion handelt, die Bilder komprimiert, und dass sie im Projektkategorie eingeordnet ist. 
Das Skript kann direkt ausgeführt werden, um die Komprimierung zu starten.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
Die Logik für die Komprimierung befindet sich in 'workers/image_compressor.py', um die Trennung von Logik und Ausführung zu gewährleisten.
'''

name = "Bilder komprimieren"
description = "Komprimiert Bilder im Content-Ordner."
category = "project"
hidden = False

if __name__ == "__main__":
    context = {
        "content_dir": "content",
        "project_root": ".",
        "config": {}
    }
    
    try:
        print("Starte Bild-Komprimierung...")
        # Nutzt jetzt die zentrale Logik aus core/image_tools.py
        result = run(context)
        print(result)
    except Exception as e:
        print(f"Fehler: {e}")
from core.normalizer import run

name = "Projekt normalisieren"
description = "Bereinigt Dateinamen und prüft Links."
category = "project"
hidden = False

if __name__ == "__main__":
    # Context für CLI-Ausführung erstellen
    context = {
        "content_dir": "content",
        "project_root": ".",
        "config": {} 
    }
    
    try:
        print("Starte Normalisierung...")
        # Nutzt jetzt die zentrale Logik aus core/normalizer.py
        result = run(context)
        print(result)
    except Exception as e:
        print(f"Fehler: {e}")
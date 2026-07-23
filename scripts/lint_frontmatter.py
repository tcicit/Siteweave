from core.linter import run
'''
Worker-Skript, das die Frontmatter-Metadaten aller Markdown-Dateien im Content-Ordner überprüft und korrigiert.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
Die Logik für die Überprüfung und Korrektur befindet sich in 'workers/frontmatter_checker.py', 
um eine saubere séparation zwischen der GUI-Integration und der eigentlichen Funktionalität zu ermöglichen.
'''

name = "Frontmatter prüfen"
description = "Überprüft und korrigiert die Metadaten der Markdown-Dateien."
category = "project"
hidden = False

if __name__ == "__main__":
    context = {
        "content_dir": "content",
        "project_root": ".",
        "config": {}
    }
    
    try:
        print("Starte Frontmatter-Check...")
        # Nutzt jetzt die zentrale Logik aus core/linter.py
        result = run(context)
        print(result)
    except Exception as e:
        print(f"Fehler: {e}")
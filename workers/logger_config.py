from core.logging import configure_logger

'''
Worker-Skript, das die Frontmatter-Metadaten aller Markdown-Dateien im Content-Ordner überprüft und korrigiert. 
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
Die Logik für die Überprüfung und Korrektur befindet sich in 'workers/frontmatter_checker.py', 
um eine saubere séparation zwischen der GUI-Integration und der eigentlichen Funktionalität zu ermöglichen.

'''

__all__ = ['configure_logger']
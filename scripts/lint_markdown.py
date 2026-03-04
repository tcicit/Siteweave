import sys
import os

'''
Worker-Skript, das alle Markdown-Dateien im Content-Ordner mit PyMarkdown überprüft.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
Die Logik für die Überprüfung befindet sich in 'workers/markdown_linter.py', 
um eine saubere Trennung zwischen der GUI-Integration und der eigentlichen Funktionalität zu gewährleisten.

'''

# Sicherstellen, dass wir Module aus dem aktuellen Verzeichnis importieren können
# Dies behebt Import-Fehler, die dazu führen, dass der Name falsch angezeigt wird
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importiere die Logik aus dem Worker-Verzeichnis (wie bei lint_frontmatter.py)
from workers.markdown_linter import run

# Metadaten für den Project Launcher / Worker
name = "Markdown Syntax (PyMarkdown)"
description = "Validiert alle Markdown-Dateien im Content-Ordner mit pymarkdownlnt."
category = "project"
hidden = False

if __name__ == "__main__":
    # Das erste Argument ist normalerweise der Projektpfad, den der Launcher übergibt
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    # Wir simulieren den Context-Aufruf
    context = {"project_root": root}
    report = run(context)

    # Ergebnis in einem Fenster anzeigen (ähnlich wie andere Worker)
    try:
        from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton
        from PyQt6.QtGui import QFont

        # Prüfen ob schon eine QApplication läuft (falls das Skript integriert läuft)
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        dialog = QDialog()
        dialog.setWindowTitle("Markdown Syntax Bericht")
        dialog.resize(800, 600)

        layout = QVBoxLayout()
        
        text_area = QTextEdit()
        text_area.setPlainText(report)
        text_area.setReadOnly(True)
        # Monospace Font für saubere Darstellung von Code/Logs
        text_area.setFont(QFont("Monospace"))
        
        layout.addWidget(text_area)
        
        btn = QPushButton("Schließen")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn)
        
        dialog.setLayout(layout)
        dialog.exec()

    except ImportError:
        # Fallback: Einfach auf der Konsole ausgeben, falls PyQt fehlt
        print(report)
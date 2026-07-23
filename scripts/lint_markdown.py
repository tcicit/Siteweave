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
    # Das erste Argument ist der Pfad zum File oder Verzeichnis
    target_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    reports = []
    
    if os.path.isfile(target_path):
        context = {
            "project_root": os.path.dirname(os.path.abspath(target_path)),
            "current_file_path": os.path.abspath(target_path)
        }
        res = run(context)
        if isinstance(res, list):
            reports.extend(res)
        else:
            reports.append(res)
    else:
        # Verzeichnis: alle Markdown-Dateien scannen
        from workers.markdown_linter import check_markdown_file
        project_root = os.path.abspath(target_path)
        found_any = False
        for root_dir, _, files in os.walk(project_root):
            for file in files:
                if file.lower().endswith(('.md', '.markdown')):
                    found_any = True
                    file_path = os.path.join(root_dir, file)
                    res = check_markdown_file(project_root, file_path)
                    if isinstance(res, list):
                        reports.extend(res)
                    else:
                        reports.append(f"{file}: {res}")
        if not found_any:
            reports.append("Keine Markdown-Dateien im Verzeichnis gefunden.")
            
    # Formatiere Berichte für die Anzeige
    if not reports:
        report_str = "Keine Fehler gefunden. Alles sieht gut aus!"
    elif len(reports) == 1 and isinstance(reports[0], str):
        report_str = reports[0]
    else:
        formatted_lines = []
        for item in reports:
            if isinstance(item, dict):
                formatted_lines.append(f"{os.path.basename(item['file_path'])}:{item['line']} - {item['display_text']}")
            else:
                formatted_lines.append(str(item))
        report_str = "\n".join(formatted_lines)

    # Ergebnis in einem Fenster anzeigen (falls PyQt vorhanden) oder ausgeben
    try:
        from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton
        from PyQt6.QtGui import QFont

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        dialog = QDialog()
        dialog.setWindowTitle("Markdown Syntax Bericht")
        dialog.resize(800, 600)

        layout = QVBoxLayout()
        
        text_area = QTextEdit()
        text_area.setPlainText(report_str)
        text_area.setReadOnly(True)
        text_area.setFont(QFont("Monospace"))
        
        layout.addWidget(text_area)
        
        btn = QPushButton("Schließen")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn)
        
        dialog.setLayout(layout)
        dialog.exec()

    except ImportError:
        print(report_str)
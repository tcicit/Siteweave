import os
import shutil
import subprocess
import re
from core.i18n import _
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import QObject, pyqtSlot, QMetaObject, Qt, Q_ARG
from PyQt6.QtGui import QFont, QColor, QBrush

'''
Worker-Skript, das die aktuell geöffnete Markdown-Datei mit PyMarkdown überprüft und einen Bericht über die gefundenen Syntaxfehler oder Warnungen anzeigt.
Es ist als eigenständiges Skript konzipiert, das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden kann.
Die Logik für die Überprüfung befindet sich in 'workers/markdown_linter.py', 
um eine saubere Trennung zwischen der GUI-Integration und der eigentlichen Funktionalität zu gewährleisten.
'''

# Metadaten für den Project Launcher / Worker
name = _("Check Markdown Syntax (Current File)")
description = _("Validates the currently open Markdown file with pymarkdownlnt.")
category = "project"
hidden = False


class LinterResultDialog(QObject):
    """
    Hilfsklasse, um den Dialog im Haupt-Thread anzuzeigen.
    """
    @pyqtSlot(str)
    def show_report(self, report):
        app = QApplication.instance()
        # Hauptfenster finden, um den Dialog daran zu binden (wichtig für nicht-modale Dialoge)
        main_window = None
        for widget in app.topLevelWidgets():
            if widget.objectName() == "MainWindow" or widget.__class__.__name__ == "MainWindow":
                main_window = widget
                break
        
        if not main_window:
            return

        # Alten Dialog schließen, falls vorhanden (verhindert mehrere offene Fenster)
        if hasattr(main_window, "linter_dialog") and main_window.linter_dialog:
            try:
                main_window.linter_dialog.close()
            except:
                pass

        dialog = QDialog(main_window)
        dialog.setWindowTitle(_("Markdown Syntax Report"))
        dialog.resize(600, 500)
        dialog.setModal(False) # Nicht-Modal: Editor bleibt bedienbar
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        layout = QVBoxLayout()
        
        label = QLabel(_("Click on an error to jump to the line:"))
        layout.addWidget(label)
        
        list_widget = QListWidget()
        
        lines = report.split('\n')
        for line in lines:
            # Regex für PyMarkdown Ausgabe: file:line:col: rule: msg
            # Beispiel: content/index.md:1:1: MD041: ...
            match = re.search(r':(\d+):(\d+): (.*)', line)
            if match:
                line_num = int(match.group(1))
                msg = match.group(3)
                item = QListWidgetItem(f"Line {line_num}: {msg}")
                item.setData(Qt.ItemDataRole.UserRole, line_num)
                
                # Farblich hervorheben
                # PyMarkdown liefert meist Regelverstöße (Warnings). Echte Fehler enthalten oft "Error".
                if "error" in msg.lower():
                    item.setForeground(QBrush(QColor("red")))
                else:
                    # Dunkles Orange ist auf weißem Hintergrund besser lesbar als reines Gelb
                    item.setForeground(QBrush(QColor("darkorange")))
                    
                list_widget.addItem(item)
            elif line.strip():
                # Andere Zeilen (z.B. Zusammenfassungen) ohne Sprungfunktion
                item = QListWidgetItem(line)
                item.setData(Qt.ItemDataRole.UserRole, -1)
                list_widget.addItem(item)

        def on_item_clicked(item):
            line_num = item.data(Qt.ItemDataRole.UserRole)
            if line_num and line_num > 0 and hasattr(main_window, 'editor'):
                # Cursor im Editor bewegen
                cursor = main_window.editor.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line_num - 1)
                cursor.select(cursor.SelectionType.LineUnderCursor) # Zeile markieren
                main_window.editor.setTextCursor(cursor)
                main_window.editor.setFocus()

        list_widget.itemClicked.connect(on_item_clicked)
        layout.addWidget(list_widget)
        
        btn = QPushButton(_("Close"))
        btn.clicked.connect(dialog.close)
        layout.addWidget(btn)
        
        dialog.setLayout(layout)
        dialog.show()
        
        # Referenz im Main Window speichern, damit der Dialog nicht vom Garbage Collector entfernt wird
        main_window.linter_dialog = dialog

def check_markdown_file(project_root, file_path):
    '''
    Prüft eine spezifische Markdown-Datei mit PyMarkdown.
    '''
    # 1. Prüfen, ob pymarkdownlnt installiert ist
    if not shutil.which("pymarkdown"):
        return _("Error: The package 'pymarkdownlnt' is not installed.\nPlease run 'pip install pymarkdownlnt'.")

    if not os.path.exists(file_path):
        return _("Error: File not found: {path}").format(path=file_path)

    print(f"Starte PyMarkdown Scan für: {file_path}\n")

    try:
        # 2. Befehl zusammenbauen
        cmd = ["pymarkdown"]
        
        # Explizit Konfigurationsdatei angeben, falls vorhanden
        config_file = os.path.join(project_root, ".pymarkdown.json")
        if os.path.exists(config_file):
            cmd.extend(["-c", config_file])
            
        # Scan-Befehl und Pfad
        cmd.extend(["scan", file_path])
        
        # Prozess starten und Ausgabe abfangen
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=project_root
        )

        if result.returncode == 0:
            return _("No syntax errors found. Everything looks good!")
        else:
            # PyMarkdown gibt Fehler auf stdout (und manchmal stderr) aus
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            
            return _("Problems found:\n\n{output}").format(output=output)

    except Exception as e:
        return _("Critical error during execution: {e}").format(e=e)

def run(context):

    """ Einstiegspunkt für den WorkerThread. "  
     :param context: Ein Dictionary mit Informationen über das aktuelle Projekt und die geöffnete Datei.
     :return: Ein Bericht über die gefundenen Syntaxfehler oder Warnungen, oder eine Fehlermeldung, falls etwas schiefgeht.
    """

    project_root = context.get("project_root", ".")
    current_file_path = context.get("current_file_path")
    
    if not current_file_path:
        return _("No file is currently open in the editor.")
        
    if not current_file_path.lower().endswith(('.md', '.markdown')):
        return _("The currently open file is not a Markdown file.")
        
    report = check_markdown_file(project_root, current_file_path)
    
    # Dialog im Main-Thread anzeigen (da Worker in einem separaten Thread läuft)
    app = QApplication.instance()
    if app:
        dialog_helper = LinterResultDialog()
        dialog_helper.moveToThread(app.thread())
        QMetaObject.invokeMethod(dialog_helper, "show_report", Qt.ConnectionType.BlockingQueuedConnection, Q_ARG(str, report))
        return _("Syntax check finished. See dialog for details.")
    else:
        return report
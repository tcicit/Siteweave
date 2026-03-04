from core.i18n import _
from core.renderer import run as run_renderer
from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt6.QtCore import QObject, pyqtSlot, QMetaObject, Qt

'''
Worker-Skript, das die statische Website generiert. Es bietet dem Benutzer die Möglichkeit,zwischen einem vollständigen Rendern (alle Seiten) oder einem inkrementellen Rendern (nur geänderte Seiten) zu wählen. Es ist als eigenständiges Skript konzipiert, 
das über die Kommandozeile aufgerufen werden kann, aber auch von der GUI als Worker genutzt werden  kann. Die Logik für die Generierung der Website befindet sich in 'core/renderer.py', um eine saubere Trennung zwischen der GUI-Integration und der eigentlichen Funktionalität zu gewährleisten.    

'''

# --- Worker Metadata ---
name = _("Generate Website") # Konsistenter Name
description = _("Generates the static website.")
hidden = False
category = "project"
# -----------------------

class RenderModeSelector(QObject):
    """
    Hilfsklasse, um den Dialog im Haupt-Thread anzuzeigen.
    """
    def __init__(self):
        super().__init__()
        self.mode = "cancel" # Standardwert

    @pyqtSlot()
    def select_mode(self):
        app = QApplication.instance()
        main_window = None
        progress_dialog = None

        # Hauptfenster finden
        for widget in app.topLevelWidgets():
            if widget.objectName() == "MainWindow":
                main_window = widget
                break
            
            # Versuche, den störenden Fortschrittsdialog zu finden
            if isinstance(widget, QProgressDialog) and widget.isVisible():
                progress_dialog = widget
        
        # Fortschrittsdialog kurz verstecken, damit unsere Frage sichtbar ist
        if progress_dialog:
            progress_dialog.hide()

        try:
            dialog = QMessageBox(main_window)
            dialog.setWindowTitle(_("Render Site"))
            dialog.setText(_("How do you want to render the site?"))
            dialog.setIcon(QMessageBox.Icon.Question)
            
            btn_full = dialog.addButton(_("Full Render"), QMessageBox.ButtonRole.AcceptRole)
            btn_inc = dialog.addButton(_("Changed Pages Only"), QMessageBox.ButtonRole.YesRole)
            btn_cancel = dialog.addButton(QMessageBox.StandardButton.Cancel)
            
            dialog.exec()
            
            clicked = dialog.clickedButton()
            if clicked == btn_full:
                self.mode = "full"
            elif clicked == btn_inc:
                self.mode = "incremental"
            else:
                self.mode = "cancel"
        finally:
            # Fortschrittsdialog wiederherstellen
            if progress_dialog:
                progress_dialog.show()

def run(context):
    app = QApplication.instance()
    if app:
        selector = RenderModeSelector()
        selector.moveToThread(app.thread())
        
        # Dialog im Main-Thread aufrufen (ohne Rückgabewert, wir nutzen selector.mode)
        QMetaObject.invokeMethod(selector, "select_mode", Qt.ConnectionType.BlockingQueuedConnection)
        
        if selector.mode == "cancel":
            return _("Rendering cancelled.")
            
        if selector.mode == "incremental":
            # Flag für den Renderer setzen
            print("INFO: Incremental rendering selected.")
            context['incremental'] = True
            # Backup deaktivieren, wie gewünscht
            if 'config' in context:
                context['config']['backup_on_render'] = False
        else:
            context['incremental'] = False
            
    return run_renderer(context)

import os
import sys
import traceback
import importlib.util
from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    """
    Ein generischer Worker, der ein Python-Skript dynamisch lädt und dessen
    'run(context)'-Funktion ausführt.
    Der Worker sendet das Ergebnis über das 'finished'-Signal zurück oder gibt Fehler über das 'error'-Signal weiter.
    Das Skript muss eine Funktion 'run(context)' definieren, die die eigentliche Arbeit ausführt.
    Der Kontext ist ein Dictionary, das relevante Informationen wie 'content_dir', 'config' oder 'project_root' enthalten kann, je nach Bedarf des Skripts. 
    Beispiel für die Verwendung eines Worker-Skripts (z.B. 'workers/compress_images.py'):
    

    """
    finished = pyqtSignal(object) # Sendet den Rückgabewert von run()
    error = pyqtSignal(str)

    def __init__(self, worker_path, context=None):
        super().__init__()
        self.worker_path = worker_path
        self.context = context or {}

    def run(self):
        try:
            # Projekt-Root zum Pfad hinzufügen, damit Importe wie 'import site_renderer' funktionieren
            if self.context and 'project_root' in self.context:
                project_root = self.context['project_root']
                # Pfad entfernen falls vorhanden und an Position 0 erzwingen
                if project_root in sys.path:
                    sys.path.remove(project_root)
                sys.path.insert(0, project_root)

            if not os.path.exists(self.worker_path):
                raise FileNotFoundError(f"Worker-Skript nicht gefunden: {self.worker_path}")

            # Modul dynamisch laden
            spec = importlib.util.spec_from_file_location("worker_module", self.worker_path)
            if not spec or not spec.loader:
                raise ImportError(f"Konnte Worker nicht laden: {self.worker_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Prüfen ob run(context) existiert
            if hasattr(module, 'run'):
                print(f"\n--- Start Worker: {os.path.basename(self.worker_path)} ---")
                # Worker ausführen und Ergebnis speichern
                result = module.run(self.context)
                print(f"--- End Worker: {os.path.basename(self.worker_path)} ---\n")
                self.finished.emit(result)
            else:
                raise AttributeError(f"Das Modul {os.path.basename(self.worker_path)} hat keine 'run(context)' Funktion.")
                
        except Exception:
            self.error.emit(traceback.format_exc())
            print(f"Fehler im Worker {os.path.basename(self.worker_path)}:\n{traceback.format_exc()}")

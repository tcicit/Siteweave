import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer, Qt
from PyQt6.QtGui import QPixmap, QColor

class PreviewGenerator:
    """
    Erzeugt ein Vorschaubild (Screenshot) der gerenderten Website.
    Nutzt QtWebEngine im Off-Screen Modus.
    """
    def __init__(self, project_root, output_dir_name="site_output"):
        self.project_root = project_root
        self.index_path = os.path.join(project_root, output_dir_name, "index.html")
        self.save_path = os.path.join(project_root, "preview.png")
        self.view = None

    def start(self):
        """Startet den Ladevorgang der Seite."""
        if not os.path.exists(self.index_path):
            return

        # WebEngineView instanziieren
        self.view = QWebEngineView()
        
        # Hintergrundfarbe erzwingen
        self.view.page().setBackgroundColor(QColor("white"))
        
        # WICHTIG: Buffers erzwingen, ohne ein echtes Fenster anzuzeigen
        self.view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        self.view.show()
        
        # Desktop-Auflösung (16:10 für gute Header-Abdeckung)
        self.view.setFixedSize(1440, 900)
        
        # Höhere Render-Qualität durch simulierten Zoom (High-DPI Effekt)
        self.view.setZoomFactor(1.5)

        # Scrollbars für das Vorschaubild ausblenden
        self.view.settings().setAttribute(self.view.settings().WebAttribute.ShowScrollBars, False)
        
        self.view.loadFinished.connect(self._on_load_finished)
        self.view.load(QUrl.fromLocalFile(self.index_path))

    def _on_load_finished(self, ok):
        if ok:
            # Sicherstellen, dass wir ganz oben sind
            self.view.page().runJavaScript("window.scrollTo(0, 0);")
            # Verzögerung für Rendering-Settling
            QTimer.singleShot(2500, self._capture)
        else:
            self._cleanup()

    def _capture(self):
        try:
            # Snapshot des Viewports
            pixmap = self.view.grab()
            
            # Skalieren auf eine gute Zielgröße für die Cards (Breite fixieren)
            # Durch die höhere Render-Auflösung oben bleibt das Bild hier scharf.
            preview = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
            preview.save(self.save_path, "PNG")
        finally:
            self._cleanup()

    def _cleanup(self):
        if self.view:
            self.view.deleteLater()
            self.view = None

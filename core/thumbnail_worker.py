import os
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal
import logging
from core.logging import configure_logger
from core.i18n import _

logger = logging.getLogger("thumbnail_worker")

class ThumbnailWorker(QThread):
    """
    Hintergrund-Thread, der Thumbnails für Bilder im Assets-Ordner erstellt.
    Speichert die Ergebnisse in .siteweave/cache/thumbs.
    """
    thumbnail_ready = pyqtSignal(str, str)  # Originaler Pfad, Thumbnail Pfad
    finished_scanning = pyqtSignal()

    def __init__(self, project_root, assets_dir):
        super().__init__()
        self.project_root = project_root
        self.assets_dir = assets_dir
        self.cache_dir = os.path.join(project_root, ".siteweave", "cache", "thumbs")
        self._is_running = True # Flag, um den Thread sicher zu beenden
        
        # Initialisiere das Logging für diesen Worker, damit Fehler in worker.log landen
        configure_logger("thumbnail_worker", project_root)
        
        self.supported_ext = (('.jpg', '.jpeg', '.png', '.svg', '.webp', '.pdf'))
        self.thumb_size = (128, 128)

    def stop(self):
        """Setzt das Flag, um den Thread zum Beenden aufzufordern."""
        self._is_running = False

    def run(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

        for root, _, files in os.walk(self.assets_dir):
            for file in files:
                if not self._is_running: # Prüfen, ob der Thread beendet werden soll
                    break
                if file.lower().endswith(self.supported_ext):
                    full_path = os.path.join(root, file)
                    thumb_path = self._get_or_create_thumbnail(full_path)
                    if thumb_path:
                        self.thumbnail_ready.emit(full_path, thumb_path)
        
        self.finished_scanning.emit()
        if not self._is_running:
            logger.info(f"ThumbnailWorker for {self.assets_dir} stopped gracefully.")

    def _get_or_create_thumbnail(self, image_path):
        """Erstellt ein Thumbnail, falls es noch nicht im Cache existiert."""
        # Eindeutiger Name basierend auf dem Pfad
        rel_path = os.path.relpath(image_path, self.project_root)
        safe_name = rel_path.replace(os.sep, "_") + ".png"
        dest_path = os.path.join(self.cache_dir, safe_name)

        # Falls Bild bereits im Cache und neuer als das Original, überspringen
        if os.path.exists(dest_path):
            if os.path.getmtime(dest_path) >= os.path.getmtime(image_path):
                return dest_path

        try:
            if image_path.lower().endswith('.svg'):
                # SVGs können direkt als Icon genutzt werden
                return image_path

            if image_path.lower().endswith('.pdf'):
                try:
                    import fitz
                    doc = fitz.open(image_path)
                    page = doc.load_page(0)
                    pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                    pix.save(dest_path) # Speichert als PNG im Cache
                    doc.close()
                    return dest_path
                except ImportError:
                    return None
            
            with Image.open(image_path) as img:
                # Exif-Rotation beachten
                try:
                    from PIL import ImageOps
                    img = ImageOps.exif_transpose(img)
                except Exception:
                    pass

                img.thumbnail(self.thumb_size)
                # Als RGBA/RGB speichern
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                
                img.save(dest_path, "PNG")
                return dest_path
        except Exception as e:
            logger.error(_("Error while creating thumbnail for {image_path}: {e}").format(image_path=image_path, e=e))
            return None
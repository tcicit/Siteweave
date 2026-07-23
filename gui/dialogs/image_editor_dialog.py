import os
import shutil
import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QScrollArea, QRubberBand, 
                             QMessageBox, QFrame, QWidget)
from PyQt6.QtCore import Qt, QSize, QPoint, QRect
from PyQt6.QtGui import QPixmap, QImage, QIcon, QMouseEvent
from PIL import Image, ImageOps
from core.i18n import _

class CroppableLabel(QLabel):
    """A QLabel that allows drawing a rubber band for cropping."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.aspect_ratio = None # None means free cropping

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.origin.isNull():
            rect = QRect(self.origin, event.pos()).normalized()
            if self.aspect_ratio:
                width = rect.width()
                height = int(width / self.aspect_ratio)
                new_x, new_y = self.origin.x(), self.origin.y()
                if event.pos().x() < self.origin.x(): new_x = self.origin.x() - width
                if event.pos().y() < self.origin.y(): new_y = self.origin.y() - height
                rect = QRect(new_x, new_y, width, height)
            self.rubber_band.setGeometry(rect.intersected(self.rect()))

    def mouseReleaseEvent(self, event: QMouseEvent):
        # Falls nur geklickt wurde ohne zu ziehen, Rahmen verstecken
        if self.rubber_band.width() < 5 or self.rubber_band.height() < 5:
            self.rubber_band.hide()

    def get_selection(self):
        if not self.rubber_band.isVisible():
            return None
        return self.rubber_band.geometry()

class ImageEditorDialog(QDialog):
    def __init__(self, image_path, project_root, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.project_root = project_root
        self.history = []
        self.setWindowTitle(_("Image Editor - {name}").format(name=os.path.basename(image_path)))
        self.resize(1000, 800)
        try:
            self.pil_image = Image.open(image_path)
            self.pil_image = ImageOps.exif_transpose(self.pil_image)
        except Exception as e:
            QMessageBox.critical(self, _("Error"), str(e))
            self.reject()
        self.init_ui()
        self.refresh_display()

    def init_ui(self):
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        
        self.undo_btn = QPushButton(QIcon.fromTheme("edit-undo"), _("Undo"))
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)

        rot_l = QPushButton(QIcon.fromTheme("object-rotate-left"), _("Rotate Left"))
        rot_l.clicked.connect(lambda: self.rotate_image(90))
        rot_r = QPushButton(QIcon.fromTheme("object-rotate-right"), _("Rotate Right"))
        rot_r.clicked.connect(lambda: self.rotate_image(-90))
        
        self.ratio_combo = QComboBox()
        ratios = [(_("Free"), None), ("1:1", 1.0), ("3:2", 1.5), ("4:3", 4/3), ("16:9", 16/9), ("DIN (1:1.41)", 1.414)]
        for text, value in ratios:
            self.ratio_combo.addItem(text, value)
        self.ratio_combo.currentIndexChanged.connect(self.update_ratio)
        
        crop_btn = QPushButton(QIcon.fromTheme("transform-crop"), _("Crop Selection"))
        crop_btn.clicked.connect(self.apply_crop)
        
        toolbar.addWidget(self.undo_btn); toolbar.addSpacing(10)
        toolbar.addWidget(rot_l); toolbar.addWidget(rot_r); toolbar.addSpacing(20)
        toolbar.addWidget(QLabel(_("Ratio:"))); toolbar.addWidget(self.ratio_combo); toolbar.addWidget(crop_btn); toolbar.addStretch()
        layout.addLayout(toolbar)
        self.scroll_area = QScrollArea(); self.scroll_area.setWidgetResizable(True)
        self.image_label = CroppableLabel(); self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label); layout.addWidget(self.scroll_area)
        btns = QHBoxLayout(); save = QPushButton(_("Save")); save.clicked.connect(self.save_image)
        cancel = QPushButton(_("Cancel")); cancel.clicked.connect(self.reject)
        btns.addStretch(); btns.addWidget(cancel); btns.addWidget(save); layout.addLayout(btns)

    def update_ratio(self):
        self.image_label.aspect_ratio = self.ratio_combo.currentData()

    def refresh_display(self):
        """Aktualisiert die Anzeige des Bildes sicher."""
        try:
            # Erstelle eine Kopie für die Anzeige (max 1200px)
            display_img = self.pil_image.copy()
            display_img.thumbnail((1200, 1200))
            
            # Manuelle Konvertierung von PIL zu QImage (stabiler als ImageQt)
            qimage = self.pil_to_qimage(display_img)
            self.image_label.setPixmap(QPixmap.fromImage(qimage))
            self.image_label.rubber_band.hide()
        except Exception as e:
            print(f"Error refreshing display: {e}")
            QMessageBox.warning(self, _("Display Error"), str(e))

    def pil_to_qimage(self, pil_img):
        """Konvertiert PIL Image zu QImage ohne ImageQt-Absturzgefahr."""
        if pil_img.mode == "RGB":
            qfmt = QImage.Format.Format_RGB888
        elif pil_img.mode == "RGBA":
            qfmt = QImage.Format.Format_RGBA8888
        elif pil_img.mode == "L":
            qfmt = QImage.Format.Format_Grayscale8
        else:
            pil_img = pil_img.convert("RGBA")
            qfmt = QImage.Format.Format_RGBA8888

        data = pil_img.tobytes("raw", pil_img.mode)
        return QImage(data, pil_img.size[0], pil_img.size[1], qfmt).copy()

    def save_history(self):
        """Speichert den aktuellen Zustand des Bildes in der Historie."""
        self.history.append(self.pil_image.copy())
        if len(self.history) > 20: # Limitiere auf 20 Schritte
            self.history.pop(0)
        self.undo_btn.setEnabled(True)

    def undo(self):
        """Rückgängig machen des letzten Schritts."""
        if self.history:
            self.pil_image = self.history.pop()
            self.refresh_display()
        if not self.history:
            self.undo_btn.setEnabled(False)

    def rotate_image(self, angle):
        try:
            self.save_history()
            self.pil_image = self.pil_image.rotate(angle, expand=True)
            self.refresh_display()
        except Exception as e:
            print(f"Rotation error: {e}")

    def apply_crop(self):
        rect = self.image_label.get_selection()
        pixmap = self.image_label.pixmap()
        if not rect or not pixmap or rect.width() < 10:
            return

        p_size = pixmap.size()
        l_size = self.image_label.size()

        # Berechne den Offset durch die Zentrierung im Label
        off_x = (l_size.width() - p_size.width()) // 2
        off_y = (l_size.height() - p_size.height()) // 2

        # Skalierungsfaktoren zwischen Label-Bild und Original-PIL-Bild
        sx = self.pil_image.width / p_size.width()
        sy = self.pil_image.height / p_size.height()

        # Koordinaten umrechnen (begrenzt auf Bildbereich)
        l = max(0, int((rect.x() - off_x) * sx))
        t = max(0, int((rect.y() - off_y) * sy))
        r = min(self.pil_image.width, int((rect.x() + rect.width() - off_x) * sx))
        b = min(self.pil_image.height, int((rect.y() + rect.height() - off_y) * sy))

        if r > l and b > t:
            self.save_history()
            self.pil_image = self.pil_image.crop((l, t, r, b))
            self.refresh_display()

    def save_image(self):
        """Sichert das Originalbild und speichert die Änderungen."""
        try:
            # 1. Backup-Pfad im Projekt-Backup-Ordner erstellen
            backup_base = os.path.join(self.project_root, "backup", "edits")
            os.makedirs(backup_base, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(self.image_path)
            backup_path = os.path.join(backup_base, f"{timestamp}_{filename}.bak")
            
            # 2. Original sichern
            shutil.copy2(self.image_path, backup_path)
            
            # 3. Neues Bild speichern
            self.pil_image.save(self.image_path)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), str(e))
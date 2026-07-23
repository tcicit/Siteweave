import os
import yaml
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout, 
                             QGraphicsDropShadowEffect, QWidget, QPushButton)
from PyQt6.QtGui import QPixmap, QFont, QColor, QDesktopServices
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from core.i18n import _

class ProjectCard(QFrame):
    """
    Ein modernes Karten-Widget für den Project Launcher.
    Realisiert die Darstellung von Projekt-Karten mit Vorschau, Logo und Pfad.
    """
    clicked = pyqtSignal(str) # Sendet den absoluten Projektpfad bei Klick

    def __init__(self, name, path, logo_path=None, preview_path=None, parent=None):
        super().__init__(parent)
        self.project_path = path
        self.exists = os.path.exists(path)
        self.output_dir = "site_output"
        self.setFixedWidth(280)
        self.setFixedHeight(260)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setObjectName("ProjectCard")
        # Modernes Styling mit abgerundeten Ecken und Hover-Effekt
        if not self.exists:
            self.setStyleSheet("""
                #ProjectCard {
                    background-color: #fff5f5;
                    border: 2px solid #fc8181;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                #ProjectCard {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 12px;
                }
                #ProjectCard:hover {
                    border: 2px solid #3498db;
                    background-color: #fcfdfe;
                }
            """)

        # Browser-Button (Overlay oben rechts) - Erstellung bleibt gleich
        self.browser_btn = QPushButton("🌐", self)
        self.browser_btn.setFixedSize(30, 30)
        self.browser_btn.move(240, 10)
        self.browser_btn.setToolTip(_("Open in Browser"))
        self.browser_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 220);
                border: 1px solid #ccc;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: white;
                border-color: #3498db;
                color: #3498db;
            }
        """)
        self.browser_btn.clicked.connect(self.open_in_browser)
        self.browser_btn.setEnabled(self.exists)

        # Schatten-Effekt für Tiefe (Card-Design)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Vorschaubild-Bereich (Oben)
        self.preview_label = QLabel()
        self.preview_label.setFixedHeight(150)
        # WICHTIG: Oben ausrichten, damit der Header sichtbar ist
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        if not self.exists:
            self.preview_label.setText(_("Path Missing"))
            self.preview_label.setStyleSheet("border-top-left-radius: 11px; border-top-right-radius: 11px; background-color: #fed7d7; color: #c53030; font-weight: bold;")
        elif preview_path and os.path.exists(preview_path):
            self.preview_label.setStyleSheet("border-top-left-radius: 11px; border-top-right-radius: 11px; background-color: #f0f2f5;")
            pixmap = QPixmap(preview_path).scaled(280, 150, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.setText("Keine Vorschau")
            self.preview_label.setStyleSheet("border-top-left-radius: 11px; border-top-right-radius: 11px; background-color: #e9ecef; color: #adb5bd; font-weight: bold;")
            
        layout.addWidget(self.preview_label)

        # 2. Informations-Bereich (Unten)
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(15, 12, 15, 15)
        info_layout.setSpacing(6)

        # Kopfzeile: Logo + Titel
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(32, 32)
        if logo_path and os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(logo_pixmap)
        else:
            self.logo_label.setText("📄") # Fallback Icon
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_label.setStyleSheet("font-size: 18px; background: #eee; border-radius: 4px;")
        header_layout.addWidget(self.logo_label)

        self.title_label = QLabel(name)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(self.title_label, 1)
        info_layout.addLayout(header_layout)

        # Dateipfad (mit Elide/Kürzung in der Mitte)
        self.path_label = QLabel(path)
        self.path_label.setFont(QFont("Segoe UI", 8))
        self.path_label.setStyleSheet("color: #95a5a6;")
        metrics = self.path_label.fontMetrics()
        elided_path = metrics.elidedText(path, Qt.TextElideMode.ElideMiddle, 240)
        self.path_label.setText(elided_path)
        self.path_label.setToolTip(path) # Zeigt vollen Pfad beim Hover
        info_layout.addWidget(self.path_label)
        
        layout.addWidget(info_container)

        # WICHTIG: Den Button in der Z-Ebene ganz nach oben bringen, 
        # damit er über dem Bild liegt.
        self.browser_btn.raise_()

    def open_in_browser(self):
        """Öffnet die index.html des Projekts im Standard-Browser."""
        index_path = os.path.normpath(os.path.join(self.project_path, self.output_dir, "index.html"))
        if os.path.exists(index_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(index_path))

    @classmethod
    def from_path(cls, project_path):
        """Fabrik-Methode: Erstellt eine Karte durch Analyse des Projektordners."""
        name = os.path.basename(project_path)
        logo_path = None
        preview_path = os.path.join(project_path, "preview.png")
        output_dir = "site_output"
        
        config_file = os.path.join(project_path, "config.yaml")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    cfg = yaml.safe_load(f)
                    name = cfg.get('site_name', name)
                    rel_logo = cfg.get('site_logo')
                    if rel_logo: logo_path = os.path.join(project_path, rel_logo)
                    output_dir = cfg.get('site_output_directory', output_dir)
            except: pass
        card = cls(name, project_path, logo_path, preview_path)
        card.output_dir = output_dir
        # Button nur anzeigen, wenn index.html existiert
        index_path = os.path.join(project_path, output_dir, "index.html")
        card.browser_btn.setVisible(os.path.exists(index_path))
        return card

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.project_path)
        super().mousePressEvent(event)
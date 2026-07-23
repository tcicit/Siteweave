from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QListWidget, QListWidgetItem, QProgressBar, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.i18n import _

class StatCard(QFrame):
    def __init__(self, title, value, color="#2980b9", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.accent_color = color
        layout = QVBoxLayout(self)
        self.title_lbl = QLabel(title.upper())
        self.value_lbl = QLabel(str(value))
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)

    def set_dark_mode(self, enabled):
        bg = "#1e1e1e" if enabled else "white"
        text_title = "#95a5a6" if enabled else "#7f8c8d"
        text_val = "#ecf0f1" if enabled else "#2c3e50"
        border = "#333" if enabled else "#ddd"
        
        # Nutze direktes Styling ohne QFrame-Selektor für mehr Stabilität
        self.setStyleSheet(f"""
            background-color: {bg};
            border-radius: 8px;
            border: 1px solid {border};
            border-left: 5px solid {self.accent_color};
            padding: 15px;
        """)
        if hasattr(self, 'title_lbl'):
            self.title_lbl.setStyleSheet(f"color: {text_title}; font-size: 10px; font-weight: bold; background: transparent; border: none;")
        if hasattr(self, 'value_lbl'):
            self.value_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {text_val}; background: transparent; border: none;")

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.setup_ui()

    def set_dark_mode(self, enabled):
        """Passt das Dashboard an das gewählte Theme an."""
        title_color = "#ecf0f1" if enabled else "#34495e"
        list_bg = "#1e1e1e" if enabled else "white"
        list_border = "#333" if enabled else "#ddd"
        
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {title_color};")
        if hasattr(self, 'recent_list'):
            self.recent_list.setStyleSheet(f"border-radius: 5px; border: 1px solid {list_border}; background: {list_bg};")
        
        if hasattr(self, 'cards'):
            for card in self.cards.values():
                card.set_dark_mode(enabled)

    def setup_ui(self):
        # Titel
        header_layout = QHBoxLayout()
        self.title_label = QLabel(_("Project Dashboard"))
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Dashboard Buttons
        self.refresh_btn = QPushButton(_("Refresh"))
        self.refresh_btn.setToolTip(_("Refresh statistics (F5)"))
        self.close_btn = QPushButton(_("Close"))
        self.close_btn.setShortcut("Esc")
        self.close_btn.setToolTip(_("Close dashboard (Esc)"))
        header_layout.addWidget(self.refresh_btn)
        header_layout.addWidget(self.close_btn)

        self.main_layout.addLayout(header_layout)

        # Grid für die Status-Karten
        grid = QGridLayout()
        self.cards = {
            'pub': StatCard(_("Published"), "0", "#27ae60", self),
            'draft': StatCard(_("Drafts"), "0", "#e67e22", self),
            'size': StatCard(_("Website Size"), "0 MB", "#9b59b6", self),
            'render': StatCard(_("Last Render"), _("Never"), "#3498db", self)
        }
        
        grid.addWidget(self.cards['pub'], 0, 0)
        grid.addWidget(self.cards['draft'], 0, 1)
        grid.addWidget(self.cards['size'], 1, 0)
        grid.addWidget(self.cards['render'], 1, 1)
        self.main_layout.addLayout(grid)

        # Sektion: Letzte Änderungen
        self.main_layout.addWidget(QLabel(f"<b>{_('Recently edited documents')}</b>"))
        self.recent_list = QListWidget()
        self.main_layout.addWidget(self.recent_list)
        
        # Status-Bar (z.B. für SEO oder Link-Warnungen)
        self.loader = QProgressBar()
        self.loader.setRange(0, 0) # Unbestimmter Modus (Animation)
        self.loader.setFixedHeight(4)
        self.loader.setTextVisible(False)
        self.loader.hide()
        self.main_layout.addWidget(self.loader)

        self.status_msg = QLabel(_("Ready."))
        self.status_msg.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.main_layout.addWidget(self.status_msg)

    def set_loading(self, enabled):
        """Zeigt oder versteckt den Lade-Indikator."""
        self.loader.setVisible(enabled)
        if enabled:
            self.status_msg.setText(_("Scanning project files..."))

    def refresh(self, stats):
        """Aktualisiert die Anzeige mit neuen Daten."""
        self.set_loading(False)
        if hasattr(self, 'cards'):
            self.cards['pub'].value_lbl.setText(str(stats.get('pages', {}).get('published', 0)))
            self.cards['draft'].value_lbl.setText(str(stats.get('pages', {}).get('drafts', 0)))
            self.cards['size'].value_lbl.setText(stats.get('output_size', '0 B'))
            self.cards['render'].value_lbl.setText(stats.get('last_render', _('Never')))
        
        if hasattr(self, 'recent_list'):
            self.recent_list.clear()
            for f in stats.get('recent_files', []):
                item = QListWidgetItem(f"{f['name']} — {f['date']}")
                item.setData(Qt.ItemDataRole.UserRole, f.get('full_path'))
                self.recent_list.addItem(item)
            
        if hasattr(self, 'status_msg'):
            if stats.get('seo_warnings', 0) > 0:
                self.status_msg.setText(_("⚠️ Warning: {count} SEO issues found (missing titles or descriptions).").format(count=stats['seo_warnings']))
                self.status_msg.setStyleSheet("color: #e74c3c; font-weight: bold;")
            else:
                self.status_msg.setText(_("✅ All documents appear to be correctly formatted."))
import os
import yaml
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QFrame, QGridLayout,
    QButtonGroup, QSizePolicy, QDialogButtonBox, QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon, QFont, QCursor
from PyQt6.QtCore import Qt, pyqtSignal

from core import APP_NAME
from core.config_manager import ConfigManager
from core.i18n import _


class TemplateCard(QFrame):
    """
    Visuelle Kachel für ein einzelnes Theme / Template in der Galerie.
    """
    clicked = pyqtSignal(str)
    double_clicked = pyqtSignal(str)

    def __init__(self, theme_data, is_selected=False, parent=None):
        super().__init__(parent)
        self.theme_data = theme_data
        self.theme_id = theme_data.get("id", "none")
        self.is_selected = is_selected

        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)

        self.init_ui()
        self.update_style()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 12)
        layout.setSpacing(8)

        # 1. Vorschaubild (Screenshot)
        self.img_lbl = QLabel()
        self.img_lbl.setFixedHeight(155)
        self.img_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setStyleSheet("border-radius: 6px; background-color: palette(alternate-base);")

        preview_path = self.theme_data.get("preview_path")
        if preview_path and os.path.exists(preview_path):
            pix = QPixmap(preview_path)
            self.img_lbl.setPixmap(
                pix.scaled(
                    280, 155,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            self.img_lbl.setText("🖼️ " + _("No preview"))

        layout.addWidget(self.img_lbl)

        # 2. Kategorie-Badge & Name
        meta_layout = QHBoxLayout()
        meta_layout.setContentsMargins(0, 0, 0, 0)

        category = self.theme_data.get("category", _("General"))
        cat_badge = QLabel(f" {category} ")
        cat_badge.setStyleSheet(
            "background-color: palette(midlight); color: palette(text); "
            "border-radius: 4px; font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )
        meta_layout.addWidget(cat_badge)
        meta_layout.addStretch()

        self.check_lbl = QLabel("✓" if self.is_selected else "")
        self.check_lbl.setStyleSheet("color: palette(highlight); font-weight: bold; font-size: 14px;")
        meta_layout.addWidget(self.check_lbl)

        layout.addLayout(meta_layout)

        # 3. Titel
        title_lbl = QLabel(self.theme_data.get("title", self.theme_id))
        title_font = title_lbl.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 1)
        title_lbl.setFont(title_font)
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        # 4. Kurzbeschreibung
        desc = self.theme_data.get("description", "")
        if len(desc) > 90:
            desc = desc[:87] + "..."
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: palette(placeholder-text); font-size: 11px;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        # 5. Tags
        tags = self.theme_data.get("tags", [])
        if tags:
            tags_text = " • ".join(tags[:3])
            tags_lbl = QLabel(tags_text)
            tags_lbl.setStyleSheet("color: palette(mid); font-size: 10px;")
            layout.addWidget(tags_lbl)

    def set_selected(self, selected):
        self.is_selected = selected
        self.check_lbl.setText("✓" if self.is_selected else "")
        self.update_style()

    def update_style(self):
        if self.is_selected:
            self.setStyleSheet(
                "TemplateCard { "
                "   border: 2px solid palette(highlight); "
                "   border-radius: 8px; "
                "   background-color: palette(base); "
                "}"
            )
        else:
            self.setStyleSheet(
                "TemplateCard { "
                "   border: 1px solid palette(mid); "
                "   border-radius: 8px; "
                "   background-color: palette(window); "
                "} "
                "TemplateCard:hover { "
                "   border: 1px solid palette(highlight); "
                "   background-color: palette(base); "
                "}"
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.theme_id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.theme_id)
        super().mouseDoubleClickEvent(event)


class TemplateLibraryDialog(QDialog):
    """
    Grafische Vorlagen-Bibliothek zur visuellen Auswahl von Themes/Templates.
    """

    def __init__(self, app_root, selected_theme="none", parent=None):
        super().__init__(parent)
        self.app_root = app_root
        self.selected_theme = selected_theme
        self.themes = []
        self.card_widgets = {}

        self.setWindowTitle(_("Template Library - Website Designs"))
        self.resize(1000, 680)
        self.setMinimumSize(880, 560)

        # App Icon
        icon_path = os.path.join(self.app_root, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.load_themes()
        self.init_ui()

    def load_themes(self):
        """Liest alle verfügbaren Themes und deren Metadaten ein."""
        self.themes = []

        # 1. Virtueller Minimal-Eintrag
        minimal_preview = os.path.join(self.app_root, "assets", "previews", "minimal.png")
        self.themes.append({
            "id": "none",
            "name": "none",
            "title": _("Minimal (No Theme)"),
            "category": _("Minimal"),
            "description": _("A clean HTML5 & CSS starter skeleton without predefined styles. Perfect if you prefer to build your own custom design from scratch."),
            "author": "Siteweave",
            "version": "1.0",
            "tags": ["Minimal", "HTML5", "Clean", "DIY"],
            "preview_path": minimal_preview,
            "layouts": ["layout_full-width.html", "base.html"]
        })

        # 2. Themes-Ordner durchsuchen
        themes_dir = os.path.join(self.app_root, "themes")
        app_config_file = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_file):
            try:
                cfg = ConfigManager(app_config_file).load() or {}
                rel = cfg.get("paths", {}).get("themes", "themes")
                themes_dir = rel if os.path.isabs(rel) else os.path.join(self.app_root, rel)
            except Exception:
                pass

        if os.path.isdir(themes_dir):
            for item in sorted(os.listdir(themes_dir)):
                theme_path = os.path.join(themes_dir, item)
                if item.startswith(".") or not os.path.isdir(theme_path):
                    continue

                theme_data = {
                    "id": item,
                    "name": item,
                    "title": item.replace("-", " ").title(),
                    "category": _("General"),
                    "description": _("Ready-to-use website layout and styles."),
                    "author": "Siteweave",
                    "version": "1.0",
                    "tags": [],
                    "preview_path": os.path.join(theme_path, "preview.png"),
                    "layouts": []
                }

                # theme.yaml einlesen falls vorhanden
                meta_file = os.path.join(theme_path, "theme.yaml")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            custom_meta = yaml.safe_load(f) or {}
                            theme_data.update(custom_meta)
                    except Exception:
                        pass

                # Vorhandene Layout-Dateien ermitteln
                tpl_dir = os.path.join(theme_path, "templates")
                if os.path.isdir(tpl_dir):
                    layouts = [
                        f for f in os.listdir(tpl_dir)
                        if f.endswith(".html") and not f.startswith("_")
                    ]
                    theme_data["layouts"] = sorted(layouts)

                self.themes.append(theme_data)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # 1. Header & Such-/Filter-Leiste
        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        h_title = QLabel(_("Template Library"))
        f = h_title.font()
        f.setPointSize(f.pointSize() + 4)
        f.setBold(True)
        h_title.setFont(f)
        title_box.addWidget(h_title)

        h_sub = QLabel(_("Choose a pre-designed layout for your website. You can customize colors and pages anytime."))
        h_sub.setStyleSheet("color: palette(placeholder-text);")
        title_box.addWidget(h_sub)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Suchfeld
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search templates..."))
        self.search_input.setFixedWidth(240)
        self.search_input.textChanged.connect(self.filter_cards)
        header_layout.addWidget(self.search_input)

        main_layout.addLayout(header_layout)

        # 2. Kategorie-Filter-Leiste
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(6)

        self.filter_group = QButtonGroup(self)
        self.filter_group.setExclusive(True)

        categories = [_("All")]
        for t in self.themes:
            cat = t.get("category")
            if cat and cat not in categories:
                categories.append(cat)

        for i, cat in enumerate(categories):
            btn = QPushButton(cat)
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            btn.setStyleSheet(
                "QPushButton { padding: 5px 14px; border-radius: 12px; border: 1px solid palette(mid); } "
                "QPushButton:checked { background-color: palette(highlight); color: palette(highlighted-text); font-weight: bold; }"
            )
            btn.clicked.connect(self.filter_cards)
            self.filter_group.addButton(btn, i)
            filter_bar.addWidget(btn)

        filter_bar.addStretch()
        main_layout.addLayout(filter_bar)

        # 3. Hauptbereich: Galerie links + Detail-Seitenleiste rechts
        content_splitter = QHBoxLayout()
        content_splitter.setSpacing(16)

        # Scrollbereich für Kacheln
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(14)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.grid_container)
        content_splitter.addWidget(self.scroll_area, stretch=3)

        # Detail-Seitenleiste
        self.detail_panel = QFrame()
        self.detail_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.detail_panel.setFixedWidth(300)
        self.detail_panel.setStyleSheet("QFrame { background-color: palette(window); border-radius: 8px; }")

        detail_layout = QVBoxLayout(self.detail_panel)
        detail_layout.setContentsMargins(14, 14, 14, 14)
        detail_layout.setSpacing(10)

        detail_header = QLabel(_("Template Details"))
        detail_header.setStyleSheet("font-weight: bold; font-size: 13px;")
        detail_layout.addWidget(detail_header)

        self.detail_preview = QLabel()
        self.detail_preview.setFixedHeight(160)
        self.detail_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_preview.setStyleSheet("border-radius: 6px; background-color: palette(alternate-base); border: 1px solid palette(mid);")
        detail_layout.addWidget(self.detail_preview)

        self.detail_title = QLabel()
        dt_font = self.detail_title.font()
        dt_font.setBold(True)
        dt_font.setPointSize(dt_font.pointSize() + 2)
        self.detail_title.setFont(dt_font)
        self.detail_title.setWordWrap(True)
        detail_layout.addWidget(self.detail_title)

        self.detail_cat = QLabel()
        self.detail_cat.setStyleSheet("color: palette(highlight); font-weight: bold; font-size: 11px;")
        detail_layout.addWidget(self.detail_cat)

        self.detail_desc = QLabel()
        self.detail_desc.setStyleSheet("color: palette(text); font-size: 12px; line-height: 1.4;")
        self.detail_desc.setWordWrap(True)
        detail_layout.addWidget(self.detail_desc)

        # Layout-Dateien
        self.layouts_hdr = QLabel(_("Included Layouts:"))
        self.layouts_hdr.setStyleSheet("font-weight: bold; font-size: 11px; margin-top: 6px;")
        detail_layout.addWidget(self.layouts_hdr)

        self.detail_layouts = QLabel()
        self.detail_layouts.setStyleSheet("color: palette(placeholder-text); font-size: 11px;")
        self.detail_layouts.setWordWrap(True)
        detail_layout.addWidget(self.detail_layouts)

        detail_layout.addStretch()

        # Auswählen Button in der Detailansicht
        self.select_in_detail_btn = QPushButton(_("Use This Template"))
        self.select_in_detail_btn.setStyleSheet(
            "QPushButton { background-color: palette(highlight); color: palette(highlighted-text); font-weight: bold; padding: 10px; border-radius: 6px; } "
            "QPushButton:hover { opacity: 0.9; }"
        )
        self.select_in_detail_btn.clicked.connect(self.accept)
        detail_layout.addWidget(self.select_in_detail_btn)

        content_splitter.addWidget(self.detail_panel, stretch=1)
        main_layout.addLayout(content_splitter)

        # 4. Fußzeile
        footer_layout = QHBoxLayout()
        self.status_lbl = QLabel()
        self.status_lbl.setStyleSheet("color: palette(placeholder-text); font-size: 11px;")
        footer_layout.addWidget(self.status_lbl)

        footer_layout.addStretch()

        self.cancel_btn = QPushButton(_("Cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton(_("Use Template"))
        self.confirm_btn.setStyleSheet("font-weight: bold; padding: 6px 18px;")
        self.confirm_btn.clicked.connect(self.accept)
        footer_layout.addWidget(self.confirm_btn)

        main_layout.addLayout(footer_layout)

        # Kacheln füllen
        self.render_cards()
        self.update_detail_panel()

    def render_cards(self):
        """Erzeugt die Template-Karten im Grid."""
        # Alte Kacheln entfernen
        for card in self.card_widgets.values():
            card.deleteLater()
        self.card_widgets.clear()

        cols = 2
        for idx, t in enumerate(self.themes):
            t_id = t.get("id")
            is_sel = (t_id == self.selected_theme)
            card = TemplateCard(t, is_selected=is_sel, parent=self.grid_container)
            card.clicked.connect(self.select_theme)
            card.double_clicked.connect(self.select_and_accept)

            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col)
            self.card_widgets[t_id] = card

        self.status_lbl.setText(_("{count} templates available").format(count=len(self.themes)))

    def filter_cards(self):
        """Filtert die angezeigten Kacheln nach Suchbegriff und Kategorie."""
        search_term = self.search_input.text().strip().lower()
        active_btn = self.filter_group.checkedButton()
        category_filter = active_btn.text() if active_btn else _("All")

        visible_count = 0
        cols = 2

        # Vorübergehend alle aus dem Layout entfernen und nur passende neu anordnen
        visible_cards = []
        for t in self.themes:
            t_id = t.get("id")
            card = self.card_widgets.get(t_id)
            if not card:
                continue

            matches_cat = (category_filter == _("All")) or (t.get("category") == category_filter)

            matches_search = True
            if search_term:
                searchable_text = f"{t.get('title', '')} {t.get('description', '')} {' '.join(t.get('tags', []))} {t_id}".lower()
                matches_search = (search_term in searchable_text)

            is_visible = matches_cat and matches_search
            card.setVisible(is_visible)
            if is_visible:
                visible_cards.append(card)
                visible_count += 1

        # Neu im Raster anordnen
        for i, card in enumerate(visible_cards):
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(card, row, col)

        self.status_lbl.setText(_("{count} templates found").format(count=visible_count))

    def select_theme(self, theme_id):
        """Wählt ein Theme aus und aktualisiert die Kachel-Markierungen und Detailansicht."""
        self.selected_theme = theme_id
        for tid, card in self.card_widgets.items():
            card.set_selected(tid == theme_id)
        self.update_detail_panel()

    def select_and_accept(self, theme_id):
        """Wählt ein Theme per Doppelklick aus und schließt den Dialog direkt mit Accept."""
        self.select_theme(theme_id)
        self.accept()

    def update_detail_panel(self):
        """Aktualisiert die rechte Detailansicht für das gewählte Theme."""
        theme_data = next((t for t in self.themes if t.get("id") == self.selected_theme), None)
        if not theme_data and self.themes:
            theme_data = self.themes[0]
            self.selected_theme = theme_data.get("id")

        if not theme_data:
            return

        self.detail_title.setText(theme_data.get("title", theme_data.get("id")))
        self.detail_cat.setText(theme_data.get("category", _("General")).upper())
        self.detail_desc.setText(theme_data.get("description", ""))

        # Preview Bild
        preview_path = theme_data.get("preview_path")
        if preview_path and os.path.exists(preview_path):
            pix = QPixmap(preview_path)
            self.detail_preview.setPixmap(
                pix.scaled(
                    270, 160,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            self.detail_preview.setText("")
        else:
            self.detail_preview.setPixmap(QPixmap())
            self.detail_preview.setText("🖼️ " + _("No preview"))

        # Layouts
        layouts = theme_data.get("layouts", [])
        if layouts:
            self.detail_layouts.setText("\n".join([f"• {l}" for l in layouts]))
        else:
            self.detail_layouts.setText(_("Default layouts"))

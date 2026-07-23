import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                             QCheckBox, QDateEdit, QComboBox, QScrollArea, QFrame, QPushButton, QSizePolicy,
                             QHBoxLayout, QFileDialog, QLabel, QCompleter, QSpinBox)
from PyQt6.QtCore import QDate, pyqtSignal, Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from core.i18n import _

'''
Docstring for main_window
Main application window.    
- Contains the editor, preview, and various panels (Outline, Snippets, Frontmatter, Log Viewer).
- Manages app and project configuration, actions, menus and toolbars.
- Allows loading, editing and saving Markdown files with frontmatter.
- Supports themes, localization and running worker scripts. 
The main class is `MainWindow`, which inherits from `QMainWindow`.
'''

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.base_path = None

    def set_base_path(self, path):
        self.base_path = path

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if self.base_path:
                    try:
                        base_dir = os.path.dirname(self.base_path)
                        rel_path = os.path.relpath(file_path, base_dir)
                        rel_path = rel_path.replace(os.path.sep, '/')
                        self.setText(rel_path)
                    except ValueError:
                        self.setText(file_path)
                else:
                    self.setText(file_path)
            event.accept()
        else:
            super().dropEvent(event)

class MultiValueLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._completer = None

    def set_completer(self, completer):
        self._completer = completer
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        text = self.text()
        cursor_pos = self.cursorPosition()
        
        # Finde den Anfang des aktuellen Tags
        last_comma_index = text.rfind(',', 0, cursor_pos)
        start_index = last_comma_index + 1
        
        prefix = text[:start_index]
        suffix = text[cursor_pos:]
        
        # Leerzeichen nach Komma erzwingen
        if prefix.endswith(','):
            prefix += " "
            
        self.setText(prefix + completion + ", " + suffix)
        self.setCursorPosition(len(prefix) + len(completion) + 2)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if not self._completer:
            return

        text = self.text()
        cursor_pos = self.cursorPosition()
        
        last_comma_index = text.rfind(',', 0, cursor_pos)
        current_prefix = text[last_comma_index + 1:cursor_pos].strip()
        
        if len(current_prefix) > 0:
            self._completer.setCompletionPrefix(current_prefix)
            if self._completer.completionCount() > 0:
                cr = self.cursorRect()
                cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
                self._completer.complete(cr)
            else:
                self._completer.popup().hide()
        else:
            self._completer.popup().hide()

class FrontmatterPanel(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle Button
        self.toggle_btn = QPushButton(_("Frontmatter ▼"))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                font-weight: bold;
                padding: 6px;
                border: 1px solid palette(mid);
                background-color: palette(button);
            }
        """)
        self.toggle_btn.toggled.connect(self.toggle_content)
        layout.addWidget(self.toggle_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        self.form_layout = QFormLayout(content_widget)
        
        # Felder definieren
        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        
        self.release_date_edit = QDateEdit()
        self.release_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.release_date_edit.setCalendarPopup(True)
        
        self.layout_combo = QComboBox()
        self.layout_combo.setEditable(True) # Erlaubt auch eigene Eingaben
        
        self.weight_edit = QSpinBox()
        self.weight_edit.setRange(-1000, 1000)
        self.weight_edit.setSingleStep(1)
        self.weight_edit.setValue(0)
        self.weight_edit.setToolTip(_("Lower numbers appear first (e.g. -10 before 0)."))

        self.tags_edit = MultiValueLineEdit()
        self.tags_edit.setPlaceholderText("tag1, tag2")
        
        self.featured_image_edit = DropLineEdit()
        self.featured_image_edit.setPlaceholderText(_("Path to image"))
        
        # Layout für Bild-Auswahl (Input + Button)
        image_layout = QHBoxLayout()
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.addWidget(self.featured_image_edit)
        self.select_image_btn = QPushButton("...")
        self.select_image_btn.setFixedWidth(30)
        self.select_image_btn.clicked.connect(self.select_featured_image)
        image_layout.addWidget(self.select_image_btn)

        # Bild-Vorschau Label
        self.image_preview_label = QLabel(_("No Image"))
        self.image_preview_label.setFixedSize(200, 150)
        self.image_preview_label.setStyleSheet("border: 1px solid palette(mid); border-radius: 4px;")
        self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.draft_check = QCheckBox()
        self.breadcrumbs_check = QCheckBox()
        
        # Formular zusammenbauen
        self.form_layout.addRow(_("Title:"), self.title_edit)
        self.form_layout.addRow(_("Author:"), self.author_edit)
        self.form_layout.addRow(_("Date:"), self.date_edit)
        self.form_layout.addRow(_("Release:"), self.release_date_edit)
        self.form_layout.addRow(_("Layout:"), self.layout_combo)
        self.form_layout.addRow(_("Weight:"), self.weight_edit)
        self.form_layout.addRow(_("Tags:"), self.tags_edit)
        self.form_layout.addRow(_("Image:"), image_layout)
        self.form_layout.addRow("", self.image_preview_label)
        self.form_layout.addRow(_("Draft:"), self.draft_check)
        self.form_layout.addRow(_("Breadcrumbs:"), self.breadcrumbs_check)
        
        self.scroll.setWidget(content_widget)
        layout.addWidget(self.scroll)
        
        # Signale verbinden
        self.title_edit.textChanged.connect(self.emit_changed)
        self.author_edit.textChanged.connect(self.emit_changed)
        self.date_edit.dateChanged.connect(self.emit_changed)
        self.release_date_edit.dateChanged.connect(self.emit_changed)
        self.layout_combo.currentTextChanged.connect(self.emit_changed)
        self.weight_edit.valueChanged.connect(self.emit_changed)
        self.tags_edit.textChanged.connect(self.emit_changed)
        self.featured_image_edit.textChanged.connect(self.emit_changed)
        self.featured_image_edit.textChanged.connect(self.update_image_preview)
        self.draft_check.toggled.connect(self.emit_changed)
        self.breadcrumbs_check.toggled.connect(self.emit_changed)
        
        # Speicher für unbekannte Felder, damit diese nicht verloren gehen
        self.extra_data = {}

        # Initiale Validierung
        self.validate_fields()

    def set_dark_mode(self, enabled):
        """Wendet das Dark-Mode-Styling auf die Panel-spezifischen Widgets an."""
        # Toggle Button aktualisieren (da er ein Stylesheet mit palette() hat)
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)
        
        # Image Preview Label aktualisieren
        self.image_preview_label.style().unpolish(self.image_preview_label)
        self.image_preview_label.style().polish(self.image_preview_label)

    def toggle_content(self, checked):
        self.scroll.setVisible(checked)
        self.toggle_btn.setText(_("Frontmatter ▼") if checked else _("Frontmatter ▶"))

        if checked:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.setMaximumHeight(16777215)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.setMaximumHeight(self.toggle_btn.sizeHint().height())

    def set_current_file_path(self, path):
        self.featured_image_edit.set_base_path(path)
        self.update_image_preview()

    def set_available_tags(self, tags):
        completer = QCompleter(tags)
        self.tags_edit.set_completer(completer)

    def select_featured_image(self):
        start_dir = "."
        if self.featured_image_edit.base_path:
             start_dir = os.path.dirname(self.featured_image_edit.base_path)
        
        file_path, unused_filter = QFileDialog.getOpenFileName(
            self, _("Select Image"), start_dir, _("Images (*.png *.jpg *.jpeg *.gif *.svg *.webp);;All Files (*)")
        )
        
        if file_path:
            if self.featured_image_edit.base_path:
                try:
                    base_dir = os.path.dirname(self.featured_image_edit.base_path)
                    rel_path = os.path.relpath(file_path, base_dir)
                    rel_path = rel_path.replace(os.path.sep, '/')
                    self.featured_image_edit.setText(rel_path)
                except ValueError:
                    self.featured_image_edit.setText(file_path)
            else:
                self.featured_image_edit.setText(file_path)

    def update_image_preview(self):
        path = self.featured_image_edit.text().strip()
        if not path:
            self.image_preview_label.clear()
            self.image_preview_label.setText(_("No Image"))
            return

        full_path = path
        if self.featured_image_edit.base_path and not os.path.isabs(path):
            base_dir = os.path.dirname(self.featured_image_edit.base_path)
            full_path = os.path.join(base_dir, path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.image_preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_preview_label.setPixmap(scaled)
            else:
                self.image_preview_label.setText(_("Invalid"))
        else:
            self.image_preview_label.setText(_("Not Found"))

    def emit_changed(self):
        self.validate_fields()
        self.dataChanged.emit()

    def validate_fields(self):
        # Titel ist ein Pflichtfeld
        if not self.title_edit.text().strip():
            self.title_edit.setStyleSheet("border: 2px solid #e74c3c;")
            self.title_edit.setToolTip(_("Title is required"))
        else:
            self.title_edit.setStyleSheet("")
            self.title_edit.setToolTip("")

    def populate_layouts(self, template_dirs):
        self.layout_combo.clear()
        self.layout_combo.addItem("full-width")
        
        if isinstance(template_dirs, str):
            template_dirs = [template_dirs]
            
        added_layouts = {"full-width"}
        
        for template_dir in template_dirs:
            if os.path.exists(template_dir):
                for filename in os.listdir(template_dir):
                    if filename.startswith("layout_") and filename.endswith(".html"):
                        layout_name = filename[7:-5]
                        if layout_name not in added_layouts:
                            self.layout_combo.addItem(layout_name)
                            added_layouts.add(layout_name)

    def set_data(self, metadata):
        self.blockSignals(True) # Verhindert dataChanged beim Laden
        try:
            self.title_edit.setText(str(metadata.get('title', '')))
            self.author_edit.setText(str(metadata.get('author', '')))
            
            # Datum sicher parsen (kann String oder date-Objekt sein)
            d = metadata.get('date', QDate.currentDate())
            self.date_edit.setDate(QDate.fromString(str(d)[:10], "yyyy-MM-dd") if d else QDate.currentDate())
            
            rd = metadata.get('release_date', QDate.currentDate())
            self.release_date_edit.setDate(QDate.fromString(str(rd)[:10], "yyyy-MM-dd") if rd else QDate.currentDate())

            self.layout_combo.setCurrentText(str(metadata.get('layout', 'full-width')))
            
            weight_val = metadata.get('weight', 0)
            try:
                self.weight_edit.setValue(int(weight_val))
            except (ValueError, TypeError):
                self.weight_edit.setValue(0)

            tags = metadata.get('tags', [])
            self.tags_edit.setText(", ".join(str(t) for t in tags) if isinstance(tags, list) else str(tags))
                
            self.featured_image_edit.setText(str(metadata.get('featured_image', '')))
            self.draft_check.setChecked(bool(metadata.get('draft', False)))
            self.breadcrumbs_check.setChecked(bool(metadata.get('breadcrumbs', True)))
            
            # Unbekannte Felder speichern
            known_keys = {'title', 'author', 'date', 'release_date', 'layout', 'weight', 'tags', 'featured_image', 'draft', 'breadcrumbs'}
            self.extra_data = {k: v for k, v in metadata.items() if k not in known_keys}
        finally:
            self.blockSignals(False)
        self.validate_fields()
        self.update_image_preview()

    def get_data(self):
        data = self.extra_data.copy()
        data['title'] = self.title_edit.text()
        data['author'] = self.author_edit.text()
        data['date'] = self.date_edit.date().toString("yyyy-MM-dd")
        data['release_date'] = self.release_date_edit.date().toString("yyyy-MM-dd")
        data['layout'] = self.layout_combo.currentText()
        
        weight_val = self.weight_edit.value()
        if weight_val != 0:
            data['weight'] = weight_val

        tags_text = self.tags_edit.text()
        data['tags'] = [t.strip() for t in tags_text.split(',') if t.strip()]
        
        data['featured_image'] = self.featured_image_edit.text().strip()
            
        data['draft'] = self.draft_check.isChecked()
        data['breadcrumbs'] = self.breadcrumbs_check.isChecked()
        
        return data
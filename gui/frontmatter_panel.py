import os
import shutil
import filecmp
import yaml
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                             QCheckBox, QDateEdit, QComboBox, QScrollArea, QFrame, QPushButton, QSizePolicy, QMessageBox,
                             QHBoxLayout, QFileDialog, QLabel, QCompleter, QSpinBox)
from PyQt6.QtCore import QDate, pyqtSignal, Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from core.i18n import _

"""
FrontmatterPanel: Dock widget for viewing and editing Markdown YAML frontmatter.
Provides inputs for title, author, dates, tags, layout, and featured image.
"""

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.base_path = None
        self.project_root = None

    def set_base_path(self, path):
        self.base_path = path

    def set_project_root(self, root):
        self.project_root = root

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
                # Wenn das Bild außerhalb des Projekts liegt: in assets/images kopieren
                if self.project_root and os.path.isfile(file_path):
                    abs_file = os.path.abspath(file_path)
                    abs_proj = os.path.abspath(self.project_root)
                    try:
                        is_inside = (os.path.commonpath([abs_proj, abs_file]) == abs_proj)
                    except ValueError:
                        is_inside = False
                    if not is_inside:
                        dest_dir = os.path.join(abs_proj, "assets", "images")
                        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
                        try:
                            os.makedirs(dest_dir, exist_ok=True)
                            counter = 1
                            name_r, ext_p = os.path.splitext(os.path.basename(file_path))
                            while os.path.exists(dest_path):
                                if os.path.samefile(abs_file, dest_path) or filecmp.cmp(
                                    abs_file, dest_path, shallow=False
                                ):
                                    break
                                dest_path = os.path.join(dest_dir, f"{name_r}_{counter}{ext_p}")
                                counter += 1
                            else:
                                shutil.copy2(abs_file, dest_path)
                            file_path = dest_path
                        except OSError as error:
                            QMessageBox.warning(
                                self, _("Asset Import Failed"),
                                _("Could not copy '{filename}' to the project assets folder:\n{error}").format(
                                    filename=os.path.basename(file_path), error=error
                                ),
                            )
                            event.ignore()
                            return

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

    KNOWN_KEYS = {
        'title', 'author', 'date', 'release_date', 'layout', 'weight',
        'tags', 'featured_image', 'draft', 'breadcrumbs',
    }

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

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
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(6)
        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setHorizontalSpacing(8)
        self.form_layout.setVerticalSpacing(3)
        self.form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        
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
        self.select_image_btn.setFixedSize(28, 26)
        self.select_image_btn.clicked.connect(self.select_featured_image)
        image_layout.addWidget(self.select_image_btn)

        # Bild-Vorschau Label
        self.image_preview_label = QLabel(_("No Image"))
        self.image_preview_label.setFixedSize(64, 48)
        self.image_preview_label.setStyleSheet("border: 1px solid palette(mid); border-radius: 4px;")
        self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.image_preview_label)

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
        flags_layout = QHBoxLayout()
        flags_layout.setContentsMargins(0, 0, 0, 0)
        flags_layout.setSpacing(12)
        flags_layout.addWidget(QLabel(_("Draft:")))
        flags_layout.addWidget(self.draft_check)
        flags_layout.addWidget(QLabel(_("Breadcrumbs:")))
        flags_layout.addWidget(self.breadcrumbs_check)
        flags_layout.addStretch()
        self.form_layout.addRow(flags_layout)
        content_layout.addLayout(self.form_layout)

        self.custom_fields_section = QWidget()
        custom_section_layout = QVBoxLayout(self.custom_fields_section)
        custom_section_layout.setContentsMargins(0, 4, 0, 0)
        custom_section_layout.setSpacing(4)
        custom_header = QHBoxLayout()
        custom_header.setContentsMargins(0, 0, 0, 0)
        custom_header.addWidget(QLabel(_("Custom Fields")))
        custom_header.addStretch()
        self.add_custom_field_button = QPushButton(_("+ Add Field"))
        self.add_custom_field_button.setFixedHeight(26)
        self.add_custom_field_button.clicked.connect(self.add_custom_field)
        custom_header.addWidget(self.add_custom_field_button)
        custom_section_layout.addLayout(custom_header)

        self.custom_fields_layout = QVBoxLayout()
        self.custom_fields_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_fields_layout.setSpacing(3)
        custom_section_layout.addLayout(self.custom_fields_layout)
        content_layout.addWidget(self.custom_fields_section)

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
        self.custom_field_rows = []
        self.custom_fields_valid = True

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

    def set_project_root(self, root):
        self.project_root = root
        self.featured_image_edit.set_project_root(root)

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
        title_valid = bool(self.title_edit.text().strip())
        self._set_field_validity(
            self.title_edit, title_valid, _("Title is required")
        )

        seen_keys = set()
        custom_fields_valid = True
        for row in self.custom_field_rows:
            key = row['key'].text().strip()
            invalid_reason = ""
            if not key:
                invalid_reason = _("Field name is required")
            elif key in self.KNOWN_KEYS:
                invalid_reason = _("This field is already managed above")
            elif key in seen_keys:
                invalid_reason = _("Field names must be unique")
            else:
                seen_keys.add(key)
            self._set_field_validity(row['key'], not invalid_reason, invalid_reason)
            custom_fields_valid = custom_fields_valid and not invalid_reason

        self.custom_fields_valid = custom_fields_valid
        return title_valid and custom_fields_valid

    @staticmethod
    def _set_field_validity(widget, valid, message=""):
        widget.setStyleSheet("" if valid else "border: 2px solid #e74c3c;")
        widget.setToolTip(message)

    def add_custom_field(self, key="", value=None):
        row_widget = QWidget(self.custom_fields_section)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        key_edit = QLineEdit()
        key_edit.setPlaceholderText(_("Field name"))
        key_edit.setText(str(key))
        value_edit = QLineEdit()
        value_edit.setPlaceholderText(_("Value"))
        value_display = yaml.safe_dump(
            value, default_flow_style=True, allow_unicode=True
        ).strip() if value is not None else "null"
        value_edit.setText(value_display if key else "")
        remove_button = QPushButton("−")
        remove_button.setFixedSize(28, 26)
        remove_button.setToolTip(_("Remove field"))

        row_layout.addWidget(key_edit, 1)
        row_layout.addWidget(value_edit, 2)
        row_layout.addWidget(remove_button)
        self.custom_fields_layout.addWidget(row_widget)

        row = {
            'widget': row_widget,
            'key': key_edit,
            'value': value_edit,
            'original_key': key,
            'original_value': value,
            'original_display': value_display,
        }
        self.custom_field_rows.append(row)
        key_edit.textChanged.connect(self.emit_changed)
        value_edit.textChanged.connect(self.emit_changed)
        remove_button.clicked.connect(
            lambda _checked=False, field_row=row: self.remove_custom_field(field_row)
        )
        self.validate_fields()
        return row

    def remove_custom_field(self, row):
        if row not in self.custom_field_rows:
            return
        self.custom_field_rows.remove(row)
        self.custom_fields_layout.removeWidget(row['widget'])
        row['widget'].deleteLater()
        self.emit_changed()

    def _clear_custom_fields(self):
        for row in self.custom_field_rows:
            self.custom_fields_layout.removeWidget(row['widget'])
            row['widget'].deleteLater()
        self.custom_field_rows.clear()

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
            self.extra_data = {
                key: value for key, value in metadata.items()
                if key not in self.KNOWN_KEYS
            }
            self._clear_custom_fields()
            for key, value in self.extra_data.items():
                self.add_custom_field(key, value)
        finally:
            self.blockSignals(False)
        self.validate_fields()
        self.update_image_preview()

    def get_data(self):
        data = {}
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

        for row in self.custom_field_rows:
            key = row['key'].text().strip()
            if not key or key in self.KNOWN_KEYS or key in data:
                continue
            value = row['value'].text()
            if key == row['original_key'] and value == row['original_display']:
                data[key] = row['original_value']
            else:
                data[key] = value

        return data
import os
import yaml
import copy
import ast
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QMessageBox, QScrollArea, QWidget,
                             QCheckBox, QSpinBox, QComboBox, QHBoxLayout, QPushButton, QFileDialog, QGroupBox,
                             QTabWidget, QFrame, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from core.i18n import _

class BaseConfigDialog(QDialog):
    '''
    Docstring für BaseConfigDialog
    Diese Basisklasse bietet eine generische Oberfläche zum Bearbeiten von YAML-Konfigurationsdateien.
    Sie unterstützt automatisch die Erkennung von Datentypen, die Gruppierung von Feldern in Tabs und die Validierung von Eingaben.
    Subklassen können die Kategorien, die Anordnung der Felder und spezielle Eingabetypen durch Überschreiben von Methoden anpassen.

    '''

    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.config_data = {}
        self.inputs = {}
        self.categories = {} # Muss von Subklassen definiert werden
        self.tab_layouts = {}
        self.priority_keys = [] # Kann von Subklassen definiert werden
        
        filename = os.path.basename(config_path)
        self.setWindowTitle(_("Settings ({filename})").format(filename=filename))
        self.resize(800, 500)
        
        # Layout setup
        self.main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Buttons werden in init_ui_rest aufgerufen oder hier
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.save_config)
        self.buttons.rejected.connect(self.reject)

    def init_ui(self):  # Diese Methode initialisiert die Benutzeroberfläche, indem sie Tabs für jede Kategorie erstellt und die Eingabefelder entsprechend der geladenen Konfigurationsdaten anordnet. Sie ruft auch die Methode load_config auf, um die Daten zu laden und die Felder zu füllen.
        for cat in self.categories:
            self.create_tab(cat)
        self.create_tab("Other")
        self.form_layout = self.tab_layouts["Other"]
        self.main_layout.addWidget(self.buttons)
        self.load_config()

    def create_tab(self, name):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QFormLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        scroll.setWidget(content)
        self.tabs.addTab(scroll, _(name))
        self.tab_layouts[name] = layout

    def load_config(self):
        if not os.path.exists(self.config_path):
            QMessageBox.critical(self, _("Error"), _("Configuration file not found:\n{config_path}").format(config_path=self.config_path))
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config_data = yaml.safe_load(f) or {}
            
            self.repair_config_data()
            self.set_defaults() # Hook für Subklassen
            self.populate_fields()
                    
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Error loading configuration:\n{e}").format(e=e))

    def _try_parse(self, val):
        """Hilfsmethode zum Parsen von Strings, die Listen oder Dicts enthalten könnten."""
        if isinstance(val, str):
            val = val.strip()
            if "}," in val and not val.startswith('['):
                val = f"[{val}]"
            if (val.startswith('{') and val.endswith('}')) or (val.startswith('[') and val.endswith(']')):
                try:
                    return ast.literal_eval(val)
                except: 
                    try:
                        return yaml.safe_load(val)
                    except: pass
        return val

    def repair_config_data(self):
        # Hook für Subklassen
        pass

    def set_defaults(self):
        pass

    def populate_fields(self):
        priority_keys = self.priority_keys
        
        def get_category(key):
            for cat, keys in self.categories.items():
                if key in keys:
                    return cat
            return "Other"

        keys_to_add = []
        for key in priority_keys:
            if key in self.config_data:
                keys_to_add.append(key)
        
        for key in self.config_data:
            if key not in keys_to_add:
                keys_to_add.append(key)
        
        for key in keys_to_add:
            cat = get_category(key)
            self.add_input_field(key, self.config_data[key], parent_layout=self.tab_layouts[cat])

    def add_input_field(self, key, value, parent_layout=None, key_path=None):
        if parent_layout is None:
            parent_layout = self.form_layout
        
        if key_path is None:
            key_path = [key]

        # Standard-Handling für Dictionaries (rekursiv)
        if isinstance(value, dict) and not self.is_special_dict(key):
            group = QGroupBox(str(key).replace("_", " ").title())
            group_layout = QFormLayout()
            group.setLayout(group_layout)
            parent_layout.addRow(group)
            
            items = list(value.items())
            for sub_key, sub_value in items:
                self.add_input_field(sub_key, sub_value, group_layout, key_path + [sub_key])
            return

        widget = None
        original_type = type(value)
        label = str(key).replace("_", " ").title()
        
        if isinstance(value, bool):
            widget = QCheckBox()
            widget.setChecked(value)
            
        elif isinstance(value, int):
            widget = QSpinBox()
            widget.setRange(-10000, 10000)
            widget.setValue(value)
            
        elif key == "log_level":
            widget = QComboBox()
            widget.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
            index = widget.findText(str(value).upper())
            if index >= 0: widget.setCurrentIndex(index)
            else: widget.setCurrentText("INFO")

        elif str(key).endswith(("_logo", "_image", "_favicon")):
            widget = self.create_file_picker(key, value, key_path)

        elif str(key).endswith(("_directory", "_path", "_dir")) or key in ["snippets", "themes", "paths"]:
            widget = self.create_dir_picker(value)

        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                text = yaml.dump(value, default_flow_style=True, sort_keys=False).strip()
                widget = QLineEdit(text)
                widget.is_complex_yaml = True
                widget.setToolTip(_("Complex List (YAML/JSON Format)"))
            else:
                widget = QLineEdit(", ".join(str(v) for v in value))
                widget.setPlaceholderText(_("Enter values comma separated"))
            
        else:
            widget = QLineEdit(str(value))
            
        parent_layout.addRow(f"{label}:", widget)
        self.inputs[tuple(key_path)] = (widget, original_type)

    def is_special_dict(self, key):
        # Kann von Subklassen erweitert werden
        return False

    def create_file_picker(self, key, value, key_path, file_filter=None):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        is_image_field = str(key).endswith(("_logo", "_image", "_favicon"))

        if is_image_field:
            icon_preview = QLabel()
            icon_preview.setFixedSize(24, 24)
            icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_preview)

        line_edit = QLineEdit(str(value))
        btn = QPushButton("...")
        btn.setFixedWidth(40)
        
        if is_image_field:
            def update_preview(text, preview_label=icon_preview):
                path_str = text.strip()
                final_path = ""
                if path_str:
                    if os.path.isabs(path_str):
                        final_path = path_str
                    else:
                        final_path = os.path.join(os.path.dirname(self.config_path), path_str)

                if final_path and os.path.exists(final_path):
                    pixmap = QIcon(final_path).pixmap(22, 22)
                    preview_label.setPixmap(pixmap)
                    preview_label.setToolTip(final_path)
                else:
                    preview_label.clear()
                    preview_label.setText("?")
            
            line_edit.textChanged.connect(lambda text, lbl=icon_preview: update_preview(text, lbl))
            update_preview(str(value), icon_preview)

        if file_filter is None:
            file_filter = _("Images (*.png *.jpg *.jpeg *.svg *.gif *.webp *.ico)") if is_image_field else _("All Files (*)")

        btn.clicked.connect(lambda: self.browse_file(line_edit, file_filter, _("Select File")))
        
        layout.addWidget(line_edit)
        layout.addWidget(btn)
        widget.line_edit = line_edit
        return widget

    def create_dir_picker(self, value):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        line_edit = QLineEdit(str(value))
        btn = QPushButton("...")
        btn.setFixedWidth(40)
        btn.clicked.connect(lambda: self.browse_directory(line_edit))
        
        layout.addWidget(line_edit)
        layout.addWidget(btn)
        widget.line_edit = line_edit
        return widget

    def browse_directory(self, line_edit):
        current_path = line_edit.text()
        start_dir = current_path if os.path.isabs(current_path) else os.path.join(os.path.dirname(self.config_path), current_path)
        if not os.path.exists(start_dir): start_dir = os.path.dirname(self.config_path)
        dir_path = QFileDialog.getExistingDirectory(self, _("Select Directory"), start_dir)
        if dir_path:
            try:
                rel_path = os.path.relpath(dir_path, os.path.dirname(self.config_path))
                line_edit.setText(rel_path)
            except ValueError:
                line_edit.setText(dir_path)

    def browse_file(self, line_edit, file_filter, dialog_title=None):
        current_path = line_edit.text()
        start_dir = os.path.dirname(self.config_path)
        if current_path:
            abs_path = current_path if os.path.isabs(current_path) else os.path.join(start_dir, current_path)
            if os.path.exists(abs_path):
                start_dir = os.path.dirname(abs_path) if os.path.isfile(abs_path) else abs_path

        if dialog_title is None: dialog_title = _("Select File")
        file_path, _ = QFileDialog.getOpenFileName(self, dialog_title, start_dir, file_filter)
        if file_path:
            try:
                rel_path = os.path.relpath(file_path, os.path.dirname(self.config_path))
                line_edit.setText(rel_path)
            except ValueError:
                line_edit.setText(file_path)

    def save_config(self):
        new_data = copy.deepcopy(self.config_data)
        validation_errors = []

        try:
            for key_path, (widget, original_type) in self.inputs.items():
                value = self.get_widget_value(widget, original_type)
                
                # Validierung
                if len(key_path) == 1 and key_path[0] in ["site_name", "site_url", "content_directory", "site_output_directory"]:
                    if isinstance(value, str) and not value.strip():
                        label = str(key_path[0]).replace("_", " ").title()
                        validation_errors.append(_("The field '{label}' is required.").format(label=label))
                
                if len(key_path) == 1 and key_path[0] == "site_url":
                    if isinstance(value, str) and value.strip() and not value.strip().startswith(('http://', 'https://')):
                        validation_errors.append(_("The field 'Site Url' must start with http:// or https://."))

                # Update nested dictionary
                target = new_data
                for k in key_path[:-1]:
                    target = target.setdefault(k, {})
                target[key_path[-1]] = value

            if validation_errors:
                QMessageBox.warning(self, _("Validation Error"), "\n".join(validation_errors))
                return

            self.write_config(new_data)
            QMessageBox.information(self, _("Success"), _("Settings saved.\nPlease restart the application to apply all changes."))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Error saving:\n{e}").format(e=e))

    def get_widget_value(self, widget, original_type):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentData() if widget.currentData() else widget.currentText()
        elif isinstance(widget, QWidget) and hasattr(widget, 'line_edit'):
            return widget.line_edit.text().strip()
        elif isinstance(widget, QLineEdit):
            text_value = widget.text().strip()
            if getattr(widget, 'is_complex_yaml', False):
                try: return yaml.safe_load(text_value) if text_value else []
                except: return []
            elif original_type == list:
                items = [item.strip() for item in text_value.split(',') if item.strip()]
                return [item.strip('"').strip("'") for item in items]
            else:
                return text_value
        return None

    def write_config(self, data):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

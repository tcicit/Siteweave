from PyQt6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QColorDialog, QMessageBox, QTabWidget, QHBoxLayout, QLabel)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal
import yaml
import os
import ast

from core.i18n import _

class ColorSettingsDialog(QDialog):
    settings_saved = pyqtSignal()

    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Markdown Color Settings"))
        self.resize(500, 400)
        self.config_path = config_path
        # Default color scheme covers common Markdown elements
        self.default_colors = {
            'header': '#000000',
            'bold': '#000000',
            'italic': '#000000',
            'inline_code': '#000000',
            'code_block': '#000000',
            'link': '#0000FF',
            'blockquote': '#666666',
            'list_marker': '#000000',
            'hr': '#999999',
            'image_alt': '#000000',
            'plugin': '#8e44ad',
            'current_line': '#e6f3ff'
        }

        # Structure with light/dark modes
        self.colors = {
            'light': dict(self.default_colors),
            'dark': {
                'header': '#FFFFFF',
                'bold': '#FFFFFF',
                'italic': '#FFFFFF',
                'inline_code': '#CCCCCC',
                'code_block': '#CCCCCC',
                'link': '#00FFFF',
                'blockquote': '#AAAAAA',
                'list_marker': '#FFFFFF',
                'hr': '#555555',
                'image_alt': '#FFFFFF',
                'plugin': '#d580ff',
                'current_line': '#303030'
            }
        }

        self.load_colors()

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.light_tab = self.create_color_tab('light')
        self.dark_tab = self.create_color_tab('dark')

        self.tabs.addTab(self.light_tab, _("Light Mode"))
        self.tabs.addTab(self.dark_tab, _("Dark Mode"))

        layout.addWidget(self.tabs)

        # Buttons Layout
        btn_layout = QHBoxLayout()

        self.save_button = QPushButton(_("Save"))
        self.save_button.clicked.connect(self.save_colors)
        btn_layout.addWidget(self.save_button)

        self.close_button = QPushButton(_("Close"))
        self.close_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.close_button)

        layout.addLayout(btn_layout)

    def create_color_tab(self, mode):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        form = QFormLayout()

        # Ensure mode exists
        mode_colors = self.colors.get(mode, {})
        # Fill missing keys from defaults
        for k, v in self.default_colors.items():
            mode_colors.setdefault(k, v)
        self.colors[mode] = mode_colors

        # Create inputs
        self._inputs = getattr(self, '_inputs', {})
        self._inputs[mode] = {}

        for key in sorted(mode_colors.keys()):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            color_input = QLineEdit(mode_colors[key])
            
            # Farb-Vorschau Label
            preview_lbl = QLabel()
            preview_lbl.setFixedSize(24, 24)
            preview_lbl.setStyleSheet(f"background-color: {mode_colors[key]}; border: 1px solid #888;")
            
            color_input.textChanged.connect(lambda text, lbl=preview_lbl: self.update_preview(text, lbl))

            color_button = QPushButton("...")
            color_button.setFixedWidth(40)
            color_button.clicked.connect(lambda _, k=key, m=mode, i=color_input: self.pick_color(m, k, i))
            
            row_layout.addWidget(color_input)
            row_layout.addWidget(color_button)
            row_layout.addWidget(preview_lbl)

            form.addRow(f"{key.replace('_', ' ').capitalize()}:", row_widget)
            self._inputs[mode][key] = color_input

        layout.addLayout(form)
        return widget

    def update_preview(self, text, label):
        if QColor(text).isValid():
            label.setStyleSheet(f"background-color: {text}; border: 1px solid #888;")

    def pick_color(self, mode, key, input_field):
        color = QColorDialog.getColor(QColor(input_field.text()), self, _("Select Color"))
        if color.isValid():
            self.colors[mode][key] = color.name()
            input_field.setText(color.name())

    def load_colors(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    full_config = yaml.safe_load(f) or {}
                    loaded = full_config.get('editor_colors', {})
                
                if isinstance(loaded, str):
                    try:
                        loaded = ast.literal_eval(loaded)
                    except Exception:
                        loaded = {}

                # Merge loaded settings with defaults to avoid missing keys
                if isinstance(loaded, dict):
                    for mode in ('light', 'dark'):
                        if mode in loaded and isinstance(loaded[mode], dict):
                            # start from defaults for this mode
                            base = dict(self.default_colors) if mode == 'light' else dict(self.colors.get('dark', {}))
                            base.update(loaded[mode])
                            self.colors[mode] = base
            except Exception as e:
                QMessageBox.warning(self, _("Error"), _("Could not load colors: {e}").format(e=e))

    def save_colors(self):
        # Werte aus den Eingabefeldern übernehmen (für manuelle Änderungen)
        for mode in ['light', 'dark']:
            if mode in self._inputs:
                for key, widget in self._inputs[mode].items():
                    self.colors[mode][key] = widget.text()

        try:
            # Lade existierende Config um nichts zu überschreiben
            full_config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    full_config = yaml.safe_load(f) or {}
            
            full_config['editor_colors'] = self.colors

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(full_config, f, default_flow_style=False, sort_keys=False)
            self.settings_saved.emit()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not save colors: {e}").format(e=e))
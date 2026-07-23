import os, shlex
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QListWidget, 
                             QAbstractItemView, QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox, QSlider, QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from core.i18n import _
from .config_base import BaseConfigDialog

class ToolbarLayoutEditor(QWidget):
    '''
    Docstring für ToolbarLayoutEditor
    Dieses Widget ermöglicht es dem Benutzer, die Anordnung der Toolbar-Elemente anzupassen.
Funktionen:
- Zwei Listen: Eine für verfügbare Aktionen und eine für die aktuelle Toolbar-Anordnung.
- Drag-and-Drop-Unterstützung zum Verschieben von Aktionen zwischen den Listen und innerhalb der Toolbar-Liste.
- Buttons zum Hinzufügen und Entfernen von Aktionen aus der Toolbar.
- Buttons zum Verschieben von Aktionen in der Toolbar nach oben oder unten.
- Methode get_data(), die die aktuelle Anordnung der Toolbar-Elemente zurückgibt.   

    '''
    def __init__(self, all_actions, current_layout, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Available actions
        available_group = QGroupBox(_("Available Items"))
        available_layout = QVBoxLayout(available_group)
        self.available_list = QListWidget()
        self.available_list.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.available_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        available_layout.addWidget(self.available_list)
        
        # Toolbar layout
        layout_group = QGroupBox(_("Toolbar Layout"))
        layout_layout = QVBoxLayout(layout_group)
        self.layout_list = QListWidget()
        self.layout_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.layout_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.layout_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout_layout.addWidget(self.layout_list)

        # Populate lists
        for item in sorted(list(set(all_actions))):
            self.available_list.addItem(item)
        
        for item in current_layout:
            self.layout_list.addItem(item)

        # Buttons in the middle
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        self.add_btn = QPushButton(" > ")
        self.remove_btn = QPushButton(" < ")
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addStretch()

        # Buttons on the right
        order_button_layout = QVBoxLayout()
        order_button_layout.addStretch()
        self.up_btn = QPushButton(_("Up"))
        self.down_btn = QPushButton(_("Down"))
        order_button_layout.addWidget(self.up_btn)
        order_button_layout.addWidget(self.down_btn)
        order_button_layout.addStretch()

        layout.addWidget(available_group, 3)
        layout.addLayout(button_layout)
        layout.addWidget(layout_group, 3)
        layout.addLayout(order_button_layout)

        # Connect signals
        self.add_btn.clicked.connect(lambda: self.layout_list.addItems([item.text() for item in self.available_list.selectedItems()]))
        self.remove_btn.clicked.connect(lambda: [self.layout_list.takeItem(self.layout_list.row(item)) for item in self.layout_list.selectedItems()])
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)

    def move_up(self):
        for item in self.layout_list.selectedItems():
            row = self.layout_list.row(item)
            if row > 0:
                self.layout_list.insertItem(row - 1, self.layout_list.takeItem(row))
                self.layout_list.setCurrentRow(row - 1)

    def move_down(self):
        for item in reversed(self.layout_list.selectedItems()):
            row = self.layout_list.row(item)
            if row < self.layout_list.count() - 1:
                self.layout_list.insertItem(row + 1, self.layout_list.takeItem(row))
                self.layout_list.setCurrentRow(row + 1)

    def get_data(self):
        return [self.layout_list.item(i).text() for i in range(self.layout_list.count())]

class ExternalEditorsEditor(QWidget):
    """Widget zur Verwaltung der Zuordnung von Endungen zu ausführbaren Programmen."""
    def __init__(self, editors_list, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.rows = []

        if not isinstance(editors_list, list): editors_list = []
        for editor in editors_list:
            self.add_row(editor)

        self.add_btn = QPushButton(_("+ Add Editor"))
        self.add_btn.clicked.connect(lambda: self.add_row())
        self.layout.addWidget(self.add_btn)

    def add_row(self, editor_dict=None):
        if editor_dict is None: editor_dict = {}
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 2, 0, 2)

        name_edit = QLineEdit(str(editor_dict.get('name', '')))
        name_edit.setPlaceholderText(_("Name (e.g., GIMP)"))
        name_edit.setFixedWidth(120)

        ext_edit = QLineEdit(", ".join(editor_dict.get('extensions', [])))
        ext_edit.setPlaceholderText(_(".jpg, .png"))
        ext_edit.setFixedWidth(100)
        
        cmd = editor_dict.get('command', '')
        if isinstance(cmd, list): cmd = " ".join(cmd)
        cmd_edit = QLineEdit(str(cmd))
        cmd_edit.setPlaceholderText(_("Path or 'flatpak run ...'"))
        
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        
        def browse(edit=cmd_edit):
            from PyQt6.QtWidgets import QFileDialog
            f_path, _filter = QFileDialog.getOpenFileName(self, _("Select a program"), "", _("Programs (*);;All files (*)"))
            if f_path:
                edit.setText(f_path)
        browse_btn.clicked.connect(lambda: browse(cmd_edit))

        del_btn = QPushButton("X")
        del_btn.setFixedWidth(30)
        del_btn.clicked.connect(lambda: self.remove_row(row_widget))

        row_layout.addWidget(name_edit)
        row_layout.addWidget(ext_edit)
        row_layout.addWidget(cmd_edit)
        row_layout.addWidget(browse_btn)
        row_layout.addWidget(del_btn)

        self.layout.insertWidget(self.layout.count() - 1, row_widget)
        self.rows.append((row_widget, name_edit, ext_edit, cmd_edit))

    def remove_row(self, row_widget):
        for i, (w, n, e, c) in enumerate(self.rows):
            if w == row_widget:
                self.rows.pop(i)
                break
        row_widget.deleteLater()

    def get_data(self):
        data = []
        for row_widget, name_edit, ext_edit, cmd_edit in self.rows:
            name = name_edit.text().strip()
            exts = [e.strip().lower() if e.strip().startswith('.') else '.' + e.strip().lower() 
                    for e in ext_edit.text().split(",") if e.strip()]
            cmd_raw = cmd_edit.text().strip()
            
            if name and exts and cmd_raw:
                cmd_parts = shlex.split(cmd_raw)
                data.append({
                    "name": name,
                    "extensions": exts,
                    "command": cmd_parts if len(cmd_parts) > 1 else cmd_raw,
                    "icon": "applications-other"
                })
        return data

class AppConfigDialog(BaseConfigDialog):
    '''
    Docstring für AppConfigDialog
    Dieses Dialogfenster ermöglicht es dem Benutzer, die Anwendungskonfiguration anzupassen. Es bietet verschiedene Kategorien von Einstellungen, darunter allgemeine Optionen, Pfade, Funktionen, Editor-Einstellungen, Toolbar-Anpassungen und erweiterte Optionen. Der Dialog lädt die aktuelle Konfiguration, zeigt sie in entsprechenden Eingabefeldern an und ermöglicht es dem Benutzer, Änderungen vorzunehmen. Nach dem Speichern werden die Änderungen in der Konfigurationsdatei gespeichert und können von der Anwendung verwendet werden.
Funktionen:
- Laden der aktuellen Konfiguration aus einer YAML-Datei.       
- Anzeige von Eingabefeldern für verschiedene Konfigurationsoptionen, organisiert in Kategorien.
- Speichern der Änderungen zurück in die YAML-Datei.
- Spezielle Unterstützung für die Anpassung der Toolbar-Anordnung über ein benutzerdefiniertes Widget.

    '''


    def __init__(self, config_path, parent=None):
        super().__init__(config_path, parent)
        # Ermittle den App-Root Pfad (3 Ebenen über dieser Datei)
        self.app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.categories = { #Diese Struktur definiert die Kategorien und die zugehörigen Schlüssel, die in der Konfigurationsdatei erwartet werden. Sie dient als Grundlage für die Erstellung der Benutzeroberfläche, indem sie angibt, welche Einstellungen in welcher Kategorie angezeigt werden sollen. Alle Schlüssel, die in der Konfigurationsdatei vorhanden sind, sollten hier aufgeführt sein, damit sie korrekt dargestellt und bearbeitet werden können.
            "General": ["language", "auto_open_last_project", "autosave_interval", "autosave_on_close", "autosave_on_switch", "log_level"],
            "Paths": ["paths", "last_file"],            
            "Editor": ["view_dark_mode", "view_show_preview", "view_show_toolbar", "view_show_line_numbers", "editor_font_family", "editor_font_size", "preview_font_family", "preview_font_size"],
            "Media": ["media_thumbnail_size", "external_editors", "media_manager_sort_index", "media_manager_sort_descending"],
            "Toolbar": ["toolbar_layout", "action_icons"]
        }
        self.priority_keys = [ #Diese Liste definiert die Reihenfolge der Eingabefelder in der Benutzeroberfläche. Sie stellt sicher, dass wichtige oder häufig verwendete Einstellungen zuerst angezeigt werden, um die Benutzerfreundlichkeit zu verbessern. Alle Schlüssel, die in den Kategorien definiert sind, sollten hier aufgeführt werden, damit sie in der gewünschten Reihenfolge angezeigt werden.
            "language", "auto_open_last_project", "log_level", "paths", "last_file", "features",
            "view_dark_mode", "view_show_preview", "view_show_toolbar", "view_show_line_numbers","editor_font_family", "editor_font_size", "preview_font_family", "preview_font_size",
            "media_thumbnail_size", "external_editors", "media_manager_sort_index", "media_manager_sort_descending",
            "toolbar_layout", "action_icons",
        ]
        self.all_toolbar_actions = [
            'new_act', 'switch_project_act', 'save_act', 'insert_img_act', 'insert_file_act', 
            'gallery_act', 'emoji_act', 'exit_act', 'undo_act', 'redo_act', 'select_all_act', 'search_act', 
            'replace_act', 'toggle_preview_act', 'dark_mode_act', 'config_act', 
            'manage_snippets_act', 'render_act', 'open_browser_act', 'about_act', 'bold_act', 
            'italic_act', 'code_act', 'h1_act', 'h2_act', 'h3_act', 'ul_act', 'ol_act', 
            'table_act', 'separator', 'spacer'
        ]
        self.init_ui()

    def init_ui(self):
        """Initialisiert die Benutzeroberfläche und fügt die Reset-Option hinzu."""
        super().init_ui()
        
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        # Schaltfläche zum Reparieren von Pfaden
        self.repair_paths_btn = QPushButton(_("Repair Paths"))
        self.repair_paths_btn.setToolTip(_("Fixes broken absolute paths and converts them to portable relative paths where possible."))
        self.repair_paths_btn.clicked.connect(self.repair_paths)

        # Schaltfläche zum Zurücksetzen des Layouts erstellen
        self.reset_layout_btn = QPushButton(_("Reset Window Layout"))
        self.reset_layout_btn.setToolTip(_("Clears all saved window positions and splitter states."))
        self.reset_layout_btn.clicked.connect(self.reset_window_layout)
        
        btn_layout.addWidget(self.repair_paths_btn)
        btn_layout.addWidget(self.reset_layout_btn)

        # Button ganz unten im Dialog (über Save/Cancel) einfügen
        self.main_layout.insertWidget(self.main_layout.count() - 1, btn_container)

    def repair_paths(self):
        """Sucht nach verwaisten oder absoluten Pfaden und versucht diese zu korrigieren."""
        changes = 0
        base_dir = os.path.abspath(os.path.dirname(self.config_path))

        # 1. Sichtbare Pfad-Eingabefelder prüfen (z.B. last_file, locales, etc.)
        for key_path, (widget, original_type) in self.inputs.items():
            line_edit = getattr(widget, 'line_edit', widget)
            if not isinstance(line_edit, QLineEdit):
                continue

            path_str = line_edit.text().strip()
            if not path_str or not (os.path.sep in path_str or '/' in path_str):
                continue

            # Absolute Pfade innerhalb der App portabel machen
            if os.path.isabs(path_str):
                abs_path = os.path.abspath(path_str)
                if abs_path.startswith(base_dir):
                    rel_path = os.path.relpath(abs_path, base_dir)
                    if rel_path != path_str:
                        line_edit.setText(rel_path)
                        changes += 1

        # 2. Versteckte Projektliste reparieren (Verwaiste entfernen, Abs -> Rel)
        if hasattr(self, '_hidden_recent_projects') and isinstance(self._hidden_recent_projects, list):
            new_recent = []
            for p in self._hidden_recent_projects:
                abs_p = p if os.path.isabs(p) else os.path.join(base_dir, p)
                abs_p = os.path.abspath(abs_p)

                if os.path.exists(abs_p):
                    # Wenn existiert und innerhalb der App -> Relativieren
                    if abs_p.startswith(base_dir):
                        portable_p = os.path.relpath(abs_p, base_dir)
                        if portable_p != p:
                            changes += 1
                        new_recent.append(portable_p)
                    else:
                        new_recent.append(p)
                else:
                    # Verwaisten Pfad entfernen
                    changes += 1
            
            self._hidden_recent_projects = new_recent

        if changes > 0:
            QMessageBox.information(self, _("Paths Repaired"), 
                                   _("{count} entries were updated, removed or converted to portable paths.\n"
                                     "Please save to apply these changes.").format(count=changes))
        else:
            QMessageBox.information(self, _("Paths Repaired"), 
                                   _("No orphaned or non-portable paths found."))

    def reset_window_layout(self):
        """Leert den versteckten Geometrie-Puffer."""
        res = QMessageBox.question(self, _("Reset Layout"), 
                                   _("Do you want to reset all window positions and splitters to default?\n"
                                     "Changes will be permanent after saving and restarting."),
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self._hidden_geometry = {}
            self.reset_layout_btn.setEnabled(False)
            self.reset_layout_btn.setText(_("Layout Reset (Save to apply)"))

    def set_defaults(self):
        self.config_data.setdefault("auto_open_last_project", True)
        self.config_data.setdefault("language", "en_US")
        self.config_data.setdefault("editor_font_size", 12)
        self.config_data.setdefault("view_dark_mode", False)
        self.config_data.setdefault("view_show_preview", True)
        self.config_data.setdefault("view_show_toolbar", True)
        self.config_data.setdefault("view_show_line_numbers", True)
        self.config_data.setdefault("window_width", 1200)
        self.config_data.setdefault("media_thumbnail_size", 100) # New default
        self.config_data.setdefault("window_height", 800)
        self.config_data.setdefault("window_x", 100)
        self.config_data.setdefault("window_y", 100)
        
        default_toolbar_layout = [
            "new_act", "save_act", "separator", "undo_act", "redo_act", "separator",
            "search_act", "spacer", "render_act"
        ]
        self.config_data.setdefault('toolbar_layout', default_toolbar_layout)
        
        default_action_icons = {
            'new_act': 'add', 'switch_project_act': 'start', 'save_act': 'save',
            'insert_img_act': 'image', 'insert_file_act': 'link', 'gallery_act': 'gallery', 'emoji_act': 'emoji',
            'exit_act': 'exit', 'undo_act': 'undo', 'redo_act': 'redo',
            'select_all_act': 'select_all', 'search_act': 'search', 'replace_act': 'replace',
            'toggle_preview_act': 'preview', 'dark_mode_act': 'dark_mode', 'config_act': 'settings',
            'manage_snippets_act': 'snippets', 'render_act': 'render', 'open_browser_act': 'browser',
            'about_act': 'about', 'bold_act': 'bold', 'italic_act': 'italic',
            'code_act': 'code', 'h1_act': 'h1', 'h2_act': 'h2', 'h3_act': 'h3',
            'ul_act': 'list_ul', 'ol_act': 'list_ol', 'table_act': 'table'
        }
        loaded_icons = self.config_data.setdefault('action_icons', {})
        for k, v in default_action_icons.items():
            if k not in loaded_icons:
                loaded_icons[k] = v
        
        loaded_paths = self.config_data.setdefault("paths", {})
        path_defaults = {
            "snippets": "snippets",
            "themes": "themes",
            "locales": "locales",
            "pdf_themes": "pdf_themes",
            "plugins": "plugins",
            "scripts": "scripts"
        }
        for k, v in path_defaults.items():
            if k not in loaded_paths:
                loaded_paths[k] = v

    def repair_config_data(self): #Diese Methode überprüft die geladenen Konfigurationsdaten und repariert sie, falls sie in einem alten Format vorliegen oder wichtige Schlüssel fehlen. Sie stellt sicher, dass die Datenstruktur konsistent ist und alle erwarteten Felder enthält, damit die Anwendung korrekt funktioniert.
        for key in ['action_icons']:
            if key in self.config_data:
                parsed = self._try_parse(self.config_data[key])
                if isinstance(parsed, (dict, list)):
                    self.config_data[key] = parsed

        # editor_colors wird in einem eigenen Dialog verwaltet und hier entfernt
        if 'editor_colors' in self.config_data:
            self._hidden_editor_colors = self.config_data['editor_colors']
            del self.config_data['editor_colors']

        # recent_projects wird automatisch verwaltet und soll nicht editierbar sein
        if 'recent_projects' in self.config_data:
            self._hidden_recent_projects = self.config_data['recent_projects']
            del self.config_data['recent_projects']

        # Geometrie-Daten ausblenden, damit sie nicht manuell editiert werden
        self._hidden_geometry = {}
        geometry_keys = ["window_width", "window_height", "window_x", "window_y"]
        for key in list(self.config_data.keys()):
            if key in geometry_keys or key.endswith(("_geometry", "_splitter")):
                self._hidden_geometry[key] = self.config_data.pop(key)

    def add_input_field(self, key, value, parent_layout=None, key_path=None):
        if parent_layout is None: parent_layout = self.form_layout
        if key_path is None: key_path = [key]

        if key == "toolbar_layout":
            
            widget = ToolbarLayoutEditor(self.all_toolbar_actions, value)
            group = QGroupBox(str(key).replace("_", " ").title())
            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(5, 5, 5, 5)
            group_layout.addWidget(widget)
            parent_layout.addRow(group)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "language":
            widget = QComboBox()
            widget.addItem("English", "en_US")
            widget.addItem("Deutsch", "de_DE")
            widget.addItem("Deutsch (Schweiz)", "de_CH")
            widget.addItem("Français", "fr_FR")
            widget.setObjectName("language_combo")
            index = widget.findData(str(value))
            if index >= 0:
                widget.setCurrentIndex(index)
            else:
                # Accept short locale codes like 'de' by mapping to 'de_DE'
                if str(value).lower().startswith('de'):
                    alt_index = widget.findData('de_DE')
                    if alt_index >= 0:
                        widget.setCurrentIndex(alt_index)
                    else:
                        widget.setCurrentIndex(0)
                else:
                    widget.setCurrentIndex(0)
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif len(key_path) > 1 and key_path[0] == "action_icons":
            widget = self.create_icon_picker(value)
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "media_thumbnail_size":
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            
            spin_box = QSpinBox()
            spin_box.setRange(50, 250)
            spin_box.setSingleStep(10)
            spin_box.setValue(int(value))
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(50, 250)
            slider.setValue(int(value))
            
            # Synchronize the SpinBox and Slider
            spin_box.valueChanged.connect(slider.setValue)
            slider.valueChanged.connect(spin_box.setValue)
            
            h_layout.addWidget(spin_box)
            h_layout.addWidget(slider)
            
            parent_layout.addRow(_("Thumbnail Size (px):"), container)
            # Store the spin_box as the target for value retrieval
            spin_box.setObjectName("thumbnail_size_spin")
            self.inputs[tuple(key_path)] = (spin_box, type(value))
            return
        elif key == "editor_font_size":
            spin = QSpinBox()
            spin.setRange(6, 72)
            spin.setValue(int(value))
            spin.setObjectName("font_size_spin")

            parent_layout.addRow(_(str(key).replace('_', ' ').title()) + ":", spin)
            self.inputs[tuple(key_path)] = (spin, type(value))
            return
        elif key == "external_editors":
            widget = ExternalEditorsEditor(value)
            group = QGroupBox(_("Externe Media-Editoren"))
            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(5, 5, 5, 5)
            group_layout.addWidget(widget)
            parent_layout.addRow(group)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return

        super().add_input_field(key, value, parent_layout, key_path)

    def create_icon_picker(self, value):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        icon_preview = QLabel()
        icon_preview.setFixedSize(24, 24)
        icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_preview)

        line_edit = QLineEdit(str(value))
        btn = QPushButton("...")
        btn.setFixedWidth(40)
        
        def update_preview(text):
            path_str = text.strip()
            final_path = ""
            if path_str:
                if os.path.isabs(path_str):
                    final_path = path_str
                else:
                    final_path = os.path.join(self.app_root, "assets", "icons", f"{path_str}.svg")

            if final_path and os.path.exists(final_path):
                pixmap = QIcon(final_path).pixmap(22, 22)
                icon_preview.setPixmap(pixmap)
                icon_preview.setToolTip(final_path)
                line_edit.setStyleSheet("")
            else:
                icon_preview.clear()
                icon_preview.setText("?")
                if path_str:
                    line_edit.setStyleSheet("border: 1px solid #e74c3c; background-color: #fdf2f2;")
                    line_edit.setToolTip(_("Icon file not found!"))
        
        line_edit.textChanged.connect(update_preview)
        update_preview(str(value))

        btn.clicked.connect(lambda: self.browse_file(line_edit, _("SVG Icons (*.svg);;All Files (*)"), _("Select Icon")))
        
        layout.addWidget(line_edit)
        layout.addWidget(btn)
        widget.line_edit = line_edit
        return widget

    def get_widget_value(self, widget, original_type):
        if isinstance(widget, (ToolbarLayoutEditor, ExternalEditorsEditor)):
            return widget.get_data()
        return super().get_widget_value(widget, original_type)

    def write_config(self, data):
        # Restore hidden fields
        if hasattr(self, '_hidden_editor_colors'):
            data['editor_colors'] = self._hidden_editor_colors
        if hasattr(self, '_hidden_recent_projects'):
            data['recent_projects'] = self._hidden_recent_projects
        if hasattr(self, '_hidden_geometry'):
            data.update(self._hidden_geometry)
        super().write_config(data)

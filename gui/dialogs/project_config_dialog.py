import os
import shutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
                             QAbstractItemView, QPushButton, QLineEdit, QGroupBox, QFormLayout, QComboBox,
                             QMessageBox)
from PyQt6.QtCore import Qt
from core.i18n import _
from .config_base import BaseConfigDialog
from core.config_manager import ConfigManager

class LinksListWidget(QListWidget):
    '''
    Docstring für LinksListWidget
Dieses Widget erweitert QListWidget, um die Verwaltung von Link-Elementen zu ermöglichen. Es unterstützt Drag-and-Drop zum Umordnen der Links und speichert die zugehörigen Daten in den Listenelementen.
Funktionen:
- Drag-and-Drop-Unterstützung zum Verschieben von Link-Elementen innerhalb der Liste.
- Speicherung der Link-Daten (z.B. Titel und URL) in den Listenelementn über die UserRole.
- Callback-Funktion create_widget_callback, die aufgerufen wird, um ein benutzerdefiniertes Widget für jedes Listenelement zu erstellen, basierend auf den gespeicherten Daten.

    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            widget = self.itemWidget(item)
            if widget:
                item.setData(Qt.ItemDataRole.UserRole, widget.get_data())
        super().startDrag(supportedActions)

    def dropEvent(self, event):
        super().dropEvent(event)
        for i in range(self.count()):
            item = self.item(i)
            if not self.itemWidget(item):
                data = item.data(Qt.ItemDataRole.UserRole)
                if data and hasattr(self, 'create_widget_callback'):
                    widget = self.create_widget_callback(data)
                    self.setItemWidget(item, widget)
                    item.setSizeHint(widget.sizeHint())

class LinksEditor(QWidget):
    '''
    Docstring für LinksEditor
Dieses Widget ermöglicht es dem Benutzer, eine Liste von Links zu bearbeiten. Jeder Link besteht aus einem Titel und einer URL. Das Widget unterstützt das Hinzufügen, Entfernen und Umordnen von Links sowie die Eingabe der Link-Daten.
Funktionen:
- Anzeige einer Liste von Links mit Titel und URL.
- Möglichkeit zum Hinzufügen neuer Links über einen "+ Add Link"-Button.        
- Möglichkeit zum Entfernen von Links über einen "X"-Button neben jedem Link.
- Drag-and-Drop-Unterstützung zum Umordnen der Links in der Liste.
- Speicherung der Link-Daten in den Listenelementen und Bereitstellung einer Methode get_data(), um die aktuelle Liste der Links als Datenstruktur zurückzugeben.

    '''
    def __init__(self, links, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_widget = LinksListWidget()
        self.list_widget.create_widget_callback = self.create_row_widget
        self.layout.addWidget(self.list_widget)

        if not isinstance(links, list):
            links = []
        
        for link in links:
            if isinstance(link, dict):
                self.add_row(link)

        self.add_btn = QPushButton(_("+ Add Link"))
        self.add_btn.clicked.connect(lambda: self.add_row())
        self.layout.addWidget(self.add_btn)

    def create_row_widget(self, link_data):
        title = link_data.get('title', '')
        url = link_data.get('url', '')

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 2, 0, 2)

        title_edit = QLineEdit(title)
        title_edit.setPlaceholderText(_("Title"))
        url_edit = QLineEdit(url)
        url_edit.setPlaceholderText(_("URL"))
        
        row_widget.title_edit = title_edit
        row_widget.url_edit = url_edit
        row_widget.link_data = link_data
        
        def get_data():
            d = row_widget.link_data
            d['title'] = row_widget.title_edit.text().strip()
            d['url'] = row_widget.url_edit.text().strip()
            return d
        row_widget.get_data = get_data

        del_btn = QPushButton("X")
        del_btn.setFixedWidth(30)
        del_btn.clicked.connect(lambda: self.remove_row(row_widget))

        row_layout.addWidget(title_edit)
        row_layout.addWidget(url_edit)
        row_layout.addWidget(del_btn)

        return row_widget

    def add_row(self, link_data=None):
        if link_data is None: link_data = {}
        row_widget = self.create_row_widget(link_data)
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(row_widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, link_data)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row_widget)

    def remove_row(self, row_widget):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if self.list_widget.itemWidget(item) == row_widget:
                self.list_widget.takeItem(i)
                break

    def get_data(self):
        data = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget: data.append(widget.get_data())
        return data

class SocialLinksEditor(QWidget):
    def __init__(self, links, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.rows = []

        if not isinstance(links, dict): links = {}
        for platform, url in links.items():
            self.add_row(platform, url)

        self.add_btn = QPushButton(_("+ Add Social Link"))
        self.add_btn.clicked.connect(lambda: self.add_row("", ""))
        self.layout.addWidget(self.add_btn)

    def add_row(self, platform, url):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 2, 0, 2)

        platform_edit = QLineEdit(str(platform))
        platform_edit.setPlaceholderText(_("Platform (e.g. twitter)"))
        url_edit = QLineEdit(str(url))
        url_edit.setPlaceholderText(_("URL"))
        
        del_btn = QPushButton("X")
        del_btn.setFixedWidth(30)
        del_btn.clicked.connect(lambda: self.remove_row(row_widget))

        row_layout.addWidget(platform_edit)
        row_layout.addWidget(url_edit)
        row_layout.addWidget(del_btn)

        self.layout.insertWidget(self.layout.count() - 1, row_widget)
        self.rows.append((row_widget, platform_edit, url_edit))

    def remove_row(self, row_widget):
        for i, (w, p, u) in enumerate(self.rows):
            if w == row_widget:
                self.rows.pop(i)
                break
        row_widget.deleteLater()

    def get_data(self):
        data = {}
        for _, platform_edit, url_edit in self.rows:
            p = platform_edit.text().strip()
            u = url_edit.text().strip()
            if p: data[p] = u
        return data

class ProjectConfigDialog(BaseConfigDialog):
    '''
    Docstring für ProjectConfigDialog
    Zeigt einen Dialog zur Bearbeitung der Projekt-Konfiguration an.    
    Funktionen:
- Anzeige der Projekt-Konfiguration in einem Formular.
- Speichern der Änderungen an der Projekt-Konfiguration.    

    '''

    def __init__(self, config_path, app_root, parent=None):
        self.app_root = app_root
        super().__init__(config_path, parent)
        self.categories = {
            "General": ["site_name", "site_theme", "default_author", "site_url", "site_logo", "site_favicon", "log_level"],
            "Navigation": ["header_links", "footer_links"],
            "SEO": ["meta_description", "meta_keywords"],
            "Directories": ["content_directory", "site_output_directory", "themes_directory", "assets_directory", "plugin_directory"],
            "Editor": ["default_template", "markdown_extensions", "spellcheck_enabled", "spellcheck_language"],
            "Backup": ["backup_directory", "backup_on_render", "backup_rotation"],
            "Social & Contact": ["contact", "social"],
            "PDF Export": ["pdf_export"],
            "Advanced": ["image_compression", "normalization", "linter"]
        }
        self.priority_keys = [
            "site_name", "site_theme", "default_author", "site_logo", "site_favicon", "site_url", "header_links", "footer_links", "contact", 
            "meta_description", "meta_keywords",
            "content_directory", "site_output_directory", "themes_directory", "default_template", 
            "assets_directory", "plugin_directory", "backup_directory", "backup_on_render", "backup_rotation", "spellcheck_enabled", "spellcheck_language",
            "pdf_export", "markdown_extensions", "log_level"
        ]
        self.init_ui()

    def set_defaults(self):
        self.config_data.setdefault("site_name", "New Project")
        self.config_data.setdefault("site_url", "http://localhost:8000")
        self.config_data.setdefault("content_directory", "content")
        self.config_data.setdefault("site_output_directory", "site_output")
        self.config_data.setdefault("themes_directory", "themes")
        self.config_data.setdefault("assets_directory", "assets")
        self.config_data.setdefault("plugin_directory", "plugins")
        self.config_data.setdefault("backup_directory", "backup")
        self.config_data.setdefault("markdown_extensions", [".md", ".markdown"])
        self.config_data.setdefault("spellcheck_enabled", True)
        self.config_data.setdefault("spellcheck_language", "en_US")
        self.config_data.setdefault("log_level", "INFO")

        self.config_data.setdefault("image_compression", {
            "compressed_suffix": "-compressed",
            "jpeg_quality": 85,
            "png_compression": 6,
            "extensions": [".jpg", ".jpeg", ".png"]
        })
        self.config_data.setdefault("normalization", {"excluded_dirs": ["_spezial"]})
        self.config_data.setdefault("linter", {"defaults": {"author": "default", "layout": "full-width"}})
        self.config_data.setdefault("default_template", "full-width")
        self.config_data.setdefault("site_theme", "default-blog")
        self.config_data.setdefault("default_author", "")
        self.config_data.setdefault("site_logo", "")
        self.config_data.setdefault("site_favicon", "")
        self.config_data.setdefault("header_links", [])
        self.config_data.setdefault("footer_links", [])
        self.config_data.setdefault("meta_description", "")
        self.config_data.setdefault("meta_keywords", "")
        self.config_data.setdefault("social", {})
        self.config_data.setdefault("pdf_export", {
            "export_path": "pdf_exports",
            "page_size": "A4",
            "orientation": "portrait",
            "margin_top": "2cm",
            "margin_right": "2cm",
            "margin_bottom": "2cm",
            "margin_left": "2cm",
            "show_cover_page": True,
            "show_page_numbers": True,
            "show_print_date": True,
            "custom_css_path": ""
        })
        self.config_data.setdefault("contact", {})
        if isinstance(self.config_data["contact"], dict):
            self.config_data["contact"].setdefault("name", "")
            self.config_data["contact"].setdefault("address", "")
            self.config_data["contact"].setdefault("email", "")
        self.config_data.setdefault("backup_on_render", True)
        self.config_data.setdefault("backup_rotation", 10)
        
        # App-Einstellungen entfernen - sie sollten nicht in der Projektkonfiguration sein
        app_only_keys = [
            "view_dark_mode", "view_show_preview", "view_show_toolbar", "view_show_line_numbers",
            "auto_open_last_project", "editor_font_size", "language", "action_icons", 
            "recent_projects", "editor_colors",
            "window_width", "window_height", "window_x", "window_y"
        ]
        for key in app_only_keys:
            if key in self.config_data:
                del self.config_data[key]

    def is_special_dict(self, key):
        return key == "social"

    def repair_config_data(self):
        for key in ['contact', 'social', 'image_compression', 'normalization', 'linter']:
            if key in self.config_data:
                parsed = self._try_parse(self.config_data[key])
                if isinstance(parsed, (dict, list)):
                    self.config_data[key] = parsed
        
        for key in ['footer_links', 'header_links']:
            if key in self.config_data:
                val = self.config_data[key]
                if isinstance(val, str):
                    self.config_data[key] = self._try_parse(val) or []
                elif isinstance(val, list) and val and isinstance(val[0], str):
                     self.config_data[key] = self._try_parse(", ".join(val)) or []

    def add_input_field(self, key, value, parent_layout=None, key_path=None):
        if parent_layout is None: parent_layout = self.form_layout
        if key_path is None: key_path = [key]

        # Handle specific dict sorting
        if isinstance(value, dict) and not self.is_special_dict(key):
            if key == "contact" or key == "pdf_export":
                group = QGroupBox(str(key).replace("_", " ").title())
                group_layout = QFormLayout()
                group.setLayout(group_layout)
                parent_layout.addRow(group)
                
                items = list(value.items())
                if key == "contact":
                    order = ["name", "address", "email"]
                    items.sort(key=lambda x: order.index(x[0]) if x[0] in order else 999)
                elif key == "pdf_export":
                    order = ["export_path", "page_size", "orientation", "margin_top", "margin_right", "margin_bottom", "margin_left", 
                             "show_cover_page", "show_page_numbers", "show_print_date", "custom_css_path"]
                    items.sort(key=lambda x: order.index(x[0]) if x[0] in order else 999)

                for sub_key, sub_value in items:
                    self.add_input_field(sub_key, sub_value, group_layout, key_path + [sub_key])
                return

        if key == "footer_links" or key == "header_links":
            widget = LinksEditor(value)
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "social":
            widget = SocialLinksEditor(value)
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "page_size":
            widget = QComboBox()
            widget.addItems(["A4", "A3", "A5", "Letter", "Legal"])
            index = widget.findText(str(value), Qt.MatchFlag.MatchFixedString)
            if index >= 0: widget.setCurrentIndex(index)
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "orientation":
            widget = QComboBox()
            widget.addItems(["portrait", "landscape"])
            index = widget.findText(str(value), Qt.MatchFlag.MatchFixedString)
            if index >= 0: widget.setCurrentIndex(index)
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "default_template":
            widget = QComboBox()
            widget.addItem("full-width")
            project_root = os.path.dirname(self.config_path)
            tpl_dir_name = self.config_data.get("themes_directory", "themes")
            tpl_dir = os.path.join(project_root, tpl_dir_name)
            if os.path.exists(tpl_dir):
                for filename in sorted(os.listdir(tpl_dir)):
                    if filename.startswith("layout_") and filename.endswith(".html"):
                        layout_name = filename[7:-5]
                        if layout_name != "full-width":
                            widget.addItem(layout_name)
            index = widget.findText(str(value))
            if index >= 0: widget.setCurrentIndex(index)
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "custom_css_path":
            widget = self.create_file_picker(key, value, key_path, file_filter=_("CSS Files (*.css);;All Files (*)"))
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "spellcheck_language":
            widget = QComboBox()
            widget.setEditable(True)
            widget.addItems(["en_US", "de_DE", "fr_FR", "es_ES"])
            widget.setCurrentText(str(value))
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return
        elif key == "site_theme":
            widget = QComboBox()
            widget.addItem("default-blog")

            # Lade App-Config, um den Pfad zu den Themes zu finden
            app_config_path = os.path.join(self.app_root, "app_config.yaml")
            if os.path.exists(app_config_path):
                app_config_manager = ConfigManager(app_config_path)
                app_config = app_config_manager.load()
                themes_path = app_config.get("paths", {}).get("themes", "themes")
                global_themes_dir = os.path.join(self.app_root, themes_path)

                if os.path.isdir(global_themes_dir):
                    for theme_name in sorted(os.listdir(global_themes_dir)):
                        if os.path.isdir(os.path.join(global_themes_dir, theme_name)):
                            widget.addItem(theme_name)
            
            index = widget.findText(str(value))
            if index >= 0:
                widget.setCurrentIndex(index)
            
            parent_layout.addRow(f"{str(key).replace('_', ' ').title()}:", widget)
            self.inputs[tuple(key_path)] = (widget, type(value))
            return

        super().add_input_field(key, value, parent_layout, key_path)

    def get_widget_value(self, widget, original_type):
        if isinstance(widget, (LinksEditor, SocialLinksEditor)):
            return widget.get_data()
        return super().get_widget_value(widget, original_type)

    def handle_theme_copy(self, old_theme, new_theme):
        if new_theme == "default-blog" or new_theme == old_theme:
            return

        project_root = os.path.dirname(self.config_path)
        themes_dir_name = self.config_data.get("themes_directory", "themes")
        dest_dir = os.path.join(project_root, themes_dir_name)
        dest_path = os.path.join(dest_dir, new_theme)

        if os.path.exists(dest_path):
            QMessageBox.information(self, _("Theme Exists"), 
                                    _("The theme '{new_theme}' already exists in your project's themes folder. No files were copied.").format(new_theme=new_theme))
            return

        # Lade App-Config, um den Pfad zu den Themes zu finden
        app_config_path = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_path):
            app_config_manager = ConfigManager(app_config_path)
            app_config = app_config_manager.load()
            themes_path = app_config.get("paths", {}).get("themes", "themes")
            source_path = os.path.join(self.app_root, themes_path, new_theme)

            if os.path.isdir(source_path):
                try:
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copytree(source_path, dest_path)
                    QMessageBox.information(self, _("Theme Copied"), 
                                            _("The theme '{new_theme}' has been copied to your project's themes folder.").format(new_theme=new_theme))
                except Exception as e:
                    QMessageBox.critical(self, _("Copy Error"), _("Could not copy theme: {e}").format(e=e))
            else:
                QMessageBox.warning(self, _("Not Found"), _("The source for theme '{new_theme}' could not be found.").format(new_theme=new_theme))

    def save_config(self):
        new_theme_value = self.inputs[('site_theme',)][0].currentText()
        original_theme_value = self.config_data.get('site_theme', 'default')

        self.handle_theme_copy(original_theme_value, new_theme_value)

        super().save_config()

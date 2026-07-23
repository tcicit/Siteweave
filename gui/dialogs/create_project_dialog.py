import os
import re
import frontmatter
from PyQt6.QtWidgets import (QFileDialog, QLineEdit, QPushButton, QHBoxLayout, QLabel, QMessageBox, QGroupBox, QVBoxLayout, QComboBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from .project_config_dialog import ProjectConfigDialog
from core.i18n import _

class CreateProjectDialog(ProjectConfigDialog):
    def __init__(self, app_root, parent=None):
        # Dummy path, will not be used for loading
        super().__init__("dummy_config.yaml", app_root, parent)
        self.setWindowTitle(_("Create New Project"))
        self.created_project_path = None
        
        # Change Save button to Create
        self.buttons.button(self.buttons.StandardButton.Save).setText(_("Create"))

    def init_ui(self):
        # Add Project Path selection at the top
        top_layout = QVBoxLayout()
        
        path_group = QGroupBox(_("Project Location"))
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(_("Select parent directory"))
        self.browse_btn = QPushButton("...")
        self.browse_btn.clicked.connect(self.browse_location)
        
        path_layout.addWidget(QLabel(_("Location:")))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        path_group.setLayout(path_layout)
        
        
        top_layout.addWidget(path_group)

        
        # Insert at the top of main layout (before tabs)
        self.main_layout.insertLayout(0, top_layout)
        
        super().init_ui()

        # Theme-Vorschau Logik hinzufügen
        self.theme_combo = None
        for key_path, (widget, unused_type) in self.inputs.items():
            if key_path == ('site_theme',):
                if isinstance(widget, QComboBox):
                    self.theme_combo = widget
                break
        
        if self.theme_combo:
            self.theme_preview = QLabel(_("No preview available"))
            self.theme_preview.setFixedSize(240, 135)
            self.theme_preview.setStyleSheet("border: 1px solid #ccc; background: #eee; border-radius: 4px;")
            self.theme_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # In den "General" Tab einfügen
            if "General" in self.tab_layouts:
                self.tab_layouts["General"].addRow(_("Theme Preview:"), self.theme_preview)
            
            self.theme_combo.currentIndexChanged.connect(self.update_theme_preview)
            self.update_theme_preview()

    def update_theme_preview(self):
        """Lädt das preview.png des aktuell gewählten Themes."""
        theme_name = self.theme_combo.currentData()
        if not theme_name or theme_name == "none":
            self.theme_preview.setText(_("Minimal Project\n(No Theme)"))
            self.theme_preview.setPixmap(QPixmap())
            return

        # Suche nach preview.png in den globalen Themes
        # (In CreateProjectDialog gibt es noch keine lokalen Projekt-Themes)
        from core.config_manager import ConfigManager
        app_config = ConfigManager(ConfigManager.get_app_config_path()).load()
        themes_path = app_config.get("paths", {}).get("themes", "themes")
        theme_dir = os.path.join(self.app_root, themes_path, theme_name)
        preview_path = os.path.join(theme_dir, "preview.png")

        if os.path.exists(preview_path):
            self.theme_preview.setPixmap(QPixmap(preview_path).scaled(self.theme_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.theme_preview.setText(_("No preview for\n{theme}").format(theme=theme_name))

    def load_config(self):
        # Override to skip file loading and just set defaults
        self.config_data = {}
        self.set_defaults()
        self.populate_fields()

    def browse_location(self):
        dir_path = QFileDialog.getExistingDirectory(self, _("Select Parent Directory"))
        if dir_path:
            self.path_input.setText(dir_path)





    def save_config(self):
        parent_dir = self.path_input.text().strip()
        if not parent_dir or not os.path.isdir(parent_dir):
            QMessageBox.warning(self, _("Error"), _("Please select a valid parent directory."))
            return

        # Reconstruct config data from widgets
        new_data = self.get_current_config_data()
        
        # Validation
        site_name = new_data.get("site_name", "New Project")
        if not site_name.strip():
             QMessageBox.warning(self, _("Error"), _("The field 'Site Name' is required."))
             return

        site_url = new_data.get("site_url", "")
        if site_url and not re.match(r'^https?://', site_url):
             QMessageBox.warning(self, _("Error"), _("The Site URL must start with http:// or https://"))
             return

        # Sanitize project name for folder name
        safe_foldername = re.sub(r'[<>:"/\\|?*]', '', site_name).strip().replace(' ', '_')
        if not safe_foldername:
            safe_foldername = "New_Project"
            
        project_path = os.path.join(parent_dir, safe_foldername)
        
        if os.path.exists(project_path):
             QMessageBox.warning(self, _("Error"), _("The folder '{folder}' already exists.").format(folder=safe_foldername))
             return

        
        try:
            
            # Create directories
            os.makedirs(project_path)
            folders = ["content", "themes", "themes/none/templates", "assets", "plugins", "site_output", "backup", "themes/none/css", "themes/none/js"]
            for folder in folders:
                os.makedirs(os.path.join(project_path, folder), exist_ok=True)
            
            # Write config.yaml
            self.config_path = os.path.join(project_path, "config.yaml")
            self.project_root = project_path
            self.config_data = new_data
             # Theme kopieren, falls eines ausgewählt wurde
            site_theme = new_data.get("site_theme", "none")
            if site_theme and site_theme != "none":
                self._copy_theme_files("", site_theme)
                self.write_config(new_data)
            
            # Create default content
            self.create_default_content(project_path, site_name)

            self.created_project_path = project_path
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not create project: {e}").format(e=e))

    def get_current_config_data(self):
        import copy
        new_data = copy.deepcopy(self.config_data)
        for key_path, (widget, original_type) in self.inputs.items():
            value = self.get_widget_value(widget, original_type)
            target = new_data
            for k in key_path[:-1]:
                target = target.setdefault(k, {})
            target[key_path[-1]] = value
        return new_data

    def create_default_content(self, path, project_name):
        # content/index.md
        index_md_path = os.path.join(path, "content", "index.md")
        if not os.path.exists(index_md_path):
            post = frontmatter.Post(
                f"# {_('Welcome')}\n\n{_('This is your new project.')}",
                title=_("Home"),
                date="2026-01-01",
                layout="full-width"
            )
            with open(index_md_path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))

        # templates/base.html
        base_html_path = os.path.join(path, "themes/none/templates", "base.html")
        if not os.path.exists(base_html_path):
            base_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>{{{{ page_title }}}} | {{{{ site_name }}}}</title>
    <link rel="stylesheet" href="{{{{ relative_prefix }}}}css/style.css">
</head>
<body>
    <header>
        <h1>{{{{ page_title }}}}</h1>
        <nav>
            <a href="{{{{ relative_prefix }}}}index.html">{_("Home")}</a>
        </nav>
    </header>
    <main>
        {{{{ content }}}}
    </main>
</body>
</html>
"""
            with open(base_html_path, "w", encoding="utf-8") as f:
                f.write(base_html)

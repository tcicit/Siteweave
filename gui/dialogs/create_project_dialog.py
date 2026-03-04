import os
import re
from PyQt6.QtWidgets import (QFileDialog, QLineEdit, QPushButton, QHBoxLayout, QLabel, QMessageBox, QGroupBox, QVBoxLayout)
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
        
        site_name = new_data.get("site_name", "New Project")
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
            folders = ["content", "templates", "assets", "plugins", "site_output", "backup"]
            for folder in folders:
                os.makedirs(os.path.join(project_path, folder), exist_ok=True)
            
            # Write config.yaml
            self.config_path = os.path.join(project_path, "config.yaml")
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
        index_content = f'---\ntitle: {_("Home")}\ndate: 2025-01-01\nlayout: full-width\n---\n\n# {_("Welcome")}\n\n{_("This is your new project.")}\n'
        with open(os.path.join(path, "content", "index.md"), "w", encoding="utf-8") as f:
            f.write(index_content)

        # templates/base.html
        base_html = f'<!DOCTYPE html>\n<html lang="de">\n<head>\n    <meta charset="UTF-8">\n    <title>{{{{ page_title }}}} | {{{{ site_name }}}}</title>\n    <link rel="stylesheet" href="{{{{ relative_prefix }}}}css/style.css">\n</head>\n<body>\n    <header>\n        <h1>{{{{ page_title }}}}</h1>\n        <nav>\n            <a href="{{{{ relative_prefix }}}}index.html">{_("Home")}</a>\n        </nav>\n    </header>\n    <main>\n        {{{{ content }}}}\n    </main>\n</body>\n</html>\n'
        with open(os.path.join(path, "templates", "base.html"), "w", encoding="utf-8") as f:
            f.write(base_html)

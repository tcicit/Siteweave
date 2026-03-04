from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, 
                             QFileDialog, QInputDialog, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import Qt
from core.config_manager import ConfigManager
import os
from core.i18n import _

class ProjectManagerDialog(QDialog):
    def __init__(self, app_config_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Manage Projects"))
        self.resize(600, 400)
        self.config_manager = ConfigManager(app_config_path)
        self.app_config = self.config_manager.load()
        self.recent_projects = self.app_config.get("recent_projects", [])
        if not isinstance(self.recent_projects, list):
            self.recent_projects = []
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.refresh_list()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton(_("Register (Add)"))
        self.btn_add.clicked.connect(self.register_project)
        
        self.btn_edit = QPushButton(_("Edit Path"))
        self.btn_edit.clicked.connect(self.edit_path)
        
        self.btn_remove = QPushButton(_("Unregister"))
        self.btn_remove.clicked.connect(self.unregister_project)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_remove)
        
        layout.addLayout(btn_layout)
        
        close_btn = QPushButton(_("Close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def refresh_list(self):
        self.list_widget.clear()
        for path in self.recent_projects:
            item = QListWidgetItem(path)
            if not os.path.exists(path):
                item.setText(f"{path} ({_('Not Found')})")
                item.setForeground(Qt.GlobalColor.red)
            self.list_widget.addItem(item)

    def save_projects(self):
        self.config_manager.update({"recent_projects": self.recent_projects})
        self.config_manager.save()

    def register_project(self):
        dir_path = QFileDialog.getExistingDirectory(self, _("Select Project Folder"))
        if dir_path:
            if dir_path not in self.recent_projects:
                self.recent_projects.insert(0, dir_path)
                self.save_projects()
                self.refresh_list()
            else:
                QMessageBox.information(self, _("Info"), _("Project is already registered."))

    def unregister_project(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            del self.recent_projects[row]
            self.save_projects()
            self.refresh_list()
        else:
            QMessageBox.warning(self, _("Warning"), _("Please select a project to unregister."))

    def edit_path(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            old_path = self.recent_projects[row]
            new_path, ok = QInputDialog.getText(self, _("Edit Path"), _("New Path:"), text=old_path)
            if ok and new_path:
                self.recent_projects[row] = new_path
                self.save_projects()
                self.refresh_list()
        else:
            QMessageBox.warning(self, _("Warning"), _("Please select a project to edit."))

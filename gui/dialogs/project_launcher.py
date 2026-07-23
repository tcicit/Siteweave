import os
import json
import shutil
import re
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, QListWidgetItem, QInputDialog, QMenu, QLineEdit, QSpacerItem, QSizePolicy,
                             QScrollArea, QGridLayout, QWidget, QFrame, QDialogButtonBox)
from PyQt6.QtCore import Qt, QSettings, QUrl, QSize
from PyQt6.QtGui import QIcon, QDesktopServices, QColor
from core.config_manager import ConfigManager
from .create_project_dialog import CreateProjectDialog
from project_card import ProjectCard

from core import SETTINGS_ORG, SETTINGS_APP

from core.i18n import _


class EditProjectDirectoryDialog(QDialog):
    """Ein kleiner Dialog zum manuellen Bearbeiten oder Auswählen eines Projektpfads."""
    def __init__(self, current_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Edit Project Path"))
        self.resize(550, 120)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(_("Path to project folder:")))
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(current_path)
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(40)
        browse_btn.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def browse_path(self):
        new_dir = QFileDialog.getExistingDirectory(self, _("Select Project Folder"), self.path_edit.text())
        if new_dir:
            self.path_edit.setText(new_dir)

    def get_path(self):
        return self.path_edit.text().strip()


class ProjectLauncher(QDialog):
    '''
    Docstring für ProjectLauncher
    Dieser Dialog wird beim Start der Anwendung angezeigt und ermöglicht es dem Benutzer, ein bestehendes Projekt zu öffnen oder ein neues Projekt zu erstellen.
    Funktionen:
- Anzeige einer Liste der zuletzt geöffneten Projekte mit Namen und Pfaden.
- Doppelklick auf ein Projekt öffnet es.
- Kontextmenü für jedes Projekt mit Optionen zum Öffnen, Bearbeiten des Pfads, Verschieben, Entfernen aus der Liste und Löschen von der Festplatte.
- Button zum Öffnen eines bestehenden Projekts über einen Ordnerauswahldialog.
- Button zum Erstellen eines neuen Projekts mit Auswahl eines Templates, Eingabe eines Namens und Auswahl eines Speicherorts.
- Automatische Validierung von Projektordnern (Vorhandensein von config.yaml oder config.toml) und Möglichkeit zur Initialisierung eines neuen Projekts, wenn kein gültiges Projekt gefunden wird.  

'''
    def __init__(self, app_root):
        super().__init__()
        self.setWindowTitle(_("Register / New Project - Sitewave"))
        self.resize(800, 600)
        self.app_root = app_root
        self.selected_project = None
        self.config_manager = ConfigManager(os.path.join(self.app_root, "app_config.yaml"))
        self.settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
        
        # Icon setzen
        icon_path = os.path.join(self.app_root, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(_("Welcome! Please select a project."))
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Recent Projects List
        layout.addWidget(QLabel(_("Recently opened:")))
        
        # Scroll Area für die Projekt-Karten
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.cards_layout.setSpacing(20)
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)

        self.load_recent_projects()

        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_open = QPushButton(_("Open Other..."))
        self.btn_open.clicked.connect(self.browse_project)
        self.btn_open.setMinimumHeight(40)

        self.btn_new = QPushButton(_("Create New Project..."))
        self.btn_new.clicked.connect(self.create_new_project)
        self.btn_new.setMinimumHeight(40)

        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_new)
        
        layout.addLayout(btn_layout)

    def load_recent_projects(self):
        """Lädt die Projekte und erstellt die Karten."""
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recent = self.get_recent_projects()

        for path in recent:
            card = ProjectCard.from_path(path)
            card.clicked.connect(self.open_project)
            card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            card.customContextMenuRequested.connect(lambda pos, p=path: self.show_context_menu(pos, p))
            # Initial hinzufügen (Position wird durch rearrange_cards korrigiert)
            self.cards_layout.addWidget(card, 0, 0)

        self.rearrange_cards()

    def rearrange_cards(self):
        """Berechnet die Spaltenanzahl basierend auf der Breite und ordnet Karten neu an."""
        if not hasattr(self, 'cards_layout') or self.cards_layout.count() == 0:
            return

        # Aktuell verfügbare Breite im Viewport der ScrollArea
        width = self.scroll_area.viewport().width()
        if width <= 100: width = self.width() # Fallback für Initialisierung

        card_width = 280
        spacing = 20
        cols = max(1, width // (card_width + spacing))

        widgets = []
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                widgets.append(item.widget())

        for i, widget in enumerate(widgets):
            row = i // cols
            col = i % cols
            self.cards_layout.addWidget(widget, row, col)

    def resizeEvent(self, event):
        """Aktualisiert das Karten-Grid beim Ändern der Fenstergröße."""
        super().resizeEvent(event)
        self.rearrange_cards()

    def add_to_recent(self, path):
        recent = self.get_recent_projects()
        
        # Portabilität: Wenn das Projekt im App-Ordner liegt, relativ speichern
        abs_path = os.path.abspath(path)
        abs_app_root = os.path.abspath(self.app_root)
        
        if abs_path.startswith(abs_app_root):
            path = os.path.relpath(abs_path, abs_app_root)
        else:
            path = abs_path

        # Remove if exists (to move to top)
        if path in recent:
            recent.remove(path)

        recent.insert(0, path)
        # Keep only last 10
        recent = recent[:10]

        self.save_recent_projects(recent)

    def get_recent_projects(self):
        config = self.config_manager.load()
        return config.get("recent_projects") or []

    def save_recent_projects(self, projects):
        try:
            # Lade aktuelle Config, um nichts zu überschreiben
            self.config_manager.load()
            self.config_manager.update({"recent_projects": projects})
            self.config_manager.save()
        except Exception as e:
            print(f"Error saving projects: {e}")

    def browse_project(self):
        dir_path = QFileDialog.getExistingDirectory(self, _("Select Project Folder"))
        if dir_path:
            self.open_project(dir_path)

    def open_project(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(self, _("Error"), _("The selected path does not exist anymore."))
            self.load_recent_projects()
            return

        # Check for config.yaml OR config.toml to verify it's a project
        has_yaml = os.path.exists(os.path.join(path, "config.yaml"))
        has_toml = os.path.exists(os.path.join(path, "config.toml"))

        if not has_yaml and not has_toml:
            reply = QMessageBox.question(
                self,
                _("No project found"),
                _("No configuration file (config.yaml or config.toml) was found in this folder.\\nWould you like to initialize a new project here?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.initialize_project(path)
            else:
                return

        self.add_to_recent(path)
        self.selected_project = path
        self.accept()

    def create_new_project(self):
        dialog = CreateProjectDialog(self.app_root, self)
        if dialog.exec():
            new_path = dialog.created_project_path
            if new_path and os.path.exists(new_path):
                self.add_to_recent(new_path)
                self.selected_project = new_path
                self.accept()

    def initialize_project(self, path, template_path=None, project_name=None):
        """Erstellt die Standard-Ordnerstruktur und Dateien."""
        if project_name is None:
            project_name = _("New Project")
        try:
            if template_path and os.path.exists(template_path):
                # Template kopieren
                shutil.copytree(template_path, path, dirs_exist_ok=True)

                # Platzhalter ersetzen
                self.replace_placeholders(path, project_name)

                QMessageBox.information(self, _("Success"), _("New project based on '{template_name}' created.").format(template_name=os.path.basename(template_path)))
                return

            # Ordnerstruktur
            folders = ["content", "templates", "assets", "plugins", "site_output"]
            for folder in folders:
                os.makedirs(os.path.join(path, folder), exist_ok=True)

            # config.yaml (YAML Format)
            config_content = f"""site_name: "{project_name}"
site_url: "http://localhost:8000"
content_directory: "content"
site_output_directory: "site_output"
template_directory: "templates"
assets_directory: "assets"
plugin_directory: "plugins"
backup_directory: "backup"
markdown_extensions: [".md", ".markdown"]
log_level: "INFO"
"""
            with open(os.path.join(path, "config.yaml"), "w", encoding="utf-8") as f:
                f.write(config_content)

            # content/index.md
            index_content = f"""---
title: {_("Home")}
date: 2025-01-01
layout: full-width
---

# {_("Welcome")}

{_("This is your new project.")}
"""
            with open(os.path.join(path, "content", "index.md"), "w", encoding="utf-8") as f:
                f.write(index_content)

            # templates/base.html
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
            with open(os.path.join(path, "templates", "base.html"), "w", encoding="utf-8") as f:
                f.write(base_html)

            QMessageBox.information(self, _("Success"), _("New project has been successfully created."))

        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not initialize project: {e}").format(e=e))

    def show_context_menu(self, pos, path):
        sender_card = self.sender()
        menu = QMenu()
        
        open_action = menu.addAction(_("Open"))
        edit_action = menu.addAction(_("Edit Path"))
        remove_action = menu.addAction(_("Remove from List"))
        
        action = menu.exec(sender_card.mapToGlobal(pos))
        
        if action == open_action:
            self.open_project(path)
        elif action == edit_action:
            dlg = EditProjectDirectoryDialog(path, self)
            if dlg.exec():
                new_path = dlg.get_path()
                recent = self.get_recent_projects()
                if path in recent:
                    recent[recent.index(path)] = new_path
                    self.save_recent_projects(recent)
                    self.load_recent_projects()
        elif action == remove_action:
            recent = self.get_recent_projects()
            if path in recent:
                recent.remove(path)
                self.save_recent_projects(recent)
                self.load_recent_projects()
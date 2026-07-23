import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                             QMenu, QMessageBox, QInputDialog, QPushButton, QSizePolicy, QLineEdit)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from core.config_manager import ConfigManager

from core import SETTINGS_ORG, SETTINGS_APP

from core.i18n import _

class ProjectPanel(QWidget):
    '''
    Docstring für ProjectPanel
    Dieses Panel zeigt die zuletzt geöffneten Projekte an und ermöglicht es dem Benutzer, schnell zwischen ihnen zu wechseln.
    Funktionen:
- Anzeige einer Liste der zuletzt geöffneten Projekte mit Namen und Pfaden.
- Hervorhebung des aktuellen Projekts in der Liste.
- Kontextmenü für jedes Projekt mit Optionen zum Öffnen, Umbenennen, Entfernen und Öffnen im Dateimanager.
- Suchfunktion zum Filtern der Projekte in der Liste.
- Toggle-Button zum Ein- und Ausblenden der Projektliste, wobei der Status gespeichert wird.
- Signal, das den Pfad zum neuen Projekt sendet, wenn ein Projekt ausgewählt oder umbenannt wird.

    '''
    project_switched = pyqtSignal(str) # Signal sendet den Pfad zum neuen Projekt

    def __init__(self, current_project_path, app_root):
        super().__init__()
        self.current_project_path = current_project_path
        self.app_root = app_root
        self.config_manager = ConfigManager(os.path.join(self.app_root, "app_config.yaml"))
        self.settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle Button (Konsistent mit anderen Panels)
        self.toggle_btn = QPushButton(_("Projects ▼"))
        self.toggle_btn.setCheckable(True)
        
        # Status laden
        is_expanded = self.settings.value("project_panel_expanded", True, type=bool)
        self.toggle_btn.setChecked(is_expanded)
        
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

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search..."))
        self.search_input.textChanged.connect(self.filter_projects)
        layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)

        # Initialen Status anwenden
        self.toggle_content(is_expanded)

        self.load_projects()

    def set_dark_mode(self, enabled):
        """Wendet das Dark-Mode-Styling auf die Panel-spezifischen Widgets an."""
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)

    def toggle_content(self, checked):
        self.settings.setValue("project_panel_expanded", checked)
        self.list_widget.setVisible(checked)
        self.search_input.setVisible(checked)
        self.toggle_btn.setText(_("Projects ▼") if checked else _("Projects ▶"))
        if checked:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.setMaximumHeight(16777215)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.setMaximumHeight(self.toggle_btn.sizeHint().height())

    def load_projects(self):
        self.list_widget.clear()
        recent = self.get_recent_projects()
        
        # Sicherstellen, dass das aktuelle Projekt in der Liste ist
        if self.current_project_path and os.path.exists(self.current_project_path):
            # Normalisiere Pfade für den Vergleich
            abs_current = os.path.abspath(self.current_project_path)
            
            # Projekt an die erste Stelle schieben (oder hinzufügen)
            recent = [p for p in recent if os.path.abspath(p) != abs_current]
            recent.insert(0, self.current_project_path)
            recent = recent[:10] # Liste auf 10 Einträge begrenzen
            self.save_recent_projects(recent)

        for path in recent:
            if os.path.exists(path) and os.path.isdir(path):
                name = os.path.basename(path)
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setToolTip(path)
                
                # Aktuelles Projekt hervorheben
                if os.path.abspath(path) == os.path.abspath(self.current_project_path):
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setText(f"{name} ({_('Current')})")
                    # Optional: Hintergrundfarbe oder Icon setzen
                
                self.list_widget.addItem(item)

        if self.search_input.text():
            self.filter_projects(self.search_input.text())

    def get_recent_projects(self):
        config = self.config_manager.load()
        return config.get("recent_projects", [])

    def save_recent_projects(self, projects):
        try:
            # Lade aktuelle Config, um nichts zu überschreiben
            self.config_manager.load()
            self.config_manager.update({"recent_projects": projects})
            self.config_manager.save()
        except Exception as e:
            print(f"Error saving projects: {e}")

    def filter_projects(self, text):
        search_text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(search_text not in item.text().lower())

    def on_item_double_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        # Nur wechseln, wenn es nicht das aktuelle Projekt ist
        if os.path.abspath(path) != os.path.abspath(self.current_project_path):
            self.project_switched.emit(path)

    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        
        path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu()
        
        open_action = menu.addAction(_("Open"))
        open_fm_action = menu.addAction(_("Open in File Manager"))
        rename_action = menu.addAction(_("Rename"))
        menu.addSeparator()
        remove_action = menu.addAction(_("Remove from List"))
        
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        
        if action == open_action:
            if os.path.abspath(path) != os.path.abspath(self.current_project_path):
                self.project_switched.emit(path)
        elif action == open_fm_action:
            self.open_in_file_manager(path)
        elif action == rename_action:
            self.rename_project(item)
        elif action == remove_action:
            self.remove_project(item)

    def rename_project(self, item):
        old_path = item.data(Qt.ItemDataRole.UserRole)
        old_name = os.path.basename(old_path)
        
        new_name, ok = QInputDialog.getText(self, _("Rename Project"), _("New Name:"), text=old_name)
        if ok and new_name and new_name != old_name:
            parent_dir = os.path.dirname(old_path)
            new_path = os.path.join(parent_dir, new_name)
            
            if os.path.exists(new_path):
                QMessageBox.warning(self, _("Error"), _("A folder with this name already exists."))
                return

            # Prüfen, ob es das aktuelle Projekt ist
            is_current = (os.path.abspath(old_path) == os.path.abspath(self.current_project_path))
            
            try:
                os.rename(old_path, new_path)
                
                # Einstellungen aktualisieren
                recent = self.get_recent_projects()
                # Pfade in der Liste aktualisieren
                for i, p in enumerate(recent):
                    if os.path.abspath(p) == os.path.abspath(old_path):
                        recent[i] = new_path
                
                self.save_recent_projects(recent)
                
                if is_current:
                    QMessageBox.information(self, _("Project Renamed"), 
                                            _("The current project was renamed. The window will reload."))
                    self.project_switched.emit(new_path)
                else:
                    self.load_projects()
                    
            except OSError as e:
                QMessageBox.critical(self, _("Error"), _("Could not rename project: {e}\nMake sure no files are open in the folder.").format(e=e))

    def remove_project(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        recent = self.get_recent_projects()
        
        # Pfad aus der Liste entfernen
        recent = [p for p in recent if os.path.abspath(p) != os.path.abspath(path)]
        
        self.save_recent_projects(recent)
        self.load_projects()

    def open_in_file_manager(self, path):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, _("Error"), _("The folder does not exist anymore."))
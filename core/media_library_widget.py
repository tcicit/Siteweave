import os, re, subprocess, shutil, shlex
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QAbstractItemView, QFrame, QMenu, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt, QSize, QMimeData, QUrl, pyqtSignal, QFileSystemWatcher, QTimer
from PyQt6.QtGui import QIcon, QDrag, QPalette, QColor
from core.utils import is_editor_available, open_external_editor
from core.thumbnail_worker import ThumbnailWorker
from core.i18n import _
from core import link_utils

class MediaLibraryWidget(QWidget):
    insert_requested = pyqtSignal(str)
    insert_plugin_requested = pyqtSignal(str)

    def __init__(self, project_root, assets_dir, content_dir, thumbnail_size, app_config=None, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.assets_dir = assets_dir
        self.content_dir = content_dir
        self.thumbnail_size = thumbnail_size # Store it here
        self.app_config = app_config or {}

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = MediaListWidget(project_root, self, thumbnail_size)
        self.layout.addWidget(self.list_widget)

        # Dateisystem-Beobachter für automatische Aktualisierung
        self.assets_watcher = QFileSystemWatcher(self)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.setInterval(1000) # 1 Sekunde Verzögerung (Debounce)
        
        self.assets_watcher.directoryChanged.connect(self.refresh_timer.start)
        self.refresh_timer.timeout.connect(self.refresh_library)

        # Worker starten
        self.refresh_library()

    def update_project(self, project_root, assets_dir, content_dir):
        """Aktualisiert die Pfade für ein neu geladenes Projekt und startet den Scan neu."""
        self.project_root = project_root
        self.assets_dir = assets_dir
        self.content_dir = content_dir
        self.list_widget.project_root = project_root # This is already set in init, but good to update if project changes
        self.refresh_library()

    def set_dark_mode(self, enabled):
        """Passt das Widget an das gewählte Theme an."""
        p = self.list_widget.palette()
        if enabled:
            p.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
            p.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        else:
            p.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
            p.setColor(QPalette.ColorRole.Text, QColor("#000000"))
        self.list_widget.setPalette(p)

    # Diese Methode wird aufgerufen, um die Mediathek zu aktualisieren, z.B. nach einem Projektwechsel oder wenn neue Dateien hinzugefügt wurden.
    def refresh_library(self):
        """Bereinigt die Ansicht und startet den Thumbnail-Worker neu."""
        # Beobachtete Pfade aktualisieren (falls Unterordner hinzugekommen sind)
        self._update_watcher_paths()

        # Bestehenden Worker stoppen, falls er noch läuft
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop() # Ruft die neu implementierte stop() Methode auf
            self.worker.wait()
            
        self.list_widget.clear_and_set_size(self.thumbnail_size) # Pass size to clear_and_set_size
        self.worker = ThumbnailWorker(self.project_root, self.assets_dir)
        self.worker.thumbnail_ready.connect(self._add_item)
        self.worker.start()

    def update_thumbnail_size(self, new_size):
        if self.thumbnail_size != new_size:
            self.thumbnail_size = new_size
            self.list_widget.clear_and_set_size(new_size)
        self.worker = ThumbnailWorker(self.project_root, self.assets_dir)
        self.worker.thumbnail_ready.connect(self._add_item)
        self.worker.start()

    def _update_watcher_paths(self):
        """Aktualisiert die Liste der vom Watcher überwachten Verzeichnisse."""
        if not os.path.exists(self.assets_dir):
            return
            
        # Aktuelle Pfade entfernen
        existing_paths = self.assets_watcher.directories()
        if existing_paths:
            self.assets_watcher.removePaths(existing_paths)
            
        # Assets-Ordner und alle Unterordner hinzufügen
        paths_to_watch = [self.assets_dir]
        for root, dirs, _ in os.walk(self.assets_dir):
            for d in dirs:
                paths_to_watch.append(os.path.join(root, d))
        
        self.assets_watcher.addPaths(paths_to_watch)

    # Fügt ein neues Element zur Liste hinzu, wenn ein Thumbnail bereit ist
    def _add_item(self, original_path, thumb_path):
        rel_path = os.path.relpath(original_path, self.assets_dir)
        filename = os.path.basename(original_path)
        
        item = QListWidgetItem(QIcon(thumb_path), filename)
        # Wir speichern den relativen Pfad für den Drag-and-Drop Export
        # Assets liegen im Output meist unter 'assets/...'
        web_path = os.path.join("assets", rel_path).replace(os.sep, "/")
        item.setData(Qt.ItemDataRole.UserRole, web_path)
        item.setData(Qt.ItemDataRole.UserRole + 1, original_path)
        item.setToolTip(_("{filename}\nPath: {web_path}").format(filename=filename, web_path=web_path))
        
        self.list_widget.addItem(item)

class MediaListWidget(QListWidget):
    """Custom ListWidget that provides icon mode and drag support."""
    def __init__(self, project_root, library_widget, thumbnail_size):
        super().__init__()
        self.project_root = project_root
        self.thumbnail_size = thumbnail_size
        self.library_widget = library_widget
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QSize(self.thumbnail_size, self.thumbnail_size))
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setDragEnabled(True)
        self.setSpacing(10)
        self.setWordWrap(True)
        self.setMovement(QListWidget.Movement.Static)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def clear_and_set_size(self, new_size):
        self.clear()
        self.thumbnail_size = new_size
        self.setIconSize(QSize(self.thumbnail_size, self.thumbnail_size))    

    def on_item_double_clicked(self, item):
        """Fügt das Bild bei Doppelklick ein."""
        abs_path = item.data(Qt.ItemDataRole.UserRole + 1)
        if abs_path:
            self.library_widget.insert_requested.emit(abs_path)


    # Kontextmenü mit Optionen zum Einfügen, Umbenennen und Löschen von Dateien
    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return
            
        menu = QMenu()

        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')
        file_path = item.data(Qt.ItemDataRole.UserRole + 1)
        if file_path and file_path.lower().endswith(image_extensions):
            plugin_act = menu.addAction(_("Insert as Image Plugin"))
            # Hier rufst du die neue Methode im Editor auf
            plugin_act.triggered.connect(lambda: self.library_widget.insert_plugin_requested.emit(file_path))

        # Externe Editoren aus Konfiguration laden
        if file_path and self.library_widget.app_config:
            ext = os.path.splitext(file_path)[1].lower()
            editors = self.library_widget.app_config.get('external_editors', [])
            
            for editor in editors:
                supported_exts = [e.lower() for e in editor.get('extensions', [])]
                if ext in supported_exts:
                    cmd = editor.get('command', [])
                    
                    # Überprüfen, ob der Editor installiert ist
                    if not is_editor_available(cmd):
                        continue

                    name = editor.get('name', 'Editor')
                    icon_name = editor.get('icon', 'applications-other')
                    
                    #act = menu.addAction(QIcon.fromTheme(icon_name), _("Edit with {name}").format(name=name))
                    # Closure-Fix: command und file_path explizit an lambda binden
                    #act.triggered.connect(lambda checked, c=cmd, p=file_path: self.open_external_editor(c, p))
                    act = menu.addAction(QIcon.fromTheme(icon_name), _("Edit with {name}").format(name=name)) # type: ignore
                    act.triggered.connect(lambda checked, c=cmd, p=file_path: self._call_external_editor(c, p)) # type: ignore

        menu.addSeparator()

        insert_action = menu.addAction(QIcon.fromTheme("document-import"), _("Insert into Document"))
        rename_action = menu.addAction(QIcon.fromTheme("edit-rename"), _("Rename"))
        delete_action = menu.addAction(QIcon.fromTheme("edit-delete"), _("Delete"))
        
        action = menu.exec(self.mapToGlobal(pos))
        if action == insert_action:
            abs_path = item.data(Qt.ItemDataRole.UserRole + 1)
            if abs_path:
                self.library_widget.insert_requested.emit(abs_path)
        elif action == rename_action:
            self.rename_item(item)
        elif action == delete_action:
            self.delete_item(item)

    def _call_external_editor(self, command, file_path):
        """
        Wrapper-Methode, die die generische open_external_editor Funktion aufruft
        und Fehler mit einer QMessageBox anzeigt.
        """
        try:
            open_external_editor(command, file_path)
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not start editor: {e}").format(e=e))

    def rename_item(self, item):
        old_path = item.data(Qt.ItemDataRole.UserRole + 1)
        if not old_path or not os.path.exists(old_path):
            return

        old_name = os.path.basename(old_path)
        new_name, ok = QInputDialog.getText(self, _("Rename File"), _("New Name:"), text=old_name)
        
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            if os.path.exists(new_path):
                QMessageBox.warning(self, _("Error"), _("A file with this name already exists."))
                return
                
            try:
                os.rename(old_path, new_path)
                
                # Links in Dokumenten aktualisieren?
                reply = QMessageBox.question(self, _("Update Links?"), 
                                             _("Do you want to update links in Markdown files to point to the new filename?"),
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if reply == QMessageBox.StandardButton.Yes:
                    count = link_utils.update_links_in_directory(self.library_widget.content_dir, old_path, new_path)
                    if count > 0:
                        QMessageBox.information(self, _("Links Updated"), 
                                                _("Updated links in {count} files.").format(count=count))

                # Die Library komplett neu laden, um Pfade und Thumbnails zu aktualisieren
                self.library_widget.refresh_library()
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Could not rename file: {e}").format(e=e))

    def delete_item(self, item):
        path = item.data(Qt.ItemDataRole.UserRole + 1)
        if not path or not os.path.exists(path):
            return
            
        confirm = QMessageBox.question(self, _("Delete"), _("Do you really want to delete '{name}'?").format(name=os.path.basename(path)),
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Prüfen ob die Datei verwendet wird
            usage_count = link_utils.get_file_usage_count(self.library_widget.content_dir, path)
            if usage_count > 0:
                warning = QMessageBox.warning(self, _("File in Use"), 
                                              _("This file is referenced in {count} Markdown files. If you delete it, these links will break. Proceed?").format(count=usage_count),
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if warning == QMessageBox.StandardButton.No:
                    return

            try:
                os.remove(path)
                self.takeItem(self.row(item))
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Could not delete file: {e}").format(e=e))

    def get_markdown_code(self, item):
        web_path = item.data(Qt.ItemDataRole.UserRole)
        alt_text = item.text().rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ').title()
        return f"![{alt_text}]({web_path})"

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return

        markdown_code = self.get_markdown_code(item)
        abs_path = item.data(Qt.ItemDataRole.UserRole + 1)

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(markdown_code)
        
        # Zusätzlich als URL senden, damit der Editor insert_file_link nutzen kann
        if abs_path:
            mime_data.setUrls([QUrl.fromLocalFile(abs_path)])
        
        drag.setMimeData(mime_data)
        
        # Optional: Thumbnail als Drag-Icon setzen
        pixmap = item.icon().pixmap(QSize(64, 64))
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())

        drag.exec(Qt.DropAction.CopyAction)
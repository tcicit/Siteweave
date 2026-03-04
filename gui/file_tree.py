'''
FileTree: A QTreeView subclass for displaying and managing the file structure of the content directory.
- Uses QFileSystemModel to display files and folders.
- Supports context menu actions for creating, renaming, cloning, moving and deleting files and folders.
- Implements a custom sorting mechanism that can sort by name, date or a custom 'weight' defined in the frontmatter of Markdown files.
- The 'set_current_file_path(path)' method can be called to highlight the currently open file in the tree.
- The 'create_file_requested' signal is emitted with the target directory when the user wants to create a new file, allowing the main window to handle the file creation logic (e.g. showing a dialog to choose a template).
- The tree automatically updates to reflect changes in the file system, and it can be refreshed manually if needed.
- The panel can be toggled between expanded and collapsed states, and it adapts its size accordingly.


'''



import os
import shutil
import re
import frontmatter
from PyQt6.QtWidgets import QTreeView, QMenu, QMessageBox, QInputDialog, QStyledItemDelegate, QFileDialog
from PyQt6.QtGui import QFileSystemModel, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QSortFilterProxyModel
from core.i18n import _

class FrontmatterSortProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sort_role = "name"
        self.weight_cache = {}

    def set_sort_role(self, role):
        self.sort_role = role
        self.invalidate()

    def lessThan(self, left, right):
        if self.sort_role == "weight":
            source_model = self.sourceModel()
            
            # Ordner immer zuerst (Standardverhalten beibehalten)
            is_dir_left = source_model.isDir(left)
            is_dir_right = source_model.isDir(right)
            if is_dir_left and not is_dir_right: return True
            if not is_dir_left and is_dir_right: return False
            
            # Wenn beides Dateien sind, Gewichtung prüfen
            path_left = source_model.filePath(left)
            path_right = source_model.filePath(right)
            
            if path_left.endswith(('.md', '.markdown')) and path_right.endswith(('.md', '.markdown')):
                w_left = self._get_weight(path_left)
                w_right = self._get_weight(path_right)
                if w_left != w_right:
                    return w_left < w_right
        
        return super().lessThan(left, right)

    def _get_weight(self, path):
        if path in self.weight_cache:
            return self.weight_cache[path]
        
        weight = 0
        try:
            if os.path.exists(path):
                # Nur Metadaten laden, nicht den ganzen Inhalt, wenn möglich (frontmatter lädt leider alles)
                post = frontmatter.load(path)
                weight = int(post.metadata.get('weight', 0))
        except:
            pass
        
        self.weight_cache[path] = weight
        return weight

class FileTreeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = None

    def set_current_path(self, path):
        self.current_path = path

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if self.current_path:
            file_path = index.data(QFileSystemModel.Roles.FilePathRole)
            if file_path and os.path.normpath(file_path) == os.path.normpath(self.current_path):
                option.font.setBold(True)

class FileTree(QTreeView):
    create_file_requested = pyqtSignal(str)

    def __init__(self, root_path):
        super().__init__()
        self.fs_model = QFileSystemModel()
        self.fs_model.setRootPath(root_path)
        
        # Proxy Model für Sortierung
        self.proxy_model = FrontmatterSortProxyModel(self)
        self.proxy_model.setSourceModel(self.fs_model)
        
        self.setModel(self.proxy_model)
        self.setRootIndex(self.proxy_model.mapFromSource(self.fs_model.index(root_path)))
        
        # Nur Namen anzeigen, andere Spalten (Größe, Typ, Datum) ausblenden
        for i in range(1, 4):
            self.setColumnHidden(i, True)
        
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder) # Standardmäßig nach Name sortieren

        # Kontextmenü aktivieren
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        # Delegate für Fettschrift
        self.delegate = FileTreeDelegate(self)
        self.setItemDelegate(self.delegate)

    def set_current_file_path(self, path):
        self.delegate.set_current_path(path)
        self.viewport().update()

    def get_file_path(self, index):
        """Gibt den Dateipfad für einen Index zurück (handhabt Proxy-Mapping)."""
        if not index.isValid():
            return None
        
        # Wenn wir ein Proxy-Model verwenden, müssen wir den Index mappen
        if isinstance(self.model(), QSortFilterProxyModel):
            index = self.proxy_model.mapToSource(index)
        return self.fs_model.filePath(index)

    def open_context_menu(self, position):
        index = self.indexAt(position)
        menu = QMenu()

        # Aktionen erstellen
        new_file_action = QAction(_("New File"), self)
        new_file_action.triggered.connect(lambda: self.create_file(index))
        menu.addAction(new_file_action)

        new_dir_action = QAction(_("New Folder"), self)
        new_dir_action.triggered.connect(lambda: self.create_directory(index))
        menu.addAction(new_dir_action)

        if index.isValid():
            menu.addSeparator()
            
            rename_action = QAction(_("Rename"), self)
            rename_action.triggered.connect(lambda: self.rename_item(index))
            menu.addAction(rename_action)

            clone_action = QAction(_("Clone"), self)
            clone_action.triggered.connect(lambda: self.clone_item(index))
            menu.addAction(clone_action)

            move_action = QAction(_("Move..."), self)
            move_action.triggered.connect(lambda: self.move_item(index))
            menu.addAction(move_action)

            delete_action = QAction(_("Delete"), self)
            delete_action.triggered.connect(lambda: self.delete_item(index))
            menu.addAction(delete_action)

        menu.addSeparator()
        sort_menu = menu.addMenu(_("Sort by"))

        sort_az_action = QAction(_("Name (A-Z)"), self)
        sort_az_action.triggered.connect(lambda: self.set_sorting("name", Qt.SortOrder.AscendingOrder))
        sort_menu.addAction(sort_az_action)

        sort_za_action = QAction(_("Name (Z-A)"), self)
        sort_za_action.triggered.connect(lambda: self.set_sorting("name", Qt.SortOrder.DescendingOrder))
        sort_menu.addAction(sort_za_action)

        sort_date_new_action = QAction(_("Date (Newest First)"), self)
        sort_date_new_action.triggered.connect(lambda: self.set_sorting("date", Qt.SortOrder.DescendingOrder))
        sort_menu.addAction(sort_date_new_action)

        sort_date_old_action = QAction(_("Date (Oldest First)"), self)
        sort_date_old_action.triggered.connect(lambda: self.set_sorting("date", Qt.SortOrder.AscendingOrder))
        sort_menu.addAction(sort_date_old_action)

        sort_weight_action = QAction(_("Weight (Frontmatter)"), self)
        sort_weight_action.triggered.connect(lambda: self.set_sorting("weight", Qt.SortOrder.AscendingOrder))
        sort_menu.addAction(sort_weight_action)

        menu.exec(self.viewport().mapToGlobal(position))

    def set_sorting(self, role, order):
        self.proxy_model.set_sort_role(role)
        column = 3 if role == "date" else 0
        self.sortByColumn(column, order)

    def create_directory(self, index):
        # Zielverzeichnis bestimmen
        if not index.isValid():
            parent_dir = self.fs_model.rootPath()
        else:
            # Index mappen, da er vom Proxy kommt
            source_index = self.proxy_model.mapToSource(index)
            if self.fs_model.isDir(source_index):
                parent_dir = self.fs_model.filePath(source_index)
            else:
                parent_dir = os.path.dirname(self.fs_model.filePath(source_index))

        dir_name, ok = QInputDialog.getText(self, _("New Folder"), _("Folder Name:"))
        if ok and dir_name:
            new_path = os.path.join(parent_dir, dir_name)
            try:
                os.mkdir(new_path)
            except OSError as e:
                QMessageBox.critical(self, _("Error"), _("Could not create folder: {e}").format(e=e))

    def create_file(self, index):
        # Zielverzeichnis bestimmen
        if not index.isValid():
            parent_dir = self.fs_model.rootPath()
        else:
            source_index = self.proxy_model.mapToSource(index)
            if self.fs_model.isDir(source_index):
                parent_dir = self.fs_model.filePath(source_index)
            else:
                parent_dir = os.path.dirname(self.fs_model.filePath(source_index))

        # Statt direkt zu erstellen, senden wir ein Signal an das Hauptfenster
        self.create_file_requested.emit(parent_dir)

    def update_links(self, root_dir, old_abs_path, new_abs_path):
        count = 0
        old_abs_path = os.path.normpath(old_abs_path)
        new_abs_path = os.path.normpath(new_abs_path)
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith(('.md', '.markdown')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        def replace_link(match):
                            prefix = match.group(1)
                            url = match.group(2)
                            suffix = match.group(3)
                            
                            if url.startswith(('http:', 'https:', 'mailto:', 'ftp:', '#')):
                                return match.group(0)
                            
                            try:
                                link_dir = os.path.dirname(file_path)
                                # Resolve absolute path of the link target
                                abs_link_target = os.path.normpath(os.path.join(link_dir, url))
                                
                                # Check if link points to the renamed file/folder or inside it
                                if abs_link_target == old_abs_path or str(abs_link_target).startswith(str(old_abs_path) + os.path.sep):
                                    if abs_link_target != old_abs_path:
                                        # It's inside the renamed directory
                                        rel_inside = os.path.relpath(abs_link_target, old_abs_path)
                                        target_abs_path = os.path.join(new_abs_path, rel_inside)
                                    else:
                                        target_abs_path = new_abs_path
                                        
                                    new_rel = os.path.relpath(target_abs_path, link_dir)
                                    new_rel = new_rel.replace(os.path.sep, '/')
                                    return f"{prefix}{new_rel}{suffix}"
                            except ValueError:
                                pass
                            return match.group(0)

                        # Regex for [text](url) and ![alt](url)
                        new_content = re.sub(r'(\[.*?\]\(|!\[.*?\]\()([^)]+)(\))', replace_link, content)
                        
                        if new_content != content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            count += 1
                    except Exception as e:
                        print(f"Error updating links in {file_path}: {e}")
        return count

    def rename_item(self, index):
        source_index = self.proxy_model.mapToSource(index)
        old_path = self.fs_model.filePath(source_index)
        old_name = self.fs_model.fileName(source_index)
        
        new_name, ok = QInputDialog.getText(self, _("Rename"), _("New Name:"), text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                
                # Links aktualisieren?
                reply = QMessageBox.question(
                    self, 
                    _("Update Links?"), 
                    _("Do you want to update links in other files to point to the new name?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    count = self.update_links(self.fs_model.rootPath(), old_path, new_path)
                    if count > 0:
                        QMessageBox.information(self, _("Links Updated"), _("Updated links in {count} files.").format(count=count))

            except OSError as e:
                QMessageBox.critical(self, _("Error"), _("Could not rename: {e}").format(e=e))

    def clone_item(self, index):
        source_index = self.proxy_model.mapToSource(index)
        source_path = self.fs_model.filePath(source_index)
        
        if not os.path.exists(source_path):
            return

        base_dir = os.path.dirname(source_path)
        name = os.path.basename(source_path)
        base_name, ext = os.path.splitext(name)
        
        # Eindeutigen Namen finden
        counter = 1
        while True:
            suffix = f"_copy{counter}" if counter > 1 else "_copy"
            new_name = f"{base_name}{suffix}{ext}"
            new_path = os.path.join(base_dir, new_name)
            
            if not os.path.exists(new_path):
                break
            counter += 1
            
        try:
            if os.path.isdir(source_path):
                shutil.copytree(source_path, new_path)
            else:
                shutil.copy2(source_path, new_path)
        except OSError as e:
            QMessageBox.critical(self, _("Error"), _("Could not clone item: {e}").format(e=e))

    def move_item(self, index):
        source_index = self.proxy_model.mapToSource(index)
        source_path = self.fs_model.filePath(source_index)
        source_name = self.fs_model.fileName(source_index)
        parent_dir = os.path.dirname(source_path)

        # Dialog zur Auswahl des Zielordners öffnen
        dest_dir = QFileDialog.getExistingDirectory(
            self,
            _("Move '{name}' to...").format(name=source_name),
            parent_dir  # Startet im aktuellen Verzeichnis
        )

        if dest_dir and os.path.normpath(dest_dir) != os.path.normpath(parent_dir):
            dest_path = os.path.join(dest_dir, source_name)

            if os.path.exists(dest_path):
                QMessageBox.warning(self, _("Error"), _("A file or folder with the name '{name}' already exists in the destination.").format(name=source_name))
                return

            try:
                shutil.move(source_path, dest_path)
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Could not move item: {e}").format(e=e))

    def delete_item(self, index):
        source_index = self.proxy_model.mapToSource(index)
        path = self.fs_model.filePath(source_index)
        name = self.fs_model.fileName(source_index)
        
        confirm = QMessageBox.question(self, _("Delete"), _("Do you really want to delete '{name}'?").format(name=name), 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                if self.fs_model.isDir(source_index):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except OSError as e:
                QMessageBox.critical(self, _("Error"), _("Could not delete: {e}").format(e=e))
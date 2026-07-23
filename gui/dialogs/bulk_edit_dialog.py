import os
import shutil
import datetime
import frontmatter
from collections import defaultdict

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, 
                             QComboBox, QLineEdit, QMessageBox, QGroupBox, 
                             QTextEdit, QSplitter, QWidget, QFormLayout, 
                             QProgressDialog, QTreeWidgetItemIterator, QApplication)
from PyQt6.QtCore import Qt, QTimer, QByteArray
from PyQt6.QtGui import QColor
from core.config_manager import ConfigManager
from core.i18n import _

class BulkEditDialog(QDialog):
    def __init__(self, project_root, content_dir):
        super().__init__()
        self.project_root = project_root
        self.content_dir = content_dir
        self.setWindowTitle(_("Bulk Frontmatter Editor"))
        
        self.init_ui()
        # Dateien erst laden, nachdem der Dialog angezeigt wurde, damit das UI nicht blockiert
        QTimer.singleShot(100, self.load_files)
        self.restore_layout()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Splitter für linke (Dateibaum) und rechte (Aktionen) Seite
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Linke Seite: Dateibaum ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_files = QLabel(_("Select files to edit:"))
        lbl_files.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(lbl_files)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(_("Content Folder"))
        self.tree.itemChanged.connect(self.update_selection_count)
        left_layout.addWidget(self.tree)
        
        self.lbl_selection_count = QLabel(_("0 files selected"))
        self.lbl_selection_count.setStyleSheet("font-weight: bold;")    
        left_layout.addWidget(self.lbl_selection_count)
        
        self.splitter.addWidget(left_widget)

        # --- Rechte Seite: Aktionen & Log ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Aktions-Box
        action_group = QGroupBox(_("Configure Action"))
        action_layout = QFormLayout()

        self.combo_action = QComboBox()
        self.combo_action.addItems([
            _("Set Attribute"),
            _("Add Tag to List"),
            _("Remove Tag from List"),
            _("Rename Attribute Key"),
            _("Delete Attribute Key"),
            _("Find & Replace (in value)")
        ])
        self.combo_action.currentIndexChanged.connect(self.update_input_fields)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText(_("e.g., author, date, tags"))
        
        self.input_value1 = QLineEdit()
        self.input_value2 = QLineEdit() # Für Suchen & Ersetzen oder Umbenennen
        
        self.lbl_key = QLabel(_("Attribute Name (Key):"))
        self.lbl_val1 = QLabel(_("Value:"))
        self.lbl_val2 = QLabel(_("Replace with:"))

        action_layout.addRow(_("Action:"), self.combo_action)
        action_layout.addRow(self.lbl_key, self.input_key)
        action_layout.addRow(self.lbl_val1, self.input_value1)
        action_layout.addRow(self.lbl_val2, self.input_value2)

        action_group.setLayout(action_layout)
        right_layout.addWidget(action_group)

        self.btn_show_tags = QPushButton(_("Show Used Tags in Selected Files"))
        self.btn_show_tags.clicked.connect(self.show_used_tags)
        right_layout.addWidget(self.btn_show_tags)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton(_("Preview (Dry Run)"))
        self.btn_preview.clicked.connect(self.run_preview)
        
        self.btn_apply = QPushButton(_("Apply Changes"))
        self.btn_apply.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.btn_apply.clicked.connect(self.run_apply)
        
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_apply)
        right_layout.addLayout(btn_layout)

        # Log Ausgabe
        lbl_log = QLabel(_("Log / Preview:"))
        lbl_log.setStyleSheet("font-weight: bold; margin-top: 10px;")
        right_layout.addWidget(lbl_log)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: Monospace;")
        right_layout.addWidget(self.log_area)

        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(1, 2) # Rechte Seite breiter machen

        main_layout.addWidget(self.splitter)
        
        # Close Button unten
        btn_close = QPushButton(_("Close"))
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        self.update_input_fields() # Initialen Status setzen

    def update_input_fields(self):
        """Passt die Eingabefelder basierend auf der gewählten Aktion an."""
        action_idx = self.combo_action.currentIndex()
        
        # Reset visibility
        self.input_value1.setVisible(True)
        self.input_value2.setVisible(False)
        self.lbl_val1.setVisible(True)
        self.lbl_val2.setVisible(False)
        self.input_key.setEnabled(True)
        self.lbl_key.setText(_("Attribute Name (Key):"))

        if action_idx == 0: # Set Attribute
            self.lbl_val1.setText(_("New Value:"))
            self.input_value1.setPlaceholderText(_("The value to set"))
        
        elif action_idx == 1: # Add Tag
            self.input_key.setText("tags")
            self.lbl_val1.setText(_("Tag Name:"))
            self.input_value1.setPlaceholderText(_("e.g., new, draft"))

        elif action_idx == 2: # Remove Tag
            self.input_key.setText("tags")
            self.lbl_val1.setText(_("Tag Name:"))
            self.input_value1.setPlaceholderText(_("The tag to remove"))

        elif action_idx == 3: # Rename Key
            self.lbl_val1.setText(_("New Name (Key):"))
            self.input_value1.setPlaceholderText(_("How the attribute should be named"))    
            self.lbl_key.setText(_("Old Name (Key):"))

        elif action_idx == 4: # Delete Key
            self.input_value1.setVisible(False)
            self.lbl_val1.setVisible(False)

        elif action_idx == 5: # Find & Replace
            self.lbl_val1.setText(_("Search for:"))
            self.input_value1.setPlaceholderText(_("Text to replace"))
            self.lbl_val2.setVisible(True)
            self.input_value2.setVisible(True)
            self.lbl_val2.setText(_("Replace with:"))
            self.input_value2.setPlaceholderText(_("New Text"))

    def load_files(self):
        """Lädt rekursiv alle Markdown-Dateien in den Baum."""
        self.tree.clear()

        progress = QProgressDialog(_("Searching for files..."), _("Cancel"), 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        # Map für Ordner-Items: Pfad -> QTreeWidgetItem
        dir_items = {}

        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, os.path.basename(os.path.normpath(self.content_dir)))
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.content_dir)
        root_item.setFlags(root_item.flags() | Qt.ItemFlag.ItemIsAutoTristate | Qt.ItemFlag.ItemIsUserCheckable)
        root_item.setCheckState(0, Qt.CheckState.Checked)
        root_item.setExpanded(True)
        
        dir_items[self.content_dir] = root_item

        count = 0
        for root, dirs, files in os.walk(self.content_dir):
            if progress.wasCanceled():
                break

            # Eltern-Item finden
            parent_item = dir_items.get(root, root_item)

            # Unterordner erstellen (für Struktur)
            dirs.sort()
            for d in dirs:
                dir_path = os.path.join(root, d)
                dir_item = QTreeWidgetItem(parent_item)
                dir_item.setText(0, d)
                dir_item.setData(0, Qt.ItemDataRole.UserRole, dir_path)
                dir_item.setFlags(dir_item.flags() | Qt.ItemFlag.ItemIsAutoTristate | Qt.ItemFlag.ItemIsUserCheckable)
                dir_item.setCheckState(0, Qt.CheckState.Checked)
                dir_item.setExpanded(False)
                dir_items[dir_path] = dir_item

            # Dateien erstellen
            files.sort()
            for file in files:
                if file.endswith((".md", ".markdown")):
                    full_path = os.path.join(root, file)
                    item = QTreeWidgetItem(parent_item)
                    item.setText(0, file)
                    item.setData(0, Qt.ItemDataRole.UserRole, full_path)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.CheckState.Checked)
                    
                    count += 1
                    if count % 20 == 0:
                        progress.setLabelText(_("Loading files... ({count} found)").format(count=count))
                        QApplication.processEvents()

        progress.close()
        self.update_selection_count()

    def update_selection_count(self):
        count = len(self.get_checked_files())
        self.lbl_selection_count.setText(_("{count} files selected").format(count=count))

    def get_checked_files(self):
        """Gibt eine Liste der vollständigen Pfade der ausgewählten Dateien zurück."""
        checked_files = []
        iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.IteratorFlag.Checked)
        while iterator.value():
            item = iterator.value()
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path and os.path.isfile(path):
                checked_files.append(path)
            iterator += 1
        return checked_files

    def log(self, message, color="black"):
        self.log_area.setTextColor(QColor(color))
        self.log_area.append(message)

    def process_file(self, file_path, action_idx, key, val1, val2, dry_run=True):
        """Führt die Logik auf einer einzelnen Datei aus."""
        try:
            post = frontmatter.load(file_path)
            changed = False
            old_val = None
            new_val_log = None
            
            key = key.strip()

            if action_idx == 0: # Set Attribute
                old_val = post.get(key, _("<not set>"))
                val1 = val1.strip()
                
                # Spezialbehandlung für Tags: String zu Liste konvertieren
                if key == "tags":
                    new_val = [t.strip() for t in val1.split(',') if t.strip()]
                else:
                    new_val = val1

                post[key] = new_val
                if str(old_val) != str(new_val):
                    changed = True
                    new_val_log = str(new_val)

            elif action_idx == 1: # Add Tag
                val1 = val1.strip()
                tags = post.get(key, [])
                if tags is None:
                    tags = []

                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',') if t.strip()]
                if not isinstance(tags, list):
                    tags = []
                
                if val1 and val1 not in tags:
                    tags.append(val1)
                    post[key] = tags
                    changed = True
                    new_val_log = _("Tag '{val1}' added").format(val1=val1)

            elif action_idx == 2: # Remove Tag
                val1 = val1.strip()
                tags = post.get(key, [])
                if tags is None:
                    tags = []

                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',') if t.strip()]
                
                if isinstance(tags, list) and val1 and val1 in tags:
                    tags.remove(val1)
                    post[key] = tags
                    changed = True
                    new_val_log = _("Tag '{val1}' removed").format(val1=val1)

            elif action_idx == 3: # Rename Key
                if key in post:
                    post[val1] = post.pop(key)
                    changed = True
                    new_val_log = _("Renamed to {val1}").format(val1=val1)

            elif action_idx == 4: # Delete Key
                if key in post:
                    del post[key]
                    changed = True
                    new_val_log = _("Deleted")

            elif action_idx == 5: # Find & Replace
                if key in post and isinstance(post[key], str):
                    if val1 in post[key]:
                        post[key] = post[key].replace(val1, val2)
                        changed = True
                        new_val_log = _("Replaced: '{val1}' -> '{val2}'").format(val1=val1, val2=val2)

            if changed:
                rel_path = os.path.relpath(file_path, self.content_dir)
                if dry_run:
                    self.log(_("[PREVIEW] {path}: {key} -> {log}").format(path=rel_path, key=key, log=new_val_log), "blue")
                else:
                    # Speichern
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(frontmatter.dumps(post))
                    self.log(_("[OK] {path} updated.").format(path=rel_path), "green")
                return True
            return False

        except Exception as e:
            self.log(f"[FEHLER] {os.path.basename(file_path)}: {e}", "red")
            return False

    def run_preview(self):
        self.log_area.clear()
        self.log(_("Start preview..."), "black")
        files = self.get_checked_files()
        action_idx = self.combo_action.currentIndex()
        key = self.input_key.text()
        val1 = self.input_value1.text()
        val2 = self.input_value2.text()

        if not key:
            QMessageBox.warning(self, _("Error"), _("Please provide an attribute name (key)."))
            return

        changes_count = 0
        for f in files:
            if self.process_file(f, action_idx, key, val1, val2, dry_run=True):
                changes_count += 1
        
        if changes_count == 0:
            self.log(_("No changes required."), "gray")
        else:
            self.log(_("\n{count} files would be changed.").format(count=changes_count), "blue")

    def create_backup(self, files):
        """Erstellt ein Backup der betroffenen Dateien."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder = os.path.join(self.project_root, "backup", f"bulk_edit_{timestamp}")
        
        try:
            os.makedirs(backup_folder, exist_ok=True)
            self.log(_("Creating backup in: {path}").format(path=backup_folder), "black")
            
            for file_path in files:
                rel_path = os.path.relpath(file_path, self.content_dir)
                dest_path = os.path.join(backup_folder, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
            
        except Exception as e:
            self.log(_("Backup failed: {error}").format(error=e), "red")
            return False

    def run_apply(self):
        files = self.get_checked_files()
        if not files:
            return

        # Bestätigung
        reply = QMessageBox.question(self, _("Apply"), 
                                     _("Do you really want to edit {count} files?\nA backup will be created automatically.").format(count=len(files)),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        self.log_area.clear()
        self.log(_("Start bulk edit..."), "black")

        # 1. Backup erstellen
        if not self.create_backup(files):
            QMessageBox.critical(self, _("Error"), _("Backup could not be created. Aborting."))
            return

        # 2. Änderungen anwenden
        action_idx = self.combo_action.currentIndex()
        key = self.input_key.text()
        val1 = self.input_value1.text()
        val2 = self.input_value2.text()

        count = 0
        for f in files:
            if self.process_file(f, action_idx, key, val1, val2, dry_run=False):
                count += 1
        
        self.log(_("\nDone! {count} files were successfully edited.").format(count=count), "green")
        QMessageBox.information(self, _("Done"), _("Process completed."))

    def show_used_tags(self):
        files = self.get_checked_files()
        if not files:
            QMessageBox.information(self, _("Info"), _("No files selected."))
            return

        tag_files = defaultdict(list)
        
        progress = QProgressDialog(_("Analyzing tags..."), _("Cancel"), 0, len(files), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        for i, file_path in enumerate(files):
            if progress.wasCanceled():
                break
            progress.setValue(i)
            
            try:
                post = frontmatter.load(file_path)
                tags = post.get('tags', [])
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(',')]
                if isinstance(tags, list):
                    for tag in tags:
                        if tag:
                            rel_path = os.path.relpath(file_path, self.content_dir)
                            tag_files[str(tag)].append(rel_path)
            except Exception:
                pass
        
        progress.setValue(len(files))
        
        if not tag_files:
            QMessageBox.information(self, _("Info"), _("No tags found in selected files."))
            return

        msg = _("Found in {count} files:\n\n").format(count=len(files))
        # Sortiert nach Häufigkeit (absteigend), dann alphabetisch
        sorted_tags = sorted(tag_files.items(), key=lambda item: (-len(item[1]), item[0]))
        
        for tag, file_list in sorted_tags:
            msg += _("=== {tag} ({count}) ===\n").format(tag=tag, count=len(file_list))
            for f in sorted(file_list):
                msg += f"  - {f}\n"
            msg += "\n"
            
        self.show_scrollable_info(_("Used Tags & Files"), msg)

    def show_scrollable_info(self, title, content):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(400, 500)
        layout = QVBoxLayout(dlg)
        text_edit = QTextEdit()
        text_edit.setPlainText(content)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        btn = QPushButton(_("Close"))
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()

    def restore_layout(self):
        """Lädt Geometrie und Splitter-Zustand aus der zentralen app_config.yaml."""
        try:
            cm = ConfigManager(ConfigManager.get_app_config_path())
            state = cm.apply_ui_state(self, "bulk_edit", default_size=(1100, 700))
            if state:
                self.splitter.restoreState(state)
        except Exception:
            self.resize(1100, 700)

    def save_layout(self):
        """Speichert die aktuelle Geometrie und den Splitter-Zustand in der app_config.yaml."""
        cm = ConfigManager(ConfigManager.get_app_config_path())
        cm.save_ui_state("bulk_edit", self.saveGeometry(), self.splitter.saveState())

    def done(self, result):
        self.save_layout()
        super().done(result)

    def closeEvent(self, event):
        self.save_layout()
        super().closeEvent(event)
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
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

class BulkEditDialog(QDialog):
    def __init__(self, project_root, content_dir):
        super().__init__()
        self.project_root = project_root
        self.content_dir = content_dir
        self.setWindowTitle("Massen-Frontmatter-Editor")
        self.resize(1100, 700)
        
        self.init_ui()
        # Dateien erst laden, nachdem der Dialog angezeigt wurde, damit das UI nicht blockiert
        QTimer.singleShot(100, self.load_files)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Splitter für linke (Dateibaum) und rechte (Aktionen) Seite
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Linke Seite: Dateibaum ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_files = QLabel("Dateien auswählen:")
        lbl_files.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(lbl_files)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Content Ordner")
        self.tree.itemChanged.connect(self.update_selection_count)
        left_layout.addWidget(self.tree)
        
        self.lbl_selection_count = QLabel("0 Dateien ausgewählt")
        left_layout.addWidget(self.lbl_selection_count)
        
        splitter.addWidget(left_widget)

        # --- Rechte Seite: Aktionen & Log ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Aktions-Box
        action_group = QGroupBox("Aktion konfigurieren")
        action_layout = QFormLayout()

        self.combo_action = QComboBox()
        self.combo_action.addItems([
            "Attribut setzen (Set)",
            "Tag hinzufügen (Add to List)",
            "Tag entfernen (Remove from List)",
            "Attribut umbenennen (Rename Key)",
            "Attribut löschen (Delete Key)",
            "Suchen & Ersetzen (im Wert)"
        ])
        self.combo_action.currentIndexChanged.connect(self.update_input_fields)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("z.B. author, date, tags")
        
        self.input_value1 = QLineEdit()
        self.input_value2 = QLineEdit() # Für Suchen & Ersetzen oder Umbenennen
        
        self.lbl_key = QLabel("Attribut Name (Key):")
        self.lbl_val1 = QLabel("Wert:")
        self.lbl_val2 = QLabel("Ersetzen durch:")

        action_layout.addRow("Aktion:", self.combo_action)
        action_layout.addRow(self.lbl_key, self.input_key)
        action_layout.addRow(self.lbl_val1, self.input_value1)
        action_layout.addRow(self.lbl_val2, self.input_value2)

        action_group.setLayout(action_layout)
        right_layout.addWidget(action_group)

        self.btn_show_tags = QPushButton("Verwendete Tags anzeigen")
        self.btn_show_tags.clicked.connect(self.show_used_tags)
        right_layout.addWidget(self.btn_show_tags)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton("Vorschau (Dry Run)")
        self.btn_preview.clicked.connect(self.run_preview)
        
        self.btn_apply = QPushButton("Änderungen anwenden")
        self.btn_apply.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.btn_apply.clicked.connect(self.run_apply)
        
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_apply)
        right_layout.addLayout(btn_layout)

        # Log Ausgabe
        lbl_log = QLabel("Protokoll / Vorschau:")
        lbl_log.setStyleSheet("font-weight: bold; margin-top: 10px;")
        right_layout.addWidget(lbl_log)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: Monospace;")
        right_layout.addWidget(self.log_area)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 2) # Rechte Seite breiter machen

        main_layout.addWidget(splitter)
        
        # Close Button unten
        btn_close = QPushButton("Schließen")
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

        self.update_input_fields() # Initialen Status setzen

    def update_input_fields(self):
        """Passt die Eingabefelder basierend auf der gewählten Aktion an."""
        action = self.combo_action.currentText()
        
        # Reset visibility
        self.input_value1.setVisible(True)
        self.input_value2.setVisible(False)
        self.lbl_val1.setVisible(True)
        self.lbl_val2.setVisible(False)
        self.input_key.setEnabled(True)

        if "Attribut setzen" in action:
            self.lbl_val1.setText("Neuer Wert:")
            self.input_value1.setPlaceholderText("Der zu setzende Wert")
        
        elif "Tag hinzufügen" in action:
            self.input_key.setText("tags")
            self.lbl_val1.setText("Tag Name:")
            self.input_value1.setPlaceholderText("z.B. neu, draft")
            
        elif "Tag entfernen" in action:
            self.input_key.setText("tags")
            self.lbl_val1.setText("Tag Name:")
            self.input_value1.setPlaceholderText("Der zu entfernende Tag")

        elif "Attribut umbenennen" in action:
            self.lbl_val1.setText("Neuer Name (Key):")
            self.input_value1.setPlaceholderText("Wie das Attribut heißen soll")
            self.lbl_key.setText("Alter Name (Key):")

        elif "Attribut löschen" in action:
            self.input_value1.setVisible(False)
            self.lbl_val1.setVisible(False)

        elif "Suchen & Ersetzen" in action:
            self.lbl_val1.setText("Suchen nach:")
            self.input_value1.setPlaceholderText("Text, der ersetzt werden soll")
            self.lbl_val2.setVisible(True)
            self.input_value2.setVisible(True)
            self.lbl_val2.setText("Ersetzen durch:")
            self.input_value2.setPlaceholderText("Neuer Text")

    def load_files(self):
        """Lädt rekursiv alle Markdown-Dateien in den Baum."""
        self.tree.clear()

        progress = QProgressDialog("Suche Dateien...", "Abbrechen", 0, 0, self)
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
                        progress.setLabelText(f"Lade Dateien... ({count} gefunden)")
                        QApplication.processEvents()

        progress.close()
        self.update_selection_count()

    def update_selection_count(self):
        count = len(self.get_checked_files())
        self.lbl_selection_count.setText(f"{count} Dateien ausgewählt")

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

    def process_file(self, file_path, action, key, val1, val2, dry_run=True):
        """Führt die Logik auf einer einzelnen Datei aus."""
        try:
            post = frontmatter.load(file_path)
            changed = False
            old_val = None
            new_val_log = None
            
            key = key.strip()

            if "Attribut setzen" in action:
                old_val = post.get(key, "<nicht gesetzt>")
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

            elif "Tag hinzufügen" in action:
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
                    new_val_log = f"Tag '{val1}' hinzugefügt"

            elif "Tag entfernen" in action:
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
                    new_val_log = f"Tag '{val1}' entfernt"

            elif "Attribut umbenennen" in action:
                if key in post:
                    post[val1] = post.pop(key)
                    changed = True
                    new_val_log = f"Umbenannt zu {val1}"

            elif "Attribut löschen" in action:
                if key in post:
                    del post[key]
                    changed = True
                    new_val_log = "Gelöscht"

            elif "Suchen & Ersetzen" in action:
                if key in post and isinstance(post[key], str):
                    if val1 in post[key]:
                        post[key] = post[key].replace(val1, val2)
                        changed = True
                        new_val_log = f"Ersetzt: '{val1}' -> '{val2}'"

            if changed:
                rel_path = os.path.relpath(file_path, self.content_dir)
                if dry_run:
                    self.log(f"[VORSCHAU] {rel_path}: {key} -> {new_val_log}", "blue")
                else:
                    # Speichern
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(frontmatter.dumps(post))
                    self.log(f"[OK] {rel_path} aktualisiert.", "green")
                return True
            return False

        except Exception as e:
            self.log(f"[FEHLER] {os.path.basename(file_path)}: {e}", "red")
            return False

    def run_preview(self):
        self.log_area.clear()
        self.log("Starte Vorschau...", "black")
        files = self.get_checked_files()
        action = self.combo_action.currentText()
        key = self.input_key.text()
        val1 = self.input_value1.text()
        val2 = self.input_value2.text()

        if not key:
            QMessageBox.warning(self, "Fehler", "Bitte einen Attribut-Namen (Key) angeben.")
            return

        changes_count = 0
        for f in files:
            if self.process_file(f, action, key, val1, val2, dry_run=True):
                changes_count += 1
        
        if changes_count == 0:
            self.log("Keine Änderungen erforderlich.", "gray")
        else:
            self.log(f"\n{changes_count} Dateien würden geändert werden.", "blue")

    def create_backup(self, files):
        """Erstellt ein Backup der betroffenen Dateien."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder = os.path.join(self.project_root, "backup", f"bulk_edit_{timestamp}")
        
        try:
            os.makedirs(backup_folder, exist_ok=True)
            self.log(f"Erstelle Backup in: {backup_folder}", "black")
            
            for file_path in files:
                rel_path = os.path.relpath(file_path, self.content_dir)
                dest_path = os.path.join(backup_folder, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
            
            return True
        except Exception as e:
            self.log(f"Backup fehlgeschlagen: {e}", "red")
            return False

    def run_apply(self):
        files = self.get_checked_files()
        if not files:
            return

        # Bestätigung
        reply = QMessageBox.question(self, "Anwenden", 
                                     f"Möchtest du {len(files)} Dateien wirklich bearbeiten?\nEin Backup wird automatisch erstellt.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        self.log_area.clear()
        self.log("Starte Massenbearbeitung...", "black")

        # 1. Backup erstellen
        if not self.create_backup(files):
            QMessageBox.critical(self, "Fehler", "Backup konnte nicht erstellt werden. Abbruch.")
            return

        # 2. Änderungen anwenden
        action = self.combo_action.currentText()
        key = self.input_key.text()
        val1 = self.input_value1.text()
        val2 = self.input_value2.text()

        count = 0
        for f in files:
            if self.process_file(f, action, key, val1, val2, dry_run=False):
                count += 1
        
        self.log(f"\nFertig! {count} Dateien wurden erfolgreich bearbeitet.", "green")
        QMessageBox.information(self, "Fertig", "Vorgang abgeschlossen.")

    def show_used_tags(self):
        files = self.get_checked_files()
        if not files:
            QMessageBox.information(self, "Info", "Keine Dateien ausgewählt.")
            return

        tag_files = defaultdict(list)
        
        progress = QProgressDialog("Analysiere Tags...", "Abbrechen", 0, len(files), self)
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
            QMessageBox.information(self, "Tags", "Keine Tags in den ausgewählten Dateien gefunden.")
            return

        msg = f"Gefunden in {len(files)} Dateien:\n\n"
        # Sortiert nach Häufigkeit (absteigend), dann alphabetisch
        sorted_tags = sorted(tag_files.items(), key=lambda item: (-len(item[1]), item[0]))
        
        for tag, file_list in sorted_tags:
            msg += f"=== {tag} ({len(file_list)}) ===\n"
            for f in sorted(file_list):
                msg += f"  - {f}\n"
            msg += "\n"
            
        self.show_scrollable_info("Verwendete Tags & Dateien", msg)

    def show_scrollable_info(self, title, content):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(400, 500)
        layout = QVBoxLayout(dlg)
        text_edit = QTextEdit()
        text_edit.setPlainText(content)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        btn = QPushButton("Schließen")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()
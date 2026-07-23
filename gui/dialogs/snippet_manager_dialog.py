import os
import json
import yaml
import re
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QDialogButtonBox, QMessageBox, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from gui.dialogs.snippet_editor_dialog import SnippetEditorDialog
from core.i18n import _



class SnippetManagerTree(QTreeWidget):
    itemDropped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.itemDropped.emit()

class SnippetManagerDialog(QDialog):
    def __init__(self, snippets_dir="snippets", parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Manage Snippets"))
        self.resize(600, 400)
        self.snippets_dir = snippets_dir

        self.snippets = []
        self.load_snippets()

        layout = QVBoxLayout(self)
        
        main_hbox = QHBoxLayout()
        
        self.tree_widget = SnippetManagerTree()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(20)
        self.tree_widget.setAnimated(True)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.itemDoubleClicked.connect(self.edit_snippet)
        self.tree_widget.itemDropped.connect(self.update_snippets_from_tree)
        main_hbox.addWidget(self.tree_widget)
        
        btn_vbox = QVBoxLayout()
        
        add_btn = QPushButton(_("Add..."))
        add_btn.clicked.connect(self.add_snippet)
        btn_vbox.addWidget(add_btn)
        
        edit_btn = QPushButton(_("Edit..."))
        edit_btn.clicked.connect(self.edit_snippet)
        btn_vbox.addWidget(edit_btn)
        
        delete_btn = QPushButton(_("Delete"))
        delete_btn.clicked.connect(self.delete_snippet)
        btn_vbox.addWidget(delete_btn)
        
        btn_vbox.addStretch()
        
        main_hbox.addLayout(btn_vbox)
        layout.addLayout(main_hbox)

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        dialog_buttons.accepted.connect(self.save_and_accept)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

        self.populate_list()

    def load_snippets(self):
        self.snippets = []
        if not os.path.exists(self.snippets_dir):
            os.makedirs(self.snippets_dir)
        else:
            # Lade alle YAML Dateien aus dem Ordner
            for filename in os.listdir(self.snippets_dir):
                if filename.endswith(('.yaml', '.yml')):
                    try:
                        with open(os.path.join(self.snippets_dir, filename), 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)
                            if data:
                                self.snippets.append(data)
                    except Exception as e:
                        print(f"Fehler beim Laden von {filename}: {e}")
            
            # Sortiere nach 'order' Feld, falls vorhanden, sonst ans Ende
            self.snippets.sort(key=lambda x: x.get('order', 999))

    def save_snippets(self):
        if not os.path.exists(self.snippets_dir):
            os.makedirs(self.snippets_dir)
            
        existing_files = set(f for f in os.listdir(self.snippets_dir) if f.endswith(('.yaml', '.yml')))
        saved_files = set()

        for i, snippet in enumerate(self.snippets):
            snippet['order'] = i # Speichere die Reihenfolge
            # Dateinamen aus dem Snippet-Namen generieren (Slugify)
            safe_name = re.sub(r'[^\w\s-]', '', snippet['name'].lower()).strip()
            safe_name = re.sub(r'[-\s]+', '-', safe_name) or "snippet"
            filename = f"{safe_name}.yaml"
            saved_files.add(filename)
            
            try:
                with open(os.path.join(self.snippets_dir, filename), 'w', encoding='utf-8') as f:
                    yaml.dump(snippet, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            except IOError as e:
                QMessageBox.critical(self, _("Error"), _("Could not save {filename}: {e}").format(filename=filename, e=e))

        # Lösche Dateien, die nicht mehr in der Liste sind (wurden gelöscht oder umbenannt)
        for f in existing_files - saved_files:
            try:
                os.remove(os.path.join(self.snippets_dir, f))
            except OSError:
                pass

    def populate_list(self):
        self.tree_widget.clear()
        
        # Gruppieren nach Kategorie
        categories = {}
        for snippet in self.snippets:
            cat = snippet.get('category', _('General'))
            if isinstance(cat, list):
                cat_key = ", ".join(cat)
            else:
                cat_key = cat
            
            if cat_key not in categories:
                categories[cat_key] = []
            categories[cat_key].append(snippet)
            
        for cat_name in sorted(categories.keys()):
            # Kategorie übersetzen
            cat_item = QTreeWidgetItem([_(cat_name)])
            # Kategorie fett darstellen
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)
            
            self.tree_widget.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)
            
            for snippet in categories[cat_name]:
                item = QTreeWidgetItem([snippet['name']])
                item.setData(0, Qt.ItemDataRole.UserRole, snippet)
                cat_item.addChild(item)

    def update_snippets_from_tree(self):
        """
        Rekonstruiert die Snippet-Liste basierend auf der aktuellen Baumstruktur.
        Wird nach Drag & Drop aufgerufen.
        """
        new_snippets = []
        root = self.tree_widget.invisibleRootItem()
        
        # Hilfsfunktion zum rekursiven Sammeln (falls Snippets in Snippets verschachtelt wurden)
        def collect_snippets(item, current_category):
            for i in range(item.childCount()):
                child = item.child(i)
                data = child.data(0, Qt.ItemDataRole.UserRole)
                
                if data: # Es ist ein Snippet
                    data['category'] = current_category
                    new_snippets.append(data)
                    # Auch Kinder dieses Snippets prüfen (Flattening)
                    collect_snippets(child, current_category)
                else: # Es ist eine Kategorie (sollte hier eigentlich nicht passieren)
                    collect_snippets(child, child.text(0))

        for i in range(root.childCount()):
            top_item = root.child(i)
            data = top_item.data(0, Qt.ItemDataRole.UserRole)
            
            if data: # Ein Snippet auf oberster Ebene -> Kategorie "Allgemein"
                data['category'] = _("General")
                new_snippets.append(data)
                collect_snippets(top_item, _("General"))
            else: # Eine Kategorie
                cat_name = top_item.text(0)
                collect_snippets(top_item, cat_name)
        
        self.snippets = new_snippets
        self.populate_list() # Baum neu aufbauen, um Struktur zu säubern

    def add_snippet(self):
        dialog = SnippetEditorDialog(self)
        if dialog.exec():
            new_data = dialog.get_data()
            self.snippets.append(new_data)
            self.populate_list()

    def edit_snippet(self):
        current_item = self.tree_widget.currentItem()
        if not current_item: return
        
        snippet_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not snippet_data: # Kategorie-Item
            return

        dialog = SnippetEditorDialog(self, name=snippet_data['name'], code=snippet_data['code'], category=snippet_data.get('category', _('General')))
        if dialog.exec():
            updated_data = dialog.get_data()
            # Aktualisiere das Snippet in der Liste
            try:
                idx = self.snippets.index(snippet_data)
                self.snippets[idx] = updated_data
                self.populate_list()
            except ValueError:
                pass

    def delete_snippet(self):
        current_item = self.tree_widget.currentItem()
        if not current_item: return
        
        snippet_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not snippet_data: # Kategorie-Item
            return

        confirm = QMessageBox.question(self, _("Delete"), _("Are you sure you want to delete the snippet '{snippet_name}'?").format(snippet_name=snippet_data['name']))
        if confirm == QMessageBox.StandardButton.Yes:
            self.snippets.remove(snippet_data)
            self.populate_list()

    def save_and_accept(self):
        self.save_snippets()
        self.accept()
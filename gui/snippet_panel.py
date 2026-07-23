import os
import json
import yaml
import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTreeWidget, QTreeWidgetItem, QFrame, QAbstractItemView, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from core.i18n import _

'''
SnippetPanel: A collapsible panel for managing and inserting code snippets.
- Snippets are stored as YAML files in the 'snippets' directory.
- Each snippet YAML file should have the following structure:
name: "Snippet Name"
category: "Category Name"  # Optional, can be a string or a list of strings
code: |
    # The actual code snippet, can be multiple lines
order: 1  # Optional, for sorting snippets within a category
- The panel allows filtering snippets by category and supports drag-and-drop insertion of the code into the editor.
- The 'insert_requested' signal is emitted when a snippet is double-clicked, sending the code to be inserted.
- The panel can be toggled between expanded and collapsed states, and it adapts its size accordingly.
- The 'set_dark_mode(enabled)' method can be called to apply dark mode styling to the panel-specific widgets.
'''     

class SnippetTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

    def mimeData(self, items):
        # Erstelle MimeData mit dem Code des Snippets als Text
        mime = QMimeData()
        if items:
            item = items[0]
            code = item.data(0, Qt.ItemDataRole.UserRole)
            if code:
                mime.setText(code)
        return mime

class SnippetPanel(QWidget):
    insert_requested = pyqtSignal(str)

    def __init__(self, snippets_dir="snippets"):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle Button
        self.toggle_btn = QPushButton(_("Snippets ▼"))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
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

        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filter
        self.category_filter = QComboBox()
        self.category_filter.addItem(_("All Categories"), "ALL")
        self.category_filter.currentTextChanged.connect(self.update_tree)
        content_layout.addWidget(self.category_filter)

        # Tree
        self.tree = SnippetTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setAnimated(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setFrameShape(QFrame.Shape.NoFrame)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        content_layout.addWidget(self.tree)

        layout.addWidget(self.content_widget)

        self.snippets_dir = snippets_dir
        self.snippets = []
        self.refresh_snippets()

    def set_dark_mode(self, enabled):
        """Wendet das Dark-Mode-Styling auf die Panel-spezifischen Widgets an."""
        # Toggle Button aktualisieren (da er ein Stylesheet mit palette() hat)
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)

    def toggle_content(self, checked):
        self.content_widget.setVisible(checked)
        self.toggle_btn.setText(_("Snippets ▼") if checked else _("Snippets ▶"))
        
        if checked:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.setMaximumHeight(16777215)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.setMaximumHeight(self.toggle_btn.sizeHint().height())

    def refresh_snippets(self):
        self.snippets = self.load_snippets()
        
        # Kategorien aktualisieren
        current_cat_data = self.category_filter.currentData()
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem(_("All Categories"), "ALL")
        
        all_cats = set()
        for s in self.snippets:
            cat = s.get('category', 'Allgemein')
            if isinstance(cat, list):
                all_cats.update(cat)
            else:
                all_cats.add(cat)
        
        categories = sorted(list(all_cats))
        for cat in categories:
            # Zeige übersetzten Namen an, speichere Original als Daten
            self.category_filter.addItem(_(cat), cat)
        
        # Versuche Auswahl wiederherzustellen
        index = self.category_filter.findData(current_cat_data)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
        self.category_filter.blockSignals(False)
        
        self.update_tree()

    def update_tree(self):
        self.tree.clear()
        selected_category_key = self.category_filter.currentData()
        
        # Gruppieren nach Kategorie
        categories = {}
        for snippet in self.snippets:
            cats = snippet.get('category', 'Allgemein')
            if isinstance(cats, str):
                cats = [cats]
            
            for cat in cats:
                if selected_category_key != "ALL" and cat != selected_category_key:
                    continue

                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(snippet)
            
        for cat_name in sorted(categories.keys()):
            # Kategorie-Name übersetzen für die Anzeige im Baum
            cat_item = QTreeWidgetItem([_(cat_name)])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.tree.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)
            
            for snippet in categories[cat_name]:
                item = QTreeWidgetItem([snippet['name']])
                item.setData(0, Qt.ItemDataRole.UserRole, snippet['code'])
                item.setToolTip(0, snippet['code'])
                cat_item.addChild(item)

    def load_snippets(self):
        snippets = []
        if not os.path.exists(self.snippets_dir):
            os.makedirs(self.snippets_dir)
        else:
            for filename in os.listdir(self.snippets_dir):
                if filename.endswith(('.yaml', '.yml')):
                    try:
                        with open(os.path.join(self.snippets_dir, filename), 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)
                            if data: snippets.append(data)
                    except: pass
            snippets.sort(key=lambda x: x.get('order', 999))
            return snippets

    def _on_item_double_clicked(self, item, column):
        code = item.data(0, Qt.ItemDataRole.UserRole)
        if code:
            self.insert_requested.emit(code)
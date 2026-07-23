from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QFrame, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from core.i18n import _

'''
OutlinePanel: A panel for displaying a hierarchical outline of the document.
- Uses a QTreeWidget to show the structure.
- Allows users to click on headings to navigate to them in the editor.
- The 'update_outline(text)' method takes the full text of the document, parses it for Markdown headings, and updates the tree structure accordingly.
- The 'heading_clicked' signal is emitted with the line number of the clicked heading, which can be used to navigate the editor to that position.
- The panel can be toggled between expanded and collapsed states, and it adapts its size accordingly.
- The 'set_dark_mode(enabled)' method can be called to apply dark mode styling to the panel-specific widgets.
'''

class OutlinePanel(QWidget):
    heading_clicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle Button
        self.toggle_btn = QPushButton(_("Outline ▼"))
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

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setAnimated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        # Styling für bessere Lesbarkeit
        self.tree.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self.tree)

    def set_dark_mode(self, enabled):
        """Wendet das Dark-Mode-Styling auf die Panel-spezifischen Widgets an."""
        # Toggle Button aktualisieren (da er ein Stylesheet mit palette() hat)
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)

    def toggle_content(self, checked):
        self.tree.setVisible(checked)
        self.toggle_btn.setText(_("Outline ▼") if checked else _("Outline ▶"))
        
        if checked:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.setMaximumHeight(16777215)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.setMaximumHeight(self.toggle_btn.sizeHint().height())

    def update_outline(self, text):
        self.tree.clear()
        
        lines = text.split('\n')
        stack = [] # Speichert Tupel: (level, item)
        
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            # Einfache Erkennung von Markdown-Überschriften
            if stripped.startswith('#'):
                # Zähle die Anzahl der Rauten für das Level
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # Markdown verlangt meist ein Leerzeichen nach den Rauten (z.B. "# Titel")
                # Wir ignorieren Zeilen wie "#Kommentar" oder "#######"
                if level > 6 or (len(stripped) > level and stripped[level] != ' '):
                     continue

                heading_text = stripped[level:].strip()
                
                item = QTreeWidgetItem([heading_text])
                item.setData(0, Qt.ItemDataRole.UserRole, i) # Zeilennummer speichern
                
                # Hierarchie im Baum aufbauen: Finde das richtige Eltern-Element
                while stack and stack[-1][0] >= level:
                    stack.pop()
                
                if stack:
                    stack[-1][1].addChild(item)
                else:
                    self.tree.addTopLevelItem(item)
                
                item.setExpanded(True)
                stack.append((level, item))

    def _on_item_clicked(self, item, column):
        line_number = item.data(0, Qt.ItemDataRole.UserRole)
        if line_number is not None:
            self.heading_clicked.emit(line_number)
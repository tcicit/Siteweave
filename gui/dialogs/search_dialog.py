from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QMessageBox)
from PyQt6.QtGui import QTextDocument

from core.i18n import _

class SearchDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle(_("Search & Replace"))
        self.resize(400, 180)
        
        layout = QVBoxLayout(self)
        
        # Suchfeld
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel(_("Find:")))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Ersetzenfeld
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel(_("Replace with:")))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Optionen
        self.case_sensitive = QCheckBox(_("Case sensitive"))
        layout.addWidget(self.case_sensitive)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.find_next_btn = QPushButton(_("Find"))
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_next_btn.setDefault(True) # Enter drückt diesen Button
        
        self.replace_btn = QPushButton(_("Replace"))
        self.replace_btn.clicked.connect(self.replace)
        
        self.replace_all_btn = QPushButton(_("Replace All"))
        self.replace_all_btn.clicked.connect(self.replace_all)
        
        btn_layout.addWidget(self.find_next_btn)
        btn_layout.addWidget(self.replace_btn)
        btn_layout.addWidget(self.replace_all_btn)
        layout.addLayout(btn_layout)

    def find_next(self):
        text = self.find_input.text()
        if not text:
            return False
            
        options = QTextDocument.FindFlag(0)
        if self.case_sensitive.isChecked():
            options |= QTextDocument.FindFlag.FindCaseSensitively
            
        # Suche vorwärts ab aktueller Cursorposition
        found = self.editor.find(text, options)
        
        if not found:
            # Wrap-Around: Wenn am Ende nichts gefunden, fange von vorne an
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text, options)
            
            if not found:
                QMessageBox.information(self, _("Search"), _("'{text}' not found.").format(text=text))
        
        return found

    def replace(self):
        cursor = self.editor.textCursor()
        search_text = self.find_input.text()
        
        if not search_text:
            return

        # Wenn die aktuelle Selektion nicht dem Suchtext entspricht (oder nichts selektiert ist), erst suchen
        if not cursor.hasSelection() or cursor.selectedText() != search_text:
            if not self.find_next():
                return

        # Ersetzen (Cursor steht jetzt auf dem gefundenen Text)
        self.editor.textCursor().insertText(self.replace_input.text())
        # Sofort zum nächsten Vorkommen springen
        self.find_next()

    def replace_all(self):
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            return
            
        options = QTextDocument.FindFlag(0)
        if self.case_sensitive.isChecked():
            options |= QTextDocument.FindFlag.FindCaseSensitively
            
        # Cursor an den Anfang setzen
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        
        count = 0
        while self.editor.find(search_text, options):
            self.editor.textCursor().insertText(replace_text)
            count += 1
            
        QMessageBox.information(self, _("Replace"), _("{count} occurrences replaced.").format(count=count))
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QMessageBox, QPlainTextEdit)
from PyQt6.QtGui import QFontDatabase

from core.i18n import _

class SnippetEditorDialog(QDialog):
    '''
    Docstring für SnippetEditorDialog
    Dieses Dialogfenster ermöglicht es dem Benutzer, Code-Snippets zu erstellen oder zu bearbeiten.
Funktionen:
- Eingabefelder für den Namen, die Kategorie und den Code des Snippets.
- Validierung, um sicherzustellen, dass der Name nicht leer ist.
- Rückgabe der eingegebenen Daten als Dictionary, das den Namen, den Code und die Kategorie enthält.
- Unterstützung für die Eingabe mehrerer Kategorien, die durch Kommas getrennt werden können.
- Benutzerfreundliche Oberfläche mit klaren Beschriftungen und Fehlermeldungen. 

    ''' 
    def __init__(self, parent=None, name="", code="", category=None):
        super().__init__(parent)
        self.setWindowTitle(_("Edit Snippet"))

        layout = QVBoxLayout(self)
        form = QFormLayout()

        if category is None:
            category = _("General")

        if isinstance(category, list):
            category = ", ".join(category)

        self.name_input = QLineEdit(name)
        self.category_input = QLineEdit(category)
        self.code_input = QPlainTextEdit(code)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.code_input.setFont(font)
        self.code_input.setMinimumHeight(100)

        form.addRow(_("Name:"), self.name_input)
        form.addRow(_("Category:"), self.category_input)
        form.addRow(_("Code:"), self.code_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, _("Error"), _("Please enter a name."))
            return
        self.accept()

    def get_data(self):
        cat_text = self.category_input.text().strip()
        if "," in cat_text:
            category = [c.strip() for c in cat_text.split(",") if c.strip()]
        else:
            category = cat_text or _("General")

        return {
            "name": self.name_input.text().strip(),
            "code": self.code_input.toPlainText(),
            "category": category
        }
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QInputDialog, QMessageBox, QLabel, QDialogButtonBox,
                             QFileDialog)
from core.i18n import _

class DictionaryManagerDialog(QDialog):
    def __init__(self, spell_checker, parent=None):
        super().__init__(parent)
        self.spell_checker = spell_checker
        self.setWindowTitle(_("Manage Custom Dictionary"))
        self.resize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(_("Custom words for this project:")))
        
        self.word_list = QListWidget()
        self.refresh_list()
        layout.addWidget(self.word_list)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton(_("Add Word"))
        add_btn.clicked.connect(self.add_word)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton(_("Remove Word"))
        remove_btn.clicked.connect(self.remove_word)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        
        # Import/Export
        import_export_layout = QHBoxLayout()
        import_btn = QPushButton(_("Import..."))
        import_btn.clicked.connect(self.import_dictionary)
        import_export_layout.addWidget(import_btn)

        export_btn = QPushButton(_("Export..."))
        export_btn.clicked.connect(self.export_dictionary)
        import_export_layout.addWidget(export_btn)
        layout.addLayout(import_export_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def refresh_list(self):
        self.word_list.clear()
        if self.spell_checker:
            words = self.spell_checker.get_user_words()
            self.word_list.addItems(sorted(words))

    def add_word(self):
        if not self.spell_checker: return
        word, ok = QInputDialog.getText(self, _("Add Word"), _("New word:"))
        if ok and word:
            self.spell_checker.add_to_user_dictionary(word.strip())
            self.refresh_list()

    def remove_word(self):
        if not self.spell_checker: return
        item = self.word_list.currentItem()
        if item:
            word = item.text()
            self.spell_checker.remove_from_user_dictionary(word)
            self.refresh_list()
        else:
            QMessageBox.warning(self, _("Warning"), _("Please select a word to remove."))

    def export_dictionary(self):
        if not self.spell_checker: return

        words = self.spell_checker.get_user_words()
        if not words:
            QMessageBox.information(self, _("Info"), _("The dictionary is empty. Nothing to export."))
            return

        file_path, _ = QFileDialog.getSaveFileName(self, _("Export Dictionary"), "", _("Text Files (*.txt);;All Files (*)"))
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for word in sorted(words):
                        f.write(f"{word}\n")
                QMessageBox.information(self, _("Success"), _("Dictionary successfully exported to {path}.").format(path=file_path))
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Could not export dictionary: {e}").format(e=e))

    def import_dictionary(self):
        if not self.spell_checker: return

        file_path, _ = QFileDialog.getOpenFileName(self, _("Import Dictionary"), "", _("Text Files (*.txt);;All Files (*)"))
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_words = {line.strip() for line in f if line.strip()}
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not read import file: {e}").format(e=e))
            return

        if not imported_words:
            QMessageBox.information(self, _("Info"), _("The selected file is empty or contains no words."))
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(_("Import Mode"))
        msg_box.setText(_("How do you want to import the words?"))
        merge_btn = msg_box.addButton(_("Merge (Add new words)"), QMessageBox.ButtonRole.ActionRole)
        replace_btn = msg_box.addButton(_("Replace (Overwrite existing)"), QMessageBox.ButtonRole.DestructiveRole)
        msg_box.addButton(QMessageBox.StandardButton.Cancel)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()
        if clicked_button == replace_btn:
            self.spell_checker.clear_user_dictionary()
            self.spell_checker.add_words_to_user_dictionary(sorted(list(imported_words)))
        elif clicked_button == merge_btn:
            existing_words = set(self.spell_checker.get_user_words())
            new_words = sorted(list(imported_words - existing_words))
            if new_words:
                self.spell_checker.add_words_to_user_dictionary(new_words)

        if clicked_button != msg_box.button(QMessageBox.StandardButton.Cancel):
            self.refresh_list()
            QMessageBox.information(self, _("Success"), _("Dictionary successfully imported."))
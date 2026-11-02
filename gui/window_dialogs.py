import os

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QVBoxLayout,
)

from core.i18n import _


class ProgressHelper(QObject):
    progress = pyqtSignal(int, int, str)


class WorkerResultDialog(QDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 500)
        layout = QVBoxLayout(self)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlainText(text)
        self.text_edit.setReadOnly(True)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)


class WorkerResultListDialog(QDialog):
    def __init__(self, title, data, main_window):
        super().__init__(main_window)
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.main_window = main_window
        layout = QVBoxLayout(self)

        info_label = QLabel(_("Double-click on an entry opens the file at the corresponding location."))
        layout.addWidget(info_label)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)

        for entry in data:
            text = entry.get("display_text", _("Unknown Error"))
            file_path = entry.get("file_path")
            line = entry.get("line", 1)

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setData(Qt.ItemDataRole.UserRole + 1, line)
            self.list_widget.addItem(item)

        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_item_double_clicked(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        line = item.data(Qt.ItemDataRole.UserRole + 1)

        if file_path and os.path.exists(file_path):
            self.main_window.load_file(file_path)
            if line:
                self.main_window.scroll_to_line(line)
            self.accept()

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget, 
                             QListWidgetItem, QFrame)
from PyQt6.QtCore import Qt, QEvent, pyqtSignal

from core.i18n import _


class QuickOpenDialog(QDialog):
    """
    Fast file launcher dialog (Ctrl+P / Quick Open).
    Allows typing to search markdown files in the project content directory,
    navigating with arrows and opening on Enter.
    """
    file_selected = pyqtSignal(str)

    def __init__(self, content_dir, parent=None):
        super().__init__(parent)
        self.content_dir = content_dir
        self.all_files = []

        self.setWindowTitle(_("Quick Open"))
        self.setMinimumWidth(550)
        self.setMinimumHeight(350)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Container frame for styling
        self.frame = QFrame()
        self.frame.setObjectName("quickOpenFrame")
        self.frame.setStyleSheet("""
            QFrame#quickOpenFrame {
                border: 2px solid palette(highlight);
                border-radius: 8px;
                background-color: palette(window);
            }
        """)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(8, 8, 8, 8)
        frame_layout.setSpacing(6)

        # Search Input
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(_("Search files by name... (↑/↓ to navigate, Enter to open, Esc to close)"))
        self.search_edit.textChanged.connect(self.filter_files)
        font = self.search_edit.font()
        font.setPointSize(font.pointSize() + 2)
        self.search_edit.setFont(font)
        frame_layout.addWidget(self.search_edit)

        # Result List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        frame_layout.addWidget(self.list_widget)

        layout.addWidget(self.frame)

        # Scan files
        self.scan_files()
        self.filter_files("")

        # Install event filter to capture arrow keys in QLineEdit
        self.search_edit.installEventFilter(self)
        self.list_widget.installEventFilter(self)

    def scan_files(self):
        """Scans the content directory for Markdown files."""
        self.all_files = []
        if not self.content_dir or not os.path.exists(self.content_dir):
            return

        for root, dirs, files in os.walk(self.content_dir):
            # Skip hidden folders
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.lower().endswith(('.md', '.markdown')):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, self.content_dir)
                    self.all_files.append((f, rel_path, full_path))

        # Sort by filename
        self.all_files.sort(key=lambda x: x[0].lower())

    def filter_files(self, query):
        """Filters the list of files based on user query."""
        self.list_widget.clear()
        query = query.strip().lower()

        for filename, rel_path, full_path in self.all_files:
            if not query or query in filename.lower() or query in rel_path.lower():
                item = QListWidgetItem(f"{filename}  —  {rel_path}")
                item.setData(Qt.ItemDataRole.UserRole, full_path)
                self.list_widget.addItem(item)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def eventFilter(self, obj, event):
        """Allows Up/Down arrow navigation and Enter from the search input."""
        if obj in (self.search_edit, self.list_widget) and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if obj == self.search_edit and key == Qt.Key.Key_Down:
                cur = self.list_widget.currentRow()
                if cur < self.list_widget.count() - 1:
                    self.list_widget.setCurrentRow(cur + 1)
                return True
            elif obj == self.search_edit and key == Qt.Key.Key_Up:
                cur = self.list_widget.currentRow()
                if cur > 0:
                    self.list_widget.setCurrentRow(cur - 1)
                return True
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.accept_selection()
                return True
            elif key == Qt.Key.Key_Escape:
                self.reject()
                return True

        return super().eventFilter(obj, event)

    def accept_selection(self):
        """Emits selected file and closes."""
        current_item = self.list_widget.currentItem()
        if current_item:
            full_path = current_item.data(Qt.ItemDataRole.UserRole)
            if full_path:
                self.file_selected.emit(full_path)
                self.accept()
                return
        self.reject()

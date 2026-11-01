import os
from PyQt6.QtWidgets import QTabWidget, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from core.i18n import _


class DocumentTabWidget(QTabWidget):
    """
    Tab widget managing multiple open documents (EditorWidgets).
    Supports closing tabs, dirty state indicators (dot in tab title),
    switching between documents, and notifying listeners.
    """
    current_document_changed = pyqtSignal(object, object)  # (editor, file_path)
    all_tabs_closed = pyqtSignal()
    save_requested = pyqtSignal(object)  # (editor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Connect tab events
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_changed)

        # Tab bar styling
        self.tabBar().setElideMode(Qt.TextElideMode.ElideRight)

    def add_document(self, editor, file_path):
        """Adds an editor as a new tab, or switches to it if already open."""
        if file_path:
            existing_index = self.find_tab_by_path(file_path)
            if existing_index != -1:
                self.setCurrentIndex(existing_index)
                return self.widget(existing_index)

        filename = os.path.basename(file_path) if file_path else _("Untitled")
        index = self.addTab(editor, filename)
        self.setTabToolTip(index, file_path or "")
        self.setCurrentIndex(index)

        editor.document().modificationChanged.connect(
            lambda _modified, document_editor=editor: self.update_tab_title(document_editor)
        )

        return editor

    def set_document_path(self, editor, file_path):
        index = self.indexOf(editor)
        if index == -1:
            return
        editor.file_path = file_path
        self.setTabText(index, os.path.basename(file_path) if file_path else _("Untitled"))
        self.setTabToolTip(index, file_path or "")
        self.update_tab_title(editor)

    def find_tab_by_path(self, file_path):
        """Finds the tab index for a given file path, or -1 if not open."""
        if not file_path:
            return -1
        target_abs = os.path.abspath(file_path)
        for i in range(self.count()):
            editor = self.widget(i)
            if hasattr(editor, 'file_path') and editor.file_path:
                if os.path.abspath(editor.file_path) == target_abs:
                    return i
        return -1

    def get_editor_for_path(self, file_path):
        """Returns the EditorWidget for the given path, or None."""
        idx = self.find_tab_by_path(file_path)
        if idx != -1:
            return self.widget(idx)
        return None

    def current_editor(self):
        """Returns the currently active EditorWidget, or None."""
        return self.currentWidget()

    def current_file_path(self):
        """Returns the file path of the currently active tab, or None."""
        editor = self.current_editor()
        if editor and hasattr(editor, 'file_path'):
            return editor.file_path
        return None

    def get_all_editors(self):
        """Returns a list of all open EditorWidget instances."""
        return [self.widget(i) for i in range(self.count())]

    def get_open_paths(self):
        """Returns a list of file paths of all currently open tabs."""
        paths = []
        for i in range(self.count()):
            editor = self.widget(i)
            if hasattr(editor, 'file_path') and editor.file_path:
                paths.append(editor.file_path)
        return paths

    def update_tab_title(self, editor):
        """Updates the tab text with a dirty dot '● ' if modified."""
        index = self.indexOf(editor)
        if index == -1:
            return

        file_path = getattr(editor, 'file_path', None)
        filename = os.path.basename(file_path) if file_path else _("Untitled")
        is_modified = editor.document().isModified() or getattr(editor, 'frontmatter_modified', False)

        title = f"● {filename}" if is_modified else filename
        self.setTabText(index, title)

    def close_tab(self, index):
        """Closes a tab at index, prompting to save if modified."""
        editor = self.widget(index)
        if not editor:
            return False

        # Check for unsaved changes in this tab
        is_modified = editor.document().isModified() or getattr(editor, 'frontmatter_modified', False)
        if is_modified:
            file_path = getattr(editor, 'file_path', None)
            filename = os.path.basename(file_path) if file_path else _('Untitled')
            reply = QMessageBox.question(
                self,
                _("Unsaved Changes"),
                _("'{filename}' has unsaved changes.\nDo you want to save before closing?").format(filename=filename),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_requested.emit(editor)
                if editor.document().isModified() or getattr(editor, 'frontmatter_modified', False):
                    return False
            elif reply == QMessageBox.StandardButton.Discard:
                editor.document().setModified(False)
                editor.frontmatter_modified = False
            elif reply == QMessageBox.StandardButton.Cancel:
                return False

        self.removeTab(index)
        editor.deleteLater()

        return True

    def close_all_tabs(self):
        """Attempts to close all tabs. Returns True if all were closed."""
        while self.count() > 0:
            # Always close the active or last tab
            success = self.close_tab(self.count() - 1)
            if not success:
                return False
        return True

    def _on_current_changed(self, index):
        if index != -1:
            editor = self.widget(index)
            file_path = getattr(editor, 'file_path', None)
            self.current_document_changed.emit(editor, file_path)
        else:
            self.all_tabs_closed.emit()

    def mousePressEvent(self, event):
        """Allow closing tab with middle mouse button."""
        if event.button() == Qt.MouseButton.MiddleButton:
            tab_index = self.tabBar().tabAt(event.position().toPoint())
            if tab_index != -1:
                self.close_tab(tab_index)
                return
        super().mousePressEvent(event)

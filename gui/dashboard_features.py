import os

from PyQt6.QtCore import Qt

from core import APP_NAME
from .dialogs.quick_open_dialog import QuickOpenDialog
from core.i18n import _


class DashboardFeaturesMixin:
    def on_tree_clicked(self, index):
        file_path = self.file_tree.get_file_path(index)
        if os.path.isfile(file_path):
            self.load_file(file_path)
    def show_quick_open(self):
        dialog = QuickOpenDialog(self.content_dir, self)
        dialog.file_selected.connect(self.load_file)
        dialog.exec()
    def show_dashboard(self):
        """Wechselt zur Dashboard-Ansicht."""
        self.refresh_dashboard()
        self.content_stack.setCurrentIndex(0)
        self.update_status_bar()
    def refresh_dashboard(self):
        """Aktualisiert die Daten im Dashboard."""
        if hasattr(self, 'dashboard_worker') and not self.dashboard_worker.isRunning():
            self.dashboard.set_loading(True)
            self.dashboard_worker.start()
    def handle_global_refresh(self):
        """Zentraler Handler für F5 Refresh, abhängig vom Kontext."""
        # 1. Wenn Dashboard aktiv ist, Statistiken neu laden
        if self.content_stack.currentIndex() == 0:
            self.refresh_dashboard()
        
        # 2. Seitenleiste aktualisieren (Explorer & Media)
        # FileTree nutzt QFileSystemModel (Auto-Refresh), aber wir erzwingen einen Re-Scan
        self.file_tree.fs_model.setRootPath(self.content_dir)
        self.media_library.refresh_library()
    def on_dashboard_item_clicked(self, item):
        """Wird aufgerufen, wenn auf eine Datei im Dashboard geklickt wird."""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            self.load_file(file_path)
    def update_status_bar(self):
        if not self.current_file_path:
            self.status_label.setText(_("Ready"))
            self.setWindowTitle(f"{self.project_name} - {APP_NAME}")
            return

        # Compute relative path for a compact display
        try:
            display_path = os.path.relpath(self.current_file_path, self.project_root)
        except ValueError:
            display_path = self.current_file_path

        is_dashboard = self.content_stack.currentIndex() == 0
        
        if not is_dashboard and self.editor.is_dirty():
            self.status_label.setText(f"[{_('UNSAVED')}] {display_path}")
            self.setWindowTitle(f"* {os.path.basename(self.current_file_path)} - {self.project_name} - {APP_NAME}")
        elif not is_dashboard:
            self.status_label.setText(display_path)
            self.setWindowTitle(f"{os.path.basename(self.current_file_path)} - {self.project_name} - {APP_NAME}")
        else:
            self.status_label.setText(_("Dashboard"))
            self.setWindowTitle(f"{self.project_name} - Dashboard - {APP_NAME}")
    def update_cursor_label(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(_("Ln {line}, Col {col}").format(line=line, col=col))
    def scroll_to_line(self, line_number):
        # Move cursor to the specified line
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line_number)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        self.editor.setFocus()
    def restore_scroll_position(self, ok=True):
        """Restores the scroll position after the preview reloads."""
        if ok:
            self.sync_scroll_and_line_numbers(self.editor.verticalScrollBar().value())
    def sync_scroll_and_line_numbers(self, value, editor=None):
        """Synchronizes scroll position from the editor to the preview."""
        editor = editor or self.editor
        if editor is not self.editor:
            return
        # Zeilennummern-Bereich aktualisieren, wenn gescrollt wird
        editor.line_number_area.update()

        if not self.preview.isVisible():
            return

        scrollbar = editor.verticalScrollBar()
        max_val = scrollbar.maximum()
        
        if max_val > 0:
            percentage = value / max_val
            # Improvement: "Stick to bottom"
            # Wenn der Editor ganz nach unten gescrollt ist, scrollt die Vorschau ebenfalls ganz nach unten.
            if value + scrollbar.pageStep() >= max_val:
                percentage = 1.0
            
            self.preview.scroll_to_percentage(percentage)

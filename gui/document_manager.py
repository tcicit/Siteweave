"""Document and tab lifecycle operations for the main window."""

import os

import frontmatter
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QMessageBox

from core.i18n import _


class DocumentManager:
    """Coordinates document loading, saving, session restore, and file watching."""

    def __init__(self, window):
        self.window = window

    def get_open_editors(self):
        tabs = self.window.__dict__.get("editor_tabs")
        if tabs is not None:
            return tabs.get_all_editors()
        editor = self.window.__dict__.get("editor")
        return [editor] if editor is not None else []

    def save_all_dirty_editors(self):
        dirty_editors = [
            editor for editor in self.get_open_editors()
            if editor.file_path and editor.is_dirty()
        ]
        for editor in dirty_editors:
            self.window.save_file(editor)
        return not any(editor.is_dirty() for editor in dirty_editors)

    def is_project_path(self, path):
        try:
            root = os.path.abspath(self.window.project_root)
            return os.path.commonpath([root, os.path.abspath(path)]) == root
        except ValueError:
            return False

    def load_last_file(self):
        window = self.window
        session_paths = window.project_config.get("open_files", [])
        if isinstance(session_paths, list):
            valid_paths = []
            for path in session_paths:
                if not isinstance(path, str) or not path:
                    continue
                path = path if os.path.isabs(path) else os.path.join(window.project_root, path)
                path = os.path.abspath(path)
                if os.path.isfile(path) and self.is_project_path(path):
                    valid_paths.append(path)
            for path in valid_paths:
                window.load_file(path)

            active_path = window.project_config.get("last_open_file")
            if isinstance(active_path, str) and active_path and not os.path.isabs(active_path):
                active_path = os.path.join(window.project_root, active_path)
            if isinstance(active_path, str):
                active_path = os.path.abspath(active_path)
            if active_path in valid_paths:
                index = window.editor_tabs.find_tab_by_path(active_path)
                if index != -1:
                    window.editor_tabs.setCurrentIndex(index)
            if valid_paths:
                return

        last_file = window.project_config.get("last_open_file")
        if isinstance(last_file, str) and last_file and not os.path.isabs(last_file):
            last_file = os.path.join(window.project_root, last_file)
        if not isinstance(last_file, str) or not last_file:
            last_file = window.app_config_manager.get("last_file")
        if isinstance(last_file, str) and last_file:
            last_file = os.path.abspath(last_file)
        if last_file and os.path.isfile(last_file) and self.is_project_path(last_file):
            window.load_file(last_file)
            return

        index_path = os.path.join(window.content_dir, "index.md")
        if os.path.exists(index_path):
            window.load_file(index_path)
            window.show_dashboard()

    def load_file(self, file_path):
        window = self.window
        if not file_path:
            return
        file_path = os.path.abspath(file_path)

        existing_index = window.editor_tabs.find_tab_by_path(file_path)
        if existing_index != -1:
            window.editor_tabs.setCurrentIndex(existing_index)
            window.content_stack.setCurrentIndex(1)
            return

        try:
            post = frontmatter.load(file_path)
            if window.editor.file_path is None and not window.editor.is_dirty():
                editor = window.editor
            else:
                editor = window._create_editor_widget()

            editor.file_path = file_path
            editor.metadata = post.metadata.copy()
            editor.frontmatter_modified = False

            if window.editor_tabs.indexOf(editor) == -1:
                window.editor_tabs.add_document(editor, file_path)
            else:
                window.editor_tabs.set_document_path(editor, file_path)

            editor.setPlainText(post.content)
            editor.moveCursor(QTextCursor.MoveOperation.End)
            editor.document().setModified(False)

            window.editor_tabs.setCurrentWidget(editor)
            window.content_stack.setCurrentIndex(1)
            window.on_document_changed(editor, file_path)

            try:
                window.app_config_manager.update({"last_file": file_path})
                window.app_config_manager.save()
            except Exception as error:
                QMessageBox.warning(
                    window, _("Error"),
                    _("The file opened, but the last-file setting could not be saved:\n{error}").format(
                        error=error
                    ),
                )
            if file_path not in window.file_watcher.files():
                window.file_watcher.addPath(file_path)
        except Exception as error:
            QMessageBox.critical(window, _("Error"), _("Could not load file: {e}").format(e=error))

    def save_file(self, editor=None):
        window = self.window
        editor = editor or window.editor
        file_path = getattr(editor, "file_path", None)
        if not file_path:
            return

        if editor is window.editor:
            window.frontmatter_panel.validate_fields()
            if not window.frontmatter_panel.custom_fields_valid:
                QMessageBox.warning(
                    window,
                    _("Invalid Custom Fields"),
                    _("Custom field names must be non-empty, unique, and different from built-in fields."),
                )
                return
            editor.metadata = window.frontmatter_panel.get_data()
        metadata = editor.metadata
        content = editor.toPlainText()

        window._ignored_file_changes.add(os.path.abspath(file_path))
        window._ignore_timer.start()

        try:
            post = frontmatter.Post(content, **metadata)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(frontmatter.dumps(post))

            editor.document().setModified(False)
            editor.frontmatter_modified = False
            if editor is window.editor:
                window.frontmatter_modified = False
                window.update_status_bar()
            window.editor_tabs.update_tab_title(editor)
            if file_path not in window.file_watcher.files():
                window.file_watcher.addPath(file_path)
        except Exception as error:
            QMessageBox.critical(window, _("Error"), _("Could not save file: {e}").format(e=error))

    def handle_external_change(self, path):
        window = self.window
        normalized_path = os.path.abspath(path)
        if normalized_path in window._ignored_file_changes:
            window._ignored_file_changes.discard(normalized_path)
            return

        if not os.path.isfile(normalized_path):
            if normalized_path in window.file_watcher.files():
                window.file_watcher.removePath(normalized_path)
            return

        editor = window.editor_tabs.get_editor_for_path(path)
        if editor is None:
            return
        if not editor.is_dirty():
            self.reload_editor(editor, path)
            return

        reply = QMessageBox.question(
            window,
            _("File Changed Externally"),
            _("The file '{filename}' has been modified externally. Do you want to reload it? "
              "Your unsaved changes will be lost.").format(filename=os.path.basename(path)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reload_editor(editor, path)

    def handle_path_renamed(self, old_path, new_path):
        window = self.window
        old_path = os.path.abspath(old_path)
        new_path = os.path.abspath(new_path)
        active_editor = None

        for editor in window.editor_tabs.get_all_editors():
            file_path = getattr(editor, "file_path", None)
            if not file_path:
                continue
            file_path = os.path.abspath(file_path)
            try:
                if os.path.commonpath((old_path, file_path)) != old_path:
                    continue
            except ValueError:
                continue

            relative_path = os.path.relpath(file_path, old_path)
            renamed_path = new_path if relative_path == os.curdir else os.path.join(new_path, relative_path)
            editor.file_path = renamed_path
            window.editor_tabs.set_document_path(editor, renamed_path)

            if file_path in window.file_watcher.files():
                window.file_watcher.removePath(file_path)
            if os.path.isfile(renamed_path) and renamed_path not in window.file_watcher.files():
                window.file_watcher.addPath(renamed_path)

            if editor is window.editor:
                active_editor = editor

        if active_editor is not None:
            window.on_document_changed(active_editor, active_editor.file_path)

    def reload_editor(self, editor, file_path):
        window = self.window
        try:
            post = frontmatter.load(file_path)
            editor.metadata = post.metadata.copy()
            editor.frontmatter_modified = False
            editor.setPlainText(post.content)
            editor.document().setModified(False)
            window.editor_tabs.update_tab_title(editor)
            if file_path not in window.file_watcher.files():
                window.file_watcher.addPath(file_path)
            if editor is window.editor:
                window.on_document_changed(editor, file_path)
        except Exception as error:
            QMessageBox.critical(
                window, _("Error"), _("Could not reload file: {error}").format(error=error)
            )

    def autosave(self):
        for editor in self.window.editor_tabs.get_all_editors():
            if editor.file_path and editor.is_dirty():
                self.window.save_file(editor)

    def confirm_unsaved_changes(self):
        window = self.window
        dirty_editors = [editor for editor in self.get_open_editors() if editor.is_dirty()]
        if not dirty_editors:
            return True
        if window.app_config.get("autosave_on_switch", False):
            return self.save_all_dirty_editors()

        reply = QMessageBox.question(
            window,
            _("Unsaved Changes"),
            _("Open documents have unsaved changes. Do you want to save them before switching?"),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Save:
            return self.save_all_dirty_editors()
        if reply == QMessageBox.StandardButton.Discard:
            for editor in dirty_editors:
                editor.document().setModified(False)
                editor.frontmatter_modified = False
                window.editor_tabs.update_tab_title(editor)
            return True
        return False

    def confirm_close(self):
        window = self.window
        dirty_editors = [editor for editor in window.editor_tabs.get_all_editors() if editor.is_dirty()]
        if not dirty_editors:
            return True
        if window.app_config.get("autosave_on_close", False):
            for editor in dirty_editors:
                window.save_file(editor)
        else:
            reply = QMessageBox.question(
                window,
                _("Unsaved Changes"),
                _("Open documents have unsaved changes. Do you want to save them before closing?"),
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                for editor in dirty_editors:
                    window.save_file(editor)
            elif reply == QMessageBox.StandardButton.Discard:
                dirty_editors = []
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        return not any(editor.is_dirty() for editor in dirty_editors)

    def save_session(self):
        window = self.window
        window.project_config_manager.update(
            {
                "open_files": window.editor_tabs.get_open_paths(),
                "last_open_file": window.current_file_path,
            }
        )
        window.project_config_manager.save()

    def reset_ignored_file_changes(self):
        self.window._ignored_file_changes.clear()

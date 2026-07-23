import os
from unittest.mock import MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QWidget
from gui.main_window import ProgressHelper, WorkerResultDialog, WorkerResultListDialog, MainWindow


def test_worker_result_dialog_displays_text(qtbot):
    dialog = WorkerResultDialog("My Title", "Hello\nWorld")
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "My Title"
    assert dialog.text_edit.toPlainText() == "Hello\nWorld"
    assert dialog.text_edit.isReadOnly()


def test_worker_result_list_dialog_populates_items_and_handles_double_click(qtbot, tmp_path):
    data_file = tmp_path / "sample.md"
    data_file.write_text("Test content\n")

    class DummyMainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.loaded = []
            self.scrolled = []

        def load_file(self, path):
            self.loaded.append(path)

        def scroll_to_line(self, line):
            self.scrolled.append(line)

    dummy_root = DummyMainWindow()
    data = [
        {'display_text': 'First entry', 'file_path': str(data_file), 'line': 5},
        {'display_text': 'Second entry', 'file_path': str(data_file), 'line': 10},
    ]

    dialog = WorkerResultListDialog("Search Results", data, dummy_root)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Search Results"
    assert dialog.list_widget.count() == 2

    item = dialog.list_widget.item(0)
    assert item.text() == 'First entry'
    assert item.data(Qt.ItemDataRole.UserRole) == str(data_file)
    assert item.data(Qt.ItemDataRole.UserRole + 1) == 5

    dialog.on_item_double_clicked(item)
    assert dummy_root.loaded == [str(data_file)]
    assert dummy_root.scrolled == [5]


def test_progress_helper_emits_signal(qtbot):
    helper = ProgressHelper()
    with qtbot.waitSignal(helper.progress, timeout=1000) as blocker:
        helper.progress.emit(1, 2, "Processing")

    assert blocker.args == [1, 2, "Processing"]


def test_main_window_get_icon_returns_null_for_missing_file(tmp_path):
    window = MainWindow.__new__(MainWindow)
    window.app_root = str(tmp_path)

    icon = window.get_icon("missing-icon.png")

    assert isinstance(icon, QIcon)
    assert icon.isNull()


def test_toggle_preview_and_line_numbers_update_state():
    window = MainWindow.__new__(MainWindow)
    window.preview = MagicMock()
    window.editor = MagicMock()
    window.app_config = {}

    window.toggle_preview(True)
    window.preview.setVisible.assert_called_once_with(True)

    window.toggle_line_numbers(False)
    window.editor.set_line_numbers_visible.assert_called_once_with(False)
    assert window.app_config['view_show_line_numbers'] is False


def test_toggle_spellcheck_updates_configuration():
    window = MainWindow.__new__(MainWindow)
    window.editor = MagicMock()
    window.project_config = {}
    window.project_config_manager = MagicMock()

    window.toggle_spellcheck(True)

    window.editor.set_spellchecker_enabled.assert_called_once_with(True)
    assert window.project_config['spellcheck_enabled'] is True
    window.project_config_manager.update.assert_called_once_with({'spellcheck_enabled': True})
    window.project_config_manager.save.assert_called_once()

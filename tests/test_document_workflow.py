from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from unittest.mock import MagicMock

from gui.dialogs.quick_open_dialog import QuickOpenDialog
from gui.document_tab_widget import DocumentTabWidget
from gui.editor_widget import EditorWidget
from gui.main_window import MainWindow


def test_document_tabs_track_paths_and_unsaved_changes(qtbot, tmp_path):
    tabs = DocumentTabWidget()
    first_path = tmp_path / "first.md"
    second_path = tmp_path / "second.md"
    first = EditorWidget()
    second = EditorWidget()
    first.file_path = str(first_path)
    second.file_path = str(second_path)
    qtbot.addWidget(tabs)

    tabs.add_document(first, str(first_path))
    tabs.add_document(second, str(second_path))

    assert tabs.count() == 2
    assert tabs.current_file_path() == str(second_path)
    assert tabs.find_tab_by_path(str(first_path)) == 0

    first.insertPlainText("Unsaved content")

    assert tabs.tabText(0) == "● first.md"


def test_external_image_drop_imports_once_and_links_relative_to_document(qtbot, tmp_path):
    project = tmp_path / "project"
    content = project / "content"
    content.mkdir(parents=True)
    source = tmp_path / "photo.png"
    source.write_bytes(b"image-data")

    editor = EditorWidget(project_root=str(project))
    editor.file_path = str(content / "page.md")
    qtbot.addWidget(editor)

    imported_path = editor.import_external_asset(str(source))
    repeated_path = editor.import_external_asset(str(source))
    editor.insert_file_link(str(source))

    assert imported_path == str(project / "assets" / "images" / "photo.png")
    assert repeated_path == imported_path
    assert (project / "assets" / "images" / "photo.png").read_bytes() == source.read_bytes()
    assert editor.toPlainText() == "![photo.png](../assets/images/photo.png)"

    conflicting_source = tmp_path / "another" / "photo.png"
    conflicting_source.parent.mkdir()
    conflicting_source.write_bytes(b"different-image")
    conflict_path = editor.import_external_asset(str(conflicting_source))

    assert conflict_path == str(project / "assets" / "images" / "photo_1.png")
    assert (project / "assets" / "images" / "photo_1.png").read_bytes() == conflicting_source.read_bytes()


def test_quick_open_filters_and_opens_with_keyboard(qtbot, tmp_path):
    content_dir = tmp_path / "content"
    nested_dir = content_dir / "guides"
    nested_dir.mkdir(parents=True)
    target = nested_dir / "setup.MD"
    target.write_text("# Setup", encoding="utf-8")
    (content_dir / "other.md").write_text("# Other", encoding="utf-8")

    dialog = QuickOpenDialog(str(content_dir))
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.search_edit.setFocus()
    QTest.keyClicks(dialog.search_edit, "setup")

    assert dialog.list_widget.count() == 1
    with qtbot.waitSignal(dialog.file_selected, timeout=1000) as selection:
        QTest.keyClick(dialog.search_edit, Qt.Key.Key_Return)

    assert selection.args[0] == str(target)


def test_project_session_restores_open_files_and_active_tab(tmp_path):
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("# First", encoding="utf-8")
    second.write_text("# Second", encoding="utf-8")

    window = MainWindow.__new__(MainWindow)
    window.project_root = str(tmp_path)
    window.project_config = {
        "open_files": [str(first), str(second)],
        "last_open_file": str(second),
    }
    window.app_config_manager = MagicMock()
    window.editor_tabs = MagicMock()
    window.editor_tabs.find_tab_by_path.return_value = 1
    window.load_file = MagicMock()

    window.load_last_file()

    assert window.load_file.call_args_list[0].args == (str(first),)
    assert window.load_file.call_args_list[1].args == (str(second),)
    window.editor_tabs.setCurrentIndex.assert_called_once_with(1)


def test_render_preparation_does_not_block_on_untitled_editor():
    window = MainWindow.__new__(MainWindow)
    untitled_editor = MagicMock()
    untitled_editor.file_path = None
    untitled_editor.is_dirty.return_value = True
    window.editor_tabs = MagicMock()
    window.editor_tabs.get_all_editors.return_value = [untitled_editor]
    window.save_file = MagicMock()

    assert window._save_all_dirty_editors() is True
    window.save_file.assert_not_called()


def test_render_preparation_saves_dirty_documents():
    window = MainWindow.__new__(MainWindow)
    editor = MagicMock()
    editor.file_path = "/project/content/page.md"
    editor.is_dirty.side_effect = [True, False]
    window.editor_tabs = MagicMock()
    window.editor_tabs.get_all_editors.return_value = [editor]
    window.save_file = MagicMock()

    assert window._save_all_dirty_editors() is True
    window.save_file.assert_called_once_with(editor)


def test_autosave_on_switch_saves_previous_dirty_document(qtbot):
    previous_editor = EditorWidget()
    next_editor = EditorWidget()
    previous_editor.file_path = "/project/content/first.md"
    previous_editor.insertPlainText("Unsaved change")
    qtbot.addWidget(previous_editor)
    qtbot.addWidget(next_editor)

    window = MainWindow.__new__(MainWindow)
    window._active_tab_editor = previous_editor
    window.editor = previous_editor
    window.current_file_path = previous_editor.file_path
    window.app_config = {"autosave_on_switch": True}
    window.frontmatter_panel = MagicMock()
    window.file_tree = MagicMock()
    window.preview = MagicMock()
    window.outline = MagicMock()
    window.update_status_bar = MagicMock()
    window.update_cursor_label = MagicMock()
    window.save_file = MagicMock()

    window.on_document_changed(next_editor, None)

    window.save_file.assert_called_once_with(previous_editor)
    assert window.editor is next_editor


def test_document_tab_widget_has_no_initial_untitled_tab(qtbot):
    tabs = DocumentTabWidget()
    qtbot.addWidget(tabs)

    assert tabs.count() == 0

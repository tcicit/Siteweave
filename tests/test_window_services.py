from types import SimpleNamespace
from unittest.mock import MagicMock

import frontmatter
from PyQt6.QtWidgets import QMainWindow

from gui.action_manager import ActionManager
from gui.document_manager import DocumentManager
from gui.editor_widget import EditorWidget
from gui.main_window import MainWindow
from gui.project_features import ProjectFeaturesMixin
from gui.theme_manager import ThemeManager


def test_document_manager_restores_session_and_active_tab(tmp_path):
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("# First", encoding="utf-8")
    second.write_text("# Second", encoding="utf-8")
    window = SimpleNamespace(
        project_root=str(tmp_path),
        project_config={
            "open_files": [str(first), str(second)],
            "last_open_file": str(second),
        },
        editor_tabs=MagicMock(),
        load_file=MagicMock(),
    )
    window.editor_tabs.find_tab_by_path.return_value = 1

    DocumentManager(window).load_last_file()

    assert [call.args[0] for call in window.load_file.call_args_list] == [
        str(first),
        str(second),
    ]
    window.editor_tabs.setCurrentIndex.assert_called_once_with(1)


def test_document_manager_saves_editor_and_clears_dirty_state(qtbot, tmp_path):
    file_path = tmp_path / "page.md"
    file_path.write_text("", encoding="utf-8")
    editor = EditorWidget()
    editor.file_path = str(file_path)
    editor.metadata = {"title": "Saved"}
    editor.setPlainText("Updated content")
    qtbot.addWidget(editor)

    window = SimpleNamespace(
        editor=editor,
        frontmatter_panel=MagicMock(custom_fields_valid=True),
        _ignored_file_changes=set(),
        _ignore_timer=MagicMock(),
        editor_tabs=MagicMock(),
        file_watcher=MagicMock(),
        update_status_bar=MagicMock(),
    )
    window.frontmatter_panel.get_data.return_value = editor.metadata

    DocumentManager(window).save_file(editor)

    saved = frontmatter.load(str(file_path))
    assert saved.content == "Updated content"
    assert saved.metadata["title"] == "Saved"
    assert not editor.is_dirty()
    window.editor_tabs.update_tab_title.assert_called_once_with(editor)


def test_document_manager_reloads_clean_external_changes(qtbot, tmp_path):
    file_path = tmp_path / "page.md"
    file_path.write_text("---\ntitle: External\n---\nNew contents", encoding="utf-8")
    editor = EditorWidget()
    editor.file_path = str(file_path)
    qtbot.addWidget(editor)
    window = SimpleNamespace(
        editor_tabs=MagicMock(),
        editor=editor,
        file_watcher=MagicMock(),
        on_document_changed=MagicMock(),
        _ignored_file_changes=set(),
    )
    window.editor_tabs.get_editor_for_path.return_value = editor
    window.file_watcher.files.return_value = [str(file_path)]

    DocumentManager(window).handle_external_change(str(file_path))

    assert editor.toPlainText() == "New contents"
    assert editor.metadata["title"] == "External"
    window.editor_tabs.update_tab_title.assert_called_once_with(editor)
    window.on_document_changed.assert_called_once_with(editor, str(file_path))


def test_document_manager_updates_open_document_after_rename(tmp_path):
    old_dir = tmp_path / "old"
    old_dir.mkdir()
    old_path = old_dir / "page.md"
    old_path.write_text("# Page", encoding="utf-8")
    new_dir = tmp_path / "renamed"
    new_dir.mkdir()
    new_path = new_dir / "page.md"
    old_path.rename(new_path)

    editor = MagicMock()
    editor.file_path = str(old_path)
    window = SimpleNamespace(
        editor_tabs=MagicMock(),
        editor=editor,
        file_watcher=MagicMock(),
        on_document_changed=MagicMock(),
    )
    window.editor_tabs.get_all_editors.return_value = [editor]
    window.file_watcher.files.return_value = [str(old_path)]

    DocumentManager(window).handle_path_renamed(str(old_dir), str(new_dir))

    assert editor.file_path == str(new_path)
    window.editor_tabs.set_document_path.assert_called_once_with(editor, str(new_path))
    window.file_watcher.removePath.assert_called_once_with(str(old_path))
    window.file_watcher.addPath.assert_called_once_with(str(new_path))
    window.on_document_changed.assert_called_once_with(editor, str(new_path))


def test_document_manager_ignores_watcher_event_for_renamed_file(tmp_path):
    missing_path = str(tmp_path / "renamed-away.md")
    window = SimpleNamespace(
        _ignored_file_changes=set(),
        file_watcher=MagicMock(),
        editor_tabs=MagicMock(),
    )
    window.file_watcher.files.return_value = [missing_path]

    DocumentManager(window).handle_external_change(missing_path)

    window.file_watcher.removePath.assert_called_once_with(missing_path)
    window.editor_tabs.get_editor_for_path.assert_not_called()


def test_theme_manager_applies_mode_and_propagates_to_widgets(monkeypatch, qtbot):
    from gui import theme_manager

    applied = []
    monkeypatch.setattr(theme_manager, "apply_dark_theme", lambda app: applied.append("dark"))
    editor = MagicMock()
    panel = MagicMock()
    window = SimpleNamespace(
        app_root=".",
        action_icons={},
        _get_open_editors=lambda: [editor],
        preview=MagicMock(),
        sidebar_panels={"panel": panel},
        dashboard=MagicMock(),
        apply_custom_colors=MagicMock(),
    )

    ThemeManager(window).apply_theme(True)

    assert applied == ["dark"]
    editor.set_dark_mode.assert_called_once_with(True)
    window.preview.set_dark_mode.assert_called_once_with(True)
    panel.set_dark_mode.assert_called_once_with(True)
    window.dashboard.set_dark_mode.assert_called_once_with(True)
    window.apply_custom_colors.assert_called_once_with()


def test_action_manager_creates_window_owned_actions(qtbot):
    class ActionWindow(QMainWindow):
        def __getattr__(self, name):
            if name.startswith("_"):
                raise AttributeError(name)
            return lambda *args, **kwargs: None

    window = ActionWindow()
    qtbot.addWidget(window)
    window.app_config = {"view_show_preview": True, "view_show_line_numbers": True}
    window.project_config = {"spellcheck_enabled": True}

    manager = ActionManager(window)
    manager.create_actions()
    manager.init_toolbar()
    manager.init_menu()

    assert window.new_act.text() == "New Post"
    assert window.new_act.parent() is window
    assert window.save_act.shortcut().toString() == "Ctrl+S"
    assert window.dark_mode_act.isCheckable()
    assert window.toolbar.actions()
    assert len(window.menuBar().actions()) == 7


def test_main_window_dark_mode_handler_applies_theme():
    window = SimpleNamespace(apply_theme=MagicMock())

    MainWindow.toggle_dark_mode(window, True)

    window.apply_theme.assert_called_once_with(True)


def test_bulk_edit_reloads_current_open_tab(monkeypatch, tmp_path):
    from gui import project_features

    file_path = str(tmp_path / "page.md")
    editor = MagicMock()
    window = SimpleNamespace(
        _save_all_dirty_editors=MagicMock(return_value=True),
        project_root=str(tmp_path),
        content_dir=str(tmp_path),
        current_file_path=file_path,
        editor_tabs=MagicMock(),
        _reload_editor=MagicMock(),
    )
    window.editor_tabs.get_editor_for_path.return_value = editor

    class AcceptedBulkEditDialog:
        def __init__(self, *_args):
            pass

        def exec(self):
            return True

    monkeypatch.setattr(project_features, "BulkEditDialog", AcceptedBulkEditDialog)
    (tmp_path / "page.md").write_text("---\ntitle: Page\n---\n", encoding="utf-8")

    ProjectFeaturesMixin.show_bulk_edit_dialog(window)

    window._reload_editor.assert_called_once_with(editor, file_path)
    assert window.current_file_path == file_path


def test_switch_to_project_path_in_place_updates_all_components(tmp_path):
    old_proj = tmp_path / "old_project"
    old_proj.mkdir()
    new_proj = tmp_path / "new_project"
    new_proj.mkdir()
    (new_proj / "content").mkdir()
    (new_proj / "config.yaml").write_text("site_name: New\n", encoding="utf-8")

    window = SimpleNamespace(
        project_root=str(old_proj),
        project_name="old_project",
        app_root=str(tmp_path),
        content_dir=str(old_proj / "content"),
        assets_dir=str(old_proj / "assets"),
        current_file_path="dummy.md",
        frontmatter_modified=False,
        setWindowTitle=MagicMock(),
        check_unsaved_changes=MagicMock(return_value=True),
        _document_manager=MagicMock(return_value=MagicMock()),
        tag_worker=MagicMock(isRunning=MagicMock(return_value=True)),
        dashboard_worker=MagicMock(isRunning=MagicMock(return_value=True)),
        worker=MagicMock(isRunning=MagicMock(return_value=False)),
        file_watcher=MagicMock(files=MagicMock(return_value=["file1.md"])),
        _ignored_file_changes={"file1.md"},
        editor_tabs=MagicMock(count=MagicMock(return_value=0)),
        project_config_manager=None,
        project_config={},
        load_project_config=MagicMock(return_value={"site_name": "New"}),
        editor=MagicMock(),
        on_document_changed=MagicMock(),
        file_tree=MagicMock(),
        media_library=MagicMock(),
        preview=MagicMock(),
        frontmatter_panel=MagicMock(),
        update_frontmatter_layouts=MagicMock(),
        log_viewer=MagicMock(),
        toggle_spellcheck_act=MagicMock(),
        init_spellchecker=MagicMock(),
        dashboard=MagicMock(),
        workers_dir=str(tmp_path / "workers"),
        app_config_manager=MagicMock(load=MagicMock(return_value={"recent_projects": []})),
        add_to_recent_projects=MagicMock(),
        load_last_file=MagicMock(),
        show_dashboard=MagicMock(),
        update_status_bar=MagicMock(),
        update_cursor_label=MagicMock(),
    )

    old_dashboard_worker = window.dashboard_worker
    ProjectFeaturesMixin.switch_to_project_path(window, str(new_proj))

    assert window.project_root == str(new_proj)
    assert window.project_name == "new_project"
    assert window.content_dir == str(new_proj / "content")
    assert window.assets_dir == str(new_proj / "assets")

    # Checked unsaved changes and saved session
    window.check_unsaved_changes.assert_called_once()
    window._document_manager().save_session.assert_called_once()

    # Stopped workers
    window.tag_worker.quit.assert_called_once()
    old_dashboard_worker.quit.assert_called_once()

    # Cleared watchers and closed tabs
    window.file_watcher.removePaths.assert_called_once_with(["file1.md"])
    window.editor_tabs.close_all_tabs.assert_called_once()

    # Updated UI widgets
    window.file_tree.set_root_path.assert_called_once_with(str(new_proj / "content"))
    window.media_library.update_project.assert_called_once_with(
        str(new_proj), str(new_proj / "assets"), str(new_proj / "content")
    )
    window.preview.set_project_root.assert_called_once_with(str(new_proj))
    window.frontmatter_panel.set_project_root.assert_called_once_with(str(new_proj))
    window.log_viewer.set_log_file.assert_called_once_with(str(new_proj / "worker.log"))
    window.init_spellchecker.assert_called_once()
    window.load_last_file.assert_called_once()
    window.show_dashboard.assert_called_once()


def test_switch_to_project_path_aborts_on_unsaved_changes(tmp_path):
    old_proj = tmp_path / "old"
    old_proj.mkdir()
    new_proj = tmp_path / "new"
    new_proj.mkdir()

    window = SimpleNamespace(
        project_root=str(old_proj),
        check_unsaved_changes=MagicMock(return_value=False),
        editor_tabs=MagicMock(),
    )

    ProjectFeaturesMixin.switch_to_project_path(window, str(new_proj))

    assert window.project_root == str(old_proj)
    window.editor_tabs.close_all_tabs.assert_not_called()


def test_switch_to_project_path_ignores_same_path(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()

    window = SimpleNamespace(
        project_root=str(proj),
        check_unsaved_changes=MagicMock(),
    )

    ProjectFeaturesMixin.switch_to_project_path(window, str(proj))
    window.check_unsaved_changes.assert_not_called()


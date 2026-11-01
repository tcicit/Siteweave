from unittest.mock import patch

from gui.frontmatter_panel import FrontmatterPanel
from gui.editor_widget import EditorWidget
from gui.main_window import MainWindow


def test_custom_frontmatter_fields_round_trip_preserves_yaml_types(qtbot):
    panel = FrontmatterPanel()
    qtbot.addWidget(panel)
    metadata = {
        "title": "Custom metadata",
        "show_sidebar": False,
        "hero_items": ["first", "second"],
        "hero_config": {"layout": "wide"},
    }

    panel.set_data(metadata)

    assert panel.get_data()["show_sidebar"] is False
    assert panel.get_data()["hero_items"] == ["first", "second"]
    assert panel.get_data()["hero_config"] == {"layout": "wide"}

    panel.custom_field_rows[0]["value"].setText("true")

    assert panel.get_data()["show_sidebar"] == "true"


def test_custom_frontmatter_field_can_be_added_and_removed(qtbot):
    panel = FrontmatterPanel()
    qtbot.addWidget(panel)
    panel.set_data({"title": "Custom metadata"})

    panel.add_custom_field()
    row = panel.custom_field_rows[0]
    row["key"].setText("hero_position")
    row["value"].setText("top")

    assert panel.get_data()["hero_position"] == "top"

    panel.remove_custom_field(row)

    assert "hero_position" not in panel.get_data()


def test_custom_field_validation_marks_empty_and_duplicate_names(qtbot):
    panel = FrontmatterPanel()
    qtbot.addWidget(panel)
    panel.set_data({"title": "Custom metadata"})

    first = panel.add_custom_field()
    second = panel.add_custom_field()
    first["key"].setText("hero")
    second["key"].setText("hero")
    panel.validate_fields()

    assert panel.custom_fields_valid is False
    assert first["key"].styleSheet() == ""
    assert "#e74c3c" in second["key"].styleSheet()

    second["key"].setText("layout")
    panel.validate_fields()

    assert panel.custom_fields_valid is False
    assert "#e74c3c" in second["key"].styleSheet()


def test_frontmatter_panel_uses_compact_image_preview(qtbot):
    panel = FrontmatterPanel()
    qtbot.addWidget(panel)

    assert panel.image_preview_label.size().width() <= 80
    assert panel.image_preview_label.size().height() <= 60


def test_invalid_custom_fields_prevent_saving_without_dropping_data(qtbot, tmp_path):
    panel = FrontmatterPanel()
    qtbot.addWidget(panel)
    panel.set_data({"title": "Custom metadata"})
    first = panel.add_custom_field()
    second = panel.add_custom_field()
    first["key"].setText("hero")
    second["key"].setText("hero")

    file_path = tmp_path / "page.md"
    original_content = "---\ntitle: Existing\n---\nOriginal"
    file_path.write_text(original_content, encoding="utf-8")
    editor = EditorWidget()
    editor.file_path = str(file_path)
    editor.insertPlainText("Unsaved content")
    qtbot.addWidget(editor)

    window = MainWindow.__new__(MainWindow)
    window.editor = editor
    window.frontmatter_panel = panel

    with patch("gui.main_window.QMessageBox.warning") as warning:
        window.save_file(editor)

    warning.assert_called_once()
    assert file_path.read_text(encoding="utf-8") == original_content

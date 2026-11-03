import pytest
from PyQt6.QtWidgets import QComboBox, QSpinBox, QMessageBox
from gui.dialogs.app_config_dialog import AppConfigDialog
from core.config_manager import ConfigManager

def test_config_dialog_loads_correct_values(qtbot, temp_app_config):
    """
    Prüft, ob der Dialog die Werte aus der temporären YAML korrekt lädt.
    """
    # Initialisiere den Dialog mit dem Pfad aus der Fixture
    dialog = AppConfigDialog(config_path=temp_app_config)
    qtbot.addWidget(dialog)

    # Wir suchen das Widget über seinen Typ und (optional) Objektnamen.
    # Falls dein Widget in app_config_dialog.py anders heißt, passe den Namen hier an:
    lang_combo = dialog.findChild(QComboBox, "language_combo")
    assert lang_combo is not None, "Widget 'language_combo' wurde im Dialog nicht gefunden."

    # Prüfen, ob der Wert aus temp_app_config ("de") korrekt geladen wurde
    assert lang_combo.currentData() == "de" or lang_combo.currentText() == "Deutsch"

def test_config_dialog_saves_values(qtbot, temp_app_config, monkeypatch):
    """
    Prüft, ob Änderungen im Dialog korrekt in die Datei zurückgeschrieben werden.
    """
    # Verhindere, dass QMessageBox.information im Testlauf blockiert
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)

    dialog = AppConfigDialog(config_path=temp_app_config)
    qtbot.addWidget(dialog)

    # Beispiel: Schriftgröße ändern (QSpinBox namens 'font_size_spin')
    font_spin = dialog.findChild(QSpinBox, "font_size_spin")
    assert font_spin is not None

    font_spin.setValue(20) # Wert auf 20 ändern
    dialog.save_config() # Methode zum Speichern aufrufen

    # Config neu laden und prüfen
    new_config = ConfigManager(temp_app_config).load()
    assert new_config["editor_font_size"] == 20


def test_create_project_dialog_creates_clean_project(qtbot, tmp_path):
    from gui.dialogs.create_project_dialog import CreateProjectDialog

    app_root = tmp_path / "app"
    app_root.mkdir()
    (app_root / "themes").mkdir()

    parent_dir = tmp_path / "projects"
    parent_dir.mkdir()

    dialog = CreateProjectDialog(app_root=str(app_root))
    qtbot.addWidget(dialog)

    dialog.name_input.setText("My Awesome Blog")
    dialog.path_input.setText(str(parent_dir))

    # Path preview updates
    expected_path = parent_dir / "My_Awesome_Blog"
    assert "My_Awesome_Blog" in dialog.path_preview_lbl.text()
    assert dialog.create_btn.isEnabled()

    # Create project
    dialog.create_project()

    assert dialog.created_project_path == str(expected_path)
    assert expected_path.is_dir()
    assert (expected_path / "config.yaml").is_file()
    assert (expected_path / "content" / "index.md").is_file()
    assert (expected_path / "site_output").is_dir()
    assert (expected_path / "assets").is_dir()

    # Verify config content
    project_cfg = ConfigManager(str(expected_path / "config.yaml")).load()
    assert project_cfg["site_name"] == "My Awesome Blog"
    assert project_cfg["backup_on_render"] is True
    assert project_cfg["backup_rotation"] == 10


def test_create_project_dialog_prevents_duplicate_folder(qtbot, tmp_path):
    from gui.dialogs.create_project_dialog import CreateProjectDialog

    app_root = tmp_path / "app"
    app_root.mkdir()
    (app_root / "themes").mkdir()

    parent_dir = tmp_path / "projects"
    parent_dir.mkdir()

    existing_dir = parent_dir / "Existing_Project"
    existing_dir.mkdir()

    dialog = CreateProjectDialog(app_root=str(app_root))
    qtbot.addWidget(dialog)

    dialog.name_input.setText("Existing Project")
    dialog.path_input.setText(str(parent_dir))

    # Should detect collision and disable create button
    assert dialog.create_btn.isEnabled() is False
    assert "Warning" in dialog.path_preview_lbl.text() or "Warnung" in dialog.path_preview_lbl.text()


def test_template_library_dialog_loads_and_selects_theme(qtbot, tmp_path):
    from gui.dialogs.template_library_dialog import TemplateLibraryDialog

    app_root = tmp_path / "app"
    app_root.mkdir()
    themes_dir = app_root / "themes"
    themes_dir.mkdir()

    # Create dummy theme
    sample_theme = themes_dir / "sample-theme"
    sample_theme.mkdir()
    (sample_theme / "theme.yaml").write_text(
        "title: 'Sample Theme'\ncategory: 'Blog'\ndescription: 'Nice blog'\n",
        encoding="utf-8"
    )

    dialog = TemplateLibraryDialog(app_root=str(app_root), selected_theme="none")
    qtbot.addWidget(dialog)

    # Has at least "none" and "sample-theme"
    assert len(dialog.themes) >= 2
    assert "sample-theme" in dialog.card_widgets

    # Selection updates
    dialog.select_theme("sample-theme")
    assert dialog.selected_theme == "sample-theme"
    assert "Sample Theme" in dialog.detail_title.text()

    # Filtering works
    dialog.search_input.setText("Sample")
    assert dialog.card_widgets["sample-theme"].isHidden() is False
    assert dialog.card_widgets["none"].isHidden() is True



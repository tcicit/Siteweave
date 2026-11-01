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

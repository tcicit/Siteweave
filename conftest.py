import sys
import os
import yaml
import pytest

# Fügt das Stammverzeichnis des Projekts zum Python-Pfad hinzu.
# Dies stellt sicher, dass pytest Module wie 'manage_translations'
# und Pakete wie 'gui' finden kann.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture
def temp_app_config(tmp_path):
    """
    Erstellt eine temporäre app_config.yaml für Tests.
    Gibt den absoluten Pfad zur Datei zurück.
    """
    config_data = {
        "autosave_interval": 60,
        "autosave_on_close": True,
        "language": "de",
        "recent_projects": [],
        "editor_font_family": "Monospace",
        "editor_font_size": 12,
        "toolbar_layout": ["save_act", "separator", "render_act"]
    }
    
    config_file = tmp_path / "app_config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)
    
    return str(config_file)
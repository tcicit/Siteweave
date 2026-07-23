import os
import sys
import yaml
import logging

'''
This ConfigManager provides a central interface for loading, saving and managing YAML configurations.
It supports merging default values, error handling and logging.
Example:
config_manager = ConfigManager("app_config.yaml")
app_config = config_manager.load(defaults={"recent_projects": [], "auto_open_last_project": True})
config_manager.set("language", "de")
config_manager.save()
'''

logger = logging.getLogger("config_manager")

DEFAULT_APP_CONFIG = {
    "language": "en",
    "auto_open_last_project": True,
    "recent_projects": [],
    "external_editors": [
        {
            "name": "GIMP",
            "command": ["flatpak", "run", "org.gimp.GIMP"],
            "icon": "gimp",
            "extensions": [".jpg", ".jpeg", ".png", ".webp", ".xcf", ".gif"]
        },
        {
            "name": "Inkscape",
            "command": ["flatpak", "run", "org.inkscape.Inkscape"],
            "icon": "inkscape",
            "extensions": [".svg"]
        }
    ]
}

class ConfigManager:
    """
    Central manager for loading, saving and managing YAML configurations.
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    @staticmethod
    def get_app_config_path():
        """Returns the absolute path to the global app_config.yaml."""
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "app_config.yaml")

    def load(self, defaults=None):
        """
        Load configuration from the file.
        If the file does not exist, use the provided defaults.
        """
        effective_defaults = DEFAULT_APP_CONFIG.copy()
        if defaults:
            effective_defaults.update(defaults)

        if not os.path.exists(self.config_path):
            self.config = effective_defaults
            return self.config

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration '{self.config_path}': {e}")
            self.config = {}

        self._merge_defaults(self.config, effective_defaults)
            
        return self.config

    def save(self):
        """Save the current configuration to the YAML file."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration '{self.config_path}': {e}")
            raise e

    def get(self, key, default=None):
        """Return the value for a key."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a value (does not save to disk)."""
        self.config[key] = value

    def update(self, data):
        """Update the configuration with a dictionary."""
        if isinstance(data, dict):
            self.config.update(data)

    def _merge_defaults(self, config, defaults):
        """Recursively merge defaults into the configuration."""
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                self._merge_defaults(config[key], value)

    def save_ui_state(self, prefix, geometry=None, state=None):
        """Speichert PyQt6 Geometrie und Status (Splitter) zentral als Hex-Strings."""
        updates = {}
        if geometry:
            updates[f"{prefix}_geometry"] = geometry.toHex().data().decode()
        if state:
            updates[f"{prefix}_splitter"] = state.toHex().data().decode()
        
        self.load()
        self.update(updates)
        self.save()

    def load_ui_state(self, prefix):
        """Lädt UI-Zustände und gibt sie als QByteArray-Tupel zurück."""
        from PyQt6.QtCore import QByteArray
        self.load()
        geo_hex = self.get(f"{prefix}_geometry")
        state_hex = self.get(f"{prefix}_splitter")

        def decode_hex(hex_val):
            """Sicherer Konverter von Hex-String zu QByteArray."""
            if not isinstance(hex_val, str) or not hex_val:
                return None
            try:
                ba = QByteArray.fromHex(hex_val.encode())
                return ba if not ba.isEmpty() else None
            except Exception:
                return None

        return decode_hex(geo_hex), decode_hex(state_hex)

    def apply_ui_state(self, widget, prefix, default_size=None):
        """Lädt UI-Zustände und wendet die Geometrie direkt auf das Widget an."""
        geo, state = self.load_ui_state(prefix)
        if geo:
            widget.restoreGeometry(geo)
        elif default_size:
            widget.resize(default_size[0], default_size[1])
            
        if state and hasattr(widget, 'restoreState'):
            # Automatisch für QMainWindow (Toolbars) oder QSplitter
            widget.restoreState(state)
            
        return state

    def apply_splitter_states(self, prefix, splitters):
        """Wendet gespeicherte Zustände auf eine Liste von Splittern an."""
        for name, splitter in splitters.items():
            # Rekonstruiert den Präfix so, wie er in MainWindow.closeEvent gespeichert wird
            # z.B. prefix='main_window', name='main' -> 'main_window_main_splitter'
            full_prefix = f"{prefix}_{name}_splitter"
            _, state = self.load_ui_state(full_prefix)
            if state:
                splitter.restoreState(state)
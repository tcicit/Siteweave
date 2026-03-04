import os
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

class ConfigManager:
    """
    Central manager for loading, saving and managing YAML configurations.
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load(self, defaults=None):
        """
        Load configuration from the file.
        If the file does not exist, use the provided defaults.
        """
        if not os.path.exists(self.config_path):
            # No file found, use defaults
            self.config = defaults or {}
            return self.config

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration '{self.config_path}': {e}")
            self.config = {}

        if defaults:
            self._merge_defaults(self.config, defaults)
            
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
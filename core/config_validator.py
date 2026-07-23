import os
import logging
from core.i18n import _

logger = logging.getLogger("config_validator")

class ConfigValidator:
    """
    Validiert die Projektkonfiguration gegen ein definiertes Schema.
    Anstatt blind zu reparieren, werden klare Fehlermeldungen erzeugt.
    """
    
    # Definition des Schemas: Key -> (Erwarteter Typ, Pflichtfeld)
    SCHEMA = {
        "site_name": (str, True),
        "site_url": (str, False),
        "content_directory": (str, False),
        "assets_directory": (str, False),
        "site_output_directory": (str, False),
        "template_directory": (str, False),
        "plugin_directory": (str, False),
        "backup_directory": (str, False),
        "header_links": (list, False),
        "footer_links": (list, False),
        "contact": (dict, False),
        "social": (dict, False),
        "markdown_extensions": (list, False),
        "backup_on_render": (bool, False),
        "backup_rotation": (int, False),
    }

    @staticmethod
    def validate(config, project_root=None):
        """
        Validiert das config-Dictionary.
        Gibt eine Liste von Fehlermeldungen zurück. Wenn die Liste leer ist, ist alles ok.
        """
        errors = []

        for key, (expected_type, required) in ConfigValidator.SCHEMA.items():
            if key not in config:
                if required:
                    errors.append(_("Required field is missing: '{key}'").format(key=key))
                continue

            value = config[key]
            
            # Da YAML-Parser bei leeren Feldern None zurückgeben können:
            if value is None:
                if required:
                    errors.append(_("Field '{key}' cannot be empty.").format(key=key))
                continue

            # Typ-Prüfung
            if not isinstance(value, expected_type):
                errors.append(_("Invalid type for '{key}': Expected {expected}, got {got}.").format(
                    key=key, expected=expected_type.__name__, got=type(value).__name__))
                continue

            # Prüfung der Verzeichnis-Existenz (falls project_root vorhanden)
            directory_keys = ["content_directory", "template_directory", "assets_directory", "plugin_directory"]
            if project_root and key in directory_keys and isinstance(value, str):
                full_path = os.path.join(project_root, value)
                if not os.path.isdir(full_path):
                    errors.append(_("Directory not found: '{path}' (configured under '{key}')").format(
                        path=value, key=key))
                continue

            # Spezifische Prüfungen für Listen (z.B. Links)
            if expected_type == list and value:
                if key in ["header_links", "footer_links"]:
                    for i, item in enumerate(value):
                        if not isinstance(item, dict):
                            errors.append(_("Entry {index} in '{key}' must be an object (Dictionary).").format(
                                index=i+1, key=key))
                elif key == "markdown_extensions":
                    for i, item in enumerate(value):
                        if not isinstance(item, str):
                            errors.append(_("Entry {index} in '{key}' must be a string.").format(
                                index=i+1, key=key))

        return errors
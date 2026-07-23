import os
import importlib.util
import logging
from core.i18n import _

class PluginManager:
    """
    Zentraler Manager für das Scannen, Laden und Ausführen von Siteweave-Plugins.
    Unterstützt sowohl globale (App-weite) als auch projektspezifische Plugins.
    Projektspezifische Plugins überschreiben globale Plugins mit demselben Namen.
    """
    def __init__(self, app_root, project_root, logger=None):
        self.app_root = app_root
        self.project_root = project_root
        self.logger = logger or logging.getLogger("plugin_manager")
        self.plugins = {}

        self.global_plugin_directory = os.path.join(self.app_root, "plugins")
        self.project_plugin_directory = os.path.join(self.project_root, "plugins")

    def load_plugins(self):
        """
        Durchsucht die Plugin-Verzeichnisse und lädt die Module dynamisch.
        Gibt ein Dictionary {name: module} zurück.
        """
        self.plugins = {}
        
        # Reihenfolge wichtig für Overrides: Global zuerst, dann Projekt
        dirs_to_scan = []
        if os.path.isdir(self.global_plugin_directory):
            dirs_to_scan.append((self.global_plugin_directory, "Global"))
        if os.path.isdir(self.project_plugin_directory):
            dirs_to_scan.append((self.project_plugin_directory, "Project"))

        if not dirs_to_scan:
            self.logger.info(_("Keine Plugin-Verzeichnisse gefunden."))
            return self.plugins

        self.logger.info(_("\nLade Plugins..."))

        for directory, source_type in dirs_to_scan:
            for item in sorted(os.listdir(directory)):
                path = os.path.join(directory, item)
                plugin_name = None
                module_path = None

                # Fall 1: Plugin ist eine einzelne .py-Datei
                if os.path.isfile(path) and item.endswith('.py') and not item.startswith('__'):
                    plugin_name = os.path.splitext(item)[0]
                    module_path = path
                
                # Fall 2: Plugin ist ein Ordner (Paket)
                elif os.path.isdir(path) and not item.startswith('__') and not item.startswith('.'):
                    init_file = os.path.join(path, "__init__.py")
                    named_file = os.path.join(path, f"{item}.py")
                    
                    if os.path.isfile(named_file):
                        plugin_name = item
                        module_path = named_file
                    elif os.path.isfile(init_file):
                        plugin_name = item
                        module_path = init_file
                
                if plugin_name and module_path:
                    try:
                        spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", module_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'handle'):
                            # Projektspezifische Plugins überschreiben globale durch dieselbe Key-Zuweisung
                            self.plugins[plugin_name.lower()] = module
                            self.logger.info(_("  - Plugin '{name}' erfolgreich geladen ({source}).").format(
                                name=plugin_name, source=source_type))
                        else:
                            self.logger.warning(_("Warnung: Plugin '{name}' hat keine 'handle'-Funktion.").format(name=plugin_name))
                    except Exception as e:
                        self.logger.error(_("Error during plugin loading '{name}': {e}").format(name=plugin_name, e=e))
        
        return self.plugins

    def execute_handle(self, plugin_name, content, args, context, env):
        """
        Führt die handle-Funktion eines Plugins sicher aus.
        """
        module = self.plugins.get(plugin_name.lower())
        if module and hasattr(module, 'handle'):
            try:
                return module.handle(content, args, context, env)
            except Exception as e:
                self.logger.error(_("Error during plugin execution '{name}': {e}").format(name=plugin_name, e=e))
        return None

    def run_page_generation(self, **kwargs):
        """
        Führt den generate_pages-Hook für alle Plugins aus, die ihn implementieren.
        """
        for name, module in self.plugins.items():
            if hasattr(module, 'generate_pages'):
                try:
                    module.generate_pages(**kwargs)
                except Exception as e:
                    self.logger.error(_("Error during page generation caused by a plugin '{name}': {e}").format(name=name, e=e))
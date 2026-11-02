import os
import sys

if __name__ == "__main__":
    print("Please start the application using 'main.py' in the project root.")
    print("Please start the application using 'run_editor.py' in the project root.")
    sys.exit(1)

from PyQt6.QtCore import QFileSystemWatcher, QSettings, QTimer, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
)

from core import APP_NAME, APP_VERSION
from core.config_manager import ConfigManager
from core.i18n import _
from .workers import WorkerThread
from .action_manager import ActionManager
from .dashboard_features import DashboardFeaturesMixin
from .document_manager import DocumentManager
from .editor_features import EditorFeaturesMixin
from .project_features import ProjectFeaturesMixin
from .theme_manager import ThemeManager
from .window_dialogs import ProgressHelper, WorkerResultDialog, WorkerResultListDialog
from .window_setup import WindowSetupMixin


class MainWindow(WindowSetupMixin, DashboardFeaturesMixin, EditorFeaturesMixin, ProjectFeaturesMixin, QMainWindow):

    def __init__(self, project_path=None):
        """
        Docstring for __init__

        :param self: instance
        :param project_path: optional project root path
        :return: None
        :rtype: None
        """
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setObjectName("MainWindow")
        self.resize(1400, 900)

        # Initialize paths
        self.app_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.app_version = APP_VERSION
        if project_path:
            self.project_root = project_path
        else:
            self.project_root = self.app_root
            
        self.project_name = os.path.basename(self.project_root)
            
        self.content_dir = os.path.join(self.project_root, "content")
        self.assets_dir = os.path.join(self.project_root, "assets")
        self.current_file_path = None
        self.workers_dir = os.path.join(self.app_root, "workers")
        self.frontmatter_modified = False
        
        # Set application icon
        icon_path = os.path.join(self.app_root, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setWindowTitle(f"{self.project_name} - {APP_NAME}")

        self.default_palette = QApplication.instance().palette()

        # Initialize settings (stores persistent "last_file")
        self.settings = QSettings("TCI", "StaticSiteEditor")

        # File system watcher for external changes
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self.on_current_file_changed_externally)
        self._ignored_file_changes = set()
        self._ignore_timer = QTimer(self)
        self._ignore_timer.setSingleShot(True)
        self._ignore_timer.setInterval(1000) # Ignore changes for 1 second after save
        self._ignore_timer.timeout.connect(self._reset_ignore_flag)
        self.document_manager = DocumentManager(self)

        # Load global app configuration (view settings)
        self.app_config_path = os.path.join(self.app_root, "app_config.yaml")
        self.app_config_manager = ConfigManager(self.app_config_path)
        self.app_config = self.load_app_config()
        
        self.spell_checker = None
        # Initialize localization
        self.init_localization()
        
        # Load project configuration (for paths etc.)
        self.project_config_manager = ConfigManager(os.path.join(self.project_root, "config.yaml"))
        self.project_config = self.load_project_config()

        # Initialize status bar (before UI to avoid early update errors)
        self.status_label = QLabel(_("Ready"))
        self.statusBar().addWidget(self.status_label)
        
        # Cursor position label (right side of the status bar)
        self.cursor_label = QLabel(_("Ln 1, Col 1"))
        self.statusBar().addPermanentWidget(self.cursor_label)

        # Icon Mapping für Theme-Support
        # Mapping: Action-Name -> Icon-Dateiname (ohne Erweiterung)
        # Wird in init_toolbar verwendet

        self.default_action_icons = {
            'new_act': 'add',
            'switch_project_act': 'start',
            'save_act': 'save',
            'insert_img_act': 'image',
            'insert_img_plugin_act': 'image',
            'insert_file_act': 'link',
            'emoji_act': 'emoji',
            'gallery_act': 'gallery',
            'exit_act': 'exit',
            'undo_act': 'undo',
            'redo_act': 'redo',
            'select_all_act': 'select_all',
            'search_act': 'search',
            'replace_act': 'replace',
            'toggle_preview_act': 'preview',
            'manage_media_act': 'image',
            'dark_mode_act': 'dark_mode',
            'refresh_act': 'refresh',
            'dashboard_act': 'home',
            'config_act': 'app_settings',
            'project_config_act': 'settings',
            'manage_snippets_act': 'snippets',
            'render_act': 'render',
            'open_browser_act': 'browser',
            'about_act': 'about',
            'bold_act': 'bold',
            'italic_act': 'italic',
            'code_act': 'code',
            'h1_act': 'h1',
            'h2_act': 'h2',
            'h3_act': 'h3',
            'ul_act': 'list_ul',
            'ol_act': 'list_ol',
            'table_act': 'table'
        }

        # Lade Icons aus Config oder nutze Defaults
        self.action_icons = self.app_config.get('action_icons', {})
        # Merge defaults for missing keys
        for k, v in self.default_action_icons.items():
            if k not in self.action_icons:
                self.action_icons[k] = v
        self.app_config['action_icons'] = self.action_icons

        self.sidebar_panels = {}

        # UI Komponenten initialisieren
        self.init_ui()

        # Schriftart und -größe anwenden
        font_size = self.app_config.get('editor_font_size', 12)
        font_family = self.app_config.get('editor_font_family', 'Monospace')
        
        font = self.editor.font()
        font.setFamily(font_family)
        self.editor.setFont(font)
        self.editor.set_font_size(font_size)

        # Preview Font anwenden
        self.update_preview_font()

        self.action_manager = ActionManager(self)
        self.theme_manager = ThemeManager(self)
        self.create_actions()
        self.init_toolbar()
        self.init_menu()
        self.init_spellchecker()
        
        # UI-Zustand (Geometrie und Toolbars/Docks) aus app_config.yaml laden
        self.app_config_manager.apply_ui_state(self, "main_window", default_size=(1400, 900))
        
        # Theme anwenden (nach UI-Initialisierung, da Editor/Preview existieren müssen)
        dark_mode = self.app_config.get('view_dark_mode', False)
        self.apply_theme(dark_mode)

        # Zuletzt geöffnete Datei beim Start laden
        self.load_last_file()

        # Autosave Timer (Konfigurierbar, Standard: 300 Sekunden = 5 Minuten)
        autosave_interval = self.app_config.get('autosave_interval', 300)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave_file)
        if autosave_interval > 0:
            self.autosave_timer.start(autosave_interval * 1000)

        # Tags im Hintergrund sammeln
        tag_worker_path = os.path.join(self.workers_dir, "tag_collector.py")
        self.tag_worker = WorkerThread(tag_worker_path, {'content_dir': self.content_dir, 'project_root': self.project_root})
        self.tag_worker.finished.connect(self.frontmatter_panel.set_available_tags)
        self.tag_worker.start()

    def closeEvent(self, event):
        manager = self._document_manager()
        if not manager.confirm_close():
            event.ignore()
            return

        try:
            manager.save_session()
        except Exception as error:
            QMessageBox.critical(
                self, _("Error"),
                _("Could not save the open-document session:\n{error}").format(error=error),
            )
            event.ignore()
            return

        self.app_config_manager.save_ui_state("main_window", self.saveGeometry(), self.saveState())
        self.app_config_manager.save_ui_state("main_window_main_splitter", state=self.splitter.saveState())
        self.app_config_manager.save_ui_state("main_window_left_splitter", state=self.left_splitter.saveState())
        self.app_config_manager.save_ui_state("main_window_editor_area_splitter", state=self.editor_area.saveState())

        if hasattr(self, 'dashboard_worker') and self.dashboard_worker.isRunning():
            self.dashboard_worker.quit()
            self.dashboard_worker.wait()

        # GUI-Einstellungen in globale App-Config speichern
        self.app_config['view_show_preview'] = self.preview.isVisible()
        self.app_config['view_show_toolbar'] = self.toolbar.isVisible()
        self.app_config['view_show_line_numbers'] = self.toggle_line_numbers_act.isChecked()
        self.app_config['view_dark_mode'] = self.dark_mode_act.isChecked()
        
        self.save_app_config()
        event.accept()

    def create_actions(self):
        self.action_manager.create_actions()

    def init_menu(self):
        self.action_manager.init_menu()

    def populate_tools_menu(self, menu, category="project"):
        return self.action_manager.populate_tools_menu(menu, category)

    def populate_help_menu(self, menu):
        return self.action_manager.populate_help_menu(menu)

    def refresh_help_menu(self):
        return self.action_manager.refresh_help_menu()

    def init_toolbar(self):
        self.action_manager.init_toolbar()

    def _document_manager(self):
        manager = self.__dict__.get("document_manager")
        if manager is None:
            manager = DocumentManager(self)
            self.document_manager = manager
        return manager

    def _get_open_editors(self):
        return self._document_manager().get_open_editors()

    def _save_all_dirty_editors(self):
        return self._document_manager().save_all_dirty_editors()

    def _reset_ignore_flag(self):
        return self._document_manager().reset_ignored_file_changes()

    def load_last_file(self):
        return self._document_manager().load_last_file()

    def _is_project_path(self, path):
        return self._document_manager().is_project_path(path)

    def check_unsaved_changes(self):
        return self._document_manager().confirm_unsaved_changes()

    def load_file(self, file_path):
        return self._document_manager().load_file(file_path)

    def save_file(self, editor=None):
        return self._document_manager().save_file(editor)

    def on_current_file_changed_externally(self, path):
        return self._document_manager().handle_external_change(path)

    def on_file_path_renamed(self, old_path, new_path):
        return self._document_manager().handle_path_renamed(old_path, new_path)

    def _reload_editor(self, editor, file_path):
        return self._document_manager().reload_editor(editor, file_path)

    def autosave_file(self):
        return self._document_manager().autosave()

    def toggle_dark_mode(self, checked):
        return self.apply_theme(checked)

    def apply_theme(self, dark_mode):
        manager = self.__dict__.get("theme_manager")
        if manager is None:
            manager = ThemeManager(self)
            self.theme_manager = manager
        return manager.apply_theme(dark_mode)

    def update_icons(self, dark_mode):
        manager = self.__dict__.get("theme_manager")
        if manager is None:
            manager = ThemeManager(self)
            self.theme_manager = manager
        return manager.update_icons(dark_mode)

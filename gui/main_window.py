import os
import sys
import shutil
import datetime

'''
Docstring for main_window
Main application window.
Contains the file explorer, editor, preview and various panels.
Manages app and project configuration, actions, menus and toolbars.
Allows loading, editing and saving Markdown files with frontmatter.
Supports themes, localization and running worker scripts.
The main class is `MainWindow`, which inherits from `QMainWindow`.

'''

if __name__ == "__main__":
    print("Please start the application using 'run_editor.py' in the project root.")
    sys.exit(1)


import frontmatter
import importlib.util
import ast
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSplitter, QListWidget, QListWidgetItem, QAbstractItemView,
                             QToolBar, QMessageBox, QLabel, QFileDialog, QApplication, QFrame, QDockWidget, QDialog,
                             QInputDialog, QPlainTextEdit, QDialogButtonBox, QSizePolicy, QLineEdit, QProgressDialog)
from PyQt6.QtGui import QAction, QKeySequence, QTextCursor, QIcon, QPalette, QColor, QPainter, QPixmap, QDesktopServices, QFontDatabase, QFont
from PyQt6.QtCore import Qt, QSettings, QTimer, QUrl, pyqtSignal, QObject

from .file_tree import FileTree
from .editor_widget import EditorWidget
from .preview_widget import PreviewWidget
from .outline_panel import OutlinePanel
from .snippet_panel import SnippetPanel
from .frontmatter_panel import FrontmatterPanel
from .dialogs.new_post_dialog import NewPostDialog
from .log_viewer_panel import LogViewerPanel
from .dialogs.search_dialog import SearchDialog
from .dialogs.app_config_dialog import AppConfigDialog
from .dialogs.project_config_dialog import ProjectConfigDialog
from .dialogs.snippet_manager_dialog import SnippetManagerDialog
from .dialogs.dictionary_manager_dialog import DictionaryManagerDialog
from .dialogs.emoji_picker import EmojiPicker
from .workers import WorkerThread
from .dialogs.help_viewer import HelpViewer
from .dialogs.color_settings_dialog import ColorSettingsDialog
from .theme import apply_dark_theme, apply_light_theme
from .dialogs.project_launcher import ProjectLauncher
from .spellchecker import SpellChecker
from .dialogs.create_project_dialog import CreateProjectDialog
from .project_panel import ProjectPanel
from core.config_manager import ConfigManager

from core import APP_NAME, APP_VERSION, SETTINGS_ORG, SETTINGS_APP

from .dialogs.bulk_edit_dialog import BulkEditDialog

from core.i18n import _

class ProgressHelper(QObject):
    progress = pyqtSignal(int, int, str)

class WorkerResultDialog(QDialog):
    """
    Docstring for WorkerResultDialog
    Displays the results of a worker in a searchable text field.

    """
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 500)
        layout = QVBoxLayout(self)
        
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlainText(text)
        self.text_edit.setReadOnly(True)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)

class WorkerResultListDialog(QDialog):
    """
    Docstring for WorkerResultListDialog
    Shows a list of results from a worker. Double-clicking an entry opens the file at the corresponding location.

    """
    def __init__(self, title, data, main_window):
        super().__init__(main_window)
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.main_window = main_window
        layout = QVBoxLayout(self)
        
        info_label = QLabel(_("Double-click on an entry opens the file at the corresponding location."))
        layout.addWidget(info_label)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        
        for entry in data:
            text = entry.get('display_text', _('Unknown Error'))
            file_path = entry.get('file_path')
            line = entry.get('line', 1)
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setData(Qt.ItemDataRole.UserRole + 1, line)
            self.list_widget.addItem(item)
            
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_item_double_clicked(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        line = item.data(Qt.ItemDataRole.UserRole + 1)
        
        if file_path and os.path.exists(file_path):
            self.main_window.load_file(file_path)
            if line:
                self.main_window.scroll_to_line(line)
            self.accept() # Dialog schließen, damit man editieren kann

class MainWindow(QMainWindow):



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

        # Restore window geometry and state (via QSettings)
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

        if self.settings.value("window_state"):
            self.restoreState(self.settings.value("window_state"))

        # App config overrides QSettings if present (for window geometry)
        win_w = self.app_config.get('window_width')
        win_h = self.app_config.get('window_height')
        win_x = self.app_config.get('window_x')
        win_y = self.app_config.get('window_y')
        if win_w and win_h:
            self.resize(int(win_w), int(win_h))
        if win_x is not None and win_y is not None:
            self.move(int(win_x), int(win_y))

        # Restore splitter sizes (applied in init_ui)
        self.splitter_state = self.settings.value("splitter_sizes")
        self.left_splitter_state = self.settings.value("left_splitter_sizes")

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
            'dark_mode_act': 'dark_mode',
            'config_act': 'settings',
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

        self.editor.cursorPositionChanged.connect(self.update_cursor_label)

        self.create_actions()
        self.init_toolbar()
        self.init_menu()
        self.init_spellchecker()
        
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

    def init_localization(self):
        lang = self.app_config.get('language', 'en')
        locales_dir = os.path.join(self.app_root, "locales")
        try:
            from core.i18n import init as i18n_init
            i18n_init(app_root=self.app_root, locale=lang)
        except Exception as e:
            print(f"Localization init failed for {lang}, using default. ({e})")

    def init_spellchecker(self):
        """Initialisiert oder aktualisiert den Spellchecker basierend auf der Projektkonfiguration."""
        # Versuche erst die spezifische Spellcheck-Sprache, dann Fallback auf Site-Language
        dict_lang = self.project_config.get('spellcheck_language')
        
        if not dict_lang:
            lang_code = self.project_config.get('language', 'en')
            # Mapping von einfachen Codes zu pyenchant-spezifischen (z.B. de -> de_DE)
            lang_map = {
                'de': 'de_DE',
                'en': 'en_US',
                'fr': 'fr_FR',
                'es': 'es_ES'
            }
            dict_lang = lang_map.get(lang_code, 'en_US')
            
        user_dict_path = os.path.join(self.project_root, ".user_dictionary.txt")

        success = False
        if self.spell_checker is None:
            self.spell_checker = SpellChecker(dict_lang, user_dict_path)
            # Prüfe, ob die initiale Erstellung erfolgreich war
            success = self.spell_checker.dictionary is not None
        else:
            success = self.spell_checker.set_language(dict_lang, user_dict_path)

        if not success:
            QMessageBox.warning(self, _("Spellchecker Warning"),
                                _("The dictionary for the language '{lang}' could not be found.\n\n"
                                  "Please install the corresponding Hunspell dictionary for your system "
                                  "(e.g., 'hunspell-de-de' on Debian/Ubuntu, or 'hunspell-de' on Arch/Fedora).").format(lang=dict_lang))
        
        self.editor.spell_checker = self.spell_checker
        if hasattr(self.editor, 'highlighter'):
            self.editor.highlighter.spell_checker = self.spell_checker
        self.editor.highlighter.rehighlight()

    def init_ui(self):
        """
        Docstring for init_ui
        
        :param self: instance
        """ 
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter for 3 columns: Tree | Editor | Preview
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left container (projects + file tree) as vertical splitter
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)

        # Project Panel
        self.project_panel = ProjectPanel(self.project_root, self.app_root)
        self.project_panel.setObjectName("ProjectPanel")
        self.project_panel.project_switched.connect(self.switch_to_project_path)
        self.left_splitter.addWidget(self.project_panel)
        self.sidebar_panels["ProjectPanel"] = self.project_panel

        # 1. File tree
        self.file_tree = FileTree(self.content_dir)
        self.file_tree.clicked.connect(self.on_tree_clicked)
        self.file_tree.create_file_requested.connect(self.create_new_post)
        
        # Enable drag & drop
        self.file_tree.setDragEnabled(True)
        self.file_tree.setAcceptDrops(True)
        self.file_tree.setDropIndicatorShown(True)
        self.file_tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.file_tree.fs_model.setReadOnly(False)
        
        self.left_splitter.addWidget(self.file_tree)
        self.splitter.addWidget(self.left_splitter)
        
        # 2. Editor
        self.editor = EditorWidget(spell_checker=self.spell_checker)
        
        show_line_numbers = self.app_config.get('view_show_line_numbers', True)
        self.editor.set_line_numbers_visible(show_line_numbers)
        
        self.splitter.addWidget(self.editor)

        # Spellchecker initial aktivieren/deaktivieren
        self.editor.set_spellchecker_enabled(self.project_config.get('spellcheck_enabled', True))
        
        # 3. Preview
        self.preview = PreviewWidget(self.project_root, self.app_root)
        show_preview = self.app_config.get('view_show_preview', True)
        self.preview.setVisible(show_preview)
        self.splitter.addWidget(self.preview)

        # Scroll synchronization: Editor -> Preview
        self.editor.verticalScrollBar().valueChanged.connect(self.sync_scroll_and_line_numbers)
        self.preview.loadFinished.connect(self.restore_scroll_position)

        # 4. Panels (docks)
        self.create_dock_panels()
        
        # Adjust column ratios (Tree, Editor, Preview, Outline)
        if self.splitter_state:
            self.splitter.restoreState(self.splitter_state)
        else:
            self.splitter.setSizes([200, 500, 500])
        
        if self.left_splitter_state:
            self.left_splitter.restoreState(self.left_splitter_state)

        main_layout.addWidget(self.splitter)

        # Signale verbinden, nachdem alle UI-Elemente (Editor, Preview, Outline) erstellt wurden
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.fontSizeChanged.connect(self.update_font_size_config)

    def create_dock_panels(self):
        # Frontmatter
        self.frontmatter_panel = FrontmatterPanel()
        self.frontmatter_panel.setObjectName("FrontmatterPanel")
        self.frontmatter_panel.dataChanged.connect(self.on_frontmatter_changed)
        self.update_frontmatter_layouts()
        self.add_dock_panel(self.frontmatter_panel, _("Frontmatter"), "FrontmatterDock")
        self.sidebar_panels["FrontmatterPanel"] = self.frontmatter_panel

        # Outline
        self.outline = OutlinePanel()
        self.outline.setObjectName("OutlinePanel")
        self.outline.heading_clicked.connect(self.scroll_to_line)
        self.add_dock_panel(self.outline, _("Outline"), "OutlineDock")
        self.sidebar_panels["OutlinePanel"] = self.outline

        # Snippets
        snippets_dir = os.path.join(self.app_root, "snippets")
        self.snippets = SnippetPanel(snippets_dir)
        self.snippets.setObjectName("SnippetPanel")
        self.snippets.insert_requested.connect(self.insert_snippet)
        self.add_dock_panel(self.snippets, _("Snippets"), "SnippetDock")
        self.sidebar_panels["SnippetPanel"] = self.snippets

        # Logs (docked at bottom)
        log_file = os.path.join(self.project_root, "worker.log")
        self.log_viewer = LogViewerPanel(log_file)
        self.log_viewer.setObjectName("LogViewerPanel")
        self.add_dock_panel(self.log_viewer, _("Logs"), "LogViewerDock", area=Qt.DockWidgetArea.BottomDockWidgetArea)
        self.sidebar_panels["LogViewerPanel"] = self.log_viewer

    def update_frontmatter_layouts(self):
        template_dirs = [os.path.join(self.project_root, "templates")]
        
        theme_name = self.project_config.get("site_theme")
        if theme_name and theme_name != "default-blog":
            themes_dir = self.project_config.get("themes_directory", "themes")
            theme_templates = os.path.join(self.project_root, themes_dir, theme_name, "templates")
            template_dirs.append(theme_templates)
            
        if hasattr(self, 'frontmatter_panel'):
            self.frontmatter_panel.populate_layouts(template_dirs)

    def add_dock_panel(self, widget, title, object_name, area=Qt.DockWidgetArea.RightDockWidgetArea):
        dock = QDockWidget(title, self)
        dock.setObjectName(object_name)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)

    def get_icon(self, name):
        path = os.path.join(self.app_root, "assets", name)
        if os.path.exists(path):
            return QIcon(path)
        return QIcon()

    def create_actions(self):
        # File Actions
        self.new_act = QAction(_("New Post"), self)
        self.new_act.setShortcut("Ctrl+N")
        self.new_act.triggered.connect(self.create_new_post)

        self.switch_project_act = QAction(_("Switch Project"), self)
        self.switch_project_act.triggered.connect(self.switch_project)

        self.create_project_act = QAction(_("Create New Project"), self)
        self.create_project_act.triggered.connect(self.create_new_project_dialog)

        self.project_settings_act = QAction(_("Project Settings"), self)
        self.project_settings_act.triggered.connect(self.show_project_config_dialog)

        # Bulk Edit Action
        self.bulk_edit_frontmatter_act = QAction(_("Bulk Edit Frontmatter"), self)
        self.bulk_edit_frontmatter_act.triggered.connect(self.show_bulk_edit_dialog)        

        self.manage_dictionary_act = QAction(_("Manage Dictionary..."), self)
        self.manage_dictionary_act.triggered.connect(self.show_dictionary_manager)

        self.save_act = QAction(_("Save"), self)
        self.save_act.setShortcut("Ctrl+S")
        self.save_act.triggered.connect(self.save_file)

        self.insert_img_act = QAction(_("Insert Image"), self)
        self.insert_img_act.setShortcut("Ctrl+Shift+I") # Changed because Ctrl+I is commonly used for Italic
        self.insert_img_act.triggered.connect(self.insert_image_dialog)

        self.insert_file_act = QAction(_("Link File"), self)
        self.insert_file_act.setToolTip(_("Insert link to a file"))
        self.insert_file_act.triggered.connect(self.insert_file_dialog)

        # Set fallback icon (will be overridden by assets/icons/gallery.svg if present)
        self.gallery_act = QAction(QIcon.fromTheme("folder-images"), _("Create Gallery"), self)
        self.gallery_act.setToolTip(_("Select images and create gallery"))
        self.gallery_act.triggered.connect(self.insert_gallery_dialog)

        self.emoji_act = QAction(_("Insert Emoji"), self)
        self.emoji_act.setToolTip(_("Insert an emoji or icon"))
        self.emoji_act.triggered.connect(self.open_emoji_picker)

        self.exit_act = QAction(_("Exit"), self)
        self.exit_act.triggered.connect(self.close)

        # Edit Actions
        self.undo_act = QAction(_("Undo"), self)
        self.undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_act.triggered.connect(self.editor.undo)

        self.redo_act = QAction(_("Redo"), self)
        self.redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_act.triggered.connect(self.editor.redo)

        self.select_all_act = QAction(_("Select All"), self)
        self.select_all_act.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_act.triggered.connect(self.editor.selectAll)
        self.select_all_act.setToolTip(_("Select All (Ctrl+A)"))

        self.search_act = QAction(_("Search"), self)
        self.search_act.setShortcut("Ctrl+F")
        self.search_act.triggered.connect(self.show_search_dialog)

        self.replace_act = QAction(_("Replace"), self)
        self.replace_act.setShortcut("Ctrl+H")
        self.replace_act.triggered.connect(lambda checked: self.show_search_dialog(focus_replace=True))

        # Formatting Actions
        self.bold_act = QAction(_("Bold"), self)
        self.bold_act.setShortcut("Ctrl+B")
        self.bold_act.setToolTip(_("Bold (Ctrl+B)"))
        self.bold_act.triggered.connect(self.editor.toggle_bold)
        
        self.italic_act = QAction(_("Italic"), self)
        self.italic_act.setShortcut("Ctrl+I")
        self.italic_act.setToolTip(_("Italic (Ctrl+I)"))
        self.italic_act.triggered.connect(self.editor.toggle_italic)
        
        self.code_act = QAction(_("Code"), self)
        self.code_act.setToolTip(_("Inline Code"))
        self.code_act.triggered.connect(self.editor.toggle_code)
        
        self.h1_act = QAction("H1", self)
        self.h1_act.triggered.connect(lambda: self.editor.set_header(1))
        
        self.h2_act = QAction("H2", self)
        self.h2_act.triggered.connect(lambda: self.editor.set_header(2))
        
        self.h3_act = QAction("H3", self)
        self.h3_act.triggered.connect(lambda: self.editor.set_header(3))
        
        self.ul_act = QAction(_("List"), self)
        self.ul_act.setToolTip(_("Bulleted List"))
        self.ul_act.triggered.connect(lambda: self.editor.toggle_list(ordered=False))
        
        self.ol_act = QAction(_("Num."), self)
        self.ol_act.setToolTip(_("Numbered List"))
        self.ol_act.triggered.connect(lambda: self.editor.toggle_list(ordered=True))

        self.table_act = QAction(_("Table"), self)
        self.table_act.setToolTip(_("Insert Table"))
        self.table_act.triggered.connect(self.insert_table_dialog)


        # View Actions
        self.toggle_preview_act = QAction(_("Preview"), self)
        self.toggle_preview_act.setCheckable(True)
        show_preview = self.app_config.get('view_show_preview', True)
        self.toggle_preview_act.setChecked(show_preview)
        self.toggle_preview_act.triggered.connect(self.toggle_preview)

        self.toggle_line_numbers_act = QAction(_("Line Numbers"), self)
        self.toggle_line_numbers_act.setCheckable(True)
        self.toggle_line_numbers_act.setChecked(self.app_config.get('view_show_line_numbers', True))
        self.toggle_line_numbers_act.triggered.connect(self.toggle_line_numbers)

        self.toggle_spellcheck_act = QAction(_("Spell Checking"), self)
        self.toggle_spellcheck_act.setCheckable(True)
        self.toggle_spellcheck_act.setChecked(self.project_config.get('spellcheck_enabled', True))
        self.toggle_spellcheck_act.triggered.connect(self.toggle_spellcheck)

        self.dark_mode_act = QAction(_("Dark Mode"), self)
        self.dark_mode_act.setCheckable(True)
        self.dark_mode_act.setChecked(self.app_config.get('view_dark_mode', False))
        self.dark_mode_act.toggled.connect(self.toggle_dark_mode)

        self.config_act = QAction(_("App Settings"), self)
        self.config_act.triggered.connect(self.show_app_config_dialog)

        self.manage_snippets_act = QAction(_("Manage Snippets..."), self)
        self.manage_snippets_act.triggered.connect(self.show_snippet_manager)

        # Render Actions
        self.render_act = QAction(_("Render Site"), self)
        self.render_act.setShortcut("Ctrl+R")
        self.render_act.triggered.connect(self.run_renderer)

        self.open_browser_act = QAction(QIcon.fromTheme("web-browser"), _("Open in Browser"), self)
        self.open_browser_act.setToolTip(_("Opens the generated site in the default browser"))
        self.open_browser_act.triggered.connect(self.open_in_browser)

        # Help Actions
        self.about_act = QAction(_("About"), self)
        self.about_act.triggered.connect(self.show_about_dialog)

    def init_menu(self):
        menubar = self.menuBar()

        # 1. File
        file_menu = menubar.addMenu(_("&File"))
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.insert_img_act)
        file_menu.addAction(self.insert_file_act)
        file_menu.addAction(self.emoji_act)
        file_menu.addSeparator()
        file_menu.addAction(self.switch_project_act)
        file_menu.addAction(self.create_project_act)
        file_menu.addAction(self.project_settings_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        # 2. Bearbeiten
        edit_menu = menubar.addMenu(_("&Edit"))
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.search_act)
        edit_menu.addAction(self.replace_act)

        # 3. Ansicht
        view_menu = menubar.addMenu(_("&View"))
        view_menu.addAction(self.toolbar.toggleViewAction())
        view_menu.addAction(self.toggle_preview_act)
        view_menu.addAction(self.toggle_line_numbers_act)
        view_menu.addAction(self.toggle_spellcheck_act)
        view_menu.addAction(self.dark_mode_act)
        view_menu.addSeparator()
        
        for dock in self.findChildren(QDockWidget):
            view_menu.addAction(dock.toggleViewAction())

        # 4. App Tools
        app_tools_menu = menubar.addMenu(_("&App Tools"))
        app_tools_menu.addAction(self.manage_snippets_act)
        app_tools_menu.addAction(self.config_act)
        
        color_settings_action = QAction(_("Color Settings"), self)
        color_settings_action.triggered.connect(self.open_color_settings_dialog)
        app_tools_menu.addAction(color_settings_action)
        
        app_tools_menu.addSeparator()
        self.populate_tools_menu(app_tools_menu, category="app")

        # 5. Project Tools
        project_tools_menu = menubar.addMenu(_("&Project Tools"))
        
        project_tools_menu.addAction(self.bulk_edit_frontmatter_act)
        project_tools_menu.addAction(self.manage_dictionary_act)
        project_tools_menu.addSeparator()

        self.populate_tools_menu(project_tools_menu, category="project")

        # 6. Rendern
        render_menu = menubar.addMenu(_("&Render"))
        render_menu.addAction(self.render_act)
        render_menu.addAction(self.open_browser_act)

        # 7. Hilfe (inkl. About)
        self.help_menu = menubar.addMenu(_("&Help"))
        self.populate_help_menu(self.help_menu)
        self.help_menu.addAction(self.about_act)

    def populate_tools_menu(self, menu, category="project"):
        """
        Load tools from the workers directory and add them to the menu.
        Scans the workers directory and appends menu entries.

        :param menu: The menu to which tools will be added.
        :param category: The category of the tools to add ("app" or "project").
        """
        if not os.path.exists(self.workers_dir):
            os.makedirs(self.workers_dir)
            return

        for filename in sorted(os.listdir(self.workers_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                file_path = os.path.join(self.workers_dir, filename)
                
                try:
                    # Static analysis using AST to avoid import errors when building the menu
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    
                    name = filename
                    hidden = False
                    has_run = False
                    worker_category = "project"

                    for node in tree.body:
                        # Look for assignments: name = "..." or hidden = True
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    val = None
                                    # 1. Simple constants (Python 3.8+)
                                    if isinstance(node.value, ast.Constant):
                                        val = node.value.value
                                    # 2. Strings/numbers in older Python versions
                                    elif hasattr(ast, 'Str') and isinstance(node.value, ast.Str):
                                        val = node.value.s
                                    # 3. Support for _("...") translations
                                    elif isinstance(node.value, ast.Call) and \
                                         isinstance(node.value.func, ast.Name) and \
                                         node.value.func.id == "_" and node.value.args:
                                        if isinstance(node.value.args[0], ast.Constant):
                                            val = node.value.args[0].value
                                    
                                    if val is not None:
                                        if target.id == "name":
                                            name = _(val) # translate string
                                        elif target.id == "hidden":
                                            hidden = val
                                        elif target.id == "category":
                                            worker_category = val
                        
                        # Look for function definition: def run(...)
                        if isinstance(node, ast.FunctionDef) and node.name == "run":
                            has_run = True

                    if hidden or not has_run:
                        continue
                    
                    if worker_category != category:
                        continue
                    
                    action = QAction(name, self)
                    # Lambda binds the path
                    action.triggered.connect(lambda checked, p=file_path, n=name: self.run_generic_worker(p, n))
                    menu.addAction(action)
                except Exception as e:
                    print(f"Error loading worker {filename}: {e}")

    def populate_help_menu(self, menu):
        """Load help files from assets/help and add them to the menu."""
        help_dir = os.path.join(self.app_root, "assets", "help")
        if not os.path.exists(help_dir):
            return

        help_files = []
        for filename in os.listdir(help_dir):
            if filename.lower().endswith(('.md', '.markdown')):
                # About is handled separately and should not be included in the dynamic list
                if filename.lower() == 'about.md':
                    continue

                file_path = os.path.join(help_dir, filename)
                try:
                    post = frontmatter.load(file_path)
                    title = post.metadata.get('title', filename)
                    help_files.append((title, file_path))
                except Exception:
                    continue
        
        # Sortieren nach Titel
        help_files.sort(key=lambda x: x[0])
        
        for title, path in help_files:
            action = QAction(title, self)
            action.triggered.connect(lambda checked, p=path: self.show_help(p))
            menu.addAction(action)
            
        if help_files:
            menu.addSeparator()

    def refresh_help_menu(self):
        if hasattr(self, 'help_menu'):
            self.help_menu.clear()
            self.populate_help_menu(self.help_menu)
            self.help_menu.addAction(self.about_act)

    def show_help(self, file_path):
        dark_mode = self.app_config.get('view_dark_mode', False)
        viewer = HelpViewer(file_path, self, dark_mode)
        viewer.exec()

    def init_toolbar(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setObjectName("MainToolbar")
        self.addToolBar(self.toolbar)
        
        show_toolbar = self.app_config.get('view_show_toolbar', True)
        self.toolbar.setVisible(show_toolbar)

        # Standard-Layout definieren
        self.default_toolbar_layout = [
            "new_act", "save_act", "separator",
            "undo_act", "redo_act", "separator",
            "insert_img_act", "insert_file_act", "gallery_act", "emoji_act", "separator",
            "search_act", "separator",
            "bold_act", "italic_act", "code_act", "separator",
            "h1_act", "h2_act", "h3_act", "separator",
            "ul_act", "ol_act", "table_act", "spacer",
            "render_act", "open_browser_act"
        ]

        # Layout aus Config laden oder Standard verwenden
        layout_config = self.app_config.get('toolbar_layout', self.default_toolbar_layout)
        self.app_config['toolbar_layout'] = layout_config

        for item in layout_config:
            if item == "separator" or item == "|":
                self.toolbar.addSeparator()
            elif item == "spacer" or item == ">":
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.toolbar.addWidget(spacer)
            elif hasattr(self, item):
                action = getattr(self, item)
                if isinstance(action, QAction):
                    self.toolbar.addAction(action)

    def closeEvent(self, event):
        # Check for unsaved changes
        if self.current_file_path and (self.editor.document().isModified() or self.frontmatter_modified):
            autosave = self.app_config.get('autosave_on_close', False)
            
            if autosave:
                self.save_file()
            else:
                reply = QMessageBox.question(
                    self, _("Unsaved Changes"),
                    _("Do you want to save changes before closing?"),
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    self.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return

        # GUI-Einstellungen in globale App-Config speichern
        self.app_config['view_show_preview'] = self.preview.isVisible()
        self.app_config['view_show_toolbar'] = self.toolbar.isVisible()
        self.app_config['view_show_line_numbers'] = self.toggle_line_numbers_act.isChecked()
        self.app_config['view_dark_mode'] = self.dark_mode_act.isChecked()
        
        # Fenstergeometrie speichern
        self.app_config['window_width'] = self.width()
        self.app_config['window_height'] = self.height()
        self.app_config['window_x'] = self.x()
        self.app_config['window_y'] = self.y()
        
        self.settings.setValue("splitter_sizes", self.splitter.saveState())
        self.settings.setValue("left_splitter_sizes", self.left_splitter.saveState())
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())

        self.save_app_config()
        event.accept()

    def on_tree_clicked(self, index):
        file_path = self.file_tree.get_file_path(index)
        if os.path.isfile(file_path):
            self.load_file(file_path)

    def load_last_file(self):
        last_file = self.settings.value("last_file")
        # Check if a path was stored and if the file still exists
        if last_file and isinstance(last_file, str) and os.path.exists(last_file):
            # Check whether the file belongs to the current project
            if os.path.abspath(last_file).startswith(os.path.abspath(self.project_root)):
                self.load_file(last_file)
                return

        # Fallback: try to load index.md in the content directory
        index_path = os.path.join(self.content_dir, "index.md")
        if os.path.exists(index_path):
            self.load_file(index_path)

    def check_unsaved_changes(self):
        """Checks for unsaved changes before switching context."""
        if self.current_file_path and (self.editor.document().isModified() or self.frontmatter_modified):
            autosave = self.app_config.get('autosave_on_switch', False)
            
            if autosave:
                self.save_file()
                return True
            else:
                reply = QMessageBox.question(
                    self, _("Unsaved Changes"),
                    _("Do you want to save changes before switching?"),
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    self.save_file()
                    return True
                elif reply == QMessageBox.StandardButton.Discard:
                    return True
                elif reply == QMessageBox.StandardButton.Cancel:
                    return False
        return True

    def load_file(self, file_path):
        # Verhindern, dass die gleiche Datei neu geladen wird
        if self.current_file_path and os.path.abspath(self.current_file_path) == os.path.abspath(file_path):
            return

        if not self.check_unsaved_changes():
            return

        try:
            # Datei mit python-frontmatter laden
            post = frontmatter.load(file_path)
            
            self.current_file_path = file_path
            self.settings.setValue("last_file", file_path)
            self.editor.file_path = file_path
            
            # Aktuelle Datei im Baum markieren
            self.file_tree.set_current_file_path(file_path)
            
            # Inhalt in Editor (ohne Frontmatter)
            self.editor.setPlainText(post.content)
            self.editor.moveCursor(QTextCursor.MoveOperation.End)
            self.editor.document().setModified(False)
            
            # Metadaten in Panel
            self.frontmatter_panel.set_data(post.metadata)
            self.frontmatter_panel.set_current_file_path(file_path)
            self.frontmatter_modified = False
            
            self.preview.set_base_path(file_path)
            self.preview.update_preview(post.content)
            self.outline.update_outline(post.content)
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not load file: {e}").format(e=e))

    def save_file(self):
        if not self.current_file_path:
            return
        
        try:
            # Daten zusammenführen
            metadata = self.frontmatter_panel.get_data()
            content = self.editor.toPlainText()
            
            post = frontmatter.Post(content, **metadata)
            
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            self.editor.document().setModified(False)
            self.frontmatter_modified = False
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not save file: {e}").format(e=e))

    def autosave_file(self):
        # Nur speichern, wenn eine Datei offen ist und Änderungen vorliegen
        is_modified = (self.current_file_path and 
                      (self.editor.document().isModified() or self.frontmatter_modified))
        if is_modified:
            self.save_file()

    def on_text_changed(self):
        # Live-Update der Vorschau
        content = self.editor.toPlainText()
        self.preview.update_preview(content)
        self.outline.update_outline(content)
        self.update_status_bar()

    def on_frontmatter_changed(self):
        self.frontmatter_modified = True
        self.update_status_bar()

    def update_font_size_config(self, size):
        self.app_config['editor_font_size'] = size

    def sync_scroll_and_line_numbers(self, value):
        """Synchronizes scroll position from the editor to the preview."""
        # Zeilennummern-Bereich aktualisieren, wenn gescrollt wird
        self.editor.line_number_area.update()

        if not self.preview.isVisible():
            return

        scrollbar = self.editor.verticalScrollBar()
        max_val = scrollbar.maximum()
        
        if max_val > 0:
            percentage = value / max_val
            # Improvement: "Stick to bottom"
            # If the editor is nearly at the bottom (tolerance), scroll the preview to 100%
            if value >= max_val - 20:
                percentage = 1.0
            self.preview.scroll_to_percentage(percentage)

    def restore_scroll_position(self, ok=True):
        """Restores the scroll position after the preview reloads."""
        if ok:
            self.sync_scroll_and_line_numbers(self.editor.verticalScrollBar().value())

    def update_status_bar(self):
        if not self.current_file_path:
            self.status_label.setText(_("Ready"))
            self.setWindowTitle(f"{self.project_name} - {APP_NAME}")
            return

        # Compute relative path for a compact display
        try:
            display_path = os.path.relpath(self.current_file_path, self.project_root)
        except ValueError:
            display_path = self.current_file_path

        if self.editor.document().isModified() or self.frontmatter_modified:
            self.status_label.setText(f"[{_('UNSAVED')}] {display_path}")
            self.setWindowTitle(f"* {os.path.basename(self.current_file_path)} - {self.project_name} - {APP_NAME}")
        else:
            self.status_label.setText(display_path)
            self.setWindowTitle(f"{os.path.basename(self.current_file_path)} - {self.project_name} - {APP_NAME}")

    def update_cursor_label(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(_("Ln {line}, Col {col}").format(line=line, col=col))

    def scroll_to_line(self, line_number):
        # Move cursor to the specified line
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line_number)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        self.editor.setFocus()

    def insert_snippet(self, text):
        # Insert text at the current cursor position
        self.editor.insertPlainText(text)
        self.editor.setFocus()

    def insert_image_dialog(self):
        if not self.current_file_path:
            QMessageBox.warning(self, _("Warning"), _("Please open a file first to insert an image."))
            return

        # Start directory: current file's folder
        start_dir = os.path.dirname(self.current_file_path)
            
        file_path, _filter = QFileDialog.getOpenFileName(
            self, _("Select Image"), start_dir, _("Images (*.png *.jpg *.jpeg *.gif *.svg *.webp);;All Files (*)")
        )
        
        if file_path:

            # Relativen Pfad berechnen
            try:
                rel_path = os.path.relpath(file_path, os.path.dirname(self.current_file_path))
                rel_path = rel_path.replace(os.path.sep, '/')
            except ValueError:
                rel_path = file_path

            filename = os.path.basename(file_path)
            alt_text = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title()
            
            text = f"![{alt_text}]({rel_path})"
            
            self.editor.insertPlainText(text)
            self.editor.setFocus()

    def insert_file_dialog(self):
        if not self.current_file_path:
            QMessageBox.warning(self, _("Warning"), _("Please open a file first to insert a link."))
            return

        # Start directory: current file's folder
        start_dir = os.path.dirname(self.current_file_path)
            
        file_path, _filter = QFileDialog.getOpenFileName(
            self, _("Select File"), start_dir, _("All Files (*)")
        )
        
        if file_path:
            self.editor.insert_file_link(file_path)
            self.editor.setFocus()

    def insert_gallery_dialog(self):
        if not self.current_file_path:
            QMessageBox.warning(self, _("Warning"), _("Please open a file first to insert a gallery."))
            return

        # Start directory: current file's folder
        start_dir = os.path.dirname(self.current_file_path)
            
        file_names, _filter = QFileDialog.getOpenFileNames(
            self, _("Select Images"), start_dir, _("Images (*.png *.jpg *.jpeg *.gif *.svg *.webp)")
        )
        
        if not file_names:
            return
            
        # Create target folder (assets/galleries/timestamp)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        gallery_folder_name = f"gallery_{timestamp}"
        
        assets_dir = os.path.join(self.project_root, "assets", "galleries", gallery_folder_name)
        
        try:
            os.makedirs(assets_dir, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, _("Error"), _("Could not create gallery folder: {e}").format(e=e))
            return
            
        markdown_lines = ['[[gallery layout="grid" cols="3"]]']
        
        for file_path in file_names:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(assets_dir, filename)
            
            try:
                shutil.copy2(file_path, dest_path)
                
                # Compute relative path
                rel_path = os.path.relpath(dest_path, os.path.dirname(self.current_file_path))
                rel_path = rel_path.replace(os.path.sep, '/')
                
                # Alt text from filename
                alt_text = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title()
                
                markdown_lines.append(f"![{alt_text}]({rel_path})")
            except Exception as e:
                print(f"Error copying {filename}: {e}")
                
        markdown_lines.append('[[/gallery]]')
        
        self.editor.insertPlainText("\n".join(markdown_lines) + "\n")
        self.editor.setFocus()

    def insert_table_dialog(self):
        rows, ok = QInputDialog.getInt(self, _("Insert Table"), _("Rows:"), 3, 1, 50)
        if not ok: return
        cols, ok = QInputDialog.getInt(self, _("Insert Table"), _("Columns:"), 3, 1, 20)
        if not ok: return
        
        self.editor.insert_table(rows, cols)

    def open_emoji_picker(self):
        picker = EmojiPicker(self)
        # If an emoji is selected, insert it at the cursor position
        picker.emoji_selected.connect(self.editor.insertPlainText)
        picker.exec()

    def show_search_dialog(self, focus_replace=False):
        # Create dialog (lazy loading: only if not existing)
        if not hasattr(self, 'search_dialog') or self.search_dialog is None:
            self.search_dialog = SearchDialog(self.editor, self)
            self.search_dialog.finished.connect(self._on_search_closed)
        
        self.search_dialog.show()
        if focus_replace:
            self.search_dialog.replace_input.setFocus()
            self.search_dialog.replace_input.selectAll()
        else:
            self.search_dialog.find_input.setFocus()
            self.search_dialog.find_input.selectAll()

    def _on_search_closed(self):
        self.search_dialog = None

    def toggle_preview(self, checked):
        self.preview.setVisible(checked)

    def toggle_line_numbers(self, checked):
        self.editor.set_line_numbers_visible(checked)
        self.app_config['view_show_line_numbers'] = checked

    def toggle_spellcheck(self, checked):
        self.editor.set_spellchecker_enabled(checked)
        self.project_config['spellcheck_enabled'] = checked
        self.project_config_manager.update({'spellcheck_enabled': checked})
        self.project_config_manager.save()

    def toggle_dark_mode(self, checked):
        self.apply_theme(checked)

    def apply_theme(self, dark_mode):
        app = QApplication.instance()
        if dark_mode:
            apply_dark_theme(app)
        else:
            apply_light_theme(app)

        self.editor.set_dark_mode(dark_mode)
        self.preview.set_dark_mode(dark_mode)
        
        # Update icons
        self.update_icons(dark_mode)
        
        # Update panels in the sidebar
        for panel in self.sidebar_panels.values():
            if hasattr(panel, 'set_dark_mode'):
                panel.set_dark_mode(dark_mode)

        self.apply_custom_colors()

    def update_preview_font(self):
        font_family = self.app_config.get('preview_font_family', 'Sans Serif')
        font_size = self.app_config.get('preview_font_size', 14)
        
        if hasattr(self.preview, 'set_font_configuration'):
            self.preview.set_font_configuration(font_family, font_size)

    def update_icons(self, dark_mode):
        """Loads and tints icons based on the current mode."""
        icon_folder = os.path.join(self.app_root, "assets", "icons")
        
        # Color for icons: white in dark mode, dark gray in light mode
        color = QColor("#ffffff") if dark_mode else QColor("#333333")
        
        for act_name, icon_name in self.action_icons.items():
            if not hasattr(self, act_name):
                continue
                
            action = getattr(self, act_name)
            
            # Look for .svg files
            if icon_name.endswith(".svg"):
                if os.path.isabs(icon_name):
                    svg_path = icon_name
                else:
                    svg_path = os.path.join(self.app_root, icon_name)
            else:
                svg_path = os.path.join(icon_folder, f"{icon_name}.svg")
            
            if os.path.exists(svg_path):
                # Load and tint SVG
                pixmap = QIcon(svg_path).pixmap(24, 24)
                if not pixmap.isNull():
                    # Tint using QPainter
                    painter = QPainter(pixmap)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    painter.fillRect(pixmap.rect(), color)
                    painter.end()
                    action.setIcon(QIcon(pixmap))

    def show_project_config_dialog(self):
        config_path = os.path.join(self.project_root, "config.yaml")
        dialog = ProjectConfigDialog(config_path, self.app_root, self)
        if dialog.exec():
            self.project_config = self.load_project_config()
            self.init_spellchecker() # Sprache könnte sich geändert haben
            self.update_frontmatter_layouts()
    
    def show_bulk_edit_dialog(self):
        # Speichere aktuelle Datei, um Konflikte zu vermeiden
        if self.current_file_path and self.editor.document().isModified():
            self.save_file()

        dialog = BulkEditDialog(self.project_root, self.content_dir)
        if dialog.exec():
            # Falls die aktuell offene Datei geändert wurde, neu laden
            if self.current_file_path and os.path.exists(self.current_file_path):
                # Merke Pfad
                path = self.current_file_path
                # Reset, damit load_file nicht abbricht (da es denkt, die Datei sei schon offen)
                self.current_file_path = None 
                self.load_file(path)

    def show_app_config_dialog(self):
        config_path = os.path.join(self.app_root, "app_config.yaml")
        dialog = AppConfigDialog(config_path, self)
        if dialog.exec():
            self.app_config = self.load_app_config()
            
            # Einstellungen sofort anwenden
            # Dark Mode (löst Signal aus, das apply_theme aufruft)
            self.dark_mode_act.setChecked(self.app_config.get('view_dark_mode', False))
            
            show_preview = self.app_config.get('view_show_preview', True)
            self.toggle_preview_act.setChecked(show_preview)
            
            show_toolbar = self.app_config.get('view_show_toolbar', True)
            self.toolbar.setVisible(show_toolbar)
            
            show_line_numbers = self.app_config.get('view_show_line_numbers', True)
            self.toggle_line_numbers_act.setChecked(show_line_numbers)
            self.editor.set_line_numbers_visible(show_line_numbers)

            # Schriftgröße anwenden
            font_size = self.app_config.get('editor_font_size', 12)
            font_family = self.app_config.get('editor_font_family', 'Monospace')
            
            font = self.editor.font()
            font.setFamily(font_family)
            self.editor.setFont(font)
            self.editor.set_font_size(font_size)
            
            # Preview Font anwenden
            self.update_preview_font()

            # Autosave Timer aktualisieren
            autosave_interval = self.app_config.get('autosave_interval', 300)
            if autosave_interval > 0:
                self.autosave_timer.start(autosave_interval * 1000)
            else:
                self.autosave_timer.stop()

    def show_snippet_manager(self):
        snippets_dir = os.path.join(self.app_root, "snippets")
        dialog = SnippetManagerDialog(snippets_dir, self)
        if dialog.exec():
            self.snippets.refresh_snippets()

    def show_dictionary_manager(self):
        if not self.spell_checker:
            QMessageBox.warning(self, _("Error"), _("Spellchecker is not initialized."))
            return
        dialog = DictionaryManagerDialog(self.spell_checker, self)
        dialog.exec()
        # Re-highlight editor to reflect changes (e.g. removed words might now be errors)
        self.editor.highlighter.rehighlight()

    def create_new_post(self, initial_dir=None):
        # Wenn die Funktion vom Menü/Toolbar aufgerufen wird, ist initial_dir ein bool (checked).
        # Wenn sie vom FileTree-Signal kommt, ist es ein String (Pfad).
        target_dir = initial_dir if isinstance(initial_dir, str) else None
        
        default_template = self.project_config.get("default_template", "full-width")
        
        template_dirs = [os.path.join(self.project_root, "templates")]
        theme_name = self.project_config.get("site_theme")
        if theme_name and theme_name != "default-blog":
            themes_dir = self.project_config.get("themes_directory", "themes")
            theme_templates = os.path.join(self.project_root, themes_dir, theme_name, "templates")
            template_dirs.append(theme_templates)
            
        dialog = NewPostDialog(self.content_dir, self, initial_dir=target_dir, default_template=default_template, template_dirs=template_dirs)
        
        if dialog.exec():
            data = dialog.get_data()
            
            # Zielpfad bestimmen
            if data['directory'] == ".":
                dir_path = self.content_dir
            else:
                dir_path = os.path.join(self.content_dir, data['directory'])
            
            file_path = os.path.join(dir_path, data['filename'])
            
            if os.path.exists(file_path):
                QMessageBox.warning(self, _("Error"), _("The file '{filename}' already exists.").format(filename=data['filename']))
                return
            
            # Frontmatter Objekt erstellen
            post = frontmatter.Post(
                "", # Leerer Inhalt am Anfang
                title=data['title'],
                author=data['author'],
                date=data['date'],
                release_date=data['date'], # Wichtig für deine Sortierung
                tags=data['tags'],
                draft=data['draft'],
                layout=data['layout'],
                weight=data.get('weight', 0),
                breadcrumbs=True
            )
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(frontmatter.dumps(post))
                
                # Datei sofort laden
                self.load_file(file_path)
                self.status_label.setText(_("Created: {filename}").format(filename=data['filename']))
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Could not create file: {e}").format(e=e))

    def run_generic_worker(self, worker_path, worker_name, extra_context=None, on_worker_finished=None):
        self.status_label.setText(_("Running '{worker_name}'...").format(worker_name=worker_name))
        
        metadata = {}
        if hasattr(self, 'frontmatter_panel'):
            metadata = self.frontmatter_panel.get_data()

        context = {
            'content_dir': self.content_dir,
            'project_root': self.project_root,
            'app_root': self.app_root,
            'snippets_dir': os.path.join(self.app_root, "snippets"),
            'current_file_path': self.current_file_path,
            'editor_content': self.editor.toPlainText() if self.current_file_path else None,
            'metadata': metadata,
            'config': self.project_config,
            'app_version': self.app_version # Hier die neue Variable hinzufügen
        }
        
        if extra_context:
            context.update(extra_context)
        
        self.worker = WorkerThread(worker_path, context)
        
        def on_finished(res):
            self.status_label.setText(_("{worker_name} finished!").format(worker_name=worker_name))
            
            if on_worker_finished:
                on_worker_finished()

            # Wenn das Ergebnis eine Liste von Dictionaries ist (z.B. vom Link-Checker)
            if isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict) and 'file_path' in res[0]:
                dlg = WorkerResultListDialog(_("Result: {worker_name}").format(worker_name=worker_name), res, self)
                dlg.exec()
                return

            res_str = str(res)
            # Wenn das Ergebnis mehrzeilig ist oder sehr lang, zeige es im Dialog
            if "\n" in res_str or len(res_str) > 150:
                dlg = WorkerResultDialog(_("Result: {worker_name}").format(worker_name=worker_name), res_str, self)
                dlg.exec()
            else:
                QMessageBox.information(self, _("Success"), res_str)
                
            if os.path.basename(worker_path) in ["plugin_docs.py", "snippet_docs.py"]:
                self.refresh_help_menu()

        def on_error(err):
            self.status_label.setText(_("Error!"))
            if on_worker_finished:
                on_worker_finished()
            QMessageBox.critical(self, _("Error"), _("Error in {worker_name}:\n{err}").format(worker_name=worker_name, err=err))

        self.worker.finished.connect(on_finished)
        self.worker.error.connect(on_error)
        self.worker.start()

    def switch_project(self):
        if not self.check_unsaved_changes():
            return

        launcher = ProjectLauncher(self.app_root)
        if launcher.exec() == QDialog.DialogCode.Accepted:
            new_project_path = launcher.selected_project
            if new_project_path and new_project_path != self.project_root:
                self.new_window = MainWindow(new_project_path)
                self.new_window.show()
                self.close()

    def create_new_project_dialog(self):
        dialog = CreateProjectDialog(self.app_root, self)
        if dialog.exec():
            new_path = dialog.created_project_path
            if new_path and os.path.exists(new_path):
                # Add to recent projects
                self.add_to_recent_projects(new_path)
                
                reply = QMessageBox.question(self, _("Project Created"), 
                                             _("New project created. Do you want to open it now?"),
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.switch_to_project_path(new_path)

    def add_to_recent_projects(self, path):
        config = self.app_config_manager.load()
        recent = config.get("recent_projects", [])
        if path not in recent:
            recent.insert(0, path)
            self.app_config_manager.update({"recent_projects": recent})
            self.app_config_manager.save()
            if hasattr(self, 'project_panel'):
                self.project_panel.load_projects()

    def switch_to_project_path(self, path):
        """Switch directly to a project path (called from ProjectPanel)."""
        if not self.check_unsaved_changes():
            return

        self.new_window = MainWindow(path)
        self.new_window.show()
        self.close()

    def run_renderer(self):
        """Triggers the site rendering process, with an optional backup step."""
        # Save unsaved changes before doing anything
        if self.current_file_path and (self.editor.document().isModified() or self.frontmatter_modified):
            self.save_file()

        # --- Progress Dialog Setup ---
        self.progress_helper = ProgressHelper()
        self.progress_dialog = QProgressDialog(_("Rendering Site..."), _("Cancel"), 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setAutoClose(False) # Wichtig, damit er nicht zu früh schließt
        # self.progress_dialog.setValue(0) # Entfernt: Dialog erst anzeigen, wenn Fortschritt gemeldet wird oder Backup startet

        # Deaktiviere Render-Action, um doppelte Aufrufe zu verhindern
        self.render_act.setEnabled(False)

        def update_progress(current, total, msg):
            self.progress_dialog.setMaximum(total)
            self.progress_dialog.setValue(current)
            self.progress_dialog.setLabelText(msg)

        self.progress_helper.progress.connect(update_progress)
        
        render_context = {'progress_callback': self.progress_helper.progress.emit}
        
        def on_render_finished():
            self.progress_dialog.close()
            self.render_act.setEnabled(True)

        # --- AUTOMATIC BACKUP ---
        if self.project_config.get("backup_on_render", False):
            self.progress_dialog.setValue(0) # Dialog explizit für Backup anzeigen
            self.status_label.setText(_("Creating backup before rendering..."))
            
            backup_worker_path = os.path.join(self.workers_dir, "backup_content.py")
            backup_context = {
                'content_dir': self.content_dir,
                'project_root': self.project_root,
                'config': self.project_config,
                'progress_callback': self.progress_helper.progress.emit
            }
            
            self.backup_worker_thread = WorkerThread(backup_worker_path, backup_context)
            
            def on_backup_finished(result):
                if "Error" in str(result):
                     QMessageBox.critical(self, _("Backup Error"), str(result))
                     self.status_label.setText(_("Backup failed!"))
                     self.render_act.setEnabled(True)
                else:
                    self.status_label.setText(_("Backup complete. Starting renderer..."))
                    renderer_path = os.path.join(self.workers_dir, "renderer.py")
                    self.run_generic_worker(renderer_path, "Renderer", extra_context=render_context, on_worker_finished=on_render_finished)

            def on_backup_error(err):
                self.status_label.setText(_("Backup Error!"))
                self.progress_dialog.close()
                QMessageBox.critical(self, _("Error"), _("Error in Backup Worker:\n{err}").format(err=err))
                self.render_act.setEnabled(True)

            self.backup_worker_thread.finished.connect(on_backup_finished)
            self.backup_worker_thread.error.connect(on_backup_error)
            self.backup_worker_thread.start()
        else:
            renderer_path = os.path.join(self.workers_dir, "renderer.py")
            self.run_generic_worker(renderer_path, "Renderer", extra_context=render_context, on_worker_finished=on_render_finished)

    def open_in_browser(self):
        output_dir = self.project_config.get("site_output_directory", "site_output")
        index_path = os.path.join(self.project_root, output_dir, "index.html")
        
        if os.path.exists(index_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(index_path))
        else:
            QMessageBox.warning(self, _("Error"), _("The start page was not found:\n{index_path}\n\nPlease render the project first.").format(index_path=index_path))

    def load_app_config(self):
        """Load the global app configuration (YAML)."""
        return self.app_config_manager.load()

    def save_app_config(self):
        """Save the global app configuration."""
        try:
            # Reload current file to avoid merge conflicts with ProjectLauncher/ProjectPanel
            # (e.g. if Recent Projects were changed by another process)
            self.app_config_manager.load()
            
            # Aktualisiere nur die Werte, die dieses Fenster verwaltet
            self.app_config_manager.update({
                'view_show_preview': self.app_config.get('view_show_preview', True),
                'view_show_toolbar': self.app_config.get('view_show_toolbar', True),
                'view_show_line_numbers': self.app_config.get('view_show_line_numbers', True),
                'view_dark_mode': self.app_config.get('view_dark_mode', False),
                'editor_font_size': self.app_config.get('editor_font_size', 12),
                'editor_font_family': self.app_config.get('editor_font_family', 'Monospace'),
                'preview_font_family': self.app_config.get('preview_font_family', 'Sans Serif'),
                'preview_font_size': self.app_config.get('preview_font_size', 14),
                'action_icons': self.app_config.get('action_icons', self.default_action_icons),
                'toolbar_layout': self.app_config.get('toolbar_layout', getattr(self, 'default_toolbar_layout', [])),
                'window_width': self.app_config.get('window_width'),
                'window_height': self.app_config.get('window_height'),
                'window_x': self.app_config.get('window_x'),
                'window_y': self.app_config.get('window_y'),
                'autosave_interval': self.app_config.get('autosave_interval', 300),
                'autosave_on_close': self.app_config.get('autosave_on_close', False),
                'autosave_on_switch': self.app_config.get('autosave_on_switch', False)
            })
            self.app_config_manager.save()
        except Exception as e:
            print(f"Error saving app config: {e}")

    def load_project_config(self):
        """Load the project configuration (YAML)."""
        # The ConfigManager automatically handles TOML migration
        return self.project_config_manager.load()

    def show_about_dialog(self):
        about_path = os.path.join(self.app_root, "assets", "help", "about.md")
        if os.path.exists(about_path):
            self.show_help(about_path)
        else:
            QMessageBox.about(self, _("About"), _("{APP_NAME}\n{APP_VERSION}\n\nA simple editor for static websites."))

    def open_color_settings_dialog(self):
        config_path = self.app_config_path
        dialog = ColorSettingsDialog(config_path, self)
        dialog.settings_saved.connect(self.apply_custom_colors)
        dialog.exec()

    def apply_custom_colors(self):
        try:
            # Konfiguration neu laden, da der Dialog sie gespeichert hat
            self.app_config = self.app_config_manager.load()
            all_colors = self.app_config.get('editor_colors', {})
            
            if isinstance(all_colors, str):
                try:
                    all_colors = ast.literal_eval(all_colors)
                except Exception:
                    all_colors = {}
                
            # Aktuellen Modus ermitteln
            is_dark = self.dark_mode_act.isChecked()
            mode_key = 'dark' if is_dark else 'light'
            color_scheme = all_colors.get(mode_key, {})

            if hasattr(self.editor, 'highlighter'):
                self.editor.highlighter.set_custom_colors(color_scheme)
                self.editor.highlighter.rehighlight()
            
            # Auch dem Editor selbst die Farben geben (für aktuelle Zeile)
            self.editor.set_custom_colors(color_scheme)
        except Exception as e:
            print(f"Error loading colors: {e}")

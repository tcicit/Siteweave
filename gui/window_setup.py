import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.dashboard_manager import DashboardWorker
from core.media_library_widget import MediaLibraryWidget
from core.spellchecker import SpellChecker
from .dashboard_widget import DashboardWidget
from .document_tab_widget import DocumentTabWidget
from .editor_widget import EditorWidget
from .file_tree import FileTree
from .frontmatter_panel import FrontmatterPanel
from .log_viewer_panel import LogViewerPanel
from .outline_panel import OutlinePanel
from .preview_widget import PreviewWidget
from .project_panel import ProjectPanel
from .snippet_panel import SnippetPanel
from core.i18n import _


class WindowSetupMixin:
    def init_localization(self):
        lang = self.app_config.get('language', 'en')
        # Retrieve locales_dir from app_config, falling back to "locales"
        locales_path_setting = self.app_config.get("paths", {}).get("locales", "locales")
        try:
            from core.i18n import init as i18n_init
            # Resolve to absolute path relative to app_root
            abs_locales_dir = locales_path_setting if os.path.isabs(locales_path_setting) else os.path.join(self.app_root, locales_path_setting)
            i18n_init(app_root=self.app_root, locale=lang, locales_dir=abs_locales_dir)
        except Exception as e:
            print(f"Localization init failed for {lang}, using default. ({e})")
    def init_spellchecker(self):
        """Initialisiert oder aktualisiert den Spellchecker basierend auf der Projektkonfiguration."""
        # Versuche erst die spezifische Spellcheck-Sprache, dann Fallback auf Site-Language
        dict_lang = self.project_config.get('spellcheck_language')
        
        if not dict_lang:
            lang_code = self.project_config.get('language', 'en')
            # Normalisierung: HTML nutzt oft Bindestriche (de-DE), Python/Enchant Unterstriche (de_DE)
            lang_code = lang_code.replace('-', '_')

            # Mapping von einfachen Codes zu pyenchant-spezifischen (z.B. de -> de_DE)
            lang_map = {
                'de': 'de_DE',
                'en': 'en_US',
                'fr': 'fr_FR',
                'es': 'es_ES'
                
            }
            # Nutze Mapping oder den Code selbst (falls er schon korrekt ist, z.B. de_DE)
            dict_lang = lang_map.get(lang_code, lang_code)
            
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

        # Sidebar Tabs (Explorer / Media)
        self.left_tabs = QTabWidget()

        # 1. File tree
        self.file_tree = FileTree(self.content_dir)
        self.file_tree.clicked.connect(self.on_tree_clicked)
        self.file_tree.create_file_requested.connect(self.create_new_post)
        self.file_tree.path_renamed.connect(self.on_file_path_renamed)
        
        # Enable drag & drop
        self.file_tree.setDragEnabled(True)
        self.file_tree.setAcceptDrops(True)
        self.file_tree.setDropIndicatorShown(True)
        self.file_tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.file_tree.fs_model.setReadOnly(False)
        
        self.left_tabs.addTab(self.file_tree, _("Explorer"))

        # 2. Media Library
        thumbnail_size = self.app_config.get('media_thumbnail_size', 100)
        self.media_library = MediaLibraryWidget(self.project_root, self.assets_dir, self.content_dir, thumbnail_size)
        # Wir suchen alle Views (List, Tree) in der Media Library und konfigurieren D&D
        for media_view in self.media_library.findChildren(QAbstractItemView):
            # Erlaube das Ziehen von Elementen
            media_view.setDragEnabled(True)
            media_view.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.left_tabs.addTab(self.media_library, _("Media"))
        self.sidebar_panels["MediaLibrary"] = self.media_library

        self.left_splitter.addWidget(self.left_tabs)
        self.splitter.addWidget(self.left_splitter)
        
        # 2. Central Content Stack (Dashboard / Editor)
        self.content_stack = QStackedWidget()
        
        # Page 0: Dashboard
        self.dashboard_worker = DashboardWorker(self.project_root, self.project_config)
        self.dashboard = DashboardWidget()
        self.dashboard.recent_list.itemDoubleClicked.connect(self.on_dashboard_item_clicked)
        self.dashboard_worker.stats_ready.connect(self.dashboard.refresh)
        self.dashboard.refresh_btn.clicked.connect(self.refresh_dashboard)
        self.dashboard.close_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.content_stack.addWidget(self.dashboard)
        
        # Page 1: Editor Area
        self.editor_area = QSplitter(Qt.Orientation.Horizontal)
        self.editor_tabs = DocumentTabWidget()
        self.editor = self._create_editor_widget()
        
        # Signal für das Einfügen von Medien verbinden (jetzt wo der Editor existiert)
        self.media_library.insert_requested.connect(self.insert_file_link)
        self.media_library.insert_plugin_requested.connect(self.insert_image_plugin)
        
        self.editor_area.addWidget(self.editor_tabs)

        # Spellchecker initial aktivieren/deaktivieren
        # 3. Preview
        self.preview = PreviewWidget(self.project_root, self.app_root)
        show_preview = self.app_config.get('view_show_preview', True)
        self.preview.setVisible(show_preview)
        self.editor_area.addWidget(self.preview)
        
        self.content_stack.addWidget(self.editor_area)
        self.splitter.addWidget(self.content_stack)
        
        # Initial Dashboard Refresh
        self.refresh_dashboard()

        # Scroll synchronization: Editor -> Preview
        self.preview.loadFinished.connect(self.restore_scroll_position)

        # 4. Panels (docks)
        self.create_dock_panels()
        
        # Generic restoration of splitter states
        # We provide default sizes in case no state is saved yet
        self.app_config_manager.apply_splitter_states("main_window", {
            "main": self.splitter,
            "left": self.left_splitter,
            "editor_area": self.editor_area
        })

        if self.splitter.sizes() == [0, 0, 0]: # Default fallback if restoration fails
            self.splitter.setSizes([200, 500, 500])

        main_layout.addWidget(self.splitter)

        # Signale verbinden, nachdem alle UI-Elemente (Editor, Preview, Outline) erstellt wurden
        self.editor_tabs.current_document_changed.connect(self.on_document_changed)
        self.editor_tabs.all_tabs_closed.connect(self.on_all_tabs_closed)
        self.editor_tabs.save_requested.connect(self.save_file)
        self.on_document_changed(self.editor, None)
    def _create_editor_widget(self):
        editor = EditorWidget(
            spell_checker=self.spell_checker,
            project_root=self.project_root,
        )
        editor.set_line_numbers_visible(self.app_config.get('view_show_line_numbers', True))
        editor.set_spellchecker_enabled(self.project_config.get('spellcheck_enabled', True))
        editor.set_dark_mode(self.app_config.get('view_dark_mode', False))

        font = editor.font()
        font.setFamily(self.app_config.get('editor_font_family', 'Monospace'))
        editor.setFont(font)
        editor.set_font_size(self.app_config.get('editor_font_size', 12))

        editor.textChanged.connect(lambda document_editor=editor: self.on_text_changed(document_editor))
        editor.fontSizeChanged.connect(self.update_font_size_config)
        editor.cursorPositionChanged.connect(
            lambda document_editor=editor: self.update_cursor_label()
            if document_editor is self.editor else None
        )
        editor.verticalScrollBar().valueChanged.connect(
            lambda value, document_editor=editor:
                self.sync_scroll_and_line_numbers(value, document_editor)
        )
        return editor
    def on_document_changed(self, editor, file_path):
        previous_editor = self.__dict__.get('_active_tab_editor')
        if (
            previous_editor is not None
            and previous_editor is not editor
            and previous_editor.is_dirty()
            and self.app_config.get('autosave_on_switch', False)
        ):
            self.save_file(previous_editor)

        self._active_tab_editor = editor
        self.editor = editor
        self.current_file_path = file_path
        self.frontmatter_modified = getattr(editor, 'frontmatter_modified', False)

        if hasattr(self, 'frontmatter_panel'):
            self.frontmatter_panel.set_data(getattr(editor, 'metadata', {}))
            self.frontmatter_panel.set_current_file_path(file_path)

        if file_path:
            self.file_tree.set_current_file_path(file_path)
            self.preview.set_base_path(file_path)
            self.preview.update_preview(editor.toPlainText())
            self.outline.update_outline(editor.toPlainText())
        else:
            self.preview.update_preview("")
            self.outline.update_outline("")

        self.update_status_bar()
        self.update_cursor_label()
    def on_all_tabs_closed(self):
        self._active_tab_editor = None
        self.current_file_path = None
        self.frontmatter_modified = False
        self.editor = self._create_editor_widget()
        if hasattr(self, 'frontmatter_panel'):
            self.frontmatter_panel.set_data({})
            self.frontmatter_panel.set_current_file_path(None)
        self.show_dashboard()
    def insert_file_link(self, target_path):
        self.editor.insert_file_link(target_path)
    def insert_image_plugin(self, target_path):
        self.editor.insert_image_plugin(target_path)
    def create_dock_panels(self):
        # Frontmatter
        self.frontmatter_panel = FrontmatterPanel()
        self.frontmatter_panel.setObjectName("FrontmatterPanel")
        self.frontmatter_panel.set_project_root(self.project_root)
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

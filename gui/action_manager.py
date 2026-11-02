import ast
import frontmatter
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import QDockWidget, QSizePolicy, QToolBar, QWidget

from core.i18n import _


class ActionManager:
    def __init__(self, window):
        self.window = window

    def create_actions(self):
        window = self.window
        # File Actions
        window.new_act = QAction(_("New Post"), window)
        window.new_act.setShortcut("Ctrl+N")
        window.new_act.triggered.connect(window.create_new_post)

        window.dashboard_act = QAction(_("Dashboard"), window)
        window.dashboard_act.setShortcut("Ctrl+D")
        window.dashboard_act.setToolTip(_("Show project overview (Ctrl+D)"))
        window.dashboard_act.triggered.connect(window.show_dashboard)

        window.refresh_act = QAction(_("Refresh"), window)
        window.refresh_act.setShortcut("F5")
        window.refresh_act.setToolTip(_("Refresh current view and sidebar (F5)"))
        window.refresh_act.triggered.connect(window.handle_global_refresh)

        window.switch_project_act = QAction(_("Switch Project"), window)
        window.switch_project_act.triggered.connect(window.switch_project)

        window.create_project_act = QAction(_("Create New Project"), window)
        window.create_project_act.triggered.connect(window.create_new_project_dialog)

        window.project_config_act = QAction(_("Project Settings"), window)
        window.project_config_act.triggered.connect(window.show_project_config_dialog)

        window.manage_media_act = QAction(_("Manage Media Library..."), window)
        window.manage_media_act.setToolTip(_("Open advanced media management"))
        window.manage_media_act.triggered.connect(window.show_media_manager_dialog)

        # Bulk Edit Action
        window.bulk_edit_frontmatter_act = QAction(_("Bulk Edit Frontmatter"), window)
        window.bulk_edit_frontmatter_act.triggered.connect(window.show_bulk_edit_dialog)        

        window.manage_dictionary_act = QAction(_("Manage Dictionary..."), window)
        window.manage_dictionary_act.triggered.connect(window.show_dictionary_manager)

        window.save_act = QAction(_("Save"), window)
        window.save_act.setShortcut("Ctrl+S")
        window.save_act.triggered.connect(lambda: window.save_file())

        window.insert_img_act = QAction(_("Insert Image"), window)
        window.insert_img_act.setShortcut("Ctrl+Shift+I") # Changed because Ctrl+I is commonly used for Italic
        window.insert_img_act.triggered.connect(window.insert_image_dialog)

        window.insert_file_act = QAction(_("Link File"), window)
        window.insert_file_act.setToolTip(_("Insert link to a file"))
        window.insert_file_act.triggered.connect(window.insert_file_dialog)

        window.insert_img_plugin_act = QAction(_("Insert as Image Plugin"), window)
        window.insert_img_plugin_act.setToolTip(_("Insert selected image using the image plugin"))
        window.insert_img_plugin_act.triggered.connect(window.insert_image_plugin_dialog)

        # Set fallback icon (will be overridden by assets/icons/gallery.svg if present)
        window.gallery_act = QAction(QIcon.fromTheme("folder-images"), _("Create Gallery"), window)
        window.gallery_act.setToolTip(_("Select images and create gallery"))
        window.gallery_act.triggered.connect(window.insert_gallery_dialog)

        window.emoji_act = QAction(_("Insert Emoji"), window)
        window.emoji_act.setToolTip(_("Insert an emoji or icon"))
        window.emoji_act.triggered.connect(window.open_emoji_picker)

        window.exit_act = QAction(_("Exit"), window)
        window.exit_act.triggered.connect(window.close)

        # Edit Actions
        window.undo_act = QAction(_("Undo"), window)
        window.undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        window.undo_act.triggered.connect(lambda: window.editor.undo())

        window.redo_act = QAction(_("Redo"), window)
        window.redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        window.redo_act.triggered.connect(lambda: window.editor.redo())

        window.select_all_act = QAction(_("Select All"), window)
        window.select_all_act.setShortcut(QKeySequence.StandardKey.SelectAll)
        window.select_all_act.triggered.connect(lambda: window.editor.selectAll())
        window.select_all_act.setToolTip(_("Select All (Ctrl+A)"))

        window.search_act = QAction(_("Search"), window)
        window.search_act.setShortcut("Ctrl+F")
        window.search_act.triggered.connect(window.show_search_dialog)

        window.quick_open_act = QAction(_("Quick Open"), window)
        window.quick_open_act.setShortcut("Ctrl+P")
        window.quick_open_act.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        window.quick_open_act.triggered.connect(window.show_quick_open)

        window.replace_act = QAction(_("Replace"), window)
        window.replace_act.setShortcut("Ctrl+H")
        window.replace_act.triggered.connect(lambda checked: window.show_search_dialog(focus_replace=True))

        # Formatting Actions
        window.bold_act = QAction(_("Bold"), window)
        window.bold_act.setShortcut("Ctrl+B")
        window.bold_act.setToolTip(_("Bold (Ctrl+B)"))
        window.bold_act.triggered.connect(lambda: window.editor.toggle_bold())
        
        window.italic_act = QAction(_("Italic"), window)
        window.italic_act.setShortcut("Ctrl+I")
        window.italic_act.setToolTip(_("Italic (Ctrl+I)"))
        window.italic_act.triggered.connect(lambda: window.editor.toggle_italic())
        
        window.code_act = QAction(_("Code"), window)
        window.code_act.setToolTip(_("Inline Code"))
        window.code_act.triggered.connect(lambda: window.editor.toggle_code())
        
        window.h1_act = QAction("H1", window)
        window.h1_act.triggered.connect(lambda: window.editor.set_header(1))
        
        window.h2_act = QAction("H2", window)
        window.h2_act.triggered.connect(lambda: window.editor.set_header(2))
        
        window.h3_act = QAction("H3", window)
        window.h3_act.triggered.connect(lambda: window.editor.set_header(3))
        
        window.ul_act = QAction(_("List"), window)
        window.ul_act.setToolTip(_("Bulleted List"))
        window.ul_act.triggered.connect(lambda: window.editor.toggle_list(ordered=False))
        
        window.ol_act = QAction(_("Num."), window)
        window.ol_act.setToolTip(_("Numbered List"))
        window.ol_act.triggered.connect(lambda: window.editor.toggle_list(ordered=True))

        window.table_act = QAction(_("Table"), window)
        window.table_act.setToolTip(_("Insert Table"))
        window.table_act.triggered.connect(window.insert_table_dialog)


        # View Actions
        window.toggle_preview_act = QAction(_("Preview"), window)
        window.toggle_preview_act.setCheckable(True)
        show_preview = window.app_config.get('view_show_preview', True)
        window.toggle_preview_act.setChecked(show_preview)
        window.toggle_preview_act.triggered.connect(window.toggle_preview)

        window.toggle_line_numbers_act = QAction(_("Line Numbers"), window)
        window.toggle_line_numbers_act.setCheckable(True)
        window.toggle_line_numbers_act.setChecked(window.app_config.get('view_show_line_numbers', True))
        window.toggle_line_numbers_act.triggered.connect(window.toggle_line_numbers)

        window.toggle_spellcheck_act = QAction(_("Spell Checking"), window)
        window.toggle_spellcheck_act.setCheckable(True)
        window.toggle_spellcheck_act.setChecked(window.project_config.get('spellcheck_enabled', True))
        window.toggle_spellcheck_act.triggered.connect(window.toggle_spellcheck)

        window.dark_mode_act = QAction(_("Dark Mode"), window)
        window.dark_mode_act.setCheckable(True)
        window.dark_mode_act.setChecked(window.app_config.get('view_dark_mode', False))
        window.dark_mode_act.toggled.connect(window.toggle_dark_mode)

        window.config_act = QAction(_("App Settings"), window)
        window.config_act.triggered.connect(window.show_app_config_dialog)

        window.manage_snippets_act = QAction(_("Manage Snippets..."), window)
        window.manage_snippets_act.triggered.connect(window.show_snippet_manager)

        # Render Actions
        window.render_act = QAction(_("Render Site"), window)
        window.render_act.setShortcut("Ctrl+R")
        window.render_act.triggered.connect(window.run_renderer)

        window.open_browser_act = QAction(QIcon.fromTheme("web-browser"), _("Open in Browser"), window)
        window.open_browser_act.setToolTip(_("Opens the generated site in the default browser"))
        window.open_browser_act.triggered.connect(window.open_in_browser)

        # Help Actions
        window.about_act = QAction(_("About"), window)
        window.about_act.triggered.connect(window.show_about_dialog)
    def init_menu(self):
        window = self.window
        menubar = window.menuBar()

        # 1. File
        file_menu = menubar.addMenu(_("&File"))
        file_menu.addAction(window.new_act)
        file_menu.addAction(window.save_act)
        file_menu.addAction(window.insert_img_act)
        file_menu.addAction(window.insert_img_plugin_act)
        file_menu.addAction(window.insert_file_act)
        file_menu.addAction(window.emoji_act)
        file_menu.addSeparator()
        file_menu.addAction(window.switch_project_act)
        file_menu.addAction(window.create_project_act)
        file_menu.addAction(window.project_config_act)
        file_menu.addSeparator()
        file_menu.addAction(window.exit_act)

        # 2. Bearbeiten
        edit_menu = menubar.addMenu(_("&Edit"))
        edit_menu.addAction(window.undo_act)
        edit_menu.addAction(window.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(window.select_all_act)
        edit_menu.addSeparator()
        edit_menu.addAction(window.search_act)
        edit_menu.addAction(window.quick_open_act)
        edit_menu.addAction(window.replace_act)

        # 3. Ansicht
        view_menu = menubar.addMenu(_("&View"))
        view_menu.addAction(window.toolbar.toggleViewAction())
        view_menu.addAction(window.refresh_act)
        view_menu.addAction(window.toggle_preview_act)
        view_menu.addAction(window.toggle_line_numbers_act)
        view_menu.addAction(window.toggle_spellcheck_act)
        view_menu.addAction(window.dark_mode_act)
        view_menu.addSeparator()
        
        for dock in window.findChildren(QDockWidget):
            view_menu.addAction(dock.toggleViewAction())

        # 4. App Tools
        app_tools_menu = menubar.addMenu(_("&App Tools"))
        app_tools_menu.addAction(window.config_act)
        
        color_settings_action = QAction(_("Color Settings"), window)
        color_settings_action.triggered.connect(window.open_color_settings_dialog)
        app_tools_menu.addAction(color_settings_action)
        
        app_tools_menu.addSeparator()
        app_tools_menu.addAction(window.manage_snippets_act)

        app_tools_menu.addSeparator()
        window.populate_tools_menu(app_tools_menu, category="app")

        # 5. Project Tools
        project_tools_menu = menubar.addMenu(_("&Project Tools"))
        project_tools_menu.addAction(window.dashboard_act)
        project_tools_menu.addSeparator()
        project_tools_menu.addAction(window.manage_media_act)
        project_tools_menu.addAction(window.bulk_edit_frontmatter_act)
        project_tools_menu.addAction(window.manage_dictionary_act)
        project_tools_menu.addSeparator()

        window.populate_tools_menu(project_tools_menu, category="project")
        
        project_tools_menu.addSeparator()
        window.populate_tools_menu(project_tools_menu, category="export")


        # 6. Rendern
        render_menu = menubar.addMenu(_("&Render"))
        render_menu.addAction(window.render_act)
        render_menu.addAction(window.open_browser_act)

        # 7. Hilfe (inkl. About)
        window.help_menu = menubar.addMenu(_("&Help"))
        window.populate_help_menu(window.help_menu)
        window.help_menu.addAction(window.about_act)
    def populate_tools_menu(self, menu, category="project"):
        """
        Load tools from the workers directory and add them to the menu.
        Scans the workers directory and appends menu entries.

        :param menu: The menu to which tools will be added.
        :param category: The category of the tools to add ("app" or "project").
        """
        window = self.window
        if not os.path.exists(window.workers_dir):
            os.makedirs(window.workers_dir)
            return

        for filename in sorted(os.listdir(window.workers_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                file_path = os.path.join(window.workers_dir, filename)
                
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
                    
                    action = QAction(name, window)
                    # Lambda binds the path
                    action.triggered.connect(lambda checked, p=file_path, n=name: window.run_generic_worker(p, n))
                    menu.addAction(action)
                except Exception as e:
                    print(f"Error loading worker {filename}: {e}")
    def populate_help_menu(self, menu):
        """Load help files from assets/help and add them to the menu."""
        window = self.window
        help_dir = os.path.join(window.app_root, "assets", "help")
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
            action = QAction(title, window)
            action.triggered.connect(lambda checked, p=path: window.show_help(p))
            menu.addAction(action)
            
        if help_files:
            menu.addSeparator()
    def refresh_help_menu(self):
        window = self.window
        if hasattr(window, 'help_menu'):
            window.help_menu.clear()
            window.populate_help_menu(window.help_menu)
            window.help_menu.addAction(window.about_act)
    def init_toolbar(self):
        window = self.window
        window.toolbar = QToolBar("Main Toolbar")
        window.toolbar.setObjectName("MainToolbar")
        window.addToolBar(window.toolbar)
        
        show_toolbar = window.app_config.get('view_show_toolbar', True)
        window.toolbar.setVisible(show_toolbar)

        # Standard-Layout definieren
        window.default_toolbar_layout = [
            "dashboard_act", "separator",
            "new_act", "save_act", "separator",
            "undo_act", "redo_act", "separator",
            "insert_img_act", "insert_img_plugin_act", "insert_file_act", "gallery_act", "emoji_act", "separator",
            "search_act", "separator",
            "bold_act", "italic_act", "code_act", "separator",
            "h1_act", "h2_act", "h3_act", "separator",
            "ul_act", "ol_act", "table_act", "spacer",
            "render_act", "open_browser_act"
        ]

        # Layout aus Config laden oder Standard verwenden
        layout_config = window.app_config.get('toolbar_layout', window.default_toolbar_layout)
        window.app_config['toolbar_layout'] = layout_config

        for item in layout_config:
            if item == "separator" or item == "|":
                window.toolbar.addSeparator()
            elif item == "spacer" or item == ">":
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                window.toolbar.addWidget(spacer)
            elif hasattr(window, item):
                action = getattr(window, item)
                if isinstance(action, QAction):
                    window.toolbar.addAction(action)

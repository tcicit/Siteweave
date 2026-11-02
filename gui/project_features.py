import ast
import frontmatter
import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QMessageBox, QProgressDialog

from .dialogs.app_config_dialog import AppConfigDialog
from .dialogs.bulk_edit_dialog import BulkEditDialog
from .dialogs.color_settings_dialog import ColorSettingsDialog
from .dialogs.create_project_dialog import CreateProjectDialog
from .dialogs.dictionary_manager_dialog import DictionaryManagerDialog
from .dialogs.help_viewer import HelpViewer
from .dialogs.new_post_dialog import NewPostDialog
from .dialogs.project_config_dialog import ProjectConfigDialog
from .dialogs.project_launcher import ProjectLauncher
from .dialogs.snippet_manager_dialog import SnippetManagerDialog
from .window_dialogs import ProgressHelper, WorkerResultDialog, WorkerResultListDialog
from .workers import WorkerThread
from core.i18n import _


class ProjectFeaturesMixin:
    def show_project_config_dialog(self):
        config_path = os.path.join(self.project_root, "config.yaml")
        dialog = ProjectConfigDialog(config_path, self.app_root, self)
        if dialog.exec():
            self.project_config = self.load_project_config()
            self.init_spellchecker() # Sprache könnte sich geändert haben
            self.update_frontmatter_layouts()
    def show_bulk_edit_dialog(self):
        if not self._save_all_dirty_editors():
            return

        dialog = BulkEditDialog(self.project_root, self.content_dir)
        if dialog.exec():
            if self.current_file_path and os.path.exists(self.current_file_path):
                path = self.current_file_path
                editor = self.editor_tabs.get_editor_for_path(path)
                if editor is not None:
                    self._reload_editor(editor, path)
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
            self.preview.setVisible(show_preview)
            
            show_toolbar = self.app_config.get('view_show_toolbar', True)
            self.toolbar.setVisible(show_toolbar)
            
            show_line_numbers = self.app_config.get('view_show_line_numbers', True)
            self.toggle_line_numbers_act.setChecked(show_line_numbers)
            for editor in self._get_open_editors():
                editor.set_line_numbers_visible(show_line_numbers)

            # Schriftgröße anwenden
            font_size = self.app_config.get('editor_font_size', 12)
            font_family = self.app_config.get('editor_font_family', 'Monospace')
            
            for editor in self._get_open_editors():
                font = editor.font()
                font.setFamily(font_family)
                editor.setFont(font)
                editor.set_font_size(font_size)

            # Thumbnail-Größe für MediaLibrary aktualisieren
            media_thumb_size = self.app_config.get('media_thumbnail_size', 100)
            self.media_library.update_thumbnail_size(media_thumb_size)
            
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
                self.new_window = self.__class__(new_project_path)
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

        self.new_window = self.__class__(path)
        self.new_window.show()
        self.close()
    def run_renderer(self):
        """Triggers the site rendering process, with an optional backup step."""
        if not self._save_all_dirty_editors():
            return

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
            
            # Automatisch Vorschau für den Launcher generieren
            try:
                from gui.preview_generator import PreviewGenerator
                output_dir = self.project_config.get("site_output_directory", "site_output")
                self.preview_generator = PreviewGenerator(self.project_root, output_dir)
                self.preview_generator.start()
            except Exception as e:
                print(f"Vorschau-Generierung fehlgeschlagen: {e}")

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
                'media_thumbnail_size': self.app_config.get('media_thumbnail_size', 100),
                'editor_font_size': self.app_config.get('editor_font_size', 12),
                'editor_font_family': self.app_config.get('editor_font_family', 'Monospace'),
                'preview_font_family': self.app_config.get('preview_font_family', 'Sans Serif'),
                'preview_font_size': self.app_config.get('preview_font_size', 14),
                'action_icons': self.app_config.get('action_icons', self.default_action_icons),
                'toolbar_layout': self.app_config.get('toolbar_layout', getattr(self, 'default_toolbar_layout', [])),
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

            for editor in self._get_open_editors():
                if hasattr(editor, 'highlighter'):
                    editor.highlighter.set_custom_colors(color_scheme)
                    editor.highlighter.rehighlight()
                editor.set_custom_colors(color_scheme)
        except Exception as e:
            print(f"Error loading colors: {e}")
    def show_help(self, file_path):
        dark_mode = self.app_config.get('view_dark_mode', False)
        viewer = HelpViewer(file_path, self, dark_mode)
        viewer.exec()

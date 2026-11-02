import datetime
import os
import shutil

from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from .dialogs.emoji_picker import EmojiPicker
from .dialogs.search_dialog import SearchDialog
from core.i18n import _


class EditorFeaturesMixin:
    def on_text_changed(self, editor=None):
        editor = editor or self.editor
        if editor is not self.editor:
            return
        # Live-Update der Vorschau
        content = editor.toPlainText()
        self.preview.update_preview(content)
        self.outline.update_outline(content)
        self.editor_tabs.update_tab_title(editor)
        self.update_status_bar()
    def on_frontmatter_changed(self):
        self.frontmatter_modified = True
        self.editor.frontmatter_modified = True
        self.editor.metadata = self.frontmatter_panel.get_data()
        self.editor_tabs.update_tab_title(self.editor)
        self.update_status_bar()
    def update_font_size_config(self, size):
        self.app_config['editor_font_size'] = size
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
    def insert_image_plugin_dialog(self):
        """Öffnet einen Dateidialog und fügt das Bild über das Plugin ein."""
        if not self.current_file_path:
            QMessageBox.warning(self, _("Warning"), _("Please open a file first to insert an image."))
            return

        # Startverzeichnis: Ordner der aktuellen Datei
        start_dir = os.path.dirname(self.current_file_path)
            
        file_path, _filter = QFileDialog.getOpenFileName(
            self, _("Select Image"), start_dir, _("Images (*.png *.jpg *.jpeg *.gif *.svg *.webp);;All Files (*)")
        )
        
        if file_path:
            self.editor.insert_image_plugin(file_path)
            self.editor.setFocus()
    def show_media_manager_dialog(self):
        """Öffnet den erweiterten Medien-Manager."""
        thumbnail_size = self.app_config.get('media_thumbnail_size', 100)
        from .dialogs.media_manager_dialog import MediaManagerDialog
        dialog = MediaManagerDialog(self.project_root, self.assets_dir, self.content_dir, thumbnail_size, self)
        dialog.exec()
        # Sidebar Library aktualisieren falls offen
        if hasattr(self, 'media_library'):
            self.media_library.refresh_library()
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
        if hasattr(self, 'search_dialog') and self.search_dialog is not None:
            self.search_dialog.close()
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
        for editor in self._get_open_editors():
            editor.set_line_numbers_visible(checked)
        self.app_config['view_show_line_numbers'] = checked
    def toggle_spellcheck(self, checked):
        for editor in self._get_open_editors():
            editor.set_spellchecker_enabled(checked)
        self.project_config['spellcheck_enabled'] = checked
        self.project_config_manager.update({'spellcheck_enabled': checked})
        self.project_config_manager.save()
    def update_preview_font(self):
        font_family = self.app_config.get('preview_font_family', 'Sans Serif')
        font_size = self.app_config.get('preview_font_size', 14)
        
        if hasattr(self.preview, 'set_font_configuration'):
            self.preview.set_font_configuration(font_family, font_size)

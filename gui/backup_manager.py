from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QMessageBox)
import os
import zipfile
import shutil

from core.i18n import _

'''BackupManager: A dialog for managing backups of the content directory.
- Displays a list of available backup files (ZIP archives) in the backup directory.     
- Allows the user to restore a selected backup, which involves extracting the ZIP file and overwriting the current content directory. A confirmation dialog is shown before restoring to prevent accidental data loss.
- Allows the user to delete a selected backup file from the backup directory.
- The 'set_dark_mode(enabled)' method can be called to apply dark mode styling to the panel-specific widgets.
- The dialog is modal and blocks interaction with the main window until it is closed.
'''

class BackupManager(QDialog):
    def __init__(self, backup_dir, content_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Backup Manager"))
        self.resize(400, 300)
        self.backup_dir = backup_dir
        self.content_dir = content_dir

        layout = QVBoxLayout(self)

        # Backup-Liste
        self.backup_list = QListWidget()
        self.load_backups()
        layout.addWidget(self.backup_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.restore_button = QPushButton(_("Restore"))
        self.restore_button.clicked.connect(self.restore_backup)
        button_layout.addWidget(self.restore_button)

        self.delete_button = QPushButton(_("Delete"))
        self.delete_button.clicked.connect(self.delete_backup)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

    def load_backups(self):
        self.backup_list.clear()
        if os.path.exists(self.backup_dir):
            backups = sorted(os.listdir(self.backup_dir), reverse=True)
            for backup in backups:
                self.backup_list.addItem(backup)

    def restore_backup(self):
        selected_item = self.backup_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, _("Error"), _("Please select a backup."))
            return

        backup_file = os.path.join(self.backup_dir, selected_item.text())
        
        confirm = QMessageBox.warning(
            self, 
            _("Warning"), 
            _("Do you really want to overwrite the content of '{content_dir}' with the backup?\nCurrent changes will be lost!").format(content_dir=self.content_dir),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # 1. Content-Ordner leeren (optional, aber sauberer)
                for filename in os.listdir(self.content_dir):
                    file_path = os.path.join(self.content_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"Fehler beim Löschen von {file_path}: {e}")

                # 2. Backup entpacken
                with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                    zip_ref.extractall(self.content_dir)
                
                QMessageBox.information(self, _("Success"), _("Backup successfully restored."))
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Error restoring backup: {e}").format(e=e))

    def delete_backup(self):
        selected_item = self.backup_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, _("Error"), _("Please select a backup."))
            return

        backup_file = os.path.join(self.backup_dir, selected_item.text())
        try:
            os.remove(backup_file)
            self.load_backups()
            QMessageBox.information(self, _("Deleted"), _("Backup {backup_file} was deleted.").format(backup_file=backup_file))
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not delete backup: {e}").format(e=e))
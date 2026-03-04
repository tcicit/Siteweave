from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QDateEdit, QCheckBox, QDialogButtonBox, QMessageBox, QSpinBox)
from PyQt6.QtCore import QDate
import os
import re
from core.i18n import _

class NewPostDialog(QDialog):
    def __init__(self, content_dir, parent=None, initial_dir=None, default_template="full-width", template_dirs=None):
        super().__init__(parent)
        self.setWindowTitle(_("Create New Post"))
        self.resize(450, 350)
        self.content_dir = content_dir
        self.default_template = default_template
        self.template_dirs = template_dirs
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Titel
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(_("Post Title"))
        self.title_input.textChanged.connect(self.update_filename)
        self.title_input.textChanged.connect(self.validate_fields)
        form.addRow(_("Title:"), self.title_input)
        
        # Autor
        self.author_input = QLineEdit()
        self.author_input.setText("TCI")
        form.addRow(_("Author:"), self.author_input)
        
        # Dateiname (automatisch generiert, aber editierbar)
        self.filename_input = QLineEdit()
        self.filename_input.textChanged.connect(self.validate_fields)
        form.addRow(_("Filename:"), self.filename_input)
        
        # Ordner Auswahl
        self.dir_combo = QComboBox()
        self.populate_dirs()
        
        # Falls ein Startordner übergeben wurde, diesen auswählen
        if initial_dir:
            try:
                rel_path = os.path.relpath(initial_dir, self.content_dir)
                if rel_path == ".":
                    index = self.dir_combo.findText(".")
                else:
                    index = self.dir_combo.findText(rel_path)
                if index >= 0:
                    self.dir_combo.setCurrentIndex(index)
            except ValueError:
                pass # Pfad liegt ausserhalb

        form.addRow(_("Folder:"), self.dir_combo)
        
        # Layout Auswahl
        self.layout_combo = QComboBox()
        self.populate_layouts()
        
        # Standard-Template auswählen
        index = self.layout_combo.findText(self.default_template)
        if index >= 0:
            self.layout_combo.setCurrentIndex(index)
        form.addRow(_("Layout:"), self.layout_combo)
        
        # Datum
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setCalendarPopup(True)
        form.addRow(_("Date:"), self.date_input)

        # Gewichtung
        self.weight_input = QSpinBox()
        self.weight_input.setRange(-1000, 1000)
        self.weight_input.setValue(0)
        self.weight_input.setToolTip(_("Niedrigere Zahlen erscheinen zuerst."))
        
        # ... (beim Hinzufügen zum Layout)
        form.addRow(_("Weight:"), self.weight_input)

        
        # Tags
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText(_("tag1, tag2 (comma separated)"))
        form.addRow(_("Tags:"), self.tags_input)
        
        # Entwurf
        self.draft_check = QCheckBox(_("Mark as Draft"))
        form.addRow("", self.draft_check)
        
        layout.addLayout(form)
        
        # Buttons (OK / Abbrechen)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Initiale Validierung
        self.validate_fields()

    def populate_dirs(self):
        """Füllt die ComboBox mit Unterordnern aus dem Content-Verzeichnis."""
        self.dir_combo.addItem(".") # Root
        for root, dirs, files in os.walk(self.content_dir):
            dirs.sort()
            for d in dirs:
                if not d.startswith('.') and not d.startswith('_'):
                    rel_path = os.path.relpath(os.path.join(root, d), self.content_dir)
                    self.dir_combo.addItem(rel_path)

    def populate_layouts(self):
        """Füllt die ComboBox mit verfügbaren Layouts aus dem templates-Ordner."""
        self.layout_combo.addItem("full-width") # Standard
        
        dirs_to_scan = self.template_dirs if self.template_dirs else []
        if not dirs_to_scan:
            # Fallback: Versuche Templates zu finden (Sibling von content_dir)
            project_root = os.path.dirname(self.content_dir)
            dirs_to_scan = [os.path.join(project_root, "templates")]
        
        added = {"full-width"}
        for d in dirs_to_scan:
            if os.path.exists(d):
                for filename in os.listdir(d):
                    if filename.startswith("layout_") and filename.endswith(".html"):
                        layout_name = filename[7:-5]
                        if layout_name not in added:
                            self.layout_combo.addItem(layout_name)
                            added.add(layout_name)

    def update_filename(self, text):
        """Generiert einen Dateinamen aus dem Titel (Slugify)."""
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        if slug:
            self.filename_input.setText(f"{slug}.md")
        else:
            self.filename_input.clear()

    def validate_fields(self):
        # Visuelle Validierung für Pflichtfelder
        if not self.title_input.text().strip():
            self.title_input.setStyleSheet("border: 2px solid #e74c3c;")
        else:
            self.title_input.setStyleSheet("")
            
        if not self.filename_input.text().strip():
            self.filename_input.setStyleSheet("border: 2px solid #e74c3c;")
        else:
            self.filename_input.setStyleSheet("")

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, _("Error"), _("Please enter a title."))
            return
        if not self.filename_input.text().strip():
            QMessageBox.warning(self, _("Error"), _("Please enter a filename."))
            return
        self.accept()

    def get_data(self):
        return {
            'title': self.title_input.text().strip(),
            'author': self.author_input.text().strip(),
            'filename': self.filename_input.text().strip(),
            'directory': self.dir_combo.currentText(),
            'layout': self.layout_combo.currentText(),
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'weight': self.weight_input.value(),
            'tags': [t.strip() for t in self.tags_input.text().split(',') if t.strip()],
            'draft': self.draft_check.isChecked()
        }
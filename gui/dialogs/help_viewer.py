import os
import frontmatter
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QHBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWebEngineCore import QWebEnginePage
from gui.preview_widget import PreviewWidget
from core.i18n import _

class HelpViewer(QDialog):
    def __init__(self, file_path, parent=None, dark_mode=False):
        super().__init__(parent)
        self.setWindowTitle(_("Help"))
        self.resize(900, 700)
        
        # Fenster-Flags setzen, damit es sich wie ein echtes Fenster verhält (Maximieren, Schließen)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinMaxButtonsHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Suchleiste
        self.search_widget = QWidget()
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(10, 10, 10, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search..."))
        self.search_input.returnPressed.connect(self.find_next)
        
        self.prev_btn = QPushButton("▲")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.clicked.connect(self.find_prev)
        
        self.next_btn = QPushButton("▼")
        self.next_btn.setFixedWidth(30)
        self.next_btn.clicked.connect(self.find_next)
        
        search_layout.addWidget(QLabel(_("Search:")))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.prev_btn)
        search_layout.addWidget(self.next_btn)
        
        layout.addWidget(self.search_widget)
        self.search_widget.hide()

        self.preview = PreviewWidget()
        self.preview.set_dark_mode(dark_mode)
        
        # Basis-Pfad setzen, damit Bilder korrekt geladen werden
        self.preview.set_base_path(file_path)
        
        layout.addWidget(self.preview)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        
        search_btn = QPushButton(_("Search"))
        search_btn.setShortcut("Ctrl+F")
        search_btn.clicked.connect(self.toggle_search)

        export_btn = QPushButton(_("Export PDF"))
        export_btn.clicked.connect(self.export_pdf)

        print_btn = QPushButton(_("Print"))
        print_btn.clicked.connect(self.print_page)
        
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 0, 10, 10)
        btn_layout.addWidget(search_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(print_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(button_box)
        layout.addLayout(btn_layout)
        
        self.load_content(file_path)

    def load_content(self, file_path):
        try:
            post = frontmatter.load(file_path)
            title = post.metadata.get('title', os.path.basename(file_path))
            self.setWindowTitle(_("Help - {title}").format(title=title))
            self.preview.update_preview(post.content)
        except Exception as e:
            self.preview.setHtml(f"<html><body><h1>{_('Error')}</h1><p>{_('Could not load file: {e}').format(e=e)}</p></body></html>")

    def find_next(self):
        text = self.search_input.text()
        if text:
            self.preview.findText(text)
        else:
            self.preview.findText("")

    def find_prev(self):
        text = self.search_input.text()
        if text:
            self.preview.findText(text, QWebEnginePage.FindFlag.FindBackward)

    def toggle_search(self):
        is_hidden = self.search_widget.isHidden()
        self.search_widget.setVisible(is_hidden)
        if is_hidden:
            self.search_input.setFocus()
            self.search_input.selectAll()

    def print_page(self):
        # PyQt6 WebEngine hat keine direkte Druckfunktion mehr.
        # Wir nutzen die Browser-eigene Druckfunktion via JavaScript.
        self.preview.page().runJavaScript("window.print();")

    def export_pdf(self):
        filename, _filter = QFileDialog.getSaveFileName(self, _("Export PDF"), "", _("PDF Files (*.pdf)"))
        if filename:
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            
            self.preview.page().printToPdf(filename)

    def keyPressEvent(self, event: QKeyEvent):
        """Fügt Tastenkürzel hinzu."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
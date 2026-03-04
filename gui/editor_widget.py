import os
import re
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QFontDatabase, QDragEnterEvent, QDropEvent, QPalette, QColor, QTextCursor, QPainter, QPaintEvent, QTextFormat
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QSize
from gui.syntax import MarkdownHighlighter

from core.i18n import _

'''
EditorWidget: A custom QPlainTextEdit for editing Markdown files.
- Supports line numbers in a dedicated area on the left.
- Implements drag-and-drop for files, inserting appropriate Markdown links.
- Provides methods for toggling bold, italic, code formatting, headers, lists, and tables   based on the current selection.
- The 'set_dark_mode(enabled)' method can be called to apply dark mode styling to the editor and its syntax highlighter.    
- The editor emits a 'fontSizeChanged' signal when the font size is changed via Ctrl + Mouse Wheel, allowing the MainWindow to update the UI accordingly.
'''


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent):
        self.editor.line_number_area_paint_event(event)

class EditorWidget(QPlainTextEdit):
    fontSizeChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.file_path = None
        self.show_line_numbers = True
        self.custom_colors = {}

        # Versuche eine Monospace-Schriftart (wie Courier) zu setzen
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)
        
        self.setPlaceholderText(_("Select a file on the left to edit..."))

        # Zeilennummern-Area initialisieren
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

        # Syntax Highlighting aktivieren
        self.highlighter = MarkdownHighlighter(self.document())

    def line_number_area_width(self):
        if not self.show_line_numbers:
            return 0
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits + 10 # +10 padding
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def set_line_numbers_visible(self, visible):
        self.show_line_numbers = visible
        self.update_line_number_area_width(0)

    def set_custom_colors(self, colors):
        self.custom_colors = colors
        self.highlight_current_line()

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        # Hintergrundfarbe anpassen (etwas dunkler/heller als Editor)
        bg_color = self.palette().color(QPalette.ColorRole.Base).darker(105)
        painter.fillRect(event.rect(), bg_color)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.palette().color(QPalette.ColorRole.Text))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            bg_color = self.palette().color(QPalette.ColorRole.Base)
            
            # Prüfe zuerst auf benutzerdefinierte Farbe
            custom_color = self.custom_colors.get('current_line')
            if custom_color:
                line_color = QColor(custom_color)
            elif bg_color.lightness() < 128:
                line_color = QColor("#303030") # Dark Mode Default
            else:
                line_color = QColor("#e6f3ff") # Light Mode Default

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def set_font_size(self, size):
        font = self.font()
        font.setPointSize(int(size))
        self.setFont(font)
        self.fontSizeChanged.emit(int(size))

    def set_dark_mode(self, enabled):
        p = self.palette()
        if enabled:
            p.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
            p.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        else:
            p.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
            p.setColor(QPalette.ColorRole.Text, QColor("#000000"))
        self.setPalette(p)
        self.highlighter.set_theme(enabled)
        self.highlight_current_line() # Update current line highlight color

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if not file_path:
                    file_path = url.toString()
                self.insert_file_link(file_path)
        else:
            super().dropEvent(event)

    def insert_file_link(self, target_path):
        # Externe Links direkt einfügen
        if target_path.startswith(('http:', 'https:', 'mailto:')):
            self.insertPlainText(f"[{target_path}]({target_path})")
            return

        # Relativen Pfad berechnen, falls wir wissen, wo wir sind
        rel_path = target_path
        if self.file_path:
            try:
                base_dir = os.path.dirname(self.file_path)
                rel_path = os.path.relpath(target_path, base_dir)
                # Windows Backslashes in Slashes umwandeln für Markdown
                rel_path = rel_path.replace(os.path.sep, '/')
            except ValueError:
                pass # Pfade auf unterschiedlichen Laufwerken
        
        filename = os.path.basename(target_path)
        ext = os.path.splitext(target_path)[1].lower()
        is_image = ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
        
        if is_image:
            self.insertPlainText(f"![{filename}]({rel_path})")
        else:
            # Bei Markdown-Dateien die Endung im Link auf .html ändern
            if ext in ['.md', '.markdown']:
                base, _ = os.path.splitext(rel_path)
                rel_path = f"{base}.html"
            
            self.insertPlainText(f"[{filename}]({rel_path})")

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            font = self.font()
            size = font.pointSize()
            
            if delta > 0:
                size += 1
            elif delta < 0:
                size = max(8, size - 1)
            
            self.set_font_size(size)
            event.accept()
        else:
            super().wheelEvent(event)

    # --- Formatierungs-Funktionen ---

    def toggle_bold(self):
        self._surround_selection("**")

    def toggle_italic(self):
        self._surround_selection("*")

    def toggle_code(self):
        self._surround_selection("`")

    def _surround_selection(self, symbol):
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            # Einfacher Check, ob bereits umschlossen (könnte verbessert werden)
            if text.startswith(symbol) and text.endswith(symbol) and len(text) >= 2*len(symbol):
                 cursor.insertText(text[len(symbol):-len(symbol)])
            else:
                cursor.insertText(f"{symbol}{text}{symbol}")
        else:
            # Kein Text markiert: Symbol einfügen und Cursor dazwischen setzen
            cursor.insertText(f"{symbol}{symbol}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(symbol))
            self.setTextCursor(cursor)
        self.setFocus()

    def set_header(self, level):
        """Setzt oder entfernt Überschriften (H1-H6) für die markierten Zeilen."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # Selektion auf ganze Blöcke erweitern
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        start_block = cursor.block().blockNumber()
        
        cursor.setPosition(end)
        # Wenn Selektion am Anfang eines Blocks endet, diesen nicht mit einbeziehen (außer es ist der gleiche)
        if cursor.atBlockStart() and end > start:
             cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
        end_block = cursor.block().blockNumber()
        
        block = self.document().findBlockByNumber(start_block)
        while block.isValid() and block.blockNumber() <= end_block:
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            text = cursor.selectedText()
            
            # Bestehende Header-Marker entfernen
            clean_text = re.sub(r'^#+\s*', '', text)
            
            if level > 0:
                new_text = f"{'#' * level} {clean_text}"
            else:
                new_text = clean_text
                
            cursor.insertText(new_text)
            block = block.next()
            
        cursor.endEditBlock()
        self.setFocus()

    def toggle_list(self, ordered=False):
        """Schaltet Listenformatierung für markierte Zeilen um."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        start_block = cursor.block().blockNumber()
        
        cursor.setPosition(end)
        if cursor.atBlockStart() and end > start:
             cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
        end_block = cursor.block().blockNumber()
        
        # Prüfen, ob wir hinzufügen oder entfernen (basierend auf der ersten Zeile)
        block = self.document().findBlockByNumber(start_block)
        text = block.text()
        is_list = bool(re.match(r'^\s*\d+\.\s', text)) if ordered else bool(re.match(r'^\s*-\s', text))
        remove = is_list
        
        block = self.document().findBlockByNumber(start_block)
        i = 1
        while block.isValid() and block.blockNumber() <= end_block:
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            text = cursor.selectedText()
            
            if remove:
                pattern = r'^\s*\d+\.\s*' if ordered else r'^\s*-\s*'
                new_text = re.sub(pattern, '', text)
            else:
                prefix = f"{i}. " if ordered else "- "
                new_text = f"{prefix}{text}"
                i += 1
            
            cursor.insertText(new_text)
            block = block.next()
            
        cursor.endEditBlock()
        self.setFocus()

    def insert_table(self, rows, cols):
        cursor = self.textCursor()
        # Ensure start on new line if not already
        if cursor.positionInBlock() > 0:
            cursor.insertText("\n")
        
        text = ""
        # Header
        text += "| " + " | ".join([f"Header {i+1}" for i in range(cols)]) + " |\n"
        # Separator
        text += "| " + " | ".join(["---"] * cols) + " |\n"
        # Body
        for _ in range(rows):
            text += "| " + " | ".join(["   "] * cols) + " |\n"
            
        cursor.insertText(text)
        self.setFocus()
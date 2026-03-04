from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QSizePolicy, QHBoxLayout, QCheckBox
from PyQt6.QtCore import QTimer, QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
import os
from core.i18n import _

'''
LogViewerPanel: A panel for viewing log files.
- Displays log content in a QPlainTextEdit widget.
- Provides controls for refreshing, auto-refreshing, and clearing the log.
- Applies syntax highlighting to different log levels (ERROR, WARNING, INFO).
- The 'set_dark_mode(enabled)' method can be called to apply dark mode styling to the panel-specific widgets.
- The panel can be toggled between expanded and collapsed states, and it adapts its size accordingly.
'''

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.dark_mode = False
        self.update_colors()

    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self.update_colors()
        self.rehighlight()

    def update_colors(self):
        if self.dark_mode:
            self.color_error = QColor("#ff5555")
            self.color_warn = QColor("#ffb86c")
            self.color_info = QColor("#8be9fd")
        else:
            self.color_error = QColor("#c0392b")
            self.color_warn = QColor("#d35400")
            self.color_info = QColor("#2980b9")

    def highlightBlock(self, text):
        text_upper = text.upper()
        
        if "ERROR" in text_upper or "CRITICAL" in text_upper or "FEHLER" in text_upper:
            fmt = QTextCharFormat()
            fmt.setForeground(self.color_error)
            fmt.setFontWeight(QFont.Weight.Bold)
            self.setFormat(0, len(text), fmt)
            
        elif "WARNING" in text_upper or "WARNUNG" in text_upper:
            fmt = QTextCharFormat()
            fmt.setForeground(self.color_warn)
            self.setFormat(0, len(text), fmt)
            
        elif "INFO" in text_upper:
            fmt = QTextCharFormat()
            fmt.setForeground(self.color_info)
            expression = QRegularExpression(r"\bINFO\b")
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class LogViewerPanel(QWidget):
    def __init__(self, log_file_path):
        super().__init__()
        self.log_file_path = log_file_path
        self.last_mtime = 0
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle Button (Konsistent mit anderen Panels)
        self.toggle_btn = QPushButton(_("Logs ▼"))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                font-weight: bold;
                padding: 6px;
                border: 1px solid palette(mid);
                background-color: palette(button);
            }
        """)
        self.toggle_btn.toggled.connect(self.toggle_content)
        layout.addWidget(self.toggle_btn)

        # Content Widget
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls (Refresh, Auto-Refresh, Clear)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(5, 5, 5, 5)
        
        self.refresh_btn = QPushButton(_("Refresh"))
        self.refresh_btn.clicked.connect(self.reload_log)
        controls_layout.addWidget(self.refresh_btn)
        
        self.auto_refresh_cb = QCheckBox(_("Auto-Refresh"))
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_cb)
        
        self.clear_btn = QPushButton(_("Clear"))
        self.clear_btn.clicked.connect(self.clear_log)
        controls_layout.addWidget(self.clear_btn)
        
        controls_layout.addStretch()
        content_layout.addLayout(controls_layout)

        # Text Area
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        font = self.text_edit.font()
        font.setFamily("Monospace")
        font.setStyleHint(font.StyleHint.Monospace)
        self.text_edit.setFont(font)
        content_layout.addWidget(self.text_edit)
        
        self.highlighter = LogHighlighter(self.text_edit.document())
        
        layout.addWidget(self.content_widget)

        # Timer für Auto-Refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_and_reload)
        self.timer.start(2000) # Alle 2 Sekunden prüfen

        # Initial laden
        self.reload_log()

    def set_dark_mode(self, enabled):
        self.toggle_btn.style().unpolish(self.toggle_btn)
        self.toggle_btn.style().polish(self.toggle_btn)
        self.highlighter.set_dark_mode(enabled)

    def toggle_content(self, checked):
        self.content_widget.setVisible(checked)
        self.toggle_btn.setText(_("Logs ▼") if checked else _("Logs ▶"))
        
        if checked:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.setMaximumHeight(16777215)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.setMaximumHeight(self.toggle_btn.sizeHint().height())

    def toggle_auto_refresh(self, checked):
        if checked:
            self.timer.start(2000)
        else:
            self.timer.stop()

    def check_and_reload(self):
        if os.path.exists(self.log_file_path):
            try:
                mtime = os.path.getmtime(self.log_file_path)
                if mtime > self.last_mtime:
                    self.reload_log()
            except OSError:
                pass

    def reload_log(self):
        if not os.path.exists(self.log_file_path):
            self.text_edit.setPlainText(_("Waiting for logs..."))
            return

        try:
            # Lese nur die letzten 50KB um Performance-Probleme bei riesigen Logs zu vermeiden
            file_size = os.path.getsize(self.log_file_path)
            read_size = 50 * 1024
            
            with open(self.log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                if file_size > read_size:
                    f.seek(file_size - read_size)
                    content = f.read()
                    # Erste (wahrscheinlich unvollständige) Zeile verwerfen
                    first_newline = content.find('\n')
                    if first_newline != -1:
                        content = content[first_newline+1:]
                    content = _("... [older logs hidden] ...\n{content}").format(content=content)
                else:
                    content = f.read()
                
                scrollbar = self.text_edit.verticalScrollBar()
                was_at_bottom = scrollbar.value() == scrollbar.maximum()
                
                self.text_edit.setPlainText(content)
                
                if was_at_bottom:
                    self.text_edit.moveCursor(self.text_edit.textCursor().MoveOperation.End)
                
            self.last_mtime = os.path.getmtime(self.log_file_path)
        except Exception as e:
            self.text_edit.setPlainText(_("Error reading logs: {e}").format(e=e))

    def clear_log(self):
        # Versuche die Datei zu leeren
        try:
            open(self.log_file_path, 'w').close()
            self.reload_log()
        except:
            self.text_edit.clear()
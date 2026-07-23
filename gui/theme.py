from PyQt6.QtGui import QPalette, QColor

'''
Docstring for main_window
Main application window.
Contains the file explorer, editor, preview and various panels.
Manages app and project configuration, actions, menus and toolbars.
Allows loading, editing and saving Markdown files with frontmatter.
Supports themes, localization and running worker scripts.
The main class is `MainWindow`, which inherits from `QMainWindow`.

'''


def apply_dark_theme(app):
    """Setzt ein dunkles Theme für die gesamte App."""
    app.setStyle("Fusion")
    
    palette = QPalette()
    dark_gray = QColor(45, 45, 45)
    gray = QColor(127, 127, 127)
    black = QColor(25, 25, 25)
    blue = QColor(42, 130, 218)
    white = QColor(255, 255, 255)

    palette.setColor(QPalette.ColorRole.Window, dark_gray)
    palette.setColor(QPalette.ColorRole.WindowText, white)
    palette.setColor(QPalette.ColorRole.Base, black)
    palette.setColor(QPalette.ColorRole.AlternateBase, dark_gray)
    palette.setColor(QPalette.ColorRole.ToolTipBase, blue)
    palette.setColor(QPalette.ColorRole.ToolTipText, white)
    palette.setColor(QPalette.ColorRole.Text, white)
    palette.setColor(QPalette.ColorRole.Button, dark_gray)
    palette.setColor(QPalette.ColorRole.ButtonText, white)
    palette.setColor(QPalette.ColorRole.Link, blue)
    palette.setColor(QPalette.ColorRole.Highlight, blue)
    palette.setColor(QPalette.ColorRole.HighlightedText, black)

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, gray)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, gray)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, gray)

    app.setPalette(palette)

    app.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }
        QDockWidget::title {
            background: #353535;
            text-align: center;
            padding: 5px;
        }
        /* Fix für helle Panels in der rechten Leiste */
        QScrollArea, QTabWidget::pane {
            background-color: #2d2d2d;
            border: none;
        }
        /* Eingabefelder */
        QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox {
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #555;
        }
        /* Listen und Bäume */
        QTreeView, QListView, QTableView {
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #555;
        }
        /* Menüs */
        QMenuBar, QMenu {
            background-color: #353535;
            color: white;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #2a82da;
        }
        /* Splitter */
        QSplitter::handle {
            background-color: #454545;
        }
    """)

def apply_light_theme(app):
    """Setzt ein helles Theme für die gesamte App."""
    app.setStyle("Fusion")

    palette = QPalette()
    light_gray = QColor(240, 240, 240)
    white = QColor(255, 255, 255)
    black = QColor(0, 0, 0)
    blue = QColor(42, 130, 218)
    gray = QColor(127, 127, 127)

    palette.setColor(QPalette.ColorRole.Window, light_gray)
    palette.setColor(QPalette.ColorRole.WindowText, black)
    palette.setColor(QPalette.ColorRole.Base, white)
    palette.setColor(QPalette.ColorRole.AlternateBase, light_gray)
    palette.setColor(QPalette.ColorRole.ToolTipBase, white)
    palette.setColor(QPalette.ColorRole.ToolTipText, black)
    palette.setColor(QPalette.ColorRole.Text, black)
    palette.setColor(QPalette.ColorRole.Button, light_gray)
    palette.setColor(QPalette.ColorRole.ButtonText, black)
    palette.setColor(QPalette.ColorRole.Link, blue)
    palette.setColor(QPalette.ColorRole.Highlight, blue)
    palette.setColor(QPalette.ColorRole.HighlightedText, white)

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, gray)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, gray)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, gray)

    app.setPalette(palette)

    # Stylesheet zurücksetzen (entfernt die Dark-Mode Anpassungen)
    app.setStyleSheet("")
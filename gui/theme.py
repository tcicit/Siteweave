from pathlib import Path

from PyQt6.QtGui import QPalette, QColor

"""
Theme definitions for the Siteweave application.
Provides functions to configure dark and light palettes and styles.
"""


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

    stylesheet = Path(__file__).with_name("themes").joinpath("dark.qss").read_text(encoding="utf-8")
    app.setStyleSheet(stylesheet)

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

    stylesheet = Path(__file__).with_name("themes").joinpath("light.qss").read_text(encoding="utf-8")
    app.setStyleSheet(stylesheet)
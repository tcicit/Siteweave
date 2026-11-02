"""Application theme orchestration."""

import os

from PyQt6.QtGui import QColor, QIcon, QPainter
from PyQt6.QtWidgets import QApplication

from .theme import apply_dark_theme, apply_light_theme


class ThemeManager:
    """Applies application styles and propagates theme changes to widgets."""

    def __init__(self, window):
        self.window = window

    def apply_theme(self, dark_mode):
        window = self.window
        app = QApplication.instance()
        (apply_dark_theme if dark_mode else apply_light_theme)(app)

        for editor in window._get_open_editors():
            editor.set_dark_mode(dark_mode)
        window.preview.set_dark_mode(dark_mode)
        self.update_icons(dark_mode)

        for panel in window.sidebar_panels.values():
            if hasattr(panel, "set_dark_mode"):
                panel.set_dark_mode(dark_mode)
        window.dashboard.set_dark_mode(dark_mode)
        window.apply_custom_colors()

    def update_icons(self, dark_mode):
        window = self.window
        icon_folder = os.path.join(window.app_root, "assets", "icons")
        color = QColor("#ffffff") if dark_mode else QColor("#333333")

        for action_name, icon_name in window.action_icons.items():
            action = getattr(window, action_name, None)
            if action is None:
                continue
            if icon_name.endswith(".svg"):
                svg_path = icon_name if os.path.isabs(icon_name) else os.path.join(window.app_root, icon_name)
            else:
                svg_path = os.path.join(icon_folder, f"{icon_name}.svg")

            if os.path.exists(svg_path):
                pixmap = QIcon(svg_path).pixmap(24, 24)
                if not pixmap.isNull():
                    painter = QPainter(pixmap)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    painter.fillRect(pixmap.rect(), color)
                    painter.end()
                    action.setIcon(QIcon(pixmap))

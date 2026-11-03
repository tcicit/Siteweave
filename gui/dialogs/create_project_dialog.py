import os
import re
import shutil
import tempfile
import yaml
from datetime import date

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QComboBox, QDialogButtonBox,
    QFileDialog, QMessageBox, QSizePolicy, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from core import APP_NAME
from core.config_manager import ConfigManager
from core.i18n import _


class CreateProjectDialog(QDialog):
    """
    Kompakter, moderner Dialog zum Anlegen eines neuen Projekts.
    Fragt nur die wesentlichen Basisdaten ab (Name, Speicherort, Theme, Sprache)
    und belegt alle weiteren Optionen automatisch mit sinnvollen Standardwerten.
    """

    LANGUAGES = [
        ("de_DE", "Deutsch (Deutschland) [de_DE]"),
        ("de_CH", "Deutsch (Schweiz) [de_CH]"),
        ("de_AT", "Deutsch (Österreich) [de_AT]"),
        ("en_US", "English (US) [en_US]"),
        ("en_GB", "English (UK) [en_GB]"),
        ("fr_FR", "Français (France) [fr_FR]"),
        ("fr_CA", "Français (Canada) [fr_CA]"),
        ("es_ES", "Español (España) [es_ES]"),
    ]

    def __init__(self, app_root, parent=None):
        super().__init__(parent)
        self.app_root = app_root
        self.created_project_path = None

        self.setWindowTitle(_("Create New Project"))
        self.setMinimumWidth(620)

        # App Icon setzen falls vorhanden
        icon_path = os.path.join(self.app_root, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title_lbl = QLabel(_("Create New Project"))
        title_font = title_lbl.font()
        title_font.setPointSize(title_font.pointSize() + 3)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        header_layout.addWidget(title_lbl)

        subtitle_lbl = QLabel(_("Set up a new static website with a few essential details."))
        subtitle_lbl.setStyleSheet("color: palette(placeholder-text);")
        header_layout.addWidget(subtitle_lbl)

        main_layout.addLayout(header_layout)

        # Trennlinie
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(sep)

        # 2. Formular-Bereich: Projektdaten
        form_group = QGroupBox(_("Project Information"))
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Projektname
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(_("e.g. My Website"))
        self.name_input.textChanged.connect(self.update_path_preview)
        form_layout.addRow(_("Project Name:"), self.name_input)

        # Speicherort
        location_layout = QHBoxLayout()
        location_layout.setContentsMargins(0, 0, 0, 0)
        location_layout.setSpacing(8)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(_("Select parent directory"))
        self.path_input.setText(self._determine_default_location())
        self.path_input.textChanged.connect(self.update_path_preview)

        self.browse_btn = QPushButton(_("Browse..."))
        self.browse_btn.clicked.connect(self.browse_location)

        location_layout.addWidget(self.path_input)
        location_layout.addWidget(self.browse_btn)
        form_layout.addRow(_("Location:"), location_layout)

        # Live-Pfadvorschau
        self.path_preview_lbl = QLabel()
        self.path_preview_lbl.setStyleSheet("padding: 4px 0; font-size: 11px;")
        self.path_preview_lbl.setWordWrap(True)
        form_layout.addRow("", self.path_preview_lbl)

        # Sprache der Website
        self.lang_combo = QComboBox()
        for code, label in self.LANGUAGES:
            self.lang_combo.addItem(label, code)
        self._preselect_language()
        form_layout.addRow(_("Language:"), self.lang_combo)

        main_layout.addWidget(form_group)

        # 3. Theme / Design-Vorlage Bereich
        theme_group = QGroupBox(_("Design & Theme"))
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.setSpacing(16)

        # Linke Seite: Theme-Auswahl
        theme_left = QVBoxLayout()
        theme_left.setSpacing(8)

        theme_lbl = QLabel(_("Select a template theme:"))
        theme_left.addWidget(theme_lbl)

        self.theme_combo = QComboBox()
        self.theme_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._populate_themes()
        self.theme_combo.currentIndexChanged.connect(self.update_theme_preview)
        theme_left.addWidget(self.theme_combo)

        theme_desc = QLabel(_("Themes define the styling and page layouts of your website."))
        theme_desc.setStyleSheet("color: palette(placeholder-text); font-size: 11px;")
        theme_desc.setWordWrap(True)
        theme_left.addWidget(theme_desc)
        theme_left.addStretch()

        theme_layout.addLayout(theme_left, stretch=3)

        # Rechte Seite: Theme-Vorschau
        self.theme_preview = QLabel(_("No preview available"))
        self.theme_preview.setFixedSize(200, 112)
        self.theme_preview.setStyleSheet(
            "border: 1px solid palette(mid); background: palette(alternate-base); border-radius: 4px;"
        )
        self.theme_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        theme_layout.addWidget(self.theme_preview, stretch=2)

        main_layout.addWidget(theme_group)

        # 4. Hinweis
        hint_lbl = QLabel(
            _("💡 All other settings (SEO, navigation menus, backups, PDF export) are pre-configured with sensible defaults and can be customized at any time via Project Settings.")
        )
        hint_lbl.setStyleSheet("color: palette(placeholder-text); font-size: 11px;")
        hint_lbl.setWordWrap(True)
        main_layout.addWidget(hint_lbl)

        # 5. Buttons
        self.buttons = QDialogButtonBox()
        self.cancel_btn = self.buttons.addButton(_("Cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        self.create_btn = self.buttons.addButton(_("Create Project"), QDialogButtonBox.ButtonRole.AcceptRole)
        self.create_btn.setDefault(True)

        self.buttons.accepted.connect(self.create_project)
        self.buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.buttons)

        # Initialisierungen
        self.update_path_preview()
        self.update_theme_preview()
        self.name_input.setFocus()

    def _determine_default_location(self):
        """Ermittelt ein sinnvolles Standardverzeichnis für neue Projekte."""
        app_config_file = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_file):
            try:
                cfg = ConfigManager(app_config_file).load() or {}
                # 1. Gespeichertes Standard-Verzeichnis für Projekte
                last_dir = cfg.get("last_projects_dir")
                if last_dir and os.path.isdir(last_dir):
                    return last_dir

                # 2. Übergeordneter Ordner der zuletzt geöffneten Projekte
                recent = cfg.get("recent_projects", [])
                if recent and isinstance(recent, list):
                    first_recent = recent[0]
                    abs_recent = first_recent if os.path.isabs(first_recent) else os.path.join(self.app_root, first_recent)
                    parent = os.path.dirname(abs_recent)
                    if os.path.isdir(parent):
                        return parent
            except Exception:
                pass

        # 3. Fallback: Dokumente oder Home-Verzeichnis
        docs_dir = os.path.expanduser("~/Documents")
        if not os.path.isdir(docs_dir):
            docs_dir = os.path.expanduser("~/Dokumente")
        if os.path.isdir(docs_dir):
            return docs_dir
        return os.path.expanduser("~")

    def _preselect_language(self):
        """Wählt standardmäßig die zur Anwendungssprache passende Projektsprache."""
        app_lang = "en"
        app_config_file = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_file):
            try:
                cfg = ConfigManager(app_config_file).load() or {}
                app_lang = cfg.get("language", "en")
            except Exception:
                pass

        lang_map = {
            "de": "de_DE",
            "en": "en_US",
            "fr": "fr_FR",
            "es": "es_ES",
        }
        target_code = lang_map.get(app_lang, "en_US")
        idx = self.lang_combo.findData(target_code)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

    def _populate_themes(self):
        """Liest alle verfügbaren globalen Themes ein."""
        self.theme_combo.addItem(_("None (Minimal)"), "none")

        themes_dir = os.path.join(self.app_root, "themes")
        app_config_file = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_file):
            try:
                cfg = ConfigManager(app_config_file).load() or {}
                themes_path = cfg.get("paths", {}).get("themes", "themes")
                themes_dir = themes_path if os.path.isabs(themes_path) else os.path.join(self.app_root, themes_path)
            except Exception:
                pass

        if os.path.isdir(themes_dir):
            for item in sorted(os.listdir(themes_dir)):
                if not item.startswith(".") and os.path.isdir(os.path.join(themes_dir, item)):
                    self.theme_combo.addItem(item, item)

        # my-blog vorselektieren, falls vorhanden, sonst "none"
        idx = self.theme_combo.findData("my-blog")
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

    def update_theme_preview(self):
        """Aktualisiert das Vorschaubild für das gewählte Theme."""
        theme_name = self.theme_combo.currentData()
        if not theme_name or theme_name == "none":
            self.theme_preview.setPixmap(QPixmap())
            self.theme_preview.setText(_("Minimal Project\n(No Theme)"))
            return

        themes_dir = os.path.join(self.app_root, "themes")
        app_config_file = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_file):
            try:
                cfg = ConfigManager(app_config_file).load() or {}
                themes_path = cfg.get("paths", {}).get("themes", "themes")
                themes_dir = themes_path if os.path.isabs(themes_path) else os.path.join(self.app_root, themes_path)
            except Exception:
                pass

        preview_path = os.path.join(themes_dir, theme_name, "preview.png")
        if os.path.exists(preview_path):
            pix = QPixmap(preview_path)
            self.theme_preview.setPixmap(
                pix.scaled(
                    self.theme_preview.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.theme_preview.setText("")
        else:
            self.theme_preview.setPixmap(QPixmap())
            self.theme_preview.setText(_("No preview for\n{theme}").format(theme=theme_name))

    def update_path_preview(self):
        """Aktualisiert die Pfadvorschau und validiert die Eingabe."""
        site_name = self.name_input.text().strip()
        parent_dir = self.path_input.text().strip()

        if not site_name:
            folder_name = "..."
        else:
            folder_name = re.sub(r'[<>:"/\\|?*]', '', site_name).strip().replace(' ', '_')
            if not folder_name:
                folder_name = "New_Project"

        if parent_dir:
            full_path = os.path.join(parent_dir, folder_name)
        else:
            full_path = folder_name

        if site_name and parent_dir and os.path.exists(full_path):
            self.path_preview_lbl.setText(
                f"📁 <span style='color: #e74c3c; font-weight: bold;'>{_('Warning: Folder already exists:')}</span> {full_path}"
            )
            self.create_btn.setEnabled(False)
        elif site_name and parent_dir and os.path.isdir(parent_dir):
            self.path_preview_lbl.setText(
                f"📁 <span style='color: #27ae60;'>{_('Target path:')}</span> {full_path}"
            )
            self.create_btn.setEnabled(True)
        else:
            self.path_preview_lbl.setText(
                f"📁 {_('Target path:')} {full_path}"
            )
            self.create_btn.setEnabled(bool(site_name and parent_dir))

    def browse_location(self):
        """Öffnet einen Dateidialog zur Auswahl des Speicherorts."""
        initial_dir = self.path_input.text().strip()
        if not os.path.isdir(initial_dir):
            initial_dir = os.path.expanduser("~")
        dir_path = QFileDialog.getExistingDirectory(self, _("Select Parent Directory"), initial_dir)
        if dir_path:
            self.path_input.setText(dir_path)

    def create_project(self):
        """Erstellt das neue Projekt mit allen Dateien und Standard-Konfigurationen."""
        site_name = self.name_input.text().strip()
        if not site_name:
            QMessageBox.warning(self, _("Error"), _("Please enter a project name."))
            self.name_input.setFocus()
            return

        parent_dir = self.path_input.text().strip()
        if not parent_dir or not os.path.isdir(parent_dir):
            QMessageBox.warning(self, _("Error"), _("Please select a valid parent directory."))
            self.path_input.setFocus()
            return

        safe_foldername = re.sub(r'[<>:"/\\|?*]', '', site_name).strip().replace(' ', '_')
        if not safe_foldername:
            safe_foldername = "New_Project"

        project_path = os.path.join(parent_dir, safe_foldername)
        if os.path.exists(project_path):
            QMessageBox.warning(self, _("Error"), _("The folder '{folder}' already exists.").format(folder=safe_foldername))
            return

        selected_theme = self.theme_combo.currentData() or "none"
        selected_language = self.lang_combo.currentData() or "en_US"

        try:
            # 1. Standard-Ordnerstruktur anlegen
            os.makedirs(project_path, exist_ok=True)
            standard_dirs = [
                "content", "assets", "assets/images", "plugins",
                "themes", "site_output", "backup", "templates"
            ]
            for folder in standard_dirs:
                os.makedirs(os.path.join(project_path, folder), exist_ok=True)

            # 2. Vollständige Konfiguration mit sinnvollen Defaults erzeugen
            config_data = self._generate_default_config(
                site_name=site_name,
                language=selected_language,
                site_theme=selected_theme
            )

            # 3. Theme kopieren oder Minimal-Layout erstellen
            if selected_theme and selected_theme != "none":
                ok, msg = self._copy_theme_files(project_path, selected_theme)
                if not ok:
                    QMessageBox.warning(
                        self,
                        _("Theme Warning"),
                        _("Could not copy theme files: {msg}\nA basic layout will be created instead.").format(msg=msg)
                    )
                    self._create_minimal_theme(project_path)
            else:
                self._create_minimal_theme(project_path)

            # 4. config.yaml schreiben
            config_file = os.path.join(project_path, "config.yaml")
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            # 5. Startinhalt (index.md) anlegen
            self.create_default_content(project_path, site_name)

            # 6. Speicherort in app_config für zukünftige Projekte merken
            self._save_last_projects_dir(parent_dir)

            self.created_project_path = project_path
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not create project: {e}").format(e=e))

    def save_config(self):
        """Kompatibilitäts-Alias für create_project."""
        self.create_project()

    def _copy_theme_files(self, project_path, theme_name):
        """Kopiert den gewählten Theme-Ordner in das neue Projekt."""
        themes_dir = os.path.join(project_path, "themes")
        dest_path = os.path.join(themes_dir, theme_name)

        themes_rel = "themes"
        app_config_file = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_file):
            try:
                cfg = ConfigManager(app_config_file).load() or {}
                themes_rel = cfg.get("paths", {}).get("themes", "themes")
            except Exception:
                pass

        source_path = themes_rel if os.path.isabs(themes_rel) else os.path.join(self.app_root, themes_rel)
        source_theme_dir = os.path.join(source_path, theme_name)

        if not os.path.isdir(source_theme_dir):
            return False, _("Source theme directory not found: {path}").format(path=source_theme_dir)

        try:
            os.makedirs(themes_dir, exist_ok=True)
            tmp_parent = tempfile.mkdtemp(prefix="siteweave_theme_")
            tmp_dest = os.path.join(tmp_parent, theme_name)
            shutil.copytree(source_theme_dir, tmp_dest, dirs_exist_ok=False)
            shutil.move(tmp_dest, dest_path)
            try:
                os.rmdir(tmp_parent)
            except Exception:
                pass
            return True, ""
        except Exception as e:
            return False, str(e)

    def _create_minimal_theme(self, project_path):
        """Erstellt eine minimale HTML/CSS-Vorlage für Projekte ohne vorgefertigtes Theme."""
        none_tpl_dir = os.path.join(project_path, "themes", "none", "templates")
        none_css_dir = os.path.join(project_path, "themes", "none", "css")
        os.makedirs(none_tpl_dir, exist_ok=True)
        os.makedirs(none_css_dir, exist_ok=True)

        base_html_path = os.path.join(none_tpl_dir, "base.html")
        if not os.path.exists(base_html_path):
            base_html = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} | {{ site_name }}</title>
    <link rel="stylesheet" href="{{ relative_prefix }}css/style.css">
</head>
<body>
    <header>
        <h1>{{ page_title }}</h1>
        <nav>
            <a href="{{ relative_prefix }}index.html">Home</a>
        </nav>
    </header>
    <main>
        {{ content }}
    </main>
</body>
</html>
"""
            with open(base_html_path, "w", encoding="utf-8") as f:
                f.write(base_html)

        style_css_path = os.path.join(none_css_dir, "style.css")
        if not os.path.exists(style_css_path):
            style_css = """body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 40px auto;
    padding: 0 20px;
    color: #333;
}
header {
    border-bottom: 1px solid #eee;
    margin-bottom: 30px;
    padding-bottom: 20px;
}
"""
            with open(style_css_path, "w", encoding="utf-8") as f:
                f.write(style_css)

    def create_default_content(self, path, project_name):
        """Erstellt die initiale index.md für die Website."""
        import frontmatter
        index_md_path = os.path.join(path, "content", "index.md")
        if not os.path.exists(index_md_path):
            today_str = date.today().strftime("%Y-%m-%d")
            post = frontmatter.Post(
                f"# {_('Welcome to {site_name}').format(site_name=project_name)}\n\n{_('This is your new project. Start editing this file to build your website.')}\n",
                title=_("Home"),
                date=today_str,
                layout="full-width"
            )
            with open(index_md_path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))

    def _generate_default_config(self, site_name, language, site_theme):
        """Erzeugt das vollständige Dictionary mit Standard-Konfigurationswerten."""
        return {
            "site_name": site_name,
            "language": language,
            "site_url": "http://localhost:8000",
            "site_theme": site_theme,
            "default_author": "",
            "site_logo": "",
            "site_favicon": "",
            "log_level": "INFO",
            "content_directory": "content",
            "site_output_directory": "site_output",
            "themes_directory": "themes",
            "assets_directory": "assets",
            "plugin_directory": "plugins",
            "backup_directory": "backup",
            "backup_on_render": True,
            "backup_rotation": 10,
            "default_template": "full-width",
            "markdown_extensions": [".md", ".markdown"],
            "spellcheck_enabled": True,
            "spellcheck_language": language,
            "header_links": [],
            "footer_links": [],
            "meta_description": "",
            "meta_keywords": "",
            "social": {},
            "image_compression": {
                "compressed_suffix": "-compressed",
                "jpeg_quality": 85,
                "png_compression": 6,
                "extensions": [".jpg", ".jpeg", ".png"]
            },
            "normalization": {
                "excluded_dirs": ["_spezial"]
            },
            "linter": {
                "defaults": {
                    "author": "default",
                    "layout": "full-width"
                }
            },
            "pdf_export": {
                "theme": "modern-handbook",
                "export_path": "pdf_exports",
                "toc_depth": 3,
                "include_index_files": False,
                "page_size": "A4",
                "orientation": "portrait",
                "margin_top": "2cm",
                "margin_right": "2cm",
                "margin_bottom": "2cm",
                "margin_left": "2cm",
                "show_cover_page": True,
                "show_page_numbers": True,
                "show_print_date": True,
                "custom_css_path": ""
            }
        }

    def _save_last_projects_dir(self, parent_dir):
        """Speichert den zuletzt gewählten Elternordner in app_config.yaml."""
        app_config_file = os.path.join(self.app_root, "app_config.yaml")
        if os.path.exists(app_config_file):
            try:
                mgr = ConfigManager(app_config_file)
                mgr.load()
                mgr.update({"last_projects_dir": parent_dir})
                mgr.save()
            except Exception:
                pass

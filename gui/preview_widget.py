import os
import importlib.util
import json
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtGui import QDesktopServices
import markdown
import markdown.serializers
from core.renderer import process_plugins, _protect_code_blocks, _restore_code_blocks
from core.i18n import _

'''
PreviewWidget: A widget for rendering Markdown content as HTML in a live preview.
- Uses QWebEngineView to display the rendered HTML.
- Supports plugins that can modify the content before rendering.
- Handles external links by opening them in the default browser.    
- Provides methods to set the base path for resolving relative links and images, toggle dark mode, and configure font settings.
- The 'update_preview(text)' method can be called to update the preview with new Markdown content, which will be processed and rendered after a short delay (debounced).
- The widget also includes a method 'scroll_to_percentage(percentage)' to scroll the preview to a specific position, which can be used to synchronize scrolling between the editor and the preview.
- The PreviewPage class is a custom QWebEnginePage that overrides the navigation behavior to handle external links appropriately.
'''


class PreviewPage(QWebEnginePage):
    """
    Docstring für PreviewPage
        
    :var padding: Beschreibung

    """
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Prüfen, ob die Navigation durch einen Link-Klick ausgelöst wurde
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            # Externe Links (http, https, mailto) im Standardbrowser öffnen
            if url.scheme() in ["http", "https", "mailto"]:
                QDesktopServices.openUrl(url)
                return False # Navigation im Widget verhindern
        return super().acceptNavigationRequest(url, _type, isMainFrame)

# Monkey-Patch für Markdown Serializer Fehler (TypeError: cannot serialize True)
# Dies behebt Probleme mit Extensions wie fenced_code, die boolesche Werte in der Config haben.
if not hasattr(markdown.serializers, '_original_escape_attrib_html'):
    markdown.serializers._original_escape_attrib_html = markdown.serializers._escape_attrib_html

    def _patched_escape_attrib_html(text):
        if isinstance(text, bool):
            return str(text)
        return markdown.serializers._original_escape_attrib_html(text)

    markdown.serializers._escape_attrib_html = _patched_escape_attrib_html

class PreviewWidget(QWebEngineView):
    """
    Docstring für PreviewWidget
        
    :var padding: Beschreibung

    """
    def __init__(self, project_root=None, app_root=None):
        super().__init__()
        self.project_root = project_root
        self.app_root = app_root
        self.current_file_path = None
        self.plugins = {}
        self.plugin_css_content = ""

        self.setPage(PreviewPage(self))
        
        # Timer für verzögertes Update (Debounce), damit nicht bei jedem Tastendruck gerendert wird
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(300) # 300ms Verzögerung für flüssigeres Gefühl
        self.update_timer.timeout.connect(self._perform_update)
        self.current_text = ""
        self.dark_mode = False
        self.font_family = "Sans Serif"
        self.font_size = 14
        self.base_url = QUrl("file://")
        self.last_base_url = None

        if self.project_root and self.app_root:
            self.load_plugins()
            self.load_plugin_css()

    def load_plugins(self):
        """Lädt Plugins dynamisch für die Vorschau."""
        plugin_dirs = []
        if self.app_root:
            plugin_dirs.append(os.path.join(self.app_root, "plugins"))
        if self.project_root:
            plugin_dirs.append(os.path.join(self.project_root, "plugins"))

        for directory in plugin_dirs:
            if not os.path.isdir(directory):
                continue
            
            for item in sorted(os.listdir(directory)):
                path = os.path.join(directory, item)
                plugin_name = None
                module_path = None
                
                if os.path.isfile(path) and item.endswith('.py') and not item.startswith('__'):
                    plugin_name = os.path.splitext(item)[0]
                    module_path = path
                elif os.path.isdir(path) and not item.startswith('__') and not item.startswith('.'):
                    init_file = os.path.join(path, "__init__.py")
                    named_file = os.path.join(path, f"{item}.py")
                    if os.path.isfile(named_file):
                        plugin_name = item
                        module_path = named_file
                    elif os.path.isfile(init_file):
                        plugin_name = item
                        module_path = init_file
                
                if plugin_name and module_path:
                    try:
                        spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", module_path)
                        plugin_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(plugin_module)
                        if hasattr(plugin_module, 'handle'):
                            self.plugins[plugin_name.lower()] = plugin_module
                    except Exception as e:
                        print(_("Error loading plugin {plugin_name} for preview: {e}").format(plugin_name=plugin_name, e=e))

    def load_plugin_css(self):
        """Lädt CSS-Dateien aus den Plugin-Verzeichnissen."""
        css_content = []
        search_dirs = []
        if self.app_root:
            search_dirs.append(os.path.join(self.app_root, "plugins"))
        if self.project_root:
            search_dirs.append(os.path.join(self.project_root, "plugins"))
            
        for p_dir in search_dirs:
            if not os.path.isdir(p_dir): continue
            
            for item in sorted(os.listdir(p_dir)):
                item_path = os.path.join(p_dir, item)
                css_files = []
                
                if os.path.isfile(item_path) and item.endswith('.css'):
                    css_files.append(item_path)
                elif os.path.isdir(item_path) and not item.startswith('__') and not item.startswith('.'):
                    for sub in os.listdir(item_path):
                        if sub.endswith('.css'):
                            css_files.append(os.path.join(item_path, sub))
                
                for css_file in css_files:
                    try:
                        with open(css_file, 'r', encoding='utf-8') as f:
                            css_content.append(f"/* {os.path.basename(css_file)} */")
                            css_content.append(f.read())
                    except: pass
        
        self.plugin_css_content = "\n".join(css_content)

    def set_base_path(self, path):
        """Setzt den Basispfad für relative Links und Bilder."""
        self.current_file_path = path
        if path:
            # Wenn es eine Datei ist, nimm das Verzeichnis
            if os.path.isfile(path):
                path = os.path.dirname(path)
            self.base_url = QUrl.fromLocalFile(path + os.path.sep)
        else:
            self.base_url = QUrl("file://")

    def set_dark_mode(self, enabled):
        self.dark_mode = enabled
        self._perform_update()

    def set_font_configuration(self, font_family, font_size):
        self.font_family = font_family
        self.font_size = font_size
        self._perform_update()

    def update_preview(self, text):
        self.current_text = text
        self.update_timer.start()

    def _perform_update(self):
        # 1. Plugins verarbeiten (Shortcodes ersetzen)
        context = {
            'current_page_path': self.current_file_path,
            'relative_prefix': '',
            'project_root': self.project_root,
            'content_dir': os.path.join(self.project_root, 'content') if self.project_root else None
        }
        
        protected_content, code_protections = _protect_code_blocks(self.current_text)
        processed_content = process_plugins(protected_content, context, None, self.plugins)
        restored_content = _restore_code_blocks(processed_content, code_protections)

        # 2. Markdown zu HTML
        md = markdown.Markdown(
            extensions=['fenced_code', 'tables', 'attr_list', 'md_in_html']
        )
        
        html_content = md.convert(restored_content)
        
        font_style = f"font-family: '{self.font_family}', sans-serif; font-size: {self.font_size}px;"
        
        if self.dark_mode:
            css = f"""
                body {{ {font_style} padding: 20px; line-height: 1.6; color: #d4d4d4; background-color: #1e1e1e; }}
                a {{ color: #9cdcfe; }}
                img {{ max-width: 100%; }}
                img.center {{ display: block; margin: 0 auto; }}
                pre {{ background: #2d2d2d; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                code {{ background: #2d2d2d; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
                blockquote {{ border-left: 4px solid #555; margin-left: 0; padding-left: 16px; color: #aaa; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 1em; }}
                th, td {{ border: 1px solid #444; padding: 8px; }}
                th {{ background-color: #2d2d2d; text-align: left; }}
            """
        else:
            css = f"""
                body {{ {font_style} padding: 20px; line-height: 1.6; color: #333; }}
                img {{ max-width: 100%; }}
                img.center {{ display: block; margin: 0 auto; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: monospace; }}
                blockquote {{ border-left: 4px solid #ccc; margin-left: 0; padding-left: 16px; color: #666; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 1em; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; text-align: left; }}
            """
        
        # Plugin CSS hinzufügen
        css += "\n" + self.plugin_css_content

        # Optimierung: JS-Update statt Full-Reload um Flackern zu verhindern
        if self.last_base_url == self.base_url:
            js_content = json.dumps(html_content)
            js_css = json.dumps(css)
            js = f"""
            var style = document.getElementById('preview-style');
            if (!style) {{
                style = document.createElement('style');
                style.id = 'preview-style';
                document.head.appendChild(style);
            }}
            style.innerHTML = {js_css};
            document.body.innerHTML = {js_content};
            """
            self.page().runJavaScript(js)
        else:
            # Einfaches HTML-Gerüst für die Vorschau
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style id="preview-style">
                    {css}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            self.setHtml(full_html, self.base_url)
            self.last_base_url = self.base_url

    def scroll_to_percentage(self, percentage):
        """Scrollt die Vorschau an die angegebene prozentuale Position (0.0 bis 1.0)."""
        percentage = max(0.0, min(1.0, percentage))
        js = f"""
        var body = document.body;
        var html = document.documentElement;
        // Gesamthöhe des Dokuments ermitteln (Cross-Browser kompatibel)
        var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
        var windowHeight = window.innerHeight;
        // Zielposition berechnen
        var scrollPos = (height - windowHeight) * {percentage};
        window.scrollTo(0, scrollPos);
        """
        self.page().runJavaScript(js)
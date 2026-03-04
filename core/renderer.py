'''
Docstring for core.renderer

This module is responsible for rendering the site using the provided configuration.
It includes functions for processing markdown files, handling plugins, and generating the final HTML output.
The SiteRenderer class encapsulates the rendering logic, while the run function serves as the entry point for both CLI and GUI usage.

''' 

import os
import shutil
import re
import importlib.util
import json
import logging
import yaml
import ast
from workers.logger_config import configure_logger
from datetime import datetime
from core.i18n import _

try:
    import markdown
    import frontmatter    
    from jinja2 import (
        Environment,
        FileSystemLoader,
        TemplateNotFound
    )
except ImportError:
    print("Required packages not found. Please install them by running: pip install markdown Jinja2 python-frontmatter Pygments")
    exit(1)

IMAGE_MD_RE = re.compile(r'^\s*!\[(.*?)\]\((.*?)\)\s*$', re.MULTILINE)

logger = logging.getLogger("site_renderer")

# Function to check if a file is a Markdown file based on its extension
def is_markdown_file(filename, extensions):
    return any(filename.endswith(ext) for ext in extensions)

def extract_title(markdown_content, fallback_filename):
    """Extracts the first H1-level title from markdown content."""
    for line in markdown_content.splitlines():
        if line.strip().startswith('# '):
            return line.strip()[2:] # Remove '# ' and leading/trailing whitespace
    # Fallback to a cleaned-up filename if no H1 is found
    return os.path.splitext(fallback_filename)[0].replace('_', ' ').replace('-', ' ').title()

def _generate_index_html_recursive(structure, relative_prefix='./', current_page_path=None, is_top_level=False):
    """
    Recursively generates a nested HTML list from the site structure,
    highlighting the active page and its parent directories.
    Returns a tuple: (html_string, has_active_child).
    """
    if not structure:
        return "", False

    ul_class = ' class="nav-menu"' if is_top_level else ''
    html_parts = [f"<ul{ul_class}>"]
    has_active_child_in_this_level = False

    # Sort keys so directories (without '__') are processed before files ('__files')
    sorted_keys = sorted(structure.keys(), key=lambda k: (k == '__files', k))

    for key in sorted_keys:
        if key == '__files':  # Process files at the end of the current level
            # Sort files by their title
            # Primary sort by 'weight' (default 0), secondary by 'title'
            for page in sorted(structure['__files'], key=lambda x: (x.get('weight', 0), x['title'])):
                link_path = relative_prefix + page["path"].lstrip('/')
                
                # Check if the current page is the active one
                is_active = current_page_path and page["path"] == current_page_path
                a_class = ' class="active"' if is_active else ''
                if is_active:
                    has_active_child_in_this_level = True

                html_parts.append(f'<li><a href="{link_path}"{a_class}>{page["title"]}</a></li>')
        else:  # Process directories
            dir_title = key.replace('_', ' ').replace('-', ' ').title()
            dir_files = structure[key].get('__files', [])

            # Find the directory's index page (if present)
            index_page = next((p for p in dir_files if p['clean_path'].endswith('/index.html')), None)

            # Remove the index page from the list to avoid duplicates
            if index_page:
                structure[key]['__files'] = [p for p in dir_files if p is not index_page]
            
            # Recursive call for the subdirectory
            child_html, has_active_child = _generate_index_html_recursive(
                structure[key], relative_prefix, current_page_path, is_top_level=False
            )

            if has_active_child:
                has_active_child_in_this_level = True

            # Build the dropdown structure
            li_class = ' class="dropdown active-parent"' if has_active_child else ' class="dropdown"'
            html_parts.append(f"<li{li_class}>")
            # If an index page exists, make the button a link
            if index_page:
                html_parts.append(f'  <a href="{relative_prefix + index_page["path"].lstrip("/")}" class="dropbtn">{dir_title}</a>')
            else:
                html_parts.append(f'  <button class="dropbtn">{dir_title}</button>')
            html_parts.append('  <div class="dropdown-content">')
            html_parts.append(child_html)  # Append the nested list
            html_parts.append('  </div>')
            html_parts.append("</li>")

    html_parts.append("</ul>")
    return "\n".join(html_parts), has_active_child_in_this_level

def generate_index_html(structure, relative_prefix='./', current_page_path=None):
    """Public-facing function to generate the index HTML, called from templates."""
    html, _ = _generate_index_html_recursive(structure, relative_prefix, current_page_path, is_top_level=True)
    return html

def slugify(value):
    """
    Converts a string into a URL-friendly slug.
    Example: "Züri Gschnätzlets" -> "zuri-gschnatzlets"
    """
    import re
    import unicodedata
    # Normalize unicode characters
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    # Replace non-alphanumeric characters with a hyphen
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    # Replace whitespace and repeated hyphens with a single hyphen
    return re.sub(r'[-\s]+', '-', value)

PLUGIN_RE = re.compile(
    r'\[\[\s*([\w-]+)(.*?)\]\]'  # 1:name, 2:args
    r'(?:'
    r'((?:(?!\[\[\s*\1\b).)*?)'  # 3:content
    r'\[\[\s*/\1\s*\]\]'
    r')?',  # Content and closing tag are optional
    re.DOTALL | re.IGNORECASE
)

ARGS_RE = re.compile(r'([\w-]+)(?:=(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'\]\]]+)))?')

def parse_plugin_args(arg_string):
    """Parses a string of key-value arguments into a dictionary."""
    args = {}
    if not arg_string:
        return args
    
    for match in ARGS_RE.finditer(arg_string):
        key = match.group(1)
        # The value is the first non-empty captured group for values, or None
        value = next((g for g in match.groups()[1:] if g is not None), None)
        
        if value is None:
            # It's a flag, like [[plugin flag]]
            args[key] = True
        else:
            args[key] = value
    return args

def _plugin_replacer(match, context, env, plugins_collection):
    """Replacement function for re.sub that calls the appropriate plugin handler."""
    plugin_name = match.group(1).lower()
    raw_args = match.group(2)
    content = match.group(3)

    args = parse_plugin_args(raw_args)

    if plugin_name in plugins_collection:
        plugin_module = plugins_collection[plugin_name]
        if hasattr(plugin_module, 'handle'):
            handler = plugin_module.handle
            # Pass content (can be None) and the parsed args dictionary
            result = handler(content, args, context, env)
            return str(result) if result is not None else ""
        else:
            logger.warning(_("Warning: Plugin '{plugin_name}' has no 'handle' function.").format(plugin_name=plugin_name))
            return match.group(0)
    else:
        # If the plugin is not found, treat it as plain text
        # and return the original match without warning.
        return match.group(0)

def process_plugins(raw_markdown, context, env, plugins_collection):
    """
    Finds and processes all plugin tags in the markdown content.
    This process is repeated until no plugin tags remain to allow nested plugins
    (for example via 'include').
    """
    processed_content = raw_markdown
    # Limit iterations to prevent potential infinite loops from buggy plugins
    for _ in range(10): # Max 10 levels of nesting
        if not PLUGIN_RE.search(processed_content):
            break
        new_content = PLUGIN_RE.sub(lambda m: _plugin_replacer(m, context, env, plugins_collection), processed_content)
        if new_content == processed_content:
            # No further changes even though tags were found (likely unknown plugins)
            break
        processed_content = new_content
    else:
        logger.warning(_("Warning: Maximum plugin nesting depth reached for page '{page_title}'. Possible infinite loop?").format(page_title=context.get('page_title', _('Unknown'))))
    return processed_content


# Regex for fenced code blocks (```...```) and inline code (`...`)
FENCED_CODE_RE = re.compile(r'^(```.*?```)', re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r'(`[^`]+?`)')

def _protect_code_blocks(markdown_content):
    """Replaces code blocks and inline code with placeholders."""
    protections = {}
    
    def _replacer(match):
        code_block = match.group(0)
        placeholder = f"__CODE_BLOCK_PLACEHOLDER_{len(protections)}__"
        protections[placeholder] = code_block
        return placeholder

    # First protect the large, multi-line blocks
    protected_content = FENCED_CODE_RE.sub(_replacer, markdown_content)
    # Then protect inline code
    protected_content = INLINE_CODE_RE.sub(_replacer, protected_content)
    
    return protected_content, protections

def _restore_code_blocks(content, protections):
    """Restores code blocks from placeholders."""
    for placeholder, code_block in protections.items():
        content = content.replace(placeholder, code_block)
    return content

def _add_copy_buttons(html_content, plugins_collection=None):
    """
    Delegates adding copy-buttons to the 'code' plugin if available.
    """
    if plugins_collection and 'code' in plugins_collection and hasattr(plugins_collection['code'], 'add_copy_buttons'):
        return plugins_collection['code'].add_copy_buttons(html_content)
    return html_content

def normalize_config(config):
    """
    Validates and corrects the structure of configuration data.
    This function should be called both when loading and BEFORE saving (in the GUI)
    to ensure lists and dictionaries have the expected types.
    """
    
    # Helper function to parse strings that look like Python dicts/lists
    def parse_if_string(val):
        if isinstance(val, str):
            val = val.strip()
            if "}," in val and not val.startswith('['):
                val = f"[{val}]"
            if (val.startswith('{') and val.endswith('}')) or (val.startswith('[') and val.endswith(']')):
                try:
                    return ast.literal_eval(val)
                except (ValueError, SyntaxError):
                    try:
                        return yaml.safe_load(val)
                    except:
                        pass
        return val

    # Ensure defaults for optional sections
    # IMPORTANT: setdefault does not overwrite None, so explicitly check for None.
    if config.get('contact') is None: config['contact'] = {}
    config['contact'] = parse_if_string(config['contact'])
    
    if config.get('social') is None: config['social'] = {}
    config['social'] = parse_if_string(config['social'])
    
    if config.get('header_links') is None: config['header_links'] = []
    if config.get('footer_links') is None: config['footer_links'] = []
    
    # Repair footer_links
    if 'footer_links' in config:
        fl = config['footer_links']
        if isinstance(fl, str):
             config['footer_links'] = parse_if_string(fl) or []
        elif isinstance(fl, list) and fl:
        # If all elements are strings, try to repair (e.g. split-by-comma errors)
            if all(isinstance(x, str) for x in fl):
            # Attempt 1: Join everything (fixes split-by-comma errors)
                joined = ", ".join(fl)
                parsed = parse_if_string(joined)
                if isinstance(parsed, list):
                    config['footer_links'] = parsed
                elif isinstance(parsed, dict):
                    config['footer_links'] = [parsed]

    # Repair header_links
    if 'header_links' in config:
        hl = config['header_links']
        if isinstance(hl, str):
             config['header_links'] = parse_if_string(hl) or []
        elif isinstance(hl, list) and hl:
            if all(isinstance(x, str) for x in hl):
                joined = ", ".join(hl)
                parsed = parse_if_string(joined)
                if isinstance(parsed, list):
                    config['header_links'] = parsed
                elif isinstance(parsed, dict):
                    config['header_links'] = [parsed]

    # footer_links must be a list
    f_links = config['footer_links']
    if isinstance(f_links, dict):
        # Case A: Single object (has 'title' or 'url')
        if 'title' in f_links or 'url' in f_links:
            logger.info(_("Config correction: 'footer_links' is a single object. Converting to list."))
            config['footer_links'] = [f_links]
        # Case B: Map of objects (e.g. {'0': {...}, '1': {...}})
        else:
            logger.info(_("Config correction: 'footer_links' is a map. Converting values to list."))
            config['footer_links'] = [v for k, v in sorted(f_links.items(), key=lambda x: str(x[0]))]

    # header_links must be a list
    h_links = config['header_links']
    if isinstance(h_links, dict):
        if 'title' in h_links or 'url' in h_links:
            logger.info(_("Config correction: 'header_links' is a single object. Converting to list."))
            config['header_links'] = [h_links]
        else:
            logger.info(_("Config correction: 'header_links' is a map. Converting values to list."))
            config['header_links'] = [v for k, v in sorted(h_links.items(), key=lambda x: str(x[0]))]

    # contact and social must be dictionaries
    if isinstance(config['contact'], list):
        config['contact'] = config['contact'][0] if config['contact'] else {}
    if isinstance(config['social'], list):
        config['social'] = config['social'][0] if config['social'] else {}
        
    return config

class SiteRenderer:

    def __init__(self, project_root, app_root=None):
        self.project_root = project_root
        self.config_path = os.path.join(project_root, "config.yaml")
        
        self.logger = configure_logger("site_renderer", project_root)
        
        if not os.path.isfile(self.config_path):
            self.logger.warning(_("Configuration file '{config_path}' not found. Using defaults.").format(config_path=self.config_path))
            self.config = {}
        else:
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                self.logger.critical(_("\nCRITICAL ERROR in '{config_path}':").format(config_path=self.config_path))
                self.logger.critical(f"  {e}")
                self.logger.critical(_("  Cause: Probably duplicate keys or sections (e.g. [contact] defined twice)."))
                self.logger.critical(_("  Solution: Open the file and remove duplicates manually.\n"))
                raise e

        # Normalize structure
        self.config = normalize_config(self.config)

        # Set paths relative to the project directory
        self.site_url = self.config.get("site_url", "http://localhost:8000")
        self.content_directory = os.path.join(project_root, self.config.get("content_directory", "content"))
        self.assets_directory = os.path.join(project_root, self.config.get("assets_directory", "assets"))
        self.markdown_extensions = self.config.get("markdown_extensions", [".md", ".markdown"])
        self.plugin_directory = os.path.join(project_root, self.config.get("plugin_directory", "plugins"))
        self.site_output_directory = os.path.join(project_root, self.config.get("site_output_directory", "site_output"))
        self.backup_directory = os.path.join(project_root, self.config.get("backup_directory", "backup"))
        self.template_directory = os.path.join(project_root, self.config.get("template_directory", "templates"))
        self.css_directory = os.path.join(project_root, self.config.get("css_directory", "css"))
        self.js_directory = os.path.join(project_root, self.config.get("js_directory", "js"))
        self.themes_directory = os.path.join(project_root, self.config.get("themes_directory", "themes"))

        # Determine global plugin directory (app_root/plugins)
        if app_root:
            self.app_root = app_root
        else:
            # Fallback: core/renderer.py is in core/, so go two levels up to the project root
            self.app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.global_plugin_directory = os.path.join(self.app_root, "plugins")
        self.global_plugin_template_directory = os.path.join(self.global_plugin_directory, "templates")

        # Ensure the output directories exist
        os.makedirs(self.site_output_directory, exist_ok=True)
        os.makedirs(self.backup_directory, exist_ok=True)
       

    def find_markdown_files(self, directory):
        """
        Search for Markdown files in the specified directory and its subdirectories.
        """
        markdown_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if is_markdown_file(file, self.markdown_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    # Note: self.config["assets_directory"] is the name (e.g. "assets"), self.assets_directory is the absolute path
                    asset_file = os.path.join(self.config["assets_directory"], relative_path.replace(self.config["content_directory"], ""))
                    
                    markdown_files.append((file, relative_path, asset_file))
        
        return markdown_files

    def copy_local_assets(self, content_dir, output_dir):
        """
        Finds all subdirectories named 'assets' within the content directory
        and copies them to the corresponding location in the output directory.
        """
        self.logger.info(_("\nCopying local assets..."))
        asset_found = False
        assets_dirname = os.path.basename(self.assets_directory)
        
        for root, dirs, files in os.walk(content_dir):
            if assets_dirname in dirs:
                asset_found = True
                source_path = os.path.join(root, assets_dirname)
                # Calculate the destination path within the output directory
                relative_root = os.path.relpath(root, content_dir)
                dest_path = os.path.join(output_dir, relative_root, assets_dirname)
                
                self.logger.info(_("  - Copying from '{source_path}' to '{dest_path}'").format(source_path=source_path, dest_path=dest_path))
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
        if not asset_found:
            self.logger.info(_("  - No local asset directories found in content folder."))

    def generate_sitemap(self, pages, output_dir):
        """
        Generates a sitemap.xml file for search engines.
        """
        self.logger.info(_("\nGenerating sitemap.xml..."))
        if not self.site_url or "127.0.0.1" in self.site_url:
            self.logger.warning(_("Warning: SITE_URL is not configured to a real domain. Skipping sitemap."))
            self.logger.warning(_("         Please adjust the SITE_URL variable in config.yaml."))
            return

        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]

        for page_info in pages:
            page_path = page_info['path']
            source_path = page_info.get('source_path')
            url = self.site_url.rstrip('/') + page_path
            
            lastmod = datetime.now().strftime('%Y-%m-%d')
            if source_path and os.path.exists(source_path):
                lastmod_ts = os.path.getmtime(source_path)
                lastmod = datetime.fromtimestamp(lastmod_ts).strftime('%Y-%m-%d')

            xml_parts.extend([f'  <url>', f'    <loc>{url}</loc>', f'    <lastmod>{lastmod}</lastmod>', f'  </url>'])

        xml_parts.append('</urlset>')

        sitemap_path = os.path.join(output_dir, 'sitemap.xml')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_parts))
        self.logger.info(_("  - sitemap.xml successfully created: {sitemap_path}").format(sitemap_path=sitemap_path))

    def copy_static_directories(self, output_dir):
        """
        Copies static asset directories like 'css' and 'js' to the output directory,
        ensuring the destination is always up-to-date.
        """
        self.logger.info(_("\nCopying static directories (CSS, JS, Assets)..."))
        # Verwende die absoluten Pfade aus der Instanz
        for source_path in [self.css_directory, self.js_directory, self.assets_directory]:
            dir_name = os.path.basename(source_path)
            dest_path = os.path.join(output_dir, dir_name)

            if os.path.isdir(source_path) and os.listdir(source_path):
                # IMPORTANT: dirs_exist_ok=True (Python 3.8+) merges directories
                # instead of replacing them. This is crucial so that global assets
                # do not remove local assets (e.g. from index.md).
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                self.logger.info(_("  - '{source_path}' successfully copied/merged to '{dest_path}'.").format(source_path=source_path, dest_path=dest_path))
            else:
                self.logger.info(_("  - Static directory '{source_path}' not found or empty, skipping.").format(source_path=source_path))

    def copy_theme_assets(self, output_dir, theme_name):
        """Copies assets from the selected theme to the output directory."""
        if not theme_name or theme_name == "default-blog":
            return

        theme_path = os.path.join(self.themes_directory, theme_name)
        if not os.path.isdir(theme_path):
            self.logger.warning(_("Theme directory not found: {path}").format(path=theme_path))
            return

        self.logger.info(_("\nCopying theme assets for '{theme}'...").format(theme=theme_name))
        
        # Copy css, js, assets from theme if they exist
        for sub in ['css', 'js', 'assets']:
            src = os.path.join(theme_path, sub)
            dst = os.path.join(output_dir, sub)
            if os.path.isdir(src):
                # Merge with existing assets
                shutil.copytree(src, dst, dirs_exist_ok=True)
                self.logger.info(_("  - Merged theme {sub} to {dst}").format(sub=sub, dst=dst))


    def copy_plugin_assets(self, output_dir):
        """
        Searches for .css and .js files directly in plugin directories (Global & Project)
        and copies them into the corresponding subfolders in the output (css/plugins/ and js/plugins/).
        This simplifies structure by keeping assets next to their plugin code.
        """
        # Ziel-Verzeichnisse basierend auf der Konfiguration ermitteln
        css_dir_name = os.path.basename(self.css_directory)
        js_dir_name = os.path.basename(self.js_directory)
        
        target_css_dir = os.path.join(output_dir, css_dir_name, 'plugins')
        target_js_dir = os.path.join(output_dir, js_dir_name, 'plugins')
        
        # Directories to search (order: Global, then Project)
        search_dirs = []
        if os.path.isdir(self.global_plugin_directory):
            search_dirs.append(self.global_plugin_directory)
        if os.path.isdir(self.plugin_directory):
            search_dirs.append(self.plugin_directory)
            
        if not search_dirs:
            return

        self.logger.info(_("\nProcessing plugin assets (CSS/JS)..."))
        # Create target directories only when needed
        os.makedirs(target_css_dir, exist_ok=True)
        os.makedirs(target_js_dir, exist_ok=True)

        for p_dir in search_dirs:
            source_type = "Global" if p_dir == self.global_plugin_directory else "Project"
            # List all items in the plugin directory
            for item in sorted(os.listdir(p_dir)):
                item_path = os.path.join(p_dir, item)
                
                # Collect assets: either directly in the plugin folder or in a subfolder (plugin bundle)
                assets_to_copy = []
                if os.path.isfile(item_path):
                    assets_to_copy.append((item, item_path))
                elif os.path.isdir(item_path) and not item.startswith('__') and not item.startswith('.'):
                    for sub_item in os.listdir(item_path):
                        sub_item_path = os.path.join(item_path, sub_item)
                        if os.path.isfile(sub_item_path):
                            assets_to_copy.append((sub_item, sub_item_path))
                
                for filename, src_file in assets_to_copy:
                    if filename.endswith('.css'):
                        shutil.copy2(src_file, os.path.join(target_css_dir, filename))
                        self.logger.info(_("  - Plugin CSS copied ({source_type}): {filename}").format(source_type=source_type, filename=filename))
                    elif filename.endswith('.js'):
                        shutil.copy2(src_file, os.path.join(target_js_dir, filename))
                        self.logger.info(_("  - Plugin JS copied ({source_type}): {filename}").format(source_type=source_type, filename=filename))

# --- Plugin System ---

    def load_plugins(self):
        """
        Dynamically loads all available plugins from the global 'plugins' folder
        and the project-specific PLUGIN_DIRECTORY.
        A plugin is a .py file that provides a 'handle' function.
        The filename (without .py) is used as the plugin name.
        Project-specific plugins override global plugins with the same name.
        """
        plugins = {}
        
        # List of directories to search (order: Global, then Project)
        plugin_dirs = []
        if os.path.isdir(self.global_plugin_directory):
            plugin_dirs.append(self.global_plugin_directory)
        if os.path.isdir(self.plugin_directory):
            plugin_dirs.append(self.plugin_directory)

        if not plugin_dirs:
            self.logger.info(_("Info: Neither global plugin directory '{global_dir}' nor project plugin directory '{project_dir}' found.").format(global_dir=self.global_plugin_directory, project_dir=self.plugin_directory))
            return plugins

        self.logger.info(_("\nLoading plugins..."))
        
        for directory in plugin_dirs:
            # Sort files for a consistent load order
            for item in sorted(os.listdir(directory)):
                path = os.path.join(directory, item)
                plugin_name = None
                module_path = None
                
                # Case 1: Plugin is a single .py file
                if os.path.isfile(path) and item.endswith('.py') and not item.startswith('__'):
                    plugin_name = os.path.splitext(item)[0]
                    module_path = path
                # Fall 2: Plugin ist ein Ordner (muss __init__.py oder [ordnername].py enthalten)
                elif os.path.isdir(path) and not item.startswith('__') and not item.startswith('.'):
                    init_file = os.path.join(path, "__init__.py")
                    named_file = os.path.join(path, f"{item}.py")
                    
                    if os.path.isfile(named_file):
                        plugin_name = item
                        module_path = named_file
                    elif os.path.isfile(init_file):
                        plugin_name = item
                        module_path = init_file
                    else:
                        self.logger.warning(_("Warning: Plugin directory '{item}' in '{directory}' ignored. Missing '{item}.py' or '__init__.py'.").format(item=item, directory=directory))
                
                if plugin_name and module_path:
                    try:
                        # Dynamically import the module
                        spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", module_path)
                        plugin_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(plugin_module)
                        
                        # Check if the 'handle' function exists
                        if hasattr(plugin_module, 'handle'):
                            plugins[plugin_name.lower()] = plugin_module # Store the full module
                            source_type = "Project" if directory == self.plugin_directory else "Global"
                            self.logger.info(_("  - Plugin '{plugin_name}' successfully loaded ({source_type}).").format(plugin_name=plugin_name, source_type=source_type))
                        else:
                            self.logger.warning(_("Warning: Plugin '{plugin_name}' in '{directory}' has no 'handle' function and is ignored.").format(plugin_name=plugin_name, directory=directory))
                    except Exception as e:
                        self.logger.error(_("Error loading plugin '{plugin_name}' from '{directory}': {e}").format(plugin_name=plugin_name, directory=directory, e=e))
                        
        return plugins

    def backup_and_clean_output_dir(self, output_dir, backup_dir):
        """
        Back up the existing output directory into a timestamped folder
        and then clean the output directory for a fresh build.
        """
        if not os.path.isdir(output_dir) or not os.listdir(output_dir):
            self.logger.info(_("\nOutput directory '{output_dir}' is empty or does not exist. Skipping backup.").format(output_dir=output_dir))
            # Ensure the directory exists for the build process.
            os.makedirs(output_dir, exist_ok=True)
            return

        # Check config for backup
        should_backup = self.config.get('backup_on_render', True)

        if should_backup:
            self.logger.info(_("\nCreating backup of existing output directory '{output_dir}'...").format(output_dir=output_dir))
            
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            backup_name_prefix = f"{os.path.basename(output_dir)}_"
            backup_dest_path = os.path.join(backup_dir, f"{backup_name_prefix}{timestamp}")
            
            try:
                # Copy the current output directory as a backup
                shutil.copytree(output_dir, backup_dest_path)
                self.logger.info(_("  - Backup successfully created at: '{backup_dest_path}'").format(backup_dest_path=backup_dest_path))
                
                # Rotation logic
                rotation_count = self.config.get("backup_rotation", 10)
                if rotation_count > 0:
                    try:
                        all_backups = []
                        for f in os.listdir(backup_dir):
                            full_path = os.path.join(backup_dir, f)
                            if f.startswith(backup_name_prefix) and os.path.isdir(full_path):
                                all_backups.append(full_path)
                        
                        all_backups.sort(key=os.path.getmtime)
                        
                        if len(all_backups) > rotation_count:
                            to_delete = all_backups[:-rotation_count]
                            for p in to_delete:
                                shutil.rmtree(p)
                                self.logger.info(_("  - Rotated (deleted) old backup: {p}").format(p=os.path.basename(p)))
                    except Exception as rot_e:
                        self.logger.warning(_("Warning during backup rotation: {e}").format(e=rot_e))

            except Exception as e:
                self.logger.error(_("ERROR backing up output directory: {e}").format(e=e))
        else:
            self.logger.info(_("\nBackup skipped (disabled in config)."))

        try:
            # Clean the original output directory
            self.logger.info(_("Cleaning output directory '{output_dir}'...").format(output_dir=output_dir))
            shutil.rmtree(output_dir)
            self.logger.info(_("  - Old output directory removed."))
            
        except Exception as e:
            self.logger.error(_("ERROR cleaning output directory: {e}").format(e=e))
            self.logger.info(_("The build process continues, but the output directory might be in an inconsistent state."))
        
        # Recreate the empty output directory for the new build
        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(_("  - Empty output directory '{output_dir}' recreated.").format(output_dir=output_dir))

    def _obfuscate_string(self, text):
        """Converts a string to HTML entities for obfuscation."""
        return "".join([f"&#{ord(c)};" for c in text])

    def _obfuscate_sensitive_data(self, html_content):
        """Obfuscates emails, phone numbers and the configured address."""
        # Protect HTML code blocks: <pre> and <code> tags
        protections = {}
        def _protect(match):
            placeholder = f"__HTML_CODE_BLOCK_{len(protections)}__"
            protections[placeholder] = match.group(0)
            return placeholder

        html_content = re.sub(r'(<pre.*?>.*?</pre>|<code.*?>.*?</code>|<script.*?>.*?</script>)', _protect, html_content, flags=re.DOTALL | re.IGNORECASE)

        # 1. E-Mails
        email_re = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        html_content = re.sub(email_re, lambda m: self._obfuscate_string(m.group(0)), html_content)

        # 2. Telefonnummern (Internationales Format: +49... oder 0049...)
        # Sucht nach Nummern, die mit + oder 00 beginnen und mindestens 5 weitere Ziffern/Trennzeichen haben.
        phone_re = r'(?:\+|00)[1-9][0-9 \-\(\)\/]{5,}[0-9]'
        html_content = re.sub(phone_re, lambda m: self._obfuscate_string(m.group(0)), html_content)

        # 3. Adresse (aus Config)
        if self.config.get('contact') and isinstance(self.config['contact'], dict):
            address = self.config['contact'].get('address')
            if address and isinstance(address, str):
                html_content = html_content.replace(address, self._obfuscate_string(address))
        
        # Restore the protected blocks
        for placeholder, code_block in protections.items():
            html_content = html_content.replace(placeholder, code_block)

        return html_content

    # Render Site
    def render(self, progress_callback=None, incremental=False):
        """Render the site using a two-pass process to ensure all pages have access to the full site structure."""
        if not incremental:
            self.backup_and_clean_output_dir(self.site_output_directory, self.backup_directory)
        else:
            self.logger.info(_("Incremental render: Skipping backup and clean."))
            # Ensure the directory exists even without cleaning
            os.makedirs(self.site_output_directory, exist_ok=True)

        self.logger.info(_("Searching for Markdown files..."))
        markdown_files = self.find_markdown_files(self.content_directory)

        PLUGINS = self.load_plugins()

        if not markdown_files:
            self.logger.info(_("No Markdown files found in '{content_dir}'. Nothing to render.").format(content_dir=self.content_directory))
            return

        self.copy_local_assets(self.content_directory, self.site_output_directory)
        self.copy_plugin_assets(self.site_output_directory)
        self.copy_static_directories(self.site_output_directory)
        
        # Copy theme assets
        current_theme = self.config.get("site_theme", "default-blog")
        self.copy_theme_assets(self.site_output_directory, current_theme)

        # Set up template search paths: project first, then global plugins
        template_search_paths = [self.template_directory]
        
        # Search for 'templates' folders in plugin directories (Project & Global)
        plugin_dirs_to_scan = []
        if os.path.isdir(self.plugin_directory):
            plugin_dirs_to_scan.append(self.plugin_directory)
        if os.path.isdir(self.global_plugin_directory):
            plugin_dirs_to_scan.append(self.global_plugin_directory)
            
        for p_dir in plugin_dirs_to_scan:
            for item in sorted(os.listdir(p_dir)):
                tpl_dir = os.path.join(p_dir, item, 'templates')
                if os.path.isdir(tpl_dir):
                    template_search_paths.append(tpl_dir)

        # Add theme templates (lower priority than project templates, but higher than plugins/global)
        if current_theme and current_theme != "default-blog":
            theme_tpl_dir = os.path.join(self.themes_directory, current_theme, "templates")
            if os.path.isdir(theme_tpl_dir):
                template_search_paths.append(theme_tpl_dir)
                self.logger.info(_("  - Added theme templates: {path}").format(path=theme_tpl_dir))

        if os.path.isdir(self.global_plugin_template_directory):
            template_search_paths.append(self.global_plugin_template_directory)
            self.logger.info(_("\nAdding global plugin template directory: '{dir}'").format(dir=self.global_plugin_template_directory))

        env = Environment(loader=FileSystemLoader(template_search_paths))

        env.filters['slugify'] = slugify
        # Filter to map month numbers to German names
        default_month_names = {
            1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni',
            7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
        }
        MONTH_NAMES = self.config.get('month_names', default_month_names)
        env.filters['month_name'] = lambda num: MONTH_NAMES.get(num, '')
        env.globals['generate_index_html'] = generate_index_html
        env.globals['config'] = self.config
        env.globals['now'] = datetime.now()

        # --- DEBUG: Check configuration ---
        self.logger.debug(_("\n--- DEBUG: Loaded configuration for footer ---"))
        self.logger.debug(f"Contact (Typ: {type(self.config.get('contact'))}): {self.config.get('contact')}")
        self.logger.debug(f"Social (Typ: {type(self.config.get('social'))}): {self.config.get('social')}")
        self.logger.debug(f"Header Links (Typ: {type(self.config.get('header_links'))}): {self.config.get('header_links')}")
        self.logger.debug(f"Footer Links (Typ: {type(self.config.get('footer_links'))}): {self.config.get('footer_links')}")
        self.logger.debug("------------------------------------------------\n")

        # Find plugin-specific CSS files and make them globally available
        plugin_css_files = []
        # Search the output directory to find both global and local plugin CSS files
        css_dir_name = os.path.basename(self.css_directory)
        plugin_css_dir = os.path.join(self.site_output_directory, css_dir_name, 'plugins')
        
        if os.path.isdir(plugin_css_dir):
            self.logger.info(_("\nSearching for plugin CSS files (Global & Local)..."))
            for filename in sorted(os.listdir(plugin_css_dir)):
                if filename.endswith('.css'):
                    full_path = os.path.join(plugin_css_dir, filename)
                    # Compute path relative to the output directory (e.g., css/plugins/name.css)
                    web_path = os.path.relpath(full_path, self.site_output_directory).replace(os.path.sep, '/')
                    plugin_css_files.append(web_path)
                    self.logger.info(_("  - Found: {web_path}").format(web_path=web_path))
        env.globals['plugin_css_files'] = plugin_css_files
        try:
            default_template = env.get_template("base.html")
        except Exception as e:
            self.logger.error(_("Error: 'base.html' could not be loaded from directory '{dir}'.").format(dir=self.template_directory))
            self.logger.error(_("Details: {e}").format(e=e))
            self.logger.error(_("Please create a 'base.html' file in the templates directory."))
            return

        # --- Phase 1: Collect data and build the page structure ---
        self.logger.info(_("\nPhase 1: Collecting data and building page structure..."))
        site_structure = {}
        tags_collection = {}
        search_index_data = []
        pages_to_render = []  # For regular content pages
        special_pages_to_render = [] # For pages not in the main index (e.g., about, help)
        all_site_pages = [] # List for the sitemap

        for file, relative_path, asset_file in markdown_files:
            path_parts = os.path.normpath(relative_path).split(os.path.sep)
            is_special_page = any(part.startswith('_') for part in path_parts)

            if is_special_page:
                input_path = os.path.join(self.content_directory, relative_path)
                # Create output path by removing the leading underscore from the directory
                # e.g., content/_about/hilfe.md -> site_output/about/hilfe.html
                output_relative_path = os.path.join(*(p.lstrip('_') for p in path_parts))
                output_path = os.path.join(self.site_output_directory, os.path.splitext(output_relative_path)[0] + ".html")
                try:
                    post = frontmatter.load(input_path)
                    # Check for "draft" status in frontmatter
                    if post.metadata.get('draft', False) is True:
                        self.logger.info(_("  - Skipping draft (special page): {relative_path}").format(relative_path=relative_path))
                        continue
                    page_title = post.metadata.get('title', extract_title(post.content, file))
                    special_pages_to_render.append({'input_path': input_path, 'output_path': output_path, 'relative_path': relative_path, 'post': post, 'page_title': page_title})
                    self.logger.info(_("  - Collected (special page): {relative_path}").format(relative_path=relative_path))
                except Exception as e:
                    self.logger.error(_("Error parsing special page {input_path}: {e}").format(input_path=input_path, e=e))
                continue

            # Skip homepage and 404 page from regular processing, they are handled at the end
            if relative_path in ['index.md', '404.md']:
                continue

            input_path = os.path.join(self.content_directory, relative_path)
            output_path = os.path.join(self.site_output_directory, os.path.splitext(relative_path)[0] + ".html")

            try:
                post = frontmatter.load(input_path)
            except Exception as e:
                self.logger.error(_("Error parsing {input_path}: {e}").format(input_path=input_path, e=e))
                continue

            # Check for "draft" status in frontmatter
            if post.metadata.get('draft', False) is True:
                self.logger.info(_("  - Skipping draft: {relative_path}").format(relative_path=relative_path))
                continue

            # NEW: Add 'release_date' if missing and write it back to the file.
            # This ensures each page has a fixed creation date for sorting.
            made_change_to_frontmatter = False
            if 'release_date' not in post.metadata:
                release_date = datetime.now().strftime('%Y-%m-%d')
                post.metadata['release_date'] = release_date
                self.logger.info(_("    -> Adding 'release_date' ({date}) to '{path}'.").format(date=release_date, path=relative_path))
                made_change_to_frontmatter = True

            # If 'date' is missing, set it to release_date to ensure consistent sorting.
            if 'date' not in post.metadata:
                post.metadata['date'] = post.metadata['release_date']
                self.logger.info(_("    -> Setting missing 'date' to '{date}' in '{path}'.").format(date=post.metadata['date'], path=relative_path))
                made_change_to_frontmatter = True

            if made_change_to_frontmatter:
                try:
                    # Instead of using frontmatter.dump() directly, export the content as a string
                    # so we can insert a comment for the automatically added date.
                    exported_content = frontmatter.dumps(post)
                    
                    # Insert the comment above the 'release_date' line.
                    lines = exported_content.splitlines()
                    new_lines = []
                    comment_added = False
                    for line in lines:
                        # Add the comment only once, in case both 'date' and 'release_date' were added.
                        if line.strip().startswith('release_date:') and not comment_added:
                            new_lines.append('# ' + _('This date is automatically added by the system and should not be removed.'))
                            new_lines.append('# ' + _('It can be adjusted to control the creation date of a post.'))
                            comment_added = True
                        new_lines.append(line)
                    
                    final_content = '\n'.join(new_lines) + '\n'
                    with open(input_path, 'w', encoding='utf-8') as f:
                        f.write(final_content)
                except Exception as e:
                    self.logger.error(_("ERROR writing back metadata in '{input_path}': {e}").format(input_path=input_path, e=e))

            page_title = post.metadata.get('title', extract_title(post.content, file))

            # 1. Add the page to the site structure for the menu, sorted by directories
            path_parts = os.path.normpath(relative_path).split(os.path.sep)
            current_level = site_structure
            for part in path_parts[:-1]:
                current_level = current_level.setdefault(part, {})
            
            file_list = current_level.setdefault('__files', [])
            
            try:
                weight = int(post.metadata.get('weight', 0))
            except (ValueError, TypeError):
                weight = 0

            page_data_for_structure = {
                'title': page_title,
                'path': '/' + os.path.relpath(output_path, self.site_output_directory).replace(os.path.sep, '/'),
                'clean_path': os.path.relpath(output_path, self.site_output_directory).replace(os.path.sep, '/'),
                'date': str(post.metadata.get('date', '')),
                'featured_image': post.metadata.get('featured_image'), # URL path to the featured image
                'weight': weight
            }
            file_list.append(page_data_for_structure)

            # Add page to the sitemap list
            all_site_pages.append({
                'path': page_data_for_structure['path'],
                'source_path': input_path,
                'title': page_title,
                'date': str(post.metadata.get('date', '')),
                'featured_image': post.metadata.get('featured_image'),
                'metadata': post.metadata
            })

            # 2. Collect tags for tag pages
            page_tags = post.metadata.get('tags', [])
            if isinstance(page_tags, list):
                for tag in page_tags:
                    if tag:
                        tags_collection.setdefault(str(tag), []).append(page_data_for_structure)

            # 3. Collect data for the search index
            search_page_data = page_data_for_structure.copy()
            search_page_data['content'] = post.content # Use raw markdown for better search
            search_index_data.append(search_page_data)

            # 4. Store data for the render phase
            pages_to_render.append({
                'input_path': input_path,
                'output_path': output_path,
                'relative_path': relative_path,
                'post': post,
                'page_title': page_title
            })
            self.logger.info(_("  - Collected (standard page): {relative_path}").format(relative_path=relative_path))

        # --- Intermediate step: Generate global pages ---
        # Now that site_structure is complete, we can generate pages that need it.
        self.logger.info(_("\nGenerating global pages and plugin pages..."))


        # Call the page-generation hook for plugins
        for plugin_name, plugin_module in PLUGINS.items():
            if hasattr(plugin_module, 'generate_pages'):
                self.logger.info(_("  - Executing page generation for plugin '{plugin_name}'...").format(plugin_name=plugin_name))
                try:
                    # The plugin function is responsible for extending the `all_site_pages` list
                    plugin_module.generate_pages(
                        tags_collection=tags_collection,
                        env=env,
                        output_dir=self.site_output_directory,
                        site_structure=site_structure,
                        all_site_pages=all_site_pages
                    )
                except Exception as e:
                    self.logger.error(_("ERROR in page generation by plugin '{plugin_name}': {e}").format(plugin_name=plugin_name, e=e))
        # Write the search index as a JSON file
        self.logger.info(_("\nGenerating search index..."))
        search_index_path = os.path.join(self.site_output_directory, 'search_index.json')
        try:
            with open(search_index_path, 'w', encoding='utf-8') as f:
                json.dump(search_index_data, f, ensure_ascii=False)
            self.logger.info(_("  - Search index successfully created: {path}").format(path=search_index_path))
        except Exception as e:
            self.logger.error(_("Error creating search index: {e}").format(e=e))

        # Prepare a clean list of all pages for the plugin context.
        # This allows plugins like 'latest_posts' to access all pages.
        all_pages_for_context = []
        for p_data in pages_to_render: # pages_to_render contains only the normal content pages
            post_metadata = p_data['post'].metadata
            featured_image_url = None
            featured_image_value = post_metadata.get('featured_image')
            if featured_image_value:
                page_dir = os.path.dirname(p_data['relative_path'])
                image_path = os.path.join(page_dir, featured_image_value)
                featured_image_url = image_path.replace(os.path.sep, '/')

            all_pages_for_context.append({
                'title': p_data['page_title'],
                'path': '/' + os.path.relpath(p_data['output_path'], self.site_output_directory).replace(os.path.sep, '/'),
                'metadata': post_metadata,
                'content': p_data['post'].content,
                'featured_image': featured_image_url # URL path to the featured image
            })
        # Sort the list once by date (if present) to improve plugin performance.
        all_pages_for_context.sort(
            key=lambda p: str(p['metadata'].get('date', '1970-01-01')), reverse=True
        )

        # --- Phase 2: Render individual pages ---
        self.logger.info(_("\nPhase 2: Generating individual pages..."))
        # Combine regular pages and special pages for rendering
        all_pages_to_render = pages_to_render + special_pages_to_render
        
        # Initialize progress calculation
        total_pages = len(all_pages_to_render) + 2 # +2 for homepage and 404
        processed_count = 0

        for page_data in all_pages_to_render:
            input_path = page_data['input_path']
            output_path = page_data['output_path']
            relative_path = page_data['relative_path']
            post = page_data['post']
            page_title = page_data['page_title']



            # Check for incremental skipping
            # We only skip if the target file exists AND the source file is older.
            if incremental and os.path.exists(output_path):
                try:
                    if os.path.getmtime(input_path) < os.path.getmtime(output_path):
                        self.logger.info(_("  - Skipping (up-to-date): {path}").format(path=relative_path))
                        processed_count += 1
                        if progress_callback:
                            progress_callback(processed_count, total_pages, _("Skipping: {path}").format(path=relative_path))
                        continue
                except OSError:
                    pass # Fallback: render if the timestamp check fails

            self.logger.info(_("  - Processing: {input_path} -> {output_path}").format(input_path=input_path, output_path=output_path))
            
            # Report progress
            processed_count += 1
            if progress_callback:
                progress_callback(processed_count, total_pages, _("Processing: {path}").format(path=relative_path))

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            depth = len(os.path.normpath(relative_path).split(os.path.sep)) - 1
            relative_prefix = '../' * depth if depth > 0 else './'

            # Choose the layout template based on the frontmatter entry.
            # Default is 'full-width' when unspecified.
            layout = post.metadata.get('layout', 'full-width')
            template_name = f"layout_{layout}.html" # e.g., layout_full-width.html
            try:
                template = env.get_template(template_name)
            except TemplateNotFound:
                self.logger.warning(_("Warning: Layout template '{template_name}' (requested by '{input_path}') not found. 'base.html' is used as fallback.").format(template_name=template_name, input_path=input_path))
                template = default_template

            context = post.metadata.copy()
            context['page_title'] = page_title
            context['current_page_path'] = input_path
            current_output_path = '/' + os.path.relpath(output_path, self.site_output_directory).replace(os.path.sep, '/')
            context['current_output_path'] = current_output_path
            context['relative_prefix'] = relative_prefix
            context['site_structure'] = site_structure
            context['tags_collection'] = tags_collection
            context['all_pages'] = all_pages_for_context # This is where the list is added
            context['breadcrumbs'] = post.metadata.get('breadcrumbs', True) # Enabled by default
            context['content_dir'] = self.content_directory
            context['project_root'] = self.project_root

            # If breadcrumbs are enabled in frontmatter, insert the shortcode
            # automatically (if it is not already present in the content)
            content_source = post.content or ''
            if context.get('breadcrumbs', True) and '[[breadcrumbs' not in content_source and context.get('current_output_path') != '/index.html':
                content_source = '[[breadcrumbs]]\n\n' + content_source

            # 1. Protect code blocks before running plugins
            protected_content, code_protections = _protect_code_blocks(content_source)
            # 2. Run plugins on the protected content
            content_with_plugins_processed = process_plugins(protected_content, context, env, PLUGINS)
            # 3. Restore code blocks
            restored_content = _restore_code_blocks(content_with_plugins_processed, code_protections)
            
            extensions = ['tables', 'fenced_code', 'md_in_html', 'codehilite', 'attr_list']
            extension_configs = {
                'codehilite': {'css_class': 'codehilite', 'guess_lang': True, 'linenums': None, 'use_pygments': True}
            }
            if 'toc_args' in context:
                extensions.append('toc')
                toc_args = context.get('toc_args', {})
                extension_configs['toc'] = {
                    'permalink': True,
                    'title': toc_args.get('title'),
                    'toc_depth': int(toc_args.get('depth', 6))
                }

            rendered_content = markdown.markdown(
                restored_content,
                extensions=extensions,
                extension_configs=extension_configs
            )
            context['content'] = _add_copy_buttons(rendered_content, PLUGINS)
            
            rendered_html = template.render(context)
            rendered_html = self._obfuscate_sensitive_data(rendered_html)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)

        # --- Final step: Generate homepage ---
        self.logger.info(_("\nGenerating homepage..."))
        
        processed_count += 1
        if progress_callback:
            progress_callback(processed_count, total_pages, _("Generating homepage..."))
            
        index_md_path = os.path.join(self.content_directory, 'index.md')
        homepage_content_html = ""
        page_title = _("My Collections")  # Default title
        index_context = {} # Context for the index page
        layout = 'index' # Default layout for homepage

        if os.path.exists(index_md_path):
            self.logger.info(_("  - Loading content for homepage from '{path}'").format(path=index_md_path))
            try:
                post = frontmatter.load(index_md_path)
                
                # Build a context for plugin processing, similar to other pages
                index_context = post.metadata.copy()
                index_context['current_page_path'] = index_md_path
                index_context['relative_prefix'] = './'
                index_context['site_structure'] = site_structure
                index_context['tags_collection'] = tags_collection
                index_context['all_pages'] = all_pages_for_context
                index_context['content_dir'] = self.content_directory
                index_context['project_root'] = self.project_root

                layout = post.metadata.get('layout', 'index')

                # Process plugins on homepage content to enable features like [[include]] or [[gallery]]
                # For the homepage: only add breadcrumbs if explicitly allowed
                index_content_source = post.content or ''
                if index_context.get('breadcrumbs', True) and '[[breadcrumbs' not in index_content_source:
                    index_content_source = '[[breadcrumbs]]\n\n' + index_content_source
                
                # Also protect code blocks here
                protected_content, code_protections = _protect_code_blocks(index_content_source)
                content_with_plugins_processed = process_plugins(protected_content, index_context, env, PLUGINS)
                restored_content = _restore_code_blocks(content_with_plugins_processed, code_protections)



                # Use the full markdown conversion to ensure consistency
                extensions = ['tables', 'fenced_code', 'md_in_html', 'codehilite', 'attr_list']
                extension_configs = {
                    'codehilite': {'css_class': 'codehilite', 'guess_lang': True, 'linenums': None, 'use_pygments': True}
                }
                if 'toc_args' in index_context:
                    extensions.append('toc')
                    toc_args = index_context.get('toc_args', {})
                    extension_configs['toc'] = {'permalink': True, 'title': toc_args.get('title'), 'toc_depth': int(toc_args.get('depth', 6))}

                homepage_content_html = markdown.markdown(restored_content, extensions=extensions, extension_configs=extension_configs)
                homepage_content_html = _add_copy_buttons(homepage_content_html, PLUGINS)

                if 'title' in post.metadata:
                    page_title = post.metadata['title']
            except Exception as e:
                self.logger.error(_("Error parsing '{path}': {e}").format(path=index_md_path, e=e))
                homepage_content_html = "<p>Fehler beim Laden des Inhalts.</p>"
        else:
            self.logger.info(_("  - '{path}/index.md' not found. Homepage will be created without additional content.").format(path=self.content_directory))

        # Template-Auswahl mit Fallback
        template_name = f"layout_{layout}.html"
        template = None
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            # Fallback 1: index_page.html (Legacy Support)
            try:
                template = env.get_template("index_page.html")
            except TemplateNotFound:
                # Fallback 2: base.html
                try:
                    template = env.get_template("base.html")
                except TemplateNotFound:
                    self.logger.error(_("Error: No suitable template found for homepage (neither layout, index_page.html nor base.html)."))

        if template:
            context = index_context.copy()
            context['page_title'] = page_title
            context['site_structure'] = site_structure
            context['relative_prefix'] = './'
            context['current_output_path'] = '/index.html'
            context['content'] = homepage_content_html
            context['homepage_content'] = homepage_content_html # For legacy templates
            context.setdefault('breadcrumbs', True)

            rendered_index_html = template.render(context)
            rendered_index_html = self._obfuscate_sensitive_data(rendered_index_html)
            with open(os.path.join(self.site_output_directory, "index.html"), 'w', encoding='utf-8') as f:
                f.write(rendered_index_html)
            self.logger.info(_("  - 'index.html' successfully created."))
        
        # --- Generate 404 error page ---
        self.logger.info(_("\nGenerating 404 error page..."))
        processed_count += 1
        if progress_callback:
            progress_callback(processed_count, total_pages, _("Generating 404 error page..."))
            
        error_404_md_path = os.path.join(self.content_directory, '404.md')
        if os.path.exists(error_404_md_path):
            try:
                post = frontmatter.load(error_404_md_path)
                page_title = post.metadata.get('title', _('Page not found'))
                
                template_name = post.metadata.get('template', 'base.html')
                try:
                    template = env.get_template(template_name)
                except TemplateNotFound:
                    self.logger.warning(_("Warning: Template '{template_name}' for 404 page not found. 'base.html' is used.").format(template_name=template_name))
                    template = default_template

                context = post.metadata.copy()
                context['page_title'] = page_title
                context['relative_prefix'] = './'
                context['site_structure'] = site_structure
                context['current_output_path'] = '/404.html'
                context['tags_collection'] = tags_collection
                context['breadcrumbs'] = post.metadata.get('breadcrumbs', True) # Enable breadcrumbs on 404 page by default
                context['content_dir'] = self.content_directory
                context['project_root'] = self.project_root

                error_content_source = post.content or ''
                if context.get('breadcrumbs', True) and '[[breadcrumbs' not in error_content_source:
                    error_content_source = '[[breadcrumbs]]\n\n' + error_content_source
                
                # Also protect code blocks here
                protected_content, code_protections = _protect_code_blocks(error_content_source)
                content_with_plugins_processed = process_plugins(protected_content, context, env, PLUGINS)
                restored_content = _restore_code_blocks(content_with_plugins_processed, code_protections)
                
                extensions = ['tables', 'fenced_code', 'md_in_html', 'codehilite', 'attr_list']
                extension_configs = {
                    'codehilite': {'css_class': 'codehilite', 'guess_lang': True, 'linenums': None, 'use_pygments': True}
                }
                rendered_content = markdown.markdown(
                    restored_content,
                    extensions=extensions,
                    extension_configs=extension_configs
                )
                context['content'] = _add_copy_buttons(rendered_content, PLUGINS)
                
                rendered_html = template.render(context)
                rendered_html = self._obfuscate_sensitive_data(rendered_html)
                output_path = os.path.join(self.site_output_directory, "404.html")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                self.logger.info(_("  - '404.html' successfully created."))
            except Exception as e:
                self.logger.error(_("Error creating 404 page: {e}").format(e=e))
        else:
            self.logger.info(_("  - '{path}' not found. No 404.html page will be created.").format(path=error_404_md_path))

        # Add the homepage to the sitemap list
        all_site_pages.append({
            'path': '/index.html',
            'source_path': index_md_path if os.path.exists(index_md_path) else None
        })

        # Generiere die Sitemap als einen der letzten Schritte
        self.generate_sitemap(all_site_pages, self.site_output_directory)

        self.logger.info(_("\nSite generation completed."))
        return list(PLUGINS.keys())

def run(context):
    """
    Entry point for the WorkerThread.
    Expects 'project_root' in the context.
    """
    project_root = context.get('project_root', '.')
    app_root = context.get('app_root')
    incremental = context.get('incremental', False)
    try:
        renderer = SiteRenderer(project_root, app_root)
        progress_callback = context.get('progress_callback')
        loaded_plugins = renderer.render(progress_callback=progress_callback, incremental=incremental)
        
        msg = _("Rendering successfully completed.")
        if loaded_plugins:
            msg += _("\n\nLoaded plugins ({count}):\n").format(count=len(loaded_plugins)) + ", ".join(sorted(loaded_plugins))
        else:
            msg += _("\n\nNo plugins loaded.")
        return msg
    except Exception as e:
        # Propagate errors so the WorkerThread can catch them
        raise e
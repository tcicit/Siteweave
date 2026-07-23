import os
import re

# Zentraler Regex für Markdown-Links: [text](url) oder ![alt](url)
# Group 1: prefix (e.g. "[text](" or "![alt](")
# Group 2: URL
# Group 3: suffix (")")
MARKDOWN_LINK_RE = re.compile(r'(\[.*?\]\(|!\[.*?\]\()([^)]+)(\))')
LINK_RE = MARKDOWN_LINK_RE

# Regex für Markdown-Bilder
IMAGE_LINK_RE = re.compile(r'!\[.*?\]\((.*?)\)')

# Regex für normale Markdown-Links (ignoriert Bilder)
PAGE_LINK_RE = re.compile(r'\[[^!].*?\]\((.*?)\)')

# Regex für HTML-Bilder
HTML_IMAGE_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)


def get_file_usage_count(search_dir, target_abs_path):
    """
    Zählt, in wie vielen Markdown-Dokumenten innerhalb von search_dir 
    die Datei target_abs_path referenziert wird.
    """
    if not search_dir or not os.path.exists(search_dir):
        return 0
        
    count = 0
    target_abs_path = os.path.normpath(target_abs_path)
    
    project_root = os.path.abspath(os.path.join(search_dir, os.pardir))

    for root, subdirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith(('.md', '.markdown')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    link_dir = os.path.dirname(file_path)
                    found_in_file = False
                    
                    for match in LINK_RE.finditer(content):
                        url = match.group(2)
                        if url.startswith(('http:', 'https:', 'mailto:', 'ftp:', '#')):
                            continue
                        
                        try:
                            # If the URL starts with a leading slash, treat it as project-root relative
                            if url.startswith('/'):
                                abs_link_target = os.path.normpath(os.path.join(project_root, url.lstrip('/')))
                            else:
                                abs_link_target = os.path.normpath(os.path.join(link_dir, url))
                            if abs_link_target == target_abs_path:
                                found_in_file = True
                                break
                        except:
                            continue
                    
                    if found_in_file:
                        count += 1
                except:
                    continue
    return count

def update_links_in_directory(search_dir, old_abs_path, new_abs_path):
    """
    Durchsucht alle Markdown-Dateien in search_dir und passt Links an, 
    die auf old_abs_path zeigen. Unterstützt Datei- und Ordner-Umbenennungen.
    """
    if not search_dir or not os.path.exists(search_dir):
        return 0

    count = 0
    old_abs_path = os.path.normpath(old_abs_path)
    new_abs_path = os.path.normpath(new_abs_path)
    
    project_root = os.path.abspath(os.path.join(search_dir, os.pardir))

    for root, subdirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith(('.md', '.markdown')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    link_dir = os.path.dirname(file_path)
                    
                    def replace_link(match):
                        prefix = match.group(1)
                        url = match.group(2)
                        suffix = match.group(3)
                        
                        if url.startswith(('http:', 'https:', 'mailto:', 'ftp:', '#')):
                            return match.group(0)
                        
                        try:
                            # Resolve URLs that start with '/' relative to the project root
                            leading_slash = url.startswith('/')
                            if leading_slash:
                                abs_link_target = os.path.normpath(os.path.join(project_root, url.lstrip('/')))
                            else:
                                abs_link_target = os.path.normpath(os.path.join(link_dir, url))
                            target_str = str(abs_link_target)
                            old_path_str = str(old_abs_path)
                            
                            if target_str == old_path_str or target_str.startswith(old_path_str + os.path.sep):
                                if target_str != old_path_str:
                                    # Ziel liegt innerhalb eines umbenannten Ordners
                                    rel_inside = os.path.relpath(abs_link_target, old_abs_path)
                                    target_abs_path = os.path.join(new_abs_path, rel_inside)
                                else:
                                    target_abs_path = new_abs_path
                                # Optionally skip shallow one-level parent-relative links (preserve legacy behavior)
                                # Skip patterns like '../assets/...' (but allow '../../assets/...')
                                if (not leading_slash) and url.startswith('../') and not url.startswith('../../'):
                                    return match.group(0)

                                # Preserve leading slash if the original URL used it
                                if leading_slash:
                                    new_rel = '/' + os.path.relpath(target_abs_path, project_root).replace(os.path.sep, '/')
                                else:
                                    new_rel = os.path.relpath(target_abs_path, link_dir).replace(os.path.sep, '/')
                                return f"{prefix}{new_rel}{suffix}"
                        except:
                            pass
                        return match.group(0)

                    new_content = LINK_RE.sub(replace_link, content)
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        count += 1
                except:
                    continue
    return count
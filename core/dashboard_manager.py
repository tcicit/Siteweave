import os
import frontmatter
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal



class DashboardWorker(QThread):
    """Hintergrund-Thread für den Dashboard-Scan, um den UI-Thread nicht zu blockieren."""
    stats_ready = pyqtSignal(dict)

    def __init__(self, project_root, config):
        super().__init__()
        self.manager = DashboardManager(project_root, config)

    def run(self):
        stats = self.manager.get_stats()
        self.stats_ready.emit(stats)

class DashboardManager:
    """Sammelt Statistiken und Status-Informationen für ein Projekt."""
    
    def __init__(self, project_root, config):
        self.project_root = project_root
        self.config = config
        self.content_dir = os.path.join(project_root, config.get('content_directory', 'content'))
        self.output_dir = os.path.join(project_root, config.get('site_output_directory', 'site_output'))
        self.assets_dir = os.path.join(project_root, config.get('assets_directory', 'assets'))

    def get_stats(self):
        """Gibt ein Dictionary mit allen wichtigen Kennzahlen zurück."""
        stats = {
            'pages': {'total': 0, 'published': 0, 'drafts': 0},
            'recent_files': [],
            'output_size': "0 B",
            'media': {'count': 0, 'size': "0 B"},
            'last_render': None,
            'seo_warnings': 0
        }
        
        # 1. Seiten-Statistiken & Zuletzt bearbeitet
        if os.path.exists(self.content_dir):
            for root, _, files in os.walk(self.content_dir):
                for f in files:
                    if f.endswith(tuple(self.config.get('markdown_extensions', ['.md']))):
                        stats['pages']['total'] += 1
                        try:
                            file_path = os.path.join(root, f)
                            post = frontmatter.load(file_path)
                            
                            if post.get('draft'):
                                stats['pages']['drafts'] += 1
                            else:
                                stats['pages']['published'] += 1
                            
                            # SEO Check
                            if not post.get('title'):
                                stats['seo_warnings'] += 1
                            if not post.get('meta_description'):
                                stats['seo_warnings'] += 1
                                
                            mtime = os.path.getmtime(file_path)
                            stats['recent_files'].append({
                                'name': f,
                                'full_path': file_path,
                                'date': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M'),
                                'timestamp': mtime
                            })
                        except Exception:
                            pass

        # Sortiere nach Datum (neueste zuerst)
        stats['recent_files'].sort(key=lambda x: x['timestamp'], reverse=True)
        stats['recent_files'] = stats['recent_files'][:5]

        # 2. Größe des Site-Outputs
        if os.path.exists(self.output_dir):
            total_size = 0
            for root, _, files in os.walk(self.output_dir):
                for f in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, f))
                    except (FileNotFoundError, OSError):
                        continue
            stats['output_size'] = self._format_size(total_size)
            
            # Zeitstempel der letzten Generierung (basierend auf index.html)
            idx = os.path.join(self.output_dir, 'index.html')
            if os.path.exists(idx):
                stats['last_render'] = datetime.fromtimestamp(os.path.getmtime(idx)).strftime('%Y-%m-%d %H:%M')

        # 3. Medien-Bibliothek
        if os.path.exists(self.assets_dir):
            m_count = 0
            for root, _, files in os.walk(self.assets_dir):
                m_count += len(files)
            stats['media']['count'] = m_count

        return stats

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
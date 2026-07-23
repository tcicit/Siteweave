import os, shlex
import shutil
import subprocess
import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, QHeaderView, 
                             QLineEdit, QSplitter, QWidget, QFrame, QAbstractItemView,
                             QProgressBar, QSizePolicy, QStackedWidget, QListWidget,
                             QListWidgetItem, QButtonGroup, QComboBox)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QByteArray, QTimer
from core.utils import is_editor_available, open_external_editor
from PyQt6.QtGui import QPixmap, QIcon
from core.i18n import _
from core import link_utils
from core.config_manager import ConfigManager

class NumericTableWidgetItem(QTableWidgetItem):
    """Custom item for numeric sorting while maintaining text display."""
    def __lt__(self, other):
        try:
            return float(self.data(Qt.ItemDataRole.UserRole)) < float(other.data(Qt.ItemDataRole.UserRole))
        except (TypeError, ValueError, AttributeError):
            return super().__lt__(other)

class UsageSearchWorker(QThread):
    """Worker thread to search for file links without freezing the UI."""
    finished = pyqtSignal(list)

    def __init__(self, content_dir, filename):
        super().__init__()
        self.content_dir = content_dir
        self.filename = filename
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        linked_files = []
        for root, dirs, files in os.walk(self.content_dir):
            if not self._is_running: return
            for f in files:
                if not self._is_running: return
                if f.endswith(('.md', '.markdown')):
                    p = os.path.join(root, f)
                    try:
                        with open(p, 'r', encoding='utf-8') as f_obj:
                            if self.filename in f_obj.read():
                                linked_files.append(p)
                    except: continue
        self.finished.emit(linked_files)

class MediaScannerWorker(QThread):
    """Worker thread to scan assets and pre-calculate usage without freezing the UI."""
    file_found = pyqtSignal(dict)
    progress = pyqtSignal(int, int)
    finished = pyqtSignal()

    def __init__(self, assets_dir, content_dir):
        super().__init__()
        self.assets_dir = assets_dir
        self.content_dir = content_dir
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        from collections import defaultdict
        usage_counts = defaultdict(int)
        
        # 1. Scan content directory ONCE to build a usage map
        # This is much faster than scanning for each file individually.
        if os.path.exists(self.content_dir):
            for root, subdirs, files in os.walk(self.content_dir):
                if not self._is_running: return
                for f in files:
                    if f.endswith(('.md', '.markdown')):
                        p = os.path.join(root, f)
                        try:
                            with open(p, 'r', encoding='utf-8') as f_obj:
                                content = f_obj.read()
                                link_dir = os.path.dirname(p)
                                # Use the centralized regex from link_utils
                                for match in link_utils.LINK_RE.finditer(content):
                                    url = match.group(2)
                                    if url.startswith(('http:', 'https:', 'mailto:', 'ftp:', '#')):
                                        continue
                                    try:
                                        abs_link_target = os.path.normpath(os.path.join(link_dir, url))
                                        usage_counts[abs_link_target] += 1
                                    except: pass
                        except: continue

        # 2. Scan assets directory
        if not os.path.exists(self.assets_dir):
            self.finished.emit()
            return

        all_asset_files = []
        for root, subdirs, files in os.walk(self.assets_dir):
            for f in files:
                if not f.startswith('.'):
                    all_asset_files.append(os.path.join(root, f))
        
        total = len(all_asset_files)
        for i, full_path in enumerate(sorted(all_asset_files)):
            if not self._is_running: return
            
            data = {
                'full_path': full_path,
                'rel_path': os.path.relpath(full_path, self.assets_dir),
                'filename': os.path.basename(full_path),
                'size_kb': os.path.getsize(full_path) / 1024,
                'usage': usage_counts.get(os.path.normpath(full_path), 0),
                'mtime': os.path.getmtime(full_path),
                'is_compressed': "-compressed" in os.path.basename(full_path)
            }
            self.file_found.emit(data)
            self.progress.emit(i + 1, total)
        
        self.finished.emit()

class MediaManagerDialog(QDialog):
    # Column Constants
    COL_ICON = 0
    COL_FILENAME = 1
    COL_TYPE = 2
    COL_SIZE = 3
    COL_DATE = 4
    COL_USAGE = 5
    COL_COMPRESSED = 6
    COL_COUNT = 7

    def __init__(self, project_root, assets_dir, content_dir, thumbnail_size, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.assets_dir = assets_dir
        self.content_dir = content_dir
        self.search_worker = None
        self.scanner_worker = None
        self.thumbnail_size = thumbnail_size
        self.current_preview_path = None
        self.current_exif_html = ""
        
        # Lade Konfiguration für externe Editoren
        cm = ConfigManager(ConfigManager.get_app_config_path())
        self.app_config = cm.load()
        self.external_editors = self.app_config.get("external_editors", [])
        
        self.setWindowTitle(_("Media Library Manager"))
        
        self.init_ui()
        self.restore_layout()
        
        # Starte den Ladevorgang mit einer minimalen Verzögerung (50ms).
        # Dies erlaubt der GUI, sich initial zu zeichnen und verhindert das "schwarze Fenster".
        QTimer.singleShot(50, self.load_media)

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Top Bar: Search and Upload
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search media..."))
        self.search_input.textChanged.connect(self.filter_table)
        
        upload_btn = QPushButton(QIcon.fromTheme("list-add"), _("Upload Media"))
        upload_btn.clicked.connect(self.upload_media)
        
        self.clear_cache_btn = QPushButton(QIcon.fromTheme("edit-clear"), _("Clear Cache"))
        self.clear_cache_btn.clicked.connect(self.clear_thumbnail_cache)
        
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(upload_btn)
        top_layout.addWidget(self.clear_cache_btn)
        self.update_cache_info()
        main_layout.addLayout(top_layout)

        # Main Area: Table and Preview Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Side Container for View Switcher and Views
        view_container = QWidget()
        view_vbox = QVBoxLayout(view_container)
        view_vbox.setContentsMargins(0, 0, 0, 0)

        # View Switcher Toolbar
        view_switcher_layout = QHBoxLayout()
        self.list_view_btn = QPushButton(QIcon.fromTheme("view-list"), "List")
        self.list_view_btn.setToolTip(_("List View"))
        self.list_view_btn.setCheckable(True)
        self.list_view_btn.setChecked(True)
        self.list_view_btn.setFixedWidth(40)

        self.grid_view_btn = QPushButton(QIcon.fromTheme("view-grid"), "Grid")
        self.grid_view_btn.setToolTip(_("Gallery View"))
        self.grid_view_btn.setCheckable(True)
        self.grid_view_btn.setFixedWidth(40)

        self.view_group = QButtonGroup(self)
        self.view_group.addButton(self.list_view_btn, 0)
        self.view_group.addButton(self.grid_view_btn, 1)
        self.view_group.idClicked.connect(self.switch_view)

        # Sort Selector
        view_switcher_layout.addSpacing(20)
        view_switcher_layout.addWidget(QLabel(_("Sort:")))
        self.sort_combo = QComboBox()
        self.sort_combo.addItem(_("Name"), "name")
        self.sort_combo.addItem(_("Size"), "size")
        self.sort_combo.addItem(_("Date"), "date")
        self.sort_combo.addItem(_("Usage"), "usage")
        self.sort_combo.currentIndexChanged.connect(self.apply_sorting)
        view_switcher_layout.addWidget(self.sort_combo)
        
        self.sort_order_btn = QPushButton()
        self.sort_order_btn.setIcon(QIcon.fromTheme("view-sort-ascending"))
        self.sort_order_btn.setCheckable(True)
        self.sort_order_btn.setFixedWidth(30)
        self.sort_order_btn.toggled.connect(self.apply_sorting)
        view_switcher_layout.addWidget(self.sort_order_btn)

        view_switcher_layout.addStretch()
        view_switcher_layout.addWidget(self.list_view_btn)
        view_switcher_layout.addWidget(self.grid_view_btn)
        view_vbox.addLayout(view_switcher_layout)

        self.view_stack = QStackedWidget()

        # View 1: Table
        self.table = QTableWidget(0, self.COL_COUNT)
        self.table.setHorizontalHeaderLabels([
            "", _("Filename"), _("Type"), _("Size"), _("Date"), _("Usage"), _("Compressed")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.update_preview)
        self.table.setSortingEnabled(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_FILENAME, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(self.COL_ICON, 40)
        self.view_stack.addWidget(self.table)

        # View 2: Gallery (Icon Mode)
        self.gallery = QListWidget()
        self.gallery.setViewMode(QListWidget.ViewMode.IconMode)
        self.gallery.setIconSize(QSize(self.thumbnail_size, self.thumbnail_size))
        self.gallery.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.gallery.setSpacing(15)
        self.gallery.setWordWrap(True)
        self.gallery.itemSelectionChanged.connect(self.update_preview)
        self.view_stack.addWidget(self.gallery)

        view_vbox.addWidget(self.view_stack)
        self.splitter.addWidget(view_container)

        # Right Side: Preview and Details
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        preview_frame.setMinimumWidth(300)
        self.preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_label = QLabel(_("Select a file to preview"))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(400, 300)
        self.preview_label.setStyleSheet("border: 1px solid palette(mid); border-radius: 4px;")
        # Initiales Icon setzen
        self.preview_label.setPixmap(QIcon.fromTheme("image-x-generic").pixmap(QSize(64, 64)))
        
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setOpenExternalLinks(False)
        self.info_label.linkActivated.connect(self.on_link_clicked)
        
        self.preview_layout.addWidget(self.preview_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.preview_layout.addWidget(self.info_label)
        self.preview_layout.addStretch()
        
        # Quick Actions in Preview
        self.edit_btn = QPushButton(_("Edit Image"))
        self.edit_btn.clicked.connect(self.edit_current_image)
        self.external_edit_btn = QPushButton(_("External Editor"))
        self.external_edit_btn.clicked.connect(self.open_external_editor)
        self.rename_btn = QPushButton(_("Rename File"))
        self.rename_btn.clicked.connect(self.rename_current)
        self.delete_btn = QPushButton(_("Delete File"))
        self.delete_btn.setStyleSheet("color: #e74c3c;")
        self.delete_btn.clicked.connect(self.delete_current)
        self.copy_path_btn = QPushButton(_("Copy Path"))
        self.copy_path_btn.clicked.connect(self.copy_current_path)
        
        self.preview_layout.addWidget(self.edit_btn)
        self.preview_layout.addWidget(self.external_edit_btn)
        self.preview_layout.addWidget(self.copy_path_btn)
        self.preview_layout.addWidget(self.rename_btn)
        self.preview_layout.addWidget(self.delete_btn)
        
        self.edit_btn.setEnabled(False)
        self.external_edit_btn.setEnabled(False)
        self.copy_path_btn.setEnabled(False)
        self.rename_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        
        self.splitter.addWidget(preview_frame)
        main_layout.addWidget(self.splitter)

        # Footer
        bottom_layout = QHBoxLayout()
        self.stats_label = QLabel(_("Ready"))
        bottom_layout.addWidget(self.stats_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setMaximumWidth(200)
        bottom_layout.addWidget(self.progress_bar)
        
        close_btn = QPushButton(_("Close"))
        close_btn.clicked.connect(self.accept)
        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_layout)

    def load_media(self):
        """Starts background scanning of media files."""
        if self.scanner_worker and self.scanner_worker.isRunning():
            self.scanner_worker.stop()
            self.scanner_worker.wait()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.gallery.clear()
        self.stats_label.setText(_("Scanning files..."))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.scanner_worker = MediaScannerWorker(self.assets_dir, self.content_dir)
        self.scanner_worker.file_found.connect(self._add_item_to_table)
        self.scanner_worker.progress.connect(self._update_load_progress)
        self.scanner_worker.finished.connect(self._on_scan_finished)
        self.scanner_worker.start()

    def _update_load_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def _on_scan_finished(self):
        self.table.setSortingEnabled(True)
        self.stats_label.setText(f"{self.table.rowCount()} " + _("Files found"))
        self.progress_bar.setVisible(False)
        self.update_cache_info()
        self.apply_sorting()

    def _add_item_to_table(self, data):
        row = self.table.rowCount()
        self.table.insertRow(row)

        full_path = data['full_path']
        filename = data['filename']
        ext = os.path.splitext(filename)[1].lower()
        
        # Wir bereiten zwei verschiedene Icons vor: 40px für die Tabelle, thumbnail_size für die Galerie
        table_icon = QIcon()
        gallery_icon = QIcon()
        
        # Icon (Thumbnail Placeholder)
        icon_item = QTableWidgetItem()
        
        # Thumbnail-Cache Pfad berechnen (Logik analog zum ThumbnailWorker)
        cache_dir = os.path.join(self.project_root, ".siteweave", "cache", "thumbs")
        rel_path_to_proj = os.path.relpath(full_path, self.project_root)
        safe_name = rel_path_to_proj.replace(os.sep, "_") + ".png"
        thumb_path = os.path.join(cache_dir, safe_name)

        # Prüfen, ob ein gültiges Thumbnail im Cache existiert
        has_thumb = os.path.exists(thumb_path) and os.path.getmtime(thumb_path) >= os.path.getmtime(full_path)

        pixmap = QPixmap()
        if ext in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.pdf'):
            try:
                # Loading from cache is significantly faster than opening full images or rendering PDFs
                if has_thumb:
                    pixmap = QPixmap(thumb_path)
                elif ext == '.pdf':
                    # QPixmap cannot load PDFs directly; we fall back to generic icon if no cache exists
                    pixmap = QPixmap() 
                else:
                    pixmap = QPixmap(full_path)
                
                if not pixmap.isNull():
                    # Skalierung für Tabelle
                    table_icon = QIcon(pixmap.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    # Skalierung für Galerie
                    gallery_icon = QIcon(pixmap.scaled(QSize(self.thumbnail_size, self.thumbnail_size), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    # Fallback icon if pixmap couldn't be loaded or doesn't exist yet
                    theme_icon = "document-pdf" if ext == ".pdf" else "image-x-generic"
                    table_icon = QIcon.fromTheme(theme_icon)
                    gallery_icon = table_icon
            except Exception:
                table_icon = QIcon.fromTheme("image-x-generic")
                gallery_icon = table_icon
        elif ext == '.svg':
            try:
                table_icon = QIcon(full_path)
                gallery_icon = table_icon
            except Exception:
                table_icon = QIcon.fromTheme("image-x-generic")
                gallery_icon = table_icon
        else:
            table_icon = QIcon.fromTheme("text-x-generic")
            gallery_icon = table_icon

        icon_item.setIcon(table_icon)

        date_str = datetime.datetime.fromtimestamp(data['mtime']).strftime('%Y-%m-%d %H:%M')
        
        size_item = NumericTableWidgetItem(f"{data['size_kb']:.1f} KB")
        size_item.setData(Qt.ItemDataRole.UserRole, data['size_kb'])
        
        usage_item = NumericTableWidgetItem(str(data['usage']))
        usage_item.setData(Qt.ItemDataRole.UserRole, data['usage'])
        
        self.table.setItem(row, self.COL_ICON, icon_item)
        self.table.setItem(row, self.COL_FILENAME, QTableWidgetItem(data['rel_path']))
        self.table.setItem(row, self.COL_TYPE, QTableWidgetItem(os.path.splitext(filename)[1].upper()))
        self.table.setItem(row, self.COL_SIZE, size_item)
        self.table.setItem(row, self.COL_DATE, QTableWidgetItem(date_str))
        self.table.setItem(row, self.COL_USAGE, usage_item)
        self.table.setItem(row, self.COL_COMPRESSED, QTableWidgetItem(_("Yes") if data['is_compressed'] else _("No")))
        
        # Store absolute path in UserRole for the table
        filename_item = self.table.item(row, self.COL_FILENAME)
        filename_item.setData(Qt.ItemDataRole.UserRole, full_path)
        
        # Add to Gallery View
        gallery_item = QListWidgetItem(gallery_icon, data['rel_path'])
        gallery_item.setData(Qt.ItemDataRole.UserRole, full_path)
        gallery_item.setData(Qt.ItemDataRole.UserRole + 1, data['usage'])
        gallery_item.setData(Qt.ItemDataRole.UserRole + 2, date_str)
        gallery_item.setData(Qt.ItemDataRole.UserRole + 3, data['mtime'])
        gallery_item.setData(Qt.ItemDataRole.UserRole + 4, data['size_kb'])
        self.gallery.addItem(gallery_item)

        if row % 10 == 0:
            self.stats_label.setText(_("Loading... ({count})").format(count=row))

    def apply_sorting(self):
        """Applies sorting to both Table and Gallery views."""
        if self.table.rowCount() == 0:
            return

        criteria = self.sort_combo.currentData()
        is_desc = self.sort_order_btn.isChecked()
        order = Qt.SortOrder.DescendingOrder if is_desc else Qt.SortOrder.AscendingOrder
        
        # Update Toggle Icon
        icon_name = "view-sort-descending" if is_desc else "view-sort-ascending"
        self.sort_order_btn.setIcon(QIcon.fromTheme(icon_name))

        # 1. Sort Table
        col_map = {
            "name": self.COL_FILENAME,
            "size": self.COL_SIZE,
            "date": self.COL_DATE,
            "usage": self.COL_USAGE
        }
        self.table.sortByColumn(col_map.get(criteria, self.COL_FILENAME), order)

        # 2. Sort Gallery (Manually reorder QListWidget)
        items = []
        while self.gallery.count() > 0:
            items.append(self.gallery.takeItem(0))
        
        def sort_key(item):
            if criteria == "name": return item.text().lower()
            if criteria == "size": return item.data(Qt.ItemDataRole.UserRole + 4)
            if criteria == "date": return item.data(Qt.ItemDataRole.UserRole + 3)
            if criteria == "usage": return item.data(Qt.ItemDataRole.UserRole + 1)
            return item.text().lower()

        items.sort(key=sort_key, reverse=is_desc)
        for item in items:
            self.gallery.addItem(item)

    def refresh_preview_image(self, update_cache=False):
        """Aktualisiert nur die Bildskalierung basierend auf der aktuellen Label-Größe."""
        if not self.current_preview_path:
            return
            
        full_path = self.current_preview_path
        
        if full_path.lower().endswith('.pdf'):
            cache_dir = os.path.join(self.project_root, ".siteweave", "cache", "thumbs")
            rel_path_to_proj = os.path.relpath(full_path, self.project_root)
            safe_name = rel_path_to_proj.replace(os.sep, "_") + ".png"
            thumb_path = os.path.join(cache_dir, safe_name)

            if os.path.exists(thumb_path) and os.path.getmtime(thumb_path) >= os.path.getmtime(full_path):
                self.preview_label.setPixmap(QPixmap(thumb_path).scaled(
                    self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                try:
                    import fitz  # PyMuPDF
                    from PyQt6.QtGui import QImage
                    doc = fitz.open(full_path)
                    page = doc.load_page(0) 
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                    
                    if update_cache:
                        os.makedirs(cache_dir, exist_ok=True)
                        qimg.save(thumb_path, "PNG")
                        self.update_cache_info()

                    self.preview_label.setPixmap(QPixmap.fromImage(qimg).scaled(
                        self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    doc.close()
                except (ImportError, Exception):
                    self.preview_label.setPixmap(QIcon.fromTheme("document-pdf").pixmap(self.preview_label.size()))

        elif full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif')):
            if full_path.lower().endswith('.svg'):
                pixmap = QIcon(full_path).pixmap(self.preview_label.size())
            else:
                pixmap = QPixmap(full_path)

            if not pixmap.isNull():
                scaled = pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
        else:
            self.preview_label.clear()
            self.preview_label.setText(_("No Preview Available"))

    def _get_exif_info(self, full_path):
        """Extrahiert grundlegende Metadaten und EXIF-Informationen."""
        if not full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            return ""

        from PIL import Image
        from PIL.ExifTags import TAGS
        info_lines = []
        try:
            with Image.open(full_path) as img:
                # Grundlegende Info (immer vorhanden)
                info_lines.append(f"<b>{_('Dimensions')}:</b> {img.width} x {img.height} px")
                
                # EXIF Daten auslesen
                exif_data = img.getexif()
                if exif_data:
                    # Interessante Tags filtern
                    interesting = {'Model': _('Camera'), 'Make': _('Manufacturer'), 'Software': _('Software')}
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        if tag_name in interesting:
                            info_lines.append(f"<b>{interesting[tag_name]}:</b> {value}")
        except Exception:
            pass
            
        return "<br>".join(info_lines)

    def update_preview(self):
        # Diese Methode wird aufgerufen, wenn der Benutzer eine andere Datei auswählt. 
        # Sie aktualisiert die Vorschau und die Metadatenanzeige.
        # Stop previous search if still running
        if self.search_worker:
            self.search_worker.stop()
            self.search_worker.wait()

        is_table = self.view_stack.currentIndex() == 0
        active_view = self.table if is_table else self.gallery
        selected = active_view.selectedItems()

        if not selected:
            self.preview_label.setPixmap(QIcon.fromTheme("image-x-generic").pixmap(QSize(64, 64)))
            self.current_preview_path = None
            self.current_exif_html = ""
            self.info_label.setText("")
            self.edit_btn.setEnabled(False)
            self.external_edit_btn.setEnabled(False)
            self.copy_path_btn.setEnabled(False)
            self.rename_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        if is_table:
            row = selected[0].row()
            full_path = self.table.item(row, self.COL_FILENAME).data(Qt.ItemDataRole.UserRole)
            usage_count = self.table.item(row, self.COL_USAGE).text()
            date_str = self.table.item(row, self.COL_DATE).text()
        else:
            item = selected[0]
            full_path = item.data(Qt.ItemDataRole.UserRole)
            usage_count = str(item.data(Qt.ItemDataRole.UserRole + 1))
            date_str = item.data(Qt.ItemDataRole.UserRole + 2)

        self.current_preview_path = full_path

        self.edit_btn.setEnabled(full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')))
        
        ext = os.path.splitext(full_path)[1].lower()
        # Prüfen ob ein passender Editor konfiguriert ist
        matching_editor = None
        for editor in self.external_editors: # type: ignore
            if ext in [e.lower() for e in editor.get('extensions', [])] and is_editor_available(editor.get('command')):
                matching_editor = editor
                break
        self.external_edit_btn.setEnabled(matching_editor is not None)

        self.copy_path_btn.setEnabled(True)
        self.rename_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        # Bilddarstellung aktualisieren
        # Bei PDF-Dateien oder wenn die Vorschaugröße geändert wurde, wird die Vorschau neu generiert.
        self.refresh_preview_image(update_cache=True)

        # Metadaten auslesen
        self.current_exif_html = self._get_exif_info(full_path)
        exif_section = f"<hr>{self.current_exif_html}" if self.current_exif_html else ""

        # Preliminary info while searching
        self.info_label.setText(f"<b>{_('Path')}:</b> {full_path}<br>"
                                f"<b>{_('Date')}:</b> {date_str}<br>"
                                f"<b>{_('Usage')}:</b> {usage_count}<br>"
                                f"{exif_section}<br>"
                                f"<b>{_('Linked in')}:</b> {_('Searching...')}")

        # Start background search
        if int(usage_count) > 0:
            self.search_worker = UsageSearchWorker(self.content_dir, os.path.basename(full_path))
            self.search_worker.finished.connect(lambda links: self.on_search_finished(links, full_path, date_str, usage_count))
            self.search_worker.start()
        else:
            self.on_search_finished([], full_path, date_str, usage_count)

    def edit_current_image(self):
        """Opens the rudimentary image editor for the current image."""
        if not self.current_preview_path:
            return
        try:
            from gui.dialogs.image_editor_dialog import ImageEditorDialog
            dialog = ImageEditorDialog(self.current_preview_path, self.project_root, self)
            if dialog.exec():
                self.load_media()
        except Exception as e:
            print(f"Failed to open ImageEditor: {e}")
            QMessageBox.critical(self, _("Error"), _("Could not open Image Editor: {e}").format(e=e))

    def open_external_editor(self):
        """Startet die Datei im konfigurierten externen Programm."""
        if not self.current_preview_path:
            return
            
        ext = os.path.splitext(self.current_preview_path)[1].lower()
        # type: ignore
        command = None
        for editor in self.external_editors:
            if ext in [e.lower() for e in editor.get('extensions', [])]:
                command = editor.get('command')
                break
                
        if not command:
            return
            
        try:
            open_external_editor(command, self.current_preview_path)
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Could not start editor: {e}").format(e=e))

    def on_search_finished(self, links, path, date_str, usage_count):
        # Check if we are still looking at the same file
        if path != self.current_preview_path:
            return

        linked_html = []
        for p in links:
            rel_p = os.path.relpath(p, self.content_dir)
            linked_html.append(f'<a href="{p}" style="color: #3498db; text-decoration: underline;">{rel_p}</a>')

        exif_section = f"<hr>{self.current_exif_html}" if self.current_exif_html else ""
        usage_list_text = "<br>".join(linked_html) if linked_html else _("None")
        
        self.info_label.setText(f"<b>{_('Path')}:</b> {path}<br>"
                                f"<b>{_('Date')}:</b> {date_str}<br>"
                                f"<b>{_('Usage')}:</b> {usage_count}<br>"
                                f"{exif_section}<br>"
                                f"<b>{_('Linked in')}:</b><br>{usage_list_text}")

    def filter_table(self, text):
        search_text = text.lower()
        for i in range(self.table.rowCount()):
            item = self.table.item(i, self.COL_FILENAME)
            hidden = search_text not in item.text().lower()
            self.table.setRowHidden(i, hidden)
            
        for i in range(self.gallery.count()):
            item = self.gallery.item(i)
            item.setHidden(search_text not in item.text().lower())

    def switch_view(self, view_id):
        """Switches between List and Gallery view and syncs selection."""
        old_is_table = self.view_stack.currentIndex() == 0
        old_view = self.table if old_is_table else self.gallery
        selected = old_view.selectedItems()
        
        self.view_stack.setCurrentIndex(view_id)
        
        # Sync selection if possible
        if selected:
            if view_id == 1: # Switching to Gallery
                row = selected[0].row()
                self.gallery.setCurrentRow(row)
            else: # Switching to Table
                idx = self.gallery.row(selected[0])
                self.table.selectRow(idx)

    def upload_media(self):
        # Öffnet einen Dateidialog zum Auswählen von Dateien und kopiert sie in den Assets-Ordner.
        files, _filter = QFileDialog.getOpenFileNames(self, _("Upload Media"), "", _("Media Files (*.png *.jpg *.jpeg *.gif *.svg *.webp *.pdf *.zip);;All Files (*)"))
        if files:
            for f in files:
                dest = os.path.join(self.assets_dir, os.path.basename(f))
                if os.path.exists(dest):
                    res = QMessageBox.question(self, _("Overwrite?"), _("File '{name}' already exists. Overwrite?").format(name=os.path.basename(f)))
                    if res == QMessageBox.StandardButton.No: continue
                shutil.copy2(f, dest)
            self.load_media()

    def clear_thumbnail_cache(self):
        """Deletes all files in the thumbnail cache directory."""
        cache_dir = os.path.join(self.project_root, ".siteweave", "cache", "thumbs")
        if not os.path.isdir(cache_dir) or not os.listdir(cache_dir):
            QMessageBox.information(self, _("Clear Cache"), _("Cache is already empty."))
            return
            
        res = QMessageBox.question(
            self, _("Clear Cache"),
            _("Do you really want to delete all cached thumbnails? They will be regenerated when needed."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if res == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                QMessageBox.information(self, _("Success"), _("Thumbnail cache cleared."))
                self.load_media()
            except Exception as e:
                QMessageBox.critical(self, _("Error"), _("Could not clear cache: {e}").format(e=e))

    def update_cache_info(self):
        """Calculates the size of the thumbnail cache and updates the button text."""
        cache_dir = os.path.join(self.project_root, ".siteweave", "cache", "thumbs")
        total_size = 0
        file_count = 0
        if os.path.isdir(cache_dir):
            try:
                for entry in os.scandir(cache_dir):
                    if entry.is_file():
                        total_size += entry.stat().st_size
                        file_count += 1
            except Exception:
                pass
        
        if total_size < 1024:
            size_str = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
            
        self.clear_cache_btn.setText(_("Clear Cache ({size})").format(size=size_str))
        self.clear_cache_btn.setToolTip(_("Delete {count} cached thumbnails ({size})").format(count=file_count, size=size_str))

    def rename_current(self):
        is_table = self.view_stack.currentIndex() == 0
        active_view = self.table if is_table else self.gallery
        selected = active_view.selectedItems()
        if not selected: return
        
        old_path = self.table.item(selected[0].row(), self.COL_FILENAME).data(Qt.ItemDataRole.UserRole) if is_table else selected[0].data(Qt.ItemDataRole.UserRole)
        old_name = os.path.basename(old_path)
        
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, _("Rename Media"), _("New Filename:"), text=old_name)
        
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                # Link Update Logik
                count = link_utils.update_links_in_directory(self.content_dir, old_path, new_path)
                if count > 0:
                    QMessageBox.information(self, _("Links Updated"), _("Updated {count} links in Markdown files.").format(count=count))
                self.load_media()
            except Exception as e:
                QMessageBox.critical(self, _("Error"), str(e))

    def delete_current(self):
        is_table = self.view_stack.currentIndex() == 0
        active_view = self.table if is_table else self.gallery
        selected = active_view.selectedItems()
        if not selected: return
        
        if is_table:
            path = self.table.item(selected[0].row(), self.COL_FILENAME).data(Qt.ItemDataRole.UserRole)
            usage = int(self.table.item(selected[0].row(), self.COL_USAGE).text())
        else:
            path = selected[0].data(Qt.ItemDataRole.UserRole)
            usage = int(selected[0].data(Qt.ItemDataRole.UserRole + 1))
        
        msg = _("Are you sure you want to delete this file?")
        if usage > 0:
            msg += "\n\n" + _("WARNING: This file is currently used in {count} documents!").format(count=usage)
            
        res = QMessageBox.warning(self, _("Delete Media"), msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if res == QMessageBox.StandardButton.Yes:
            try:
                os.remove(path)
                self.load_media()
            except Exception as e:
                QMessageBox.critical(self, _("Error"), str(e))

    def copy_current_path(self):
        is_table = self.view_stack.currentIndex() == 0
        active_view = self.table if is_table else self.gallery
        selected = active_view.selectedItems()
        if not selected: return
        
        full_path = self.table.item(selected[0].row(), self.COL_FILENAME).data(Qt.ItemDataRole.UserRole) if is_table else selected[0].data(Qt.ItemDataRole.UserRole)
        # Wir berechnen den Pfad relativ zum Content-Ordner für das einfache Einfügen
        # Assets liegen meist in einem Parallelordner oder Unterordner
        try:
            rel_web_path = os.path.join("assets", os.path.relpath(full_path, self.assets_dir)).replace(os.path.sep, '/')
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(rel_web_path)
        except:
            pass

    def on_link_clicked(self, link):
        """Opens the linked file in the editor and closes the dialog."""
        if os.path.exists(link):
            main_win = self.parent()
            if hasattr(main_win, 'load_file'):
                main_win.load_file(link)
                self.accept()

    def restore_layout(self):
        """Lädt Geometrie und Splitter-Zustand aus der zentralen app_config.yaml."""
        try:
            cm = ConfigManager(ConfigManager.get_app_config_path())
            state = cm.apply_ui_state(self, "media_manager", default_size=(1100, 650))
            if state:
                self.splitter.restoreState(state)
            else:
                # Setze Standard-Größen (z.B. 70% Tabelle, 30% Vorschau), falls kein Zustand existiert
                self.splitter.setSizes([750, 350])

            # Sortiereinstellungen laden
            sort_idx = cm.get("media_manager_sort_index", 0)
            sort_desc = cm.get("media_manager_sort_descending", False)
            self.sort_combo.setCurrentIndex(sort_idx)
            self.sort_order_btn.setChecked(sort_desc)
        except Exception:
            self.resize(1100, 650)
            self.splitter.setSizes([750, 350])

    def save_layout(self):
        """Speichert die aktuelle Geometrie und den Splitter-Zustand in der app_config.yaml."""
        cm = ConfigManager(ConfigManager.get_app_config_path())
        cm.save_ui_state("media_manager", self.saveGeometry(), self.splitter.saveState())

        # Sortiereinstellungen speichern
        cm.load()
        cm.update({
            "media_manager_sort_index": self.sort_combo.currentIndex(),
            "media_manager_sort_descending": self.sort_order_btn.isChecked()
        })
        cm.save()

    def done(self, result):
        """Wird aufgerufen, wenn der Dialog mit accept() oder reject() geschlossen wird."""
        if self.scanner_worker:
            self.scanner_worker.stop()
            self.scanner_worker.wait()
        self.save_layout()
        super().done(result)

    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster über das 'X' geschlossen wird."""
        if self.scanner_worker:
            self.scanner_worker.stop()
            self.scanner_worker.wait()
        self.save_layout()
        super().closeEvent(event)
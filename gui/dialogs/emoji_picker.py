import os
import logging
import yaml
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QTabWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from core.i18n import _

logger = logging.getLogger(__name__)

def validate_emoji_data(data):
    """Return only emoji entries matching the [character, keywords] schema."""
    if not isinstance(data, dict):
        logger.warning("Emoji configuration must contain a mapping of categories.")
        return {}

    validated_data = {}
    for category, emojis in data.items():
        if not isinstance(category, str) or not category.strip():
            logger.warning("Skipping emoji category with an invalid name: %r", category)
            continue
        if not isinstance(emojis, list):
            logger.warning("Skipping emoji category '%s': expected a list.", category)
            continue

        valid_emojis = []
        for index, entry in enumerate(emojis, 1):
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                logger.warning(
                    "Skipping invalid emoji entry %s in category '%s': expected [character, keywords].",
                    index,
                    category,
                )
                continue

            char, keywords = entry
            if not isinstance(char, str) or not char.strip():
                logger.warning("Skipping emoji entry %s in category '%s': character is empty.", index, category)
                continue
            if not isinstance(keywords, str):
                logger.warning("Skipping emoji entry %s in category '%s': keywords must be text.", index, category)
                continue

            valid_emojis.append((char, keywords))

        if valid_emojis:
            validated_data[category] = valid_emojis

    return validated_data

class EmojiPicker(QDialog):
    """
    Ein Dialog zur Auswahl von Emojis mit Kategorien (Tabs).
    Sendet das Signal emoji_selected(str) wenn ein Emoji angeklickt wird.
    Funktionen:
- Anzeige von Emojis in Kategorien (z.B. Gesichter, Objekte, Natur, Symbole).
- Suchfunktion, die sowohl die Emojis als auch die zugehörigen Keywords durchsucht.
- Tooltips mit Beschreibung und Hex-Code der Emojis.
- Anpassung der Emoji-Größe für bessere Sichtbarkeit.

    """
    emoji_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Insert Emoji"))
        self.resize(700, 500)
        
        # Pfad zur Emoji-Konfiguration ermitteln
        self.app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.emoji_config_path = os.path.join(self.app_root, "emojis.yaml")

        layout = QVBoxLayout(self)
        
        # Suchfeld
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(_("Search emojis..."))
        self.search_input.textChanged.connect(self.filter_emojis)
        layout.addWidget(self.search_input)
        
        # Tabs für Kategorien
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.emoji_lists = [] # Liste aller QListWidgets für die Suche
        
        self.emoji_data = self.get_emoji_data()
        self.populate_tabs()

    def get_emoji_data(self):
        """Gibt ein Dictionary mit Kategorien und Emojis zurück."""
        if os.path.exists(self.emoji_config_path):
            try:
                with open(self.emoji_config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    validated_data = validate_emoji_data(data)
                    if validated_data:
                        return validated_data
            except Exception as e:
                print(f"Fehler beim Laden der Emoji-Konfiguration: {e}")
        
        # Fallback (Minimal), falls die Datei nicht existiert oder fehlerhaft ist
        return {
            _("Faces & Emotions"): [
                ("😀", _("grin smile happy lucky")),
                ("😂", _("laugh tears joy funny")),
            ]
        }

    def populate_tabs(self):
        font = QFont()
        font.setPointSize(28) # Größere Schrift für bessere Sichtbarkeit der Emojis

        for category, emojis in self.emoji_data.items():
            list_widget = QListWidget()
            list_widget.setViewMode(QListWidget.ViewMode.IconMode)
            list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
            list_widget.setSpacing(10)
            list_widget.setFont(font)
            list_widget.itemClicked.connect(self.on_item_clicked)
            
            for entry in emojis:
                if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                    logger.warning("Skipping malformed emoji entry in category '%s'.", category)
                    continue
                char, keywords = entry
                item = QListWidgetItem(char)
                
                # Hex Code berechnen (für Tooltip und Suche)
                # Behandelt auch zusammengesetzte Emojis
                hex_codes = " ".join([f"{ord(c):X}" for c in char])
                
                # Suchindex: Kategorie + Keywords + Hex Code
                search_text = f"{category} {keywords} {hex_codes}"
                item.setData(Qt.ItemDataRole.UserRole, search_text)
                
                # Tooltip mit Name und Hex Code
                item.setToolTip(_("{keywords}\nHex: {hex_codes}").format(keywords=keywords, hex_codes=hex_codes))
                
                list_widget.addItem(item)
            
            self.tabs.addTab(list_widget, category)
            self.emoji_lists.append(list_widget)

    def filter_emojis(self, text):
        search_query = text.lower().strip()
        search_terms = search_query.split()
        
        first_visible_tab = -1
        current_tab_still_visible = False
        
        for i, list_widget in enumerate(self.emoji_lists):
            has_matches = False
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if not search_terms:
                    item.setHidden(False)
                    has_matches = True
                else:
                    item_data = item.data(Qt.ItemDataRole.UserRole).lower()
                    emoji_char = item.text().lower()
                    # Überprüfen, ob ALLE Suchbegriffe im Index oder im Emoji vorkommen
                    match = all(term in item_data or term in emoji_char for term in search_terms)
                    item.setHidden(not match)
                    if match:
                        has_matches = True
            
            # Tab nur anzeigen, wenn er Treffer hat (oder die Suche leer ist)
            tab_visible = has_matches or not search_query
            self.tabs.setTabVisible(i, tab_visible)
            
            if tab_visible:
                if first_visible_tab == -1:
                    first_visible_tab = i
                if i == self.tabs.currentIndex():
                    current_tab_still_visible = True

        # Falls der aktuelle Tab verschwindet, zum ersten Tab mit Treffern wechseln
        if search_query and not current_tab_still_visible and first_visible_tab != -1:
            self.tabs.setCurrentIndex(first_visible_tab)

    def on_item_clicked(self, item):
        # Signal senden und Dialog schließen
        self.emoji_selected.emit(item.text())
        self.accept()
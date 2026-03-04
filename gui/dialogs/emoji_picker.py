from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QTabWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

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
        self.setWindowTitle("Emoji einfügen")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Suchfeld
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suchen (z.B. 'lachen', '1F600')...")
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
        return {
            "Gesichter & Emotionen": [
                ("😀", "grinsen smile happy glücklich"), 
                ("😂", "lachen tränen joy lustig"), 
                ("🥰", "liebe love herz verliebt"),
                ("😎", "cool sonnenbrille"), 
                ("🤔", "denken thinking nachdenken"), 
                ("👍", "daumen hoch like gut"), 
                ("👎", "daumen runter dislike schlecht"),
                ("❤️", "herz rot liebe"), 
                ("💙", "herz blau"), 
                ("💚", "herz grün"),
                ("🎉", "party konfetti feiern"), 
                ("✨", "funkeln sparkles neu"),
                ("🔥", "feuer fire hot heiß"),
                ("😢", "traurig weinen traurig"),
                ("😡", "wütend sauer ärger"), 
                ("😱", "schreien angst schock"), 
                ("🤗", "umarmen hug liebe"),

            ],
            "Objekte & Technik": [
                ("🚀", "rakete rocket start launch"), 
                ("💻", "computer laptop pc code"), 
                ("💾", "speichern disk save"),
                ("📱", "handy smartphone"),
                ("📷", "kamera foto bild"), 
                ("🎥", "video film movie"),
                ("📞", "telefon anruf kontakt"), 
                ("📧", "email mail nachricht"), 
                ("🔒", "schloss sicherheit privat"), 
                ("🔓", "offen unlock public"),
                ("⚙️", "einstellungen zahnrad config"), 
                ("🔧", "werkzeug tool fix"), 
                ("📦", "paket box archiv"),
                ("🔍", "lupe suchen search"),
                ("💡", "idee licht lampe tipp"),
                ("📌", "pin anheften wichtig"),
                ("📎", "büroklammer anhang datei"),
                ("🖥️", "desktop monitor computer"),
                ("📚", "buch bibliothek"),
                ("🎧", "kopfhörer musik audio"),
                ("🖨️", "drucker printer"),
                ("💳", "kreditkarte bank bezahlen"),
                ("📖", "buch lesen lernen"),
                ("🗑️", "mülleimer löschen trash"),
                ("🔋", "batterie energie power"),
                ("✏️", "bleistift schreiben schreibzeug"),
                ("📊", "diagramm statistik chart"),
                ("📈", "aufwärts trend wachstum"),
                ("📉", "abwärts trend rückgang"),
                ("🖱️", "maus computer klicken"),
                ("⌨️", "tastatur computer tippen"),
                ("📄", "blatt papier dokument"),
            ],
            "Natur & Tiere": [
                ("🌍", "erde welt earth global"), 
                ("🐍", "schlange python code"), 
                ("🐧", "pinguin linux"), 
                ("🐱", "katze cat"), 
                ("🐶", "hund dog"), 
                ("🦄", "einhorn unicorn magic"), 
                ("👻", "geist ghost"),
                ("🤖", "roboter bot automat"),
                ("🍎", "apfel mac osx"), 
                ("🍕", "pizza essen food"), 
                ("☕", "kaffee coffee drink"), 
                ("🍺", "bier beer drink"),
                ("🌸", "blume blüte spring"), 
                ("🌞", "sonne sommer heiß"), 
                ("🌧️", "regen wolke nass"),
                ("❄️", "schnee winter kalt"),
                ("🌈", "regenbogen bunt hope"), 
                ("⚡", "blitz energie schnell"), 
                ("💨", "wind schnell weg"),
                ("🌊", "welle wasser meer"),
                ("🌳", "baum natur grün"),
                ("🌵", "kaktus wüste trocken"),
                ("🌺", "hibiskus blume exotisch"),
                ("🌙", "mond nacht dunkel"),
                ("🌟", "stern nacht glänzen"),
                ("🌼", "gänseblümchen blume gelb"),
                ("🌻", "sonnenblume blume gelb groß"),
                ("🌾", "getreide reifen ernte"),
                ("🌿", "blatt pflanze grün"),
                ("🍂", "herbst blätter fall autumn"),
                ("🍁", "ahornblatt herbst fall autumn"),
                ("🍇", "trauben wein frucht"),                
                ("🍷", "wein trinken alkohol"),
                ("🌑", "mondphase neue_mond"),
                ("🌒", "mondphase zunehmender_mond"),
                ("🌓", "mondphase erstes_viertel"),
                ("🌔", "mondphase zweites_viertel"),
                ("🌕", "mondphase viertes_viertel"),
                ("🌧️", "regen wolke nass"),
                ("⛈️", "gewitter blitz regen wolke"),
                ("🌩️", "blitz gewitter"),
                ("🌨️", "schnee winter kalt"),
                ("❄️", "schnee winter kalt"),
                ("🌪️", "tornado wind sturm"),
                ("🌫️", "nebel fog"),
                ("🌬️", "wind schnell weg"),
                ("☀️", "sonne sommer heiß"),
                ("🌤️", "sonne wolken mix"),
                ("🌥️", "wolken sonne mix"),
                ("🌦️", "regen wolke nass"),
            ],
            "Symbole & UI": [
                ("✅", "check haken ok fertig"), 
                ("❌", "kreuz x falsch fehler"), 
                ("⚠️", "warnung achtung warning"),
                ("ℹ️", "info information"), 
                ("❓", "fragezeichen hilfe help"), 
                ("❗", "ausrufezeichen wichtig"), 
                ("📅", "kalender datum zeit"), 
                ("⭐", "stern star favorit"), 
                ("📝", "notiz memo schreiben dokument"), 
                ("📁", "ordner folder verzeichnis"), 
                ("🔗", "link kette verbindung"), 
                ("🎨", "kunst farbe design"), 
                ("🎵", "musik note sound"), 
                ("🏠", "haus home start"), 
                ("🚗", "auto car fahrzeug"), 
                ("✈️", "flugzeug plane reise"), 
                ("🛑", "stop halt"), 
                ("🚩", "flagge fahne ziel"), 
                ("➡️", "pfeil rechts next"), 
                ("⬅️", "pfeil links back"), 
                ("⬆️", "pfeil oben up"), 
                ("⬇️", "pfeil unten down"), 
                ("©️", "copyright recht"), 
                ("™️", "trademark marke"), 
                ("®️", "registered"),
                ("🪟", "fenster windows"), 
            ],
            "Fahnen": [
                ("🏁", "flagge ziel finish"), 
                ("🚩", "flagge fahne ziel"), 
                ("🎌", "fahnen kreuz"), 
                ("🏴", "schwarze flagge"), 
                ("🏳️", "weiße flagge"), 
            ],
            "Länder Fahnen": [
                ("🇨🇭", "schweiz switzerland"),
                ("🇩🇪", "deutschland germany flagge"), 
                ("🇺🇸", "usa amerika united states flagge"), 
                ("🇫🇷", "frankreich france flagge"), 
                ("🇬🇧", "großbritannien uk england flagge"), 
                ("🇨🇳", "china flagge"), 
                ("🇯🇵", "japan flagge"), 
                ("🇰🇷", "südkorea south korea flagge"), 
                ("🇮🇳", "indien india flagge"), 
                ("🇧🇷", "brasilien brazil flagge"), 
                ("🇨🇦", "kanada canada flagge"), 
                ("🇪🇸", "spanien spain flagge"),
                ("🇮🇹", "italien italy flagge"), 
                ("🇷🇺", "russland russia flagge"), 
                ("🇦🇺", "australien australia flagge"), 
                ("🇸🇪", "schweden sweden flagge"), 
                ("🇳🇱", "niederlande netherlands flagge"), 
                ("🇧🇪", "belgien belgium flagge"), 
                ("🇩🇰", "dänemark denmark flagge"), 
                ("🇫🇮", "finnland finland flagge"), 
                ("🇳🇴", "norwegen norway flagge"), 
                ("🇵🇱", "polen poland flagge"), 
                ("🇵🇹", "portugal flagge"), 
                ("🇬🇷", "griechenland greece flagge"), 
                ("🇨🇿", "tschechien czech republic flagge"), 
                ("🇭🇺", "ungarn hungary flagge"), 
                ("🇷🇴", "rumänien romania flagge"), 
                ("🇸🇰", "slowakei slovakia flagge"), 
                ("🇸🇮", "slowenien slovenia flagge"), 
                ("🇱🇹", "litauen latvia flagge"),
                ("🇱🇺", "luxemburg luxemburg flagge"),    
                ("🇱🇻", "lettland latvia flagge"), 
                ("🇪🇪", "estland estonia flagge"), 
                ("🇨🇾", "zypern cyprus flagge"), 
                ("🇲🇹", "malta flagge"), 
                ("🇮🇸", "island iceland flagge"), 
                ("🇲🇩", "moldawien moldova flagge"), 
                ("🇧🇬", "bulgarien bulgaria flagge"), 
                ("🇷🇸", "serbien serbia flagge"), 
                ("🇭🇷", "kroatien croatia flagge"), 
                ("🇧🇦", "bosnien bosnia flagge"), 
                ("🇦🇱", "albanien albania flagge"), 
                ("🇲🇰", "mazedonien macedonia flagge"),
                ("🇦🇿", "aserbaidschan azerbaijan flagge"), 
                ("🇬🇪", "georgien georgia flagge"), 
                ("🇦🇲", "armenien armenia flagge"), 
                ("🇧🇾", "weißrussland belarus flagge"), 
                ("🇺🇦", "ukraine flagge"), 
                ("🇰🇿", "kasachstan kazakhstan flagge"), 
                ("🇹🇷", "türkei turkey flagge"), 
                ("🇮🇷", "iran flagge"), 
                ("🇸🇦", "saudi arabien saudi arabia flagge"), 
                ("🇮🇶", "irak iraq flagge"), 
                ("🇸🇾", "syrien syria flagge"), 
                ("🇱🇧", "libanon lebanon flagge"), 
                ("🇯🇴", "jordanien jordan flagge"), 
                ("🇰🇼", "kuwait flagge"), 
                ("🇶🇦", "katar qatar flagge"), 
                ("🇧🇭", "bahrain flagge"), 
                ("🇧🇳", "brunei flagge"), 
                ("🇧🇹", "bhutan flagge"),
                ("🇲🇾", "malaysia flagge"), 
                ("🇸🇬", "singapur singapore flagge"), 
                ("🇮🇩", "indonesien indonesia flagge"), 
                ("🇻🇳", "vietnam flagge"), 
                ("🇹🇭", "thailand flagge"), 
                ("🇵🇭", "philippinen philippines flagge"), 
                ("🇱🇦", "laos flagge"), 
                ("🇰🇭", "kambodscha cambodia flagge"), 
                ("🇲🇲", "myanmar flagge"), 
                ("🇳🇵", "nepal flagge"), 
                ("🇧🇩", "bangladesch bangladesh flagge"), 
                ("🇱🇰", "sri lanka flagge"), 
                ("🇦🇫", "afghanistan flagge"),
            ]

                
        }

    def populate_tabs(self):
        font = QFont()
        font.setPointSize(24)

        for category, emojis in self.emoji_data.items():
            list_widget = QListWidget()
            list_widget.setViewMode(QListWidget.ViewMode.IconMode)
            list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
            list_widget.setSpacing(10)
            list_widget.setFont(font)
            list_widget.itemClicked.connect(self.on_item_clicked)
            
            for char, keywords in emojis:
                item = QListWidgetItem(char)
                
                # Hex Code berechnen (für Tooltip und Suche)
                # Behandelt auch zusammengesetzte Emojis
                hex_codes = " ".join([f"{ord(c):X}" for c in char])
                
                # Wir speichern die Suchbegriffe + Hex Code in den User-Daten
                search_text = f"{keywords} {hex_codes}"
                item.setData(Qt.ItemDataRole.UserRole, search_text)
                
                # Tooltip mit Name und Hex Code
                item.setToolTip(f"{keywords}\nHex: {hex_codes}")
                
                list_widget.addItem(item)
            
            self.tabs.addTab(list_widget, category)
            self.emoji_lists.append(list_widget)

    def filter_emojis(self, text):
        text = text.lower()
        for list_widget in self.emoji_lists:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                keywords = item.data(Qt.ItemDataRole.UserRole).lower()
                # Suche im Emoji selbst oder in den Keywords (inkl. Hex)
                if not text or text in item.text() or text in keywords:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def on_item_clicked(self, item):
        # Signal senden und Dialog schließen
        self.emoji_selected.emit(item.text())
        self.accept()
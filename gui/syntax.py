from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

'''
Docstring für syntax.py
Dieser Code definiert die Klasse MarkdownHighlighter, die von QSyntaxHighlighter erbt und für die Syntaxhervorhebung von Markdown-Texten in einem QTextDocument verantwortlich ist.
Die Klasse unterstützt verschiedene Markdown-Elemente wie Überschriften, Fett- und Kursivschrift, Inline-Code, Links, Zitate, Plugins, Listen, horizontale Linien und Bilder.
DieFarben für die Hervorhebung können je nach Theme (Hell/Dunkel) angepasst werden,und es gibt auch die Möglichkeit, benutzerdefinierte Farben zu setzen.
Die Logik für die Hervorhebung basiert auf regulären Ausdrücken, die in der update_rules-Methode definit werden. Die highlightBlock-Methode wendet diese Regeln auf den Text an und behandelt auch mehrzeilige Code-Blöcke korrekt. 
Diese Klasse wird in der GUI verwendet, um die Markdown-Dateien mit ansprechender Syntaxhervorhebung darzustellen.

'''

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        self.dark_mode = False
        self.custom_colors = {}
        self.update_rules()

    def set_theme(self, dark_mode):
        self.dark_mode = dark_mode
        self.update_rules()
        self.rehighlight()

    def update_rules(self):
        self.highlighting_rules = []

        # Standard-Farben definieren
        colors = {
            'header': "#2980b9",
            'bold': "#000000",
            'italic': "#000000",
            'inline_code': "#d35400",
            'code_block': "#d35400",
            'link': "#8e44ad",
            'blockquote': "#7f8c8d",
            'plugin': "#c0392b",
            'list_marker': "#000000",
            'hr': "#999999",
            'image_alt': "#000000"
        }

        if self.dark_mode:
            colors = {
                'header': "#569cd6",
                'bold': "#d4d4d4",
                'italic': "#d4d4d4",
                'inline_code': "#ce9178",
                'code_block': "#ce9178",
                'link': "#9cdcfe",
                'blockquote': "#6a9955",
                'plugin': "#c586c0",
                'list_marker': "#d4d4d4",
                'hr': "#555555",
                'image_alt': "#d4d4d4"
            }

        # Benutzerdefinierte Farben anwenden
        if self.custom_colors:
            colors.update(self.custom_colors)
        
        self.current_colors = colors # Speichern für highlightBlock

        # 1. Überschriften (z.B. # Titel)
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(colors['header'])) 
        header_format.setFontWeight(QFont.Weight.Bold)
        self.add_rule(r"^#+ .*", header_format)

        # 2. Fett (**text** oder __text__)
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)
        bold_format.setForeground(QColor(colors['bold']))
        self.add_rule(r"\*\*.*?\*\*", bold_format)
        self.add_rule(r"__.*?__", bold_format)

        # 3. Kursiv (*text* oder _text_)
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        italic_format.setForeground(QColor(colors['italic']))
        self.add_rule(r"\*.*?\*", italic_format)
        self.add_rule(r"_.*?_", italic_format)

        # 4. Inline Code (`text`)
        code_format = QTextCharFormat()
        code_format.setForeground(QColor(colors['inline_code']))
        code_format.setFontFamily("Courier New")
        self.add_rule(r"`[^`]+`", code_format)

        # 5. Links (text)
        link_format = QTextCharFormat()
        link_format.setForeground(QColor(colors['link']))
        link_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        self.add_rule(r"\[.*?\]\(.*?\)", link_format)

        # 6. Zitate (> text)
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor(colors['blockquote']))
        self.add_rule(r"^> .*", quote_format)

        # 7. Deine Plugins ([[plugin]])
        plugin_format = QTextCharFormat()
        plugin_format.setForeground(QColor(colors['plugin']))
        plugin_format.setFontWeight(QFont.Weight.Bold)
        self.add_rule(r"\[\[.*?\]\]", plugin_format)

        # 8. Listen (-, *, + oder 1.)
        list_format = QTextCharFormat()
        list_format.setForeground(QColor(colors['list_marker']))
        list_format.setFontWeight(QFont.Weight.Bold)
        self.add_rule(r"^\s*([-*+]|\d+\.)\s+", list_format)

        # 9. Horizontale Linie (---, ***, ___)
        hr_format = QTextCharFormat()
        hr_format.setForeground(QColor(colors['hr']))
        self.add_rule(r"^\s*([-*_]){3,}\s*$", hr_format)

        # 10. Bilder (![alt](url))
        image_format = QTextCharFormat()
        image_format.setForeground(QColor(colors['image_alt']))
        self.add_rule(r"!\[[^\]]*\]\([^)]+\)", image_format)

    def add_rule(self, pattern, format):
        rule = (QRegularExpression(pattern), format)
        self.highlighting_rules.append(rule)

    def highlightBlock(self, text):
        # 1. Standard-Regeln anwenden (Regex)
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # 2. Multiline Code Blöcke (``` ... ```)
        # Wir nutzen den Block-Status: 0 = Normal, 1 = Innerhalb Code-Block
        
        code_block_format = QTextCharFormat()
        code_block_format.setForeground(QColor(self.current_colors.get('code_block', '#d35400')))
        code_block_format.setFontFamily("Courier New")

        state = self.previousBlockState()
        if state == -1: state = 0

        if text.strip().startswith("```"):
            # Umschalten: Wenn wir drin waren (1), sind wir jetzt draußen (0), und umgekehrt.
            # Die Zeile selbst gehört noch zum Block.
            self.setFormat(0, len(text), code_block_format)
            if state == 1:
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(1)
        else:
            if state == 1:
                # Wir sind im Block -> Alles einfärben
                self.setFormat(0, len(text), code_block_format)
                self.setCurrentBlockState(1)
            else:
                self.setCurrentBlockState(0)

    def set_custom_colors(self, color_scheme):
        """
        Setzt benutzerdefinierte Farben und aktualisiert die Regeln.
        """
        self.custom_colors = color_scheme
        self.update_rules()
        self.rehighlight()
import enchant
import os

class SpellChecker:
    """
    Ein Wrapper um pyenchant, der das Wörterbuch verwaltet und
    eine persönliche Wortliste (User-Dictionary) unterstützt.
    """
    def __init__(self, language_code="en_US", user_dict_path=None):
        self.dictionary = None
        self.user_dictionary = None
        self.user_dict_path = user_dict_path
        self.set_language(language_code, user_dict_path)

    def set_language(self, language_code, user_dict_path=None):
        """Lädt ein neues Wörterbuch für die angegebene Sprache. Gibt True bei Erfolg zurück, sonst False."""
        self.language_code = language_code
        if user_dict_path:
            self.user_dict_path = user_dict_path

        try:
            # Das Hauptwörterbuch laden
            self.dictionary = enchant.Dict(self.language_code)
            
            # Ein persönliches Wörterbuch für "Zum Wörterbuch hinzufügen"
            if self.user_dict_path:
                # Sicherstellen, dass die Datei existiert
                if not os.path.exists(self.user_dict_path):
                    open(self.user_dict_path, 'a').close()
                self.user_dictionary = enchant.PyPWL(self.user_dict_path)
            
            return True # Erfolg

        except enchant.errors.DictNotFoundError:
            print(f"Fehler: Wörterbuch für '{self.language_code}' nicht gefunden.")
            self.dictionary = None
            self.user_dictionary = None
            return False # Fehler

    def check(self, word):
        """Prüft, ob ein Wort korrekt ist."""
        if not self.dictionary:
            return True
        # Prüfe gegen Hauptwörterbuch und Benutzerwörterbuch
        return self.dictionary.check(word) or (self.user_dictionary and self.user_dictionary.check(word))

    def suggest(self, word):
        """Gibt eine Liste von Korrekturvorschlägen zurück."""
        if not self.dictionary:
            return []
        return self.dictionary.suggest(word)

    def add_to_user_dictionary(self, word):
        """Fügt ein Wort zum persönlichen Wörterbuch hinzu und speichert es."""
        if self.user_dictionary is not None:
            self.user_dictionary.add(word)

    def add_words_to_user_dictionary(self, words_to_add):
        """Adds a list of words to the user dictionary efficiently."""
        if self.user_dictionary is not None and words_to_add:
            for word in words_to_add:
                self.user_dictionary.add(word)

    def get_user_words(self):
        """Gibt eine Liste der Wörter im Benutzerwörterbuch zurück."""
        if not self.user_dict_path or not os.path.exists(self.user_dict_path):
            return []
        try:
            with open(self.user_dict_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []

    def remove_from_user_dictionary(self, word):
        """Entfernt ein Wort aus dem persönlichen Wörterbuch."""
        if self.user_dictionary is not None:
            try:
                self.user_dictionary.remove(word)
            except Exception:
                pass
            
            words = self.get_user_words()
            if word in words:
                words = [w for w in words if w != word]
                try:
                    with open(self.user_dict_path, 'w', encoding='utf-8') as f:
                        for w in words:
                            f.write(f"{w}\n")
                except Exception as e:
                    print(f"Fehler beim Speichern des Wörterbuchs: {e}")

    def clear_user_dictionary(self):
        """Clears all words from the user dictionary."""
        if self.user_dict_path and os.path.exists(self.user_dict_path):
            try:
                # Clear the file on disk
                with open(self.user_dict_path, 'w', encoding='utf-8') as f:
                    f.truncate(0)
                # Re-initialize the in-memory dictionary from the now-empty file
                self.user_dictionary = enchant.PyPWL(self.user_dict_path)
                return True
            except Exception as e:
                print(f"Error clearing user dictionary: {e}")
                return False
        return False
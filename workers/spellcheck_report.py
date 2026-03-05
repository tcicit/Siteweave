import os
import re
import enchant
from core.i18n import _

name = _("Spellcheck Report")
description = _("Checks the current file for spelling errors and lists them.")
category = "project"
hidden = False

def run(context):
    project_root = context.get("project_root", ".")
    current_file_path = context.get("current_file_path")
    editor_content = context.get("editor_content")
    config = context.get("config", {})

    if not current_file_path:
        return _("No file is currently open.")
    
    if not editor_content:
        return _("File is empty.")

    # Sprache ermitteln (aus Projektkonfiguration)
    lang_code = config.get('language', 'en')
    spellcheck_lang = config.get('spellcheck_language')
    
    # Mapping für pyenchant (ähnlich wie im MainWindow)
    lang_map = {
        'de': 'de_DE',
        'en': 'en_US',
        'fr': 'fr_FR',
        'es': 'es_ES'
    }
    
    dict_lang = spellcheck_lang
    if not dict_lang:
        dict_lang = lang_map.get(lang_code, 'en_US')

    user_dict_path = os.path.join(project_root, ".user_dictionary.txt")

    try:
        # Wörterbuch laden
        try:
            dictionary = enchant.Dict(dict_lang)
        except enchant.errors.DictNotFoundError:
             return _("Dictionary for language '{lang}' not found. Please install it (e.g. hunspell-{lang}).").format(lang=dict_lang)
        
        # Benutzerwörterbuch manuell laden
        user_words = set()
        if os.path.exists(user_dict_path):
            try:
                with open(user_dict_path, 'r', encoding='utf-8') as f:
                    user_words = {line.strip() for line in f if line.strip()}
            except Exception:
                pass

        # Regex für Wörter (Unicode-fähig)
        word_pattern = re.compile(r"[\w']+", re.UNICODE)
        
        errors = []
        lines = editor_content.splitlines()
        
        in_code_block = False
        in_frontmatter = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Frontmatter überspringen
            if i == 0 and stripped == "---":
                in_frontmatter = True
                continue
            if in_frontmatter:
                if stripped == "---":
                    in_frontmatter = False
                continue 
            
            # Code-Blöcke überspringen (```)
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue

            # Inline Code entfernen (`...`)
            line_clean = re.sub(r'`[^`]+`', '', line)
            
            # URLs grob entfernen, um Fehlalarme zu vermeiden
            line_clean = re.sub(r'\(http[^)]+\)', '', line_clean)

            for match in word_pattern.finditer(line_clean):
                word = match.group(0)
                
                # Ignoriere Zahlen, Pfade, oder Wörter mit Unterstrichen
                if word.isnumeric() or '/' in word or '\\' in word or '_' in word:
                    continue
                
                # Prüfen: Ist es im Hauptwörterbuch oder im Benutzerwörterbuch?
                if not dictionary.check(word) and word not in user_words:
                    errors.append({
                        'file_path': current_file_path,
                        'line': i + 1,
                        'display_text': f"Line {i+1}: {word}"
                    })

        if not errors:
            return _("No spelling errors found.")
            
        return errors

    except Exception as e:
        return _("Error during spell check: {e}").format(e=e)
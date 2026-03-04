import re

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import HtmlFormatter
except ImportError:
    highlight = None

def handle(content, args, context, env):
    """
    Plugin Name: Code

    Description: Generates code blocks with Pygments highlighting.

    Syntax: [[code lang="python"]]Content...[[/code]]

    Parameters:
      - lang: The language of the code (e.g. "python", "javascript").

    Examples:
      [[code lang="python"]]
         print("Hallo Welt!")
      [[/code]]
        Generates a code block with Pygments highlighting for "python".
        
    Result:
        <div class="codehilite"><pre><code>print("Hallo Welt!")</code></pre></div>
    """
    if not content:
        return ""
    
    # Entferne führende/nachfolgende Leerzeichen des Blocks, aber behalte Einrückung bei
    content = content.strip()
    
    if not highlight:
        # Fallback, falls Pygments nicht geladen werden konnte
        return f'<div class="codehilite"><pre>{content}</pre></div>'
    
    lang = args.get('lang')
    try:
        if lang:
            lexer = get_lexer_by_name(lang)
        else:
            lexer = guess_lexer(content)
    except Exception:
        # Fallback auf Text, wenn Sprache unbekannt
        from pygments.lexers.special import TextLexer
        lexer = TextLexer()
        
    # cssclass='codehilite' sorgt dafür, dass das CSS des Themes auch hier greift
    formatter = HtmlFormatter(cssclass='codehilite', wrapcode=True)
    
    return highlight(content, lexer, formatter)

def add_copy_buttons(html_content):
    """
    Fügt einen 'Kopieren'-Button zu Code-Blöcken (class="codehilite") hinzu.
    Diese Funktion wird vom Site-Renderer aufgerufen, um auch normale Markdown-Codeblöcke
    zu erweitern.
    """
    if 'class="codehilite"' not in html_content:
        return html_content

    # Button mit Inline-Styles und Inline-JS für maximale Portabilität
    button_html = (
        '<button class="copy-code-btn" style="'
        'position: absolute; top: 0.5em; right: 0.5em; '
        'background: rgba(100, 100, 100, 0.5); color: #fff; border: none; '
        'padding: 0.2em 0.5em; border-radius: 3px; cursor: pointer; font-size: 0.8em; '
        'z-index: 10; transition: background 0.2s;" '
        'onmouseover="this.style.background=\'rgba(100, 100, 100, 0.8)\'" '
        'onmouseout="this.style.background=\'rgba(100, 100, 100, 0.5)\'" '
        'onclick="'
        'const pre = this.parentElement.querySelector(\'pre\'); '
        'const code = pre.innerText; '
        'navigator.clipboard.writeText(code).then(() => { '
        'this.textContent = \'Kopiert!\'; '
        'setTimeout(() => { this.textContent = \'Kopieren\'; }, 2000); '
        '}).catch(err => console.error(\'Fehler beim Kopieren:\', err));'
        '">Kopieren</button>'
    )

    def replacer(match):
        tag = match.group(0)
        if 'style="' in tag:
            tag = tag.replace('style="', 'style="position: relative; ')
        else:
            tag = tag.replace('>', ' style="position: relative;">')
        return f'{tag}{button_html}'

    return re.sub(r'<div[^>]*class="[^"]*\bcodehilite\b[^"]*"[^>]*>', replacer, html_content)
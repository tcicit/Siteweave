import re

def is_valid_color(color_string):
    """
    Eine einfache Überprüfung auf gültige Farbnamen, Hex-Codes oder rgb/rgba-Funktionen.
    Dies ist eine grundlegende Sicherheitsmaßnahme, um CSS-Injection zu erschweren.
    """
    if not isinstance(color_string, str):
        return False
    # Erlaubt einfache Farbnamen (z.B. "red"), Hex-Codes (#fff, #ffffff), rgb und rgba.
    pattern = re.compile(r'^(#[0-9a-fA-F]{3,8}|[a-zA-Z]+|rgb\s*\([^)]+\)|rgba\s*\([^)]+\))$')
    return bool(pattern.match(color_string))

def handle(content, args, context, env):
    """
    Plugin Name: Color

    Description: Highlights the enclosed text with the specified text and background colors.

    Syntax: [[color text="red" bg="#f0f0f0"]]Text[[/color]]

    Parameters:
      - text: Text color (e.g. "red", "#ff0000", "rgb(255,0,0)").
      - bg: Background color (e.g. "#f0f0f0", "lightblue", "rgba(255,255,255,0.5)").

    Examples:
      [[color text="blue" bg="#e0e0ff"]]Blue text on light blue background.[[/color]]
        Highlights the text with blue font color and light blue background.
      [[color text="#ffffff" bg="black"]]White text on black background.[[/color]]
        Highlights the text with white font color and black background.
        
    Result:
        <span style="color: blue; background-color: #e0e0ff;">Blue text on light blue background.</span>
    """
    if not content:
        return ""

    text_color = args.get('text')
    bg_color = args.get('bg')

    styles = []
    if text_color and is_valid_color(text_color):
        styles.append(f"color: {text_color};")
    
    if bg_color and is_valid_color(bg_color):
        styles.append(f"background-color: {bg_color};")

    style_attr = " ".join(styles)
    return f'<span style="{style_attr}">{content}</span>'
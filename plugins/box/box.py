# plugins/box.py


try:
    import markdown
except ImportError:
    print("Markdown-Paket nicht gefunden. Bitte installieren: pip install markdown")
    markdown = None

def handle(content, args, context, env):
    """
    Plugin Name: Box
    Description: Creates a box with an optional title and background color.
    Syntax: [[box title="Title" bgcolor="#f0f0f0"]]Content...[[/box]]
    Parameters:
      - title: Optional title of the box.
      - bgcolor: Optional background color of the box (e.g. "#f0f0f" or "lightblue").
    Examples:
      [[box title="Important Information" bgcolor="#FF0000"]]
      This is important information in a red box.
      [[/box]]
        Creates a box with the title "Important Information" and a red background.
      [[box bgcolor="lightgreen"]]
      This is a box with a green background without a title.
      [[/box]]
        Creates a box with a green background without a title.
    Result:
        HTML code for the box with the specified content and styles.
    """
    if not markdown:
        return '<p style="color: red;">Fehler: Markdown-Bibliothek ist nicht installiert.</p>'

    title = args.get('title')
    bgcolor = args.get('bgcolor')
    
    style_attr = f'style="background-color: {bgcolor};"' if bgcolor else ''
    title_html = f'<h3 class="plugin-box-title">{title}</h3>' if title else ''
    
    html_content = markdown.markdown(content.strip() if content else '', extensions=['tables', 'fenced_code', 'md_in_html', 'attr_list'])
    
    return f'''<div class="plugin-box" {style_attr}>{title_html}<div class="plugin-box-content">{html_content}</div></div>'''
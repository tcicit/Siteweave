def handle(content, args, context, env):
    """
    Plugin Name: TOC
    
    Description: Inserts the [TOC] marker for the Python-Markdown 'toc' extension.
    
    Extended Functionality:
    Can automatically hide the table of contents based on the number of headers
    (for short articles).

    Syntax: [[toc title="Inhalt" depth="3" min_headers="4"]]
    
    Parameters:
    - title (str): Title of the table of contents.
    - depth (int): Maximum depth of headers. Default: 6.
    - min_headers (int): Minimum number of headers required to show the TOC.

    Examples:
    - [[toc title="Inhalt" depth="3"]]
      Inserts a table of contents with the title "Inhalt" and includes headers up to level 3.
    - [[toc min_headers="5"]]
      Inserts a table of contents only if there are at least 5 headers in the article.  
     
    
    Result:
    The [TOC] marker or an empty string.
    """
    
    min_headers = 0
    if 'min_headers' in args:
        try:
            min_headers = int(args['min_headers'])
        except ValueError:
            pass

    # Wenn min_headers gesetzt ist, prüfen wir die Länge des Artikels
    if min_headers > 0:
        current_path = context.get('current_output_path')
        all_pages = context.get('all_pages', [])
        
        # Finde den Inhalt der aktuellen Seite
        page_content = next((p.get('content', '') for p in all_pages if p.get('path') == current_path), "")
        
        if page_content:
            # Zähle die Markdown-Überschriften (Zeilen, die mit # beginnen)
            header_count = sum(1 for line in page_content.splitlines() if line.lstrip().startswith('#'))
            
            if header_count < min_headers:
                # Zu wenige Überschriften -> Kein Inhaltsverzeichnis
                return ""

    context['toc_args'] = args
    return "[TOC]"
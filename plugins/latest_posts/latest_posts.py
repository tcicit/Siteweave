# plugins/latest_posts.py
import markdown
import re
from datetime import datetime



def _truncate_words(text, num_words):
    """Trims text to a specified number of words."""
    # Remove HTML tags for a clean word count
    clean_text = re.sub('<[^<]+?>', '', text)
    words = clean_text.split()
    if len(words) > num_words:
        return ' '.join(words[:num_words]) + '...'
    return ' '.join(words)

def handle(content, args, context, env):
    """
    Pluginname: Latest Posts
    Beschreibung: Zeigt eine Liste der neuesten Blog-Beiträge an, mit verschiedenen Filter- und Anzeigeoptionen.
    Syntax: [[latest_posts count="5" sort="desc" tags="tag1,tag2" tag_mode="all" show_excerpt="true" excerpt_length="30" show_image="true"]]
    Parameter:
      - count: Anzahl der anzuzeigenden Beiträge. Standard: 5
      - sort: Sortierreihenfolge der Beiträge. Mögliche Werte: "asc" oder "desc". Standard: "desc"
      - tags: Kommagetrennte Liste von Tags zum Filtern der Beiträge. Standard: keine Filterung
      - tag_mode: Modus für die Tag-Filterung. Mögliche Werte: "all" (alle Tags müssen übereinstimmen) oder "any" (mindestens ein Tag muss übereinstimmen). Standard: "all"
      - show_excerpt: Ob ein Auszug des Beitragsinhalts angezeigt werden soll. Mögliche Werte: "true" oder "false". Standard: "false"
      - excerpt_length: Anzahl der Wörter im Auszug, falls show_excerpt auf "true" gesetzt ist. Standard: 30
      - show_image: Ob das Beitragsbild angezeigt werden soll, falls vorhanden. Mögliche Werte: "true" oder "false". Standard: "false"
    Beispiele:
      [[latest_posts count="3" sort="desc" tags="python,programmierung" tag_mode="any" show_excerpt="true" excerpt_length="20" show_image="true"]]
        Zeigt die 3 neuesten Beiträge an, die entweder das Tag "python" oder "programmierung" haben, mit einem 20-Wörter-Auszug und dem Beitragsbild.
      [[latest_posts count="5" sort="asc" show_excerpt="false" show_image="false"]]
        Zeigt die 5 ältesten Beiträge ohne Auszug und ohne Bild an.
    Ergebnis:
        HTML-Liste der neuesten Beiträge entsprechend den angegebenen Parametern.   
        

    """
    all_pages = context.get('all_pages', [])
    relative_prefix = context.get('relative_prefix', './')

    # --- Parameter auslesen ---
    try:
        count = int(args.get('count', 5))
    except ValueError:
        count = 5
    
    sort_order = args.get('sort', 'desc').lower()
    tags_str = args.get('tags')
    tag_mode = args.get('tag_mode', 'all').lower()
    show_excerpt = args.get('show_excerpt', 'false').lower() == 'true'
    show_image = args.get('show_image', 'false').lower() == 'true'
    try:
        excerpt_length = int(args.get('excerpt_length', 30))
    except ValueError:
        excerpt_length = 30

    # --- Seiten filtern ---
    filtered_pages = all_pages
    if tags_str:
        required_tags = {tag.strip().lower() for tag in tags_str.split(',')}
        if tag_mode == 'any':
            # OR-Modus: Seite muss mindestens einen der Tags haben
            filtered_pages = [
                p for p in all_pages 
                if required_tags.intersection({t.lower() for t in p['metadata'].get('tags', [])})
            ]
        else: # 'all' Modus
            # AND-Modus: Seite muss alle angegebenen Tags haben
            filtered_pages = [
                p for p in all_pages
                if required_tags.issubset({t.lower() for t in p['metadata'].get('tags', [])})
            ]

    # --- Seiten sortieren ---
    # Die `all_pages` Liste aus dem Kontext ist bereits absteigend sortiert.
    final_pages = filtered_pages
    if sort_order == 'asc':
        final_pages.reverse()

    # --- HTML generieren ---
    if not final_pages:
        return "<p>Keine Beiträge gefunden, die den Kriterien entsprechen.</p>"

    html_parts = ['<ul class="latest-posts-list">']
    
    for page in final_pages[:count]:
        metadata = page.get('metadata', {})
        date_str = metadata.get('date')
        date_obj = None
        if date_str:
            try:
                date_obj = datetime.fromisoformat(str(date_str))
            except (ValueError, TypeError):
                date_obj = None

        li_classes = []
        if show_excerpt:
            li_classes.append("with-excerpt")
        if show_image and page.get('featured_image'):
             li_classes.append("with-image")

        class_attr = f' class="{" ".join(li_classes)}"' if li_classes else ''
        html_parts.append(f'<li{class_attr}>')

        # Bild hinzufügen, falls gewünscht und vorhanden
        if show_image and page.get('featured_image'):
            image_url = relative_prefix + page['featured_image']
            html_parts.append(
                f'<div class="post-image">'
                f'<a href="{relative_prefix}{page["path"].lstrip("/")}">'
                f'<img src="{image_url}" alt="Vorschaubild für {page["title"]}" loading="lazy">'
                f'</a>'
                f'</div>'
            )
        
        # Container für den Textinhalt
        html_parts.append('<div class="post-content">')
        
        # Header mit Titel und Datum
        html_parts.append('<div class="post-header">')
        html_parts.append(f'<a href="{relative_prefix}{page["path"].lstrip("/")}">{page["title"]}</a>')
        if date_obj:
            html_parts.append(f'<span class="post-date">{date_obj.strftime("%d.%m.%Y")}</span>')
        html_parts.append('</div>') # Ende post-header

        # Auszug hinzufügen, falls gewünscht
        if show_excerpt:
            # Konvertiere den Markdown-Inhalt zu HTML, um ihn dann zu kürzen
            html_content = markdown.markdown(page['content'])
            excerpt = _truncate_words(html_content, excerpt_length)
            html_parts.append(f'<p class="post-excerpt">{excerpt}</p>')
        
        html_parts.append('</div>') # Ende post-content
        html_parts.append('</li>')

    html_parts.append('</ul>')
    return "\n".join(html_parts)

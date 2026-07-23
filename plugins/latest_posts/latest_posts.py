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
Plugin Name: Latest Posts
    Description: Displays a list of the latest blog posts, with various filtering and display options.
    Syntax: [[latest_posts count="5" sort="desc" tags="tag1,tag2" tag_mode="all" show_excerpt="true" excerpt_length="30" show_image="true"]]
    Parameters:
      - count: Number of posts to display. Default: 5
      - sort: Sort order of the posts. Possible values: “asc” or ‘desc’. Default: “desc”
      - tags: Comma-separated list of tags to filter the posts. Default: no filtering
      - tag_mode: Mode for tag filtering. Possible values: “all” (all tags must match) or “any” (at least one tag must match). Default: ‘all’
      - show_excerpt: Whether to display an excerpt of the post content. Possible values: “true” or “false”. Default: “false”
      - excerpt_length: Number of words in the excerpt, if show_excerpt is set to “true”. Default: 30
      - show_image: Whether the post image should be displayed, if available. Possible values: “true” or “false”. Default: “false”
Examples:
      [[latest_posts count="3" sort="desc" tags="python,programming" tag_mode="any" show_excerpt="true" excerpt_length="20" show_image="true"]]
        Displays the 3 most recent posts that have either the “python” or “programming” tag, with a 20-word excerpt and the post image.
      [[latest_posts count="5" sort="asc" show_excerpt="false" show_image="false"]]
        Displays the 5 oldest posts without an excerpt and without an image.
    Result:
        HTML list of the latest posts according to the specified parameters.
        

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

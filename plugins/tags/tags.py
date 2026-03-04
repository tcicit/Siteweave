import os
import random
from collections import defaultdict
from jinja2 import TemplateNotFound

# --- Helper Functions ---

def slugify(value):
    """
    Erstellt einen URL-freundlichen Slug aus einem String.
    Beispiel: "Züri Gschnätzlets" -> "zuri-gschnatzlets"
    """
    import re
    import unicodedata
    
    # Sicherstellen, dass wir einen String haben, um Abstürze bei Zahlen-Tags zu vermeiden
    value = str(value)
    
    # Unicode-Normalisierung (z.B. Umlaute auflösen)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    
    # Alles ausser Buchstaben, Zahlen und Bindestrichen entfernen
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    
    # Leerzeichen und wiederholte Bindestriche durch einen einzelnen Bindestrich ersetzen
    return re.sub(r'[-\s]+', '-', value)

def _get_normalized_tags(tags_collection):
    """
    Verarbeitet die rohe Tag-Sammlung und bereinigt sie.
    
    Probleme, die hier gelöst werden:
    1. Case-Sensitivity: "Reisen" und "reisen" werden zusammengeführt.
    2. Duplikate: Beiträge, die durch Zusammenführung doppelt wären, werden bereinigt.
    3. Sortierung: Tags werden alphabetisch sortiert.
    
    Rückgabe:
    Eine Liste von Dictionaries, sortiert nach Tag-Namen:
    [
        {
            'name': 'Reisen',       # Der "schönste" Anzeigename
            'slug': 'reisen',       # Der URL-Slug
            'count': 5,             # Anzahl der Beiträge
            'posts': [ ... ]        # Liste der Beiträge (dicts aus site_renderer)
        },
        ...
    ]
    """
    if not tags_collection:
        return []

    # 1. Gruppieren nach Slug (führt "Python" und "python" zusammen)
    grouped_tags = defaultdict(lambda: {'display_name': None, 'posts': []})
    
    for tag_raw, posts in tags_collection.items():
        slug = slugify(tag_raw)
        if not slug:
            continue
            
        group = grouped_tags[slug]
        group['posts'].extend(posts)
        
        # Versuche, den besten Anzeigenamen zu finden.
        # Wir bevorzugen Namen, die mit Grossbuchstaben beginnen.
        if group['display_name'] is None:
            group['display_name'] = tag_raw
        elif tag_raw[0].isupper() and (not group['display_name'] or not group['display_name'][0].isupper()):
            group['display_name'] = tag_raw

    # 2. Ergebnisliste erstellen und Posts deduplizieren
    normalized_list = []
    for slug, data in grouped_tags.items():
        # Deduplizierung der Posts basierend auf dem Pfad
        unique_posts_dict = {p['path']: p for p in data['posts']}
        unique_posts = list(unique_posts_dict.values())
        
        # Sortiere die Posts nach Datum (neueste zuerst)
        unique_posts.sort(key=lambda p: p.get('date', ''), reverse=True)

        normalized_list.append({
            'name': data['display_name'],
            'slug': slug,
            'count': len(unique_posts),
            'posts': unique_posts
        })

    # 3. Sortiere die Tags alphabetisch nach Namen
    normalized_list.sort(key=lambda x: x['name'].lower())
    
    return normalized_list

# --- Plugin Hooks ---
def handle(content, args, context, env):
    """
    Plugin Name: Tags

    Description: Generates a tag cloud or a list. 

    Syntax: 
        [[tags type="list"]] 
        [[tags type="cloud"]]

    Parameters:
      - type: 'list' (default) or 'cloud'
      - exclude: Comma-separated list of tags to exclude (e.g. "draft,entwurf")
      - min_count: Only show tags with at least this number of posts (e.g. min_count=3)
      - limit: Only show the top N tags (e.g. limit=10)
      - random: "true" for random order (e.g. random=true)
      - sort_by: "count" for sorting by count (e.g. sort_by=count)
      - group: "true" for grouping by initial letter (e.g. group=true)
      - cols: Number of columns for the list view (e.g. cols=3)
      - show_count: "true" to show the number of posts next to the tag (e.g. show_count=true)
      - color: "random" for random colors in the tag cloud (e.g. color=random)       

    Examples: 
      [[tags type="cloud" min_count=2 limit=20 random=true color=random]]
      [[tags type="list" exclude="draft,entwurf" sort_by="count" show_count=true cols=2]]

    Result:
      - For the cloud: A visual tag cloud where font size and optionally color reflect the number of posts.
      - For the list: An alphabetically sorted list of tags, optionally with columns and the number of posts next to each tag.     

    """
    tags_collection = context.get('tags_collection', {})
    if not tags_collection:
        return ""

    # Daten normalisieren
    tag_data = _get_normalized_tags(tags_collection)

    # --- Filterung und Limitierung ---
    # Exclude Filter
    exclude_str = args.get('exclude', '')
    if exclude_str:
        excluded_slugs = [slugify(t) for t in exclude_str.split(',') if t.strip()]
        tag_data = [t for t in tag_data if t['slug'] not in excluded_slugs]

    # 1. Min Count Filter
    min_count = int(args.get('min_count', 0))
    if min_count > 0:
        tag_data = [t for t in tag_data if t['count'] >= min_count]

    # 2. Limit (Top N)
    limit = int(args.get('limit', 0))
    if limit > 0 and len(tag_data) > limit:
        # Sortiere nach Anzahl absteigend für das Limit
        tag_data.sort(key=lambda x: x['count'], reverse=True)
        tag_data = tag_data[:limit]

    # Sortierung: Zufällig, nach Anzahl oder Alphabetisch
    if args.get('random', 'false').lower() == 'true':
        random.shuffle(tag_data)
    elif args.get('sort_by', '').lower() == 'count':
        tag_data.sort(key=lambda x: (-x['count'], x['name'].lower()))
    else:
        tag_data.sort(key=lambda x: x['name'].lower())

    tag_type = args.get('type', 'list').lower()
    group = args.get('group', 'false').lower() == 'true'
    
    # --- Template Wahl & Cloud Berechnung ---
    template_name = 'tag_list.html'
    if tag_type == 'cloud':
        template_name = 'tag_cloud.html'
        
        # Gewichtung für Tag Cloud berechnen
        if tag_data:
            counts = [t['count'] for t in tag_data]
            min_c = min(counts)
            max_c = max(counts)
            spread = max_c - min_c
            
            for tag in tag_data:
                # Schriftgröße zwischen 0.8em und 2.5em
                if spread > 0:
                    weight = (tag['count'] - min_c) / spread
                    size = 0.8 + (weight * 1.7)
                    opacity = 0.7 + (weight * 0.3)
                else:
                    size = 1.0
                    opacity = 1.0
                
                tag['size'] = f"{size:.2f}em"
                tag['opacity'] = f"{opacity:.2f}"
                
                if args.get('color', '').lower() == 'random':
                    r = random.randint(40, 200)
                    g = random.randint(40, 200)
                    b = random.randint(40, 200)
                    tag['color'] = f"rgb({r},{g},{b})"
    elif group:
        template_name = 'tag_list_grouped.html'
        # Gruppieren nach Anfangsbuchstaben
        grouped_data = defaultdict(list)
        for tag in tag_data:
            letter = tag['name'][0].upper()
            if not letter.isalpha():
                letter = '#'
            grouped_data[letter].append(tag)
        tag_data = dict(sorted(grouped_data.items()))
    
    # Listen-Optionen
    cols = int(args.get('cols', 1))
    show_count = args.get('show_count', 'true').lower() == 'true'

    # Pfad-Korrektur für Links
    relative_prefix = context.get('relative_prefix', './')
    # Wenn wir im Root sind (./), ist der Pfad zu Tags "tags".
    # Wenn wir tiefer sind (../../), ist er "../../tags".
    # Wichtig: Kein os.path.join, um Backslashes unter Windows zu vermeiden.
    if relative_prefix == './':
        tags_base_url = 'tags'
    else:
        tags_base_url = f"{relative_prefix}tags"

    try:
        template = env.get_template(template_name)
        return template.render(
            tags=tag_data,
            relative_path_to_tags=tags_base_url,
            cols=cols,
            show_count=show_count
        )
    except TemplateNotFound:
        # Fallback-Darstellung, falls Template fehlt
        if tag_type == 'cloud':
            html = '<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; align-items: baseline;">'
            for tag in tag_data:
                size = tag.get('size', '1em')
                opacity = tag.get('opacity', '1.0')
                color_style = f"color: {tag['color']};" if 'color' in tag else "color: inherit;"
                html += f'<a href="{tags_base_url}/{tag["slug"]}.html" style="font-size: {size}; opacity: {opacity}; text-decoration: none; {color_style}">{tag["name"]}</a> '
            html += '</div>'
            return html
        elif group:
            # Gruppierter Fallback
            html = '<div class="tag-groups">'
            for letter, group_tags in tag_data.items():
                html += f'<div class="tag-group"><h3>{letter}</h3>'
                style = f"display: grid; grid-template-columns: repeat({cols}, 1fr); gap: 10px;" if cols > 1 else ""
                html += f'<ul style="{style} list-style: none; padding: 0;">'
                for tag in group_tags:
                    count_str = f" <small>({tag['count']})</small>" if show_count else ""
                    html += f'<li><a href="{tags_base_url}/{tag["slug"]}.html">{tag["name"]}</a>{count_str}</li>'
                html += '</ul></div>'
            html += '</div>'
            return html
        else:
            # Listen-Fallback mit Spalten
            style = f"display: grid; grid-template-columns: repeat({cols}, 1fr); gap: 10px;" if cols > 1 else ""
            html = f'<ul style="{style} list-style: none; padding: 0;">'
            for tag in tag_data:
                count_str = f" <small>({tag['count']})</small>" if show_count else ""
                html += f'<li><a href="{tags_base_url}/{tag["slug"]}.html">{tag["name"]}</a>{count_str}</li>'
            html += '</ul>'
            return html
    except Exception as e:
        print(f"FEHLER im Tags-Plugin (handle): {e}")
        return f"<!-- Fehler im Tags-Plugin: {e} -->"

def generate_pages(tags_collection, env, output_dir, site_structure, all_site_pages):
    """
    Generiert die statischen HTML-Seiten für jeden Tag und den Index.
    """
    if not tags_collection:
        return

    # Daten normalisieren (gleiche Logik wie im Shortcode!)
    tag_data = _get_normalized_tags(tags_collection)
    
    tags_output_dir = os.path.join(output_dir, 'tags')
    os.makedirs(tags_output_dir, exist_ok=True)

    # 1. Einzelne Tag-Seiten generieren
    try:
        # Lade Templates
        tag_page_template = env.get_template('tag_page.html')
        try:
            # Versuche das Standard-Layout zu laden, Fallback auf base.html
            base_template = env.get_template('layout_full-width.html')
        except TemplateNotFound:
            base_template = env.get_template('base.html')
        
        for tag_entry in tag_data:
            slug = tag_entry['slug']
            output_path = os.path.join(tags_output_dir, f"{slug}.html")
            
            context = {
                'page_title': f"Tag: {tag_entry['name']}",
                'tag_name': tag_entry['name'],
                'pages': tag_entry['posts'], # Die bereits sortierten Posts
                'relative_prefix': '../',    # Tags sind immer in /tags/, also eine Ebene tief
                'site_structure': site_structure,
                'current_output_path': f'/tags/{slug}.html',
                'tags_collection': tags_collection
            }
            
            # 1. Inhalt rendern (Fragment)
            content_html = tag_page_template.render(context)
            context['content'] = content_html
            
            # 2. Volle Seite mit Base-Template rendern
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(base_template.render(context))
                
            # Zur Sitemap hinzufügen
            all_site_pages.append({
                'path': f'/tags/{slug}.html',
                'source_path': None
            })
            
        print(f"    - Plugin 'tags': {len(tag_data)} Tag-Seiten erstellt.")
        
    except TemplateNotFound:
        print("    - WARNUNG: 'tag_page.html' Template nicht gefunden.")
    except Exception as e:
        print(f"    - FEHLER beim Erstellen der Tag-Seiten: {e}")

    # 2. Tag-Index-Seite generieren (Übersicht)
    try:
        tags_index_template = env.get_template('tags_index.html')
        try:
            base_template = env.get_template('layout_full-width.html')
        except TemplateNotFound:
            base_template = env.get_template('base.html')
        
        context = {
            'page_title': 'Alle Tags',
            'tags': tag_data,
            'relative_prefix': '../',
            'site_structure': site_structure,
            'current_output_path': '/tags/index.html',
            'tags_collection': tags_collection
        }
        
        # 1. Inhalt rendern
        content_html = tags_index_template.render(context)
        context['content'] = content_html
        
        # 2. Volle Seite rendern
        output_path = os.path.join(tags_output_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(base_template.render(context))
            
        all_site_pages.append({
            'path': '/tags/index.html',
            'source_path': None
        })
        print("    - Plugin 'tags': Index-Seite erstellt.")
        
    except TemplateNotFound:
        print("    - INFO: 'tags_index.html' Template nicht gefunden.")
    except Exception as e:
        print(f"    - FEHLER beim Erstellen des Tag-Index: {e}")

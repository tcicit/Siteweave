import os
import csv
import html

def handle(content, args, context, env):
    """
    Plugin Name: CSV Table
    Description: Reads a CSV file and renders it as an HTML table.
    Syntax: [[csv_table src="daten.csv" delimiter=";" header="true" class="my-table"]]
    Parameters:
      - src: Path to the CSV file (relative to the markdown file).
      - delimiter: Delimiter character (Default: ","). Use "\\t" for tab.
      - header: "true" (Default) or "false". Whether the first row contains headers.
      - class: CSS class for the `<table>` element (Default: "csv-table").
      - caption: Optional title for the table.
    Examples:
      [[csv_table src="data.csv" delimiter=";" header="true" class="my-table" caption="My Data"]]
        Reads "data.csv" using ";" as a delimiter, treats the first row as headers, applies the CSS class "my-table", and adds a caption "My Data".
    Result:
        HTML code for the table displaying the CSV data.
    """
    src = args.get('src')
    if not src:
        return '<p style="color: red;">[CSV Plugin: "src" Attribut fehlt]</p>'

    delimiter = args.get('delimiter', ',')
    if delimiter == '\\t':
        delimiter = '\t'
        
    has_header = args.get('header', 'true').lower() != 'false'
    css_class = args.get('class', 'csv-table')
    caption = args.get('caption')

    # Pfad auflösen (relativ zur aktuellen Seite)
    current_page_path = context.get('current_page_path')
    if not current_page_path:
        return '<p style="color: red;">[CSV Plugin: Kontext fehlt]</p>'

    base_dir = os.path.dirname(current_page_path)
    full_path = os.path.normpath(os.path.join(base_dir, src))

    if not os.path.exists(full_path):
        return f'<p style="color: red;">[CSV Plugin: Datei "{src}" nicht gefunden]</p>'

    try:
        with open(full_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
    except Exception as e:
        return f'<p style="color: red;">[CSV Plugin: Fehler beim Lesen der Datei: {e}]</p>'

    if not rows:
        return '<p><em>[Leere CSV-Datei]</em></p>'

    # HTML zusammenbauen
    html_parts = [f'<div class="table-responsive"><table class="{css_class}">']
    
    if caption:
        html_parts.append(f'<caption>{html.escape(caption)}</caption>')

    if has_header:
        header_row = rows[0]
        rows = rows[1:]
        html_parts.append('<thead><tr>')
        for cell in header_row:
            html_parts.append(f'<th>{html.escape(cell)}</th>')
        html_parts.append('</tr></thead>')

    html_parts.append('<tbody>')
    for row in rows:
        html_parts.append('<tr>')
        for cell in row:
            html_parts.append(f'<td>{html.escape(cell)}</td>')
        html_parts.append('</tr>')
    html_parts.append('</tbody>')
    html_parts.append('</table></div>')

    return "".join(html_parts)

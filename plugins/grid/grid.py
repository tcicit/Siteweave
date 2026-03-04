# plugins/grid.py

def handle(content, args, context, env):
    """
    Plugin Name: Grid
    Description: Creates a grid layout with a configurable number of columns.
    Syntax: [[grid cols="3"]]Content...[[/grid]]
    Parameters:
      - cols: Number of columns in the grid. Default: "3".
    Examples:
      [[grid cols="4"]]
      Content for the first column.
      Content for the second column.
      Content for the third column.
      Content for the fourth column.
      [[/grid]]
        Creates a 4-column grid with the specified content.
    Result:
        <div class="plugin-grid" style="grid-template-columns: repeat(4, 1fr);">
            Content for the first column.
            ...
        </div>
    """
    cols = args.get('cols', '3')
    
    # Wir verwenden CSS Grid. Die Anzahl der Spalten wird via Inline-Style konfiguriert.
    style = f"grid-template-columns: repeat({cols}, 1fr);"
    processed_content = content.strip() if content else ''

    return f'<div class="plugin-grid" style="{style}">\n{processed_content}\n</div>'
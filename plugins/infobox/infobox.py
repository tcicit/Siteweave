import markdown

def handle(content, args, context, env):
    """
    Plugin Name: Infobox
    Description: Creates an infobox with different styles and an optional title.
    Syntax: [[infobox type="warning" title="Attention!"]]Content...[[/infobox]]
    Parameters:
      - type: The type of the infobox. Possible values: "info", "warning", "error", "success". Default: "info".
      - title: Optional title of the infobox.

    Examples:
      [[infobox type="warning" title="Attention!"]]
      This is a warning.
      [[/infobox]]
        Creates a yellow warning infobox with the title "Attention!".
      [[infobox type="success"]]
      This is a success message.
      [[/infobox]]
        Creates a green success infobox without a title.
        
    Result:
        <div class="infobox infobox-warning">
            <div class="infobox-title">Attention!</div>
            <div class="infobox-content">
        
                        <p>This is a warning.</p>
            </div>
        </div>  
          

    """
    box_type = args.get('type', 'info')
    title = args.get('title')
    
    inner_html = markdown.markdown(content.strip() if content else '', extensions=['tables'])
    title_html = f'<div class="infobox-title">{title}</div>' if title else ''

    return f'<div class="infobox infobox-{box_type}">{title_html}{inner_html}</div>'
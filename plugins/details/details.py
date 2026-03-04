import markdown

def handle(content, args, context, env):
    """
    Plugin Name: Details
    Description: Creates a collapsible content block (`<details>`).
    Syntax: [[details summary="Summary Title"]]Content...[[/details]]
    Parameters:
      - summary: The text displayed in the summary. Default: "Details".
      
    Examples:
      [[details summary="More Information"]]
      Here is more information that can be expanded.
      [[/details]]
        Creates a collapsible area with the summary "More Information".

    Result:
        HTML code for the `<details>` block with the specified content.
    """
    summary = args.get('summary', "Details")
    inner_html = markdown.markdown(content.strip() if content else '', extensions=['tables'])
    return f"<details><summary>{summary}</summary>{inner_html}</details>"
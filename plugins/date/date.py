# plugins/date.py
from datetime import datetime

def handle(content, args, context, env):
    """
    Plugin Name: Date
    Description: Returns the current date in the specified format.
    Syntax: [[date format="%d.%m.%Y"]]
    Parameters:
      - format: The format for the date. Default: "%d.%m.%Y".
    Examples:
      [[date format="%A, %d. %B %Y"]] 
        Returns the current date in the format "Monday, 24. December 2024".
      [[date]]
        Returns the current date in the default format "24.12.2024".  
    Result:
        24.12.2024


  

    """
    # Hole das Format aus den Argumenten, mit einem sinnvollen Standardwert.
    date_format = args.get('format', '%d.%m.%Y')
    
    now = datetime.now()
    
    try:
        # Formatiere das Datum und gib es zurück.
        return now.strftime(date_format)
    except Exception as e:
        # Fange mögliche Fehler ab, falls ein ungültiges Format übergeben wird.
        return f'<span style="color: red; font-family: monospace;">Fehler im Datumsformat: {e}</span>'

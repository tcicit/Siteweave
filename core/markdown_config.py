import logging
'''
Gibt die Standard-Markdown-Erweiterungen und deren Konfiguration zurück.
Diese Funktion ermöglicht es, die Markdown-Konfiguration zentral zu verwalten und in Zukunft über die config.yaml 
anpassbar zu machen, falls gewünscht. Aktuell werden die Standarderweiterungen und deren Konfiguration zurückgegeben, 
aber die Struktur erlaubt es, dies später einfach zu erweitern.

Beispiel für zukünftige Erweiterung: In der config.yaml könnte ein Abschnitt "markdown_extensions" hinzugefügt werden,
der es ermöglicht, zusätzliche Erweiterungen zu definieren oder die Standardkonfigurationen zu überschreiben. 
Die Funktion könnte dann diese Informationen einlesen und entsprechend zurückgeben.  

Beispiel config.yaml Erweiterung:
markdown_extensions:
  - toc
  - tables
markdown_extension_configs:
  codehilite:
    css_class: 'my-codehilite'
    linenums: true
    guess_lang: false
    use_pygments: false

https://python-markdown.github.io/extensions/

'''



logger = logging.getLogger("markdown_config")

DEFAULT_EXTENSIONS = ['tables', 'fenced_code', 'md_in_html', 'codehilite', 'attr_list']

DEFAULT_EXTENSION_CONFIGS = {
    'codehilite': {
        'css_class': 'codehilite',
        'guess_lang': True,
        'linenums': None,
        'use_pygments': True
    }
}

def get_markdown_config(project_config=None):
    """
    Gibt die Markdown-Erweiterungen und deren Konfiguration zurück.
    Ermöglicht zukünftige Overrides über die config.yaml.
    """
    extensions = DEFAULT_EXTENSIONS.copy()
    configs = DEFAULT_EXTENSION_CONFIGS.copy()

    if project_config:
        # Hier könnten in Zukunft projektspezifische Erweiterungen 
        # aus der config.yaml eingelesen und gemergt werden.
        pass
        

    return extensions, configs
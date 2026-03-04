"""
CLI wrapper for the Siteweave renderer.

Usage:
    python scripts/render.py [project_path]

Example:
    python scripts/render.py ~/my-website
"""

import os
import sys
import inspect
from core.renderer import SiteRenderer, run

# Dies ist ein CLI-Wrapper und sollte nicht mehr als Worker im Menü erscheinen.
# Die GUI verwendet stattdessen 'workers/renderer.py'.
# name = "Webseite generieren"
# category = "project"

def progress_handler(current, total, message=""):
    """Gibt den Fortschritt in einem Format aus, das die GUI parsen kann."""
    if total > 0:
        percent = int((current / total) * 100)
        # Format: PROGRESS:PROZENT:NACHRICHT
        print(f"PROGRESS:{percent}:{message}")
        sys.stdout.flush()

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.isfile(os.path.join(root, "config.yaml")):
        print(f"Fehler: Keine 'config.yaml' in '{os.path.abspath(root)}' gefunden.")
        print("Verwendung: python site_renderer.py [PROJEKT_PFAD]")
        sys.exit(1)

    try:
        renderer = SiteRenderer(root)
        
        # Prüfen, ob die render-Methode 'progress_callback' unterstützt
        sig = inspect.signature(renderer.render)
        if 'progress_callback' in sig.parameters:
            renderer.render(progress_callback=progress_handler)
        else:
            renderer.render()
    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)

import subprocess
import os
import sys

from core import I18N_DOMAIN

'''
Script for managing translations with Babel.
It performs the following steps:
1. Extract texts from code and templates into a .pot file.
2. Update .po files for different languages based on the .pot file.
3. Compile .po files into .mo files that can be used by the application.
The configuration for extraction (e.g., which files are scanned) is defined in 'babel.cfg'.
'''

# Configuration
PROJECT_NAME = I18N_DOMAIN
LOCALES_DIR = "locales"
POT_FILE = os.path.join(LOCALES_DIR, f"{PROJECT_NAME}.pot")
BABEL_CFG = "babel.cfg"

def run_command(command, allow_failure=False):
    """Executes a shell command and exits the script on error."""
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if not allow_failure:
            sys.exit(1)
    except FileNotFoundError:
        print("Error: 'pybabel' not found. Is Babel installed? (pip install Babel)")
        sys.exit(1)

def main():
    # Ensure the locales directory exists
    if not os.path.exists(LOCALES_DIR):
        os.makedirs(LOCALES_DIR)
        print(f"Directory '{LOCALES_DIR}' created.")

    # 1. Extract texts
    print("--- 1. Extract texts ---")
    if not os.path.exists(BABEL_CFG):
        print(f"Error: Configuration file '{BABEL_CFG}' missing.")
        sys.exit(1)

    # Command: pybabel extract -F babel.cfg -o locales/siteweave.pot .
    run_command(["pybabel", "extract", "-F", BABEL_CFG, "-o", POT_FILE, "."])

    # Check if any language catalogs (.po files) exist before trying to update/compile
    has_catalogs = False
    if os.path.isdir(LOCALES_DIR):
        for lang in os.listdir(LOCALES_DIR):
            lang_path = os.path.join(LOCALES_DIR, lang)
            if os.path.isdir(lang_path):
                po_file = os.path.join(lang_path, 'LC_MESSAGES', f'{PROJECT_NAME}.po')
                if os.path.isfile(po_file):
                    has_catalogs = True
                    break
    
    if not has_catalogs:
        print("\nNo language catalogs found. Skipping update and compile.")
        print(f"To add a new language (e.g., 'en'), run:\n  pybabel init -i {POT_FILE} -d {LOCALES_DIR} -l en -D {PROJECT_NAME}")
        sys.exit(0)

    # 2. Update catalogs
    print("\n--- 2. Update catalogs ---")
    # Command: pybabel update -i locales/siteweave.pot -d locales -D siteweave
    if os.path.exists(POT_FILE):
        run_command(["pybabel", "update", "-i", POT_FILE, "-d", LOCALES_DIR, "-D", PROJECT_NAME])

    # 3. Compile catalogs
    print("\n--- 3. Compile catalogs ---")
    # Command: pybabel compile -d locales -D siteweave
    run_command(["pybabel", "compile", "-d", LOCALES_DIR, "-D", PROJECT_NAME])

    print("\n--- Done! ---")

if __name__ == "__main__":
    main()
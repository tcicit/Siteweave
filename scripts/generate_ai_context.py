import os

"""
Dieses Skript generiert eine GEMINI.md Datei, die den gesamten relevanten 
Quellcode des Projekts für LLMs zusammenfasst.
"""

def generate_ai_context(root_dir, output_file):
    # Verzeichnisse und Dateien, die ignoriert werden sollen
    ignore_list = {
        '.git', 'venv', '__pycache__', '.pytest_cache', 
        'site_output', 'backup', '.vscode', 'assets'
    }
    # Relevante Dateiendungen
    valid_extensions = ('.py', '.md', '.yaml', '.yml', '.html', '.css', '.js')

    print(f"Generiere Kontext aus: {root_dir} -> {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write("# Projekt Kontext für Gemini\n\n")
        f_out.write("Dieses Dokument enthält den Quellcode und die Struktur des Projekts.\n\n")

        for root, dirs, files in os.walk(root_dir):
            # Ignoriere versteckte Ordner und die in der ignore_list
            dirs[:] = [d for d in dirs if d not in ignore_list and not d.startswith('.')]
            
            for file in files:
                if file.endswith(valid_extensions) and file != output_file:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    f_out.write(f"\n## FILE: {rel_path}\n")
                    f_out.write("```" + (file.split('.')[-1] if '.' in file else "") + "\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f_in:
                            content = f_in.read()
                            f_out.write(content)
                    except Exception as e:
                        f_out.write(f"// Fehler beim Lesen der Datei: {e}\n")
                    
                    f_out.write("\n```\n")
                    f_out.write("-" * 40 + "\n")

    print("Fertig! Die Datei GEMINI.md wurde aktualisiert.")

if __name__ == "__main__":
    # Pfad zum Projekt-Root (angenommen, das Skript liegt in scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, 'GEMINI.md')
    
    generate_ai_context(project_root, output_path)
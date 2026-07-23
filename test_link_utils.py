import os
import pytest
from core import link_utils

# Fixture, um eine temporäre Dateisystemstruktur zu erstellen
@pytest.fixture
def temp_project_structure(tmp_path):
    """
    Erstellt eine temporäre Projektstruktur für Tests.
    tmp_path ist ein pytest-Fixture, das ein temporäres Verzeichnis bereitstellt.
    """
    content_dir = tmp_path / "content"
    assets_dir = tmp_path / "assets"
    
    content_dir.mkdir()
    assets_dir.mkdir()

    # Beispiel-Markdown-Dateien
    (content_dir / "page1.md").write_text("![Image](/assets/image1.png)\n[Link to Page2](page2.md)\n[External Link](https://example.com)")
    (content_dir / "page2.md").write_text("![Image2](../assets/image2.jpg)\n[Link to Page1](page1.md)")
    (content_dir / "subdir").mkdir()
    (content_dir / "subdir" / "page3.md").write_text("[Link to Image1](../../assets/image1.png)")

    # Beispiel-Asset-Dateien
    (assets_dir / "image1.png").touch()
    (assets_dir / "image2.jpg").touch()
    (assets_dir / "unused.txt").touch()

    return {
        "tmp_path": tmp_path,
        "content_dir": content_dir,
        "assets_dir": assets_dir,
        "page1_md": content_dir / "page1.md",
        "page2_md": content_dir / "page2.md",
        "page3_md": content_dir / "subdir" / "page3.md",
        "image1_png": assets_dir / "image1.png",
        "image2_jpg": assets_dir / "image2.jpg",
    }

class TestLinkUtils:

    def test_get_file_usage_count_found(self, temp_project_structure):
        content_dir = temp_project_structure["content_dir"]
        image1_png = temp_project_structure["image1_png"]
        
        # image1.png wird von page1.md und page3.md verwendet
        count = link_utils.get_file_usage_count(str(content_dir), str(image1_png))
        assert count == 2

    def test_get_file_usage_count_not_found(self, temp_project_structure):
        content_dir = temp_project_structure["content_dir"]
        unused_txt = temp_project_structure["assets_dir"] / "unused.txt"
        
        count = link_utils.get_file_usage_count(str(content_dir), str(unused_txt))
        assert count == 0

    def test_get_file_usage_count_external_link_ignored(self, temp_project_structure):
        content_dir = temp_project_structure["content_dir"]
        # Eine externe URL sollte nicht als "Nutzung" gezählt werden
        count = link_utils.get_file_usage_count(str(content_dir), "https://example.com")
        assert count == 0

    def test_update_links_in_directory_file_rename(self, temp_project_structure):
        content_dir = temp_project_structure["content_dir"]
        image1_png = temp_project_structure["image1_png"]
        
        old_abs_path = str(image1_png)
        new_abs_path = str(temp_project_structure["assets_dir"] / "new-image1.png")
        
        # Simuliere das Umbenennen der Datei auf dem Dateisystem
        os.rename(old_abs_path, new_abs_path)

        # Links aktualisieren
        updated_files = link_utils.update_links_in_directory(str(content_dir), old_abs_path, new_abs_path)
        assert updated_files == 2 # page1.md und page3.md sollten aktualisiert werden

        # Inhalt von page1.md prüfen
        page1_content = temp_project_structure["page1_md"].read_text()
        assert "![Image](/assets/new-image1.png)" in page1_content
        assert "![Image](/assets/image1.png)" not in page1_content

        # Inhalt von page3.md prüfen (relativer Pfad sollte korrekt sein)
        page3_content = temp_project_structure["page3_md"].read_text()
        assert "[Link to Image1](../../assets/new-image1.png)" in page3_content
        assert "[Link to Image1](../../assets/image1.png)" not in page3_content

    def test_update_links_in_directory_folder_rename(self, temp_project_structure):
        content_dir = temp_project_structure["content_dir"]
        old_assets_path = str(temp_project_structure["assets_dir"])
        new_assets_path = str(temp_project_structure["tmp_path"] / "media")

        os.rename(old_assets_path, new_assets_path)

        updated_files = link_utils.update_links_in_directory(str(content_dir), old_assets_path, new_assets_path)
        assert updated_files == 2 # page1.md und page3.md

        page1_content = temp_project_structure["page1_md"].read_text()
        assert "![Image](/media/image1.png)" in page1_content

        page3_content = temp_project_structure["page3_md"].read_text()
        assert "[Link to Image1](../../media/image1.png)" in page3_content
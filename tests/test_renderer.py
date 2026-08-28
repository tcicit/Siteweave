import pytest
import os
import yaml
from unittest.mock import MagicMock
from core.renderer import (
    is_markdown_file,
    slugify,
    extract_title,
    parse_plugin_args,
    normalize_config,
    SiteRenderer,
    process_plugins
)
from gui.dialogs.emoji_picker import validate_emoji_data

def test_is_markdown_file():
    extensions = [".md", ".markdown"]
    assert is_markdown_file("index.md", extensions) is True
    assert is_markdown_file("README.MARKDOWN", extensions) is False # Case sensitive check
    assert is_markdown_file("script.py", extensions) is False

def test_slugify():
    assert slugify("Züri Gschnätzlets") == "zuri-gschnatzlets"
    assert slugify("Hello World!") == "hello-world"
    assert slugify("Markdown & Plugins") == "markdown-plugins"
    assert slugify("   viele   leerzeichen   ") == "viele-leerzeichen"

def test_extract_title():
    # Test mit H1 Überschrift
    content = "# Mein Titel\nDies ist ein Text."
    assert extract_title(content, "test.md") == "Mein Titel"
    
    # Test ohne H1 (Fallback auf Dateiname)
    content_no_h1 = "Dies ist nur Text ohne Überschrift."
    assert extract_title(content_no_h1, "mein_artikel_name.md") == "Mein Artikel Name"

def test_parse_plugin_args():
    # Teste Key-Value Paare
    input_str = 'title="Test" count=5 border=true'
    args = parse_plugin_args(input_str)
    assert args["title"] == "Test"
    assert args["count"] == "5"
    assert args["border"] == "true"

    # Teste Flags (ohne Wert)
    input_flag = 'shadow lightbox="false"'
    args_flag = parse_plugin_args(input_flag)
    assert args_flag["shadow"] is True
    assert args_flag["lightbox"] == "false"

def test_normalize_config_repairs_structures():
    # 1. Test: Konvertierung von Dictionary zu Liste (bei Links)
    config = {
        "footer_links": {"title": "Impressum", "url": "/legal.html"}
    }
    normalized = normalize_config(config)
    assert isinstance(normalized["footer_links"], list)
    assert normalized["footer_links"][0]["title"] == "Impressum"

    # 2. Test: Reparatur von Strings, die wie Listen aussehen
    config_str = {
        "header_links": "[{'title': 'Home', 'url': '/'}]"
    }
    normalized_str = normalize_config(config_str)
    assert isinstance(normalized_str["header_links"], list)
    assert normalized_str["header_links"][0]["title"] == "Home"

    # 3. Test: Standardwerte für contact und social
    config_empty = {}
    normalized_empty = normalize_config(config_empty)
    assert isinstance(normalized_empty["contact"], dict)
    assert isinstance(normalized_empty["social"], dict)

def test_site_renderer_initialization(tmp_path):
    """Testet, ob der SiteRenderer mit einer minimalen Konfiguration startet."""
    # Erstelle ein temporäres Projektverzeichnis
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    config_data = {
        "site_name": "Test Site",
        "content_directory": "my_content"
    }
    config_file = project_dir / "config.yaml"
    config_file.write_text(yaml.dump(config_data), encoding="utf-8")

    renderer = SiteRenderer(str(project_dir))
    assert renderer.config["site_name"] == "Test Site"
    assert os.path.abspath(renderer.content_directory) == os.path.abspath(str(project_dir / "my_content"))

def test_validate_emoji_data_skips_malformed_entries():
    data = {
        "Valid": [["😀", "happy"], ["🧩"]],
        "Not a list": "invalid",
        "Empty character": [["", "ignored"]],
        "Invalid keywords": [["✅", 42]],
    }

    assert validate_emoji_data(data) == {"Valid": [("😀", "happy")]}

def test_copy_local_assets_ignores_underscore_directories(tmp_path):
    content_dir = tmp_path / "content"
    output_dir = tmp_path / "output"
    content_dir.mkdir()

    (content_dir / "assets").mkdir()
    (content_dir / "assets" / "image.txt").write_text("asset", encoding="utf-8")
    (content_dir / "_assets").mkdir()
    (content_dir / "_assets" / "private.txt").write_text("private", encoding="utf-8")
    (content_dir / "_about").mkdir()
    (content_dir / "_about" / "help.md").write_text("# Help", encoding="utf-8")

    renderer = SiteRenderer.__new__(SiteRenderer)
    renderer.assets_directory = str(content_dir / "assets")
    renderer.logger = MagicMock()

    renderer.copy_local_assets(str(content_dir), str(output_dir))

    assert (output_dir / "assets" / "image.txt").is_file()
    assert not (output_dir / "_assets").exists()
    assert not (output_dir / "_about").exists()

def test_process_plugins_with_failing_plugin():
    """Testet, wie das System reagiert, wenn ein Plugin-Handler eine Exception wirft."""
    # Erstelle ein Mock-Plugin-Modul
    mock_plugin = MagicMock()
    # Simuliere einen Absturz bei Aufruf der handle-Funktion
    mock_plugin.handle.side_effect = RuntimeError("Plugin critical failure")
    
    plugins_collection = {"fail": mock_plugin}
    context = {"page_title": "Test Page"}
    
    # Aktuell wird die Exception nach oben durchgereicht
    with pytest.raises(RuntimeError, match="Plugin critical failure"):
        process_plugins("Text mit [[fail]] Plugin", context, None, plugins_collection)
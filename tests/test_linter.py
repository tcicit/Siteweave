import pytest
import os
import frontmatter
from core.linter import check_and_update_frontmatter, run

def test_linter_dry_run_does_not_modify_files(tmp_path):
    """Prüft, ob der Linter im Dry-Run Modus (fix=False) keine Dateien ändert."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()

    # Markdown-Datei mit fehlenden Feldern (z.B. title, date, release_date)
    test_file = content_dir / "article.md"
    original_text = "# Test Title\n\nSome body text."
    test_file.write_text(original_text, encoding="utf-8")

    result = check_and_update_frontmatter(str(content_dir), fix=False)

    # Datei darf nicht verändert worden sein
    assert test_file.read_text(encoding="utf-8") == original_text
    assert result["warnings"] > 0
    assert result["updated_files"] == 0

def test_linter_fix_mode_updates_frontmatter(tmp_path):
    """Prüft, ob der Linter mit fix=True fehlende Metadaten ergänzt."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()

    # Vorhandene index.md bereitstellen
    (content_dir / "index.md").write_text("---\ntitle: Home\n---\nWelcome", encoding="utf-8")

    test_file = content_dir / "article.md"
    test_file.write_text("# My Generated Post\n\nSome text.", encoding="utf-8")

    result = check_and_update_frontmatter(str(content_dir), fix=True)

    assert result["updated_files"] >= 1
    post = frontmatter.load(str(test_file))
    assert post.metadata["title"] == "My Generated Post"
    assert "date" in post.metadata
    assert "release_date" in post.metadata

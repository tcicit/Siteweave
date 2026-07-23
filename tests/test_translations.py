import pytest
from unittest.mock import patch, MagicMock
import subprocess
from manage_translations import run_command

def test_run_command_success():
    """Prüft, ob run_command ohne Fehler durchläuft."""
    with patch("subprocess.check_call") as mock_call:
        run_command(["echo", "test"])
        mock_call.assert_called_once_with(["echo", "test"])

def test_run_command_failure():
    """Prüft, ob das Skript bei einem Fehler mit SystemExit(1) beendet wird."""
    with patch("subprocess.check_call", side_effect=subprocess.CalledProcessError(1, "cmd")):
        with pytest.raises(SystemExit) as e:
            run_command(["false"])
        assert e.value.code == 1
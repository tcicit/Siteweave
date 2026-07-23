import pytest
import os
import tempfile
from gui.workers import WorkerThread

def test_worker_script_not_found(qtbot):
    """Testet, ob der Worker einen Fehler meldet, wenn das Skript fehlt."""
    worker = WorkerThread("non_existent_script.py")
    
    with qtbot.waitSignal(worker.error, timeout=1000) as blocker:
        worker.start()
    
    assert "FileNotFoundError" in blocker.args[0]

def test_worker_execution_success(qtbot):
    """Testet die erfolgreiche Ausführung eines dynamischen Skripts."""
    # Erstelle ein temporäres Worker-Skript
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
        tmp.write("""
def run(context):
    return f"Hello {context.get('name')}"
""")
        tmp_path = tmp.name

    try:
        context = {"name": "Siteweave"}
        worker = WorkerThread(tmp_path, context)

        with qtbot.waitSignal(worker.finished, timeout=2000) as blocker:
            worker.start()

        assert blocker.args[0] == "Hello Siteweave"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
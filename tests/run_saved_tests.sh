#!/usr/bin/env bash
# Ausführbares Skript zum Starten der Tests und Speichern der Log-Ausgabe

set -euo pipefail
PYTHON="/home/tci/Dokumente/Entwicklung/Python/apps/Siteweave/venv/bin/python"

# Führe pytest aus und speichere die Ausgabe in tests/test_run_log.txt
mkdir -p tests
$PYTHON -m pytest -q | tee tests/test_run_log.txt

# Exit-Code von pytest wird durch 'set -e' weitergegeben

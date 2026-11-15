"""Fuehrt die eingebauten Selbsttests der Skripte aus.

Jedes Skript bringt mit `--selftest` einen eigenen Test mit, der ohne
Kursmaterial laeuft. pytest ruft sie einzeln auf, damit ein Fehler genau
einem Skript zugeordnet ist.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"

SKRIPTE = [
    "lernblatt-generator/scripts/lernblatt_html.py",
    "lernblatt-generator/scripts/slides.py",
    "lernblatt-generator/scripts/check_crops.py",
    "themen-analyse/scripts/extract_and_map.py",
    "themen-analyse/scripts/annots.py",
    "themen-analyse/scripts/graph.py",
]


@pytest.mark.parametrize("skript", SKRIPTE, ids=lambda s: Path(s).stem)
def test_selftest(skript):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    res = subprocess.run(
        [sys.executable, str(SKILLS / skript), "--selftest"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    assert res.returncode == 0, res.stdout + res.stderr
    assert "selftest ok" in res.stdout, res.stdout + res.stderr

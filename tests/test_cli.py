"""Die Kommandozeile `lernblatt` startet, zeigt Hilfe und meldet Fehler."""

import subprocess
import sys

import pytest

from lernblatt import __version__
from lernblatt.cli import BEFEHLE, main


def test_hilfe_nennt_alle_befehle(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    for befehl in [*BEFEHLE, "selftest"]:
        assert befehl in out


def test_version(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == __version__


def test_unbekannter_befehl(capsys):
    assert main(["gibtsnicht"]) == 2
    assert "Unbekannter Befehl" in capsys.readouterr().err


@pytest.mark.parametrize("befehl", sorted(BEFEHLE))
def test_befehl_hilfe(befehl, capsys):
    """Jeder Befehl laesst sich importieren und beantwortet --help."""
    try:
        code = main([befehl, "--help"])
    except SystemExit as exc:  # argparse beendet nach --help
        code = exc.code
    assert code in (0, None)
    assert befehl in capsys.readouterr().out


def test_modulaufruf():
    """python -m lernblatt funktioniert wie der installierte Befehl."""
    res = subprocess.run(
        [sys.executable, "-m", "lernblatt", "--version"], capture_output=True, text=True
    )
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == __version__

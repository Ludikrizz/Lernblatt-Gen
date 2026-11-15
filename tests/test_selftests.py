"""Fuehrt die eingebauten Selbsttests der Module aus.

Jedes Modul bringt einen `_selftest()` mit, der ohne Kursmaterial laeuft.
pytest ruft sie einzeln auf, damit ein Fehler genau einem Modul zugeordnet ist.
"""

import importlib

import pytest

from lernblatt.cli import SELBSTTESTS


@pytest.mark.parametrize("modul", SELBSTTESTS, ids=lambda m: m.rsplit(".", 1)[-1])
def test_selftest(modul, capsys):
    importlib.import_module(modul)._selftest()
    assert "selftest ok" in capsys.readouterr().out

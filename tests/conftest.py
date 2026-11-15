"""Gemeinsame Einstellungen fuer alle Tests."""

# PyMuPDF bindet seinen Meldungskanal beim ersten Import an sys.stdout. Passiert
# das innerhalb eines Tests, ist es der Capture-Strom dieses Tests, den pytest
# danach schliesst. Spaetere OCR-Aufrufe scheitern dann mit "I/O operation on
# closed file". Der Import hier bindet den Kanal einmal fuer die ganze Sitzung.
import pymupdf  # noqa: F401

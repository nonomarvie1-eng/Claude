"""Intégrité des fichiers et import sécurisé des archives de transfert."""
import json
import lzma
import struct
import zipfile

import pytest

from nexus.data.integrity import build_manifest, check_bi5, safe_import_zip


def _bi5(rows):
    raw = b"".join(struct.pack(">5If", *r) for r in rows)
    return lzma.compress(raw, format=lzma.FORMAT_ALONE)


def test_check_bi5():
    good = _bi5([(0, 110000, 110010, 109990, 110020, 1.0), (60, 110010, 110000, 109995, 110015, 1.0)])
    assert check_bi5(good, 1e5) is None
    assert check_bi5(b"", 1e5) is None
    assert check_bi5(b"garbage", 1e5) == "LZMA illisible"
    bad = _bi5([(0, 110000, 110010, 110005, 110020, 1.0)])   # low > open
    assert check_bi5(bad, 1e5) == "OHLC incohérent"


def _make_zip(tmp_path, members, manifest_files=None):
    src = tmp_path / "src"
    for name, data in members.items():
        p = src / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    files = [src / n for n in (manifest_files or members)]
    man = build_manifest(files, src)
    zp = tmp_path / "t.zip"
    with zipfile.ZipFile(zp, "w") as z:
        for n, d in members.items():
            z.writestr(n, d)
        z.writestr("manifest.json", json.dumps(man))
    return zp


def test_safe_import_accepts_expected_files(tmp_path):
    zp = _make_zip(tmp_path, {"data/bars/EURUSD/2020.parquet": b"x" * 10})
    dest = tmp_path / "dest"
    rep = safe_import_zip(zp, dest)
    assert rep["n"] == 1 and (dest / "data/bars/EURUSD/2020.parquet").read_bytes() == b"x" * 10


def test_safe_import_rejects_unexpected_or_traversal(tmp_path):
    zp = _make_zip(tmp_path, {"data/bars/EURUSD/2020.parquet": b"x", "nexus/evil.py": b"print(1)"},
                   manifest_files=["data/bars/EURUSD/2020.parquet"])
    with pytest.raises(ValueError):
        safe_import_zip(zp, tmp_path / "dest")
    zp2 = tmp_path / "t2.zip"
    with zipfile.ZipFile(zp2, "w") as z:
        z.writestr("../../etc/x", b"x"); z.writestr("manifest.json", "{}")
    with pytest.raises(ValueError):
        safe_import_zip(zp2, tmp_path / "dest")


def test_safe_import_detects_tampering(tmp_path):
    zp = _make_zip(tmp_path, {"data/bars/EURUSD/2020.parquet": b"abc"})
    tampered = tmp_path / "t3.zip"
    with zipfile.ZipFile(zp) as zin, zipfile.ZipFile(tampered, "w") as zout:
        zout.writestr("manifest.json", zin.read("manifest.json"))
        zout.writestr("data/bars/EURUSD/2020.parquet", b"abd")
    with pytest.raises(ValueError):
        safe_import_zip(tampered, tmp_path / "dest")


def test_dukascopy_downloader_blocked_without_written_consent(monkeypatch):
    from datetime import date
    from nexus.data import dukascopy
    monkeypatch.delenv(dukascopy.CONSENT_ENV, raising=False)
    with pytest.raises(dukascopy.DukascopyTermsError):
        dukascopy.download_range("EURUSD", date(2020, 1, 1), date(2020, 1, 2))

"""Vérification du cache, préparation et import du transfert de données.

    python scripts/transfer.py verify EURUSD 2019-12-01 2026-07-01 [--repair]
        contrôle chaque fichier téléchargé ; --repair supprime les fichiers corrompus
        (le prochain lancement du téléchargement les reprendra).
    python scripts/transfer.py pack EURUSD <archive.zip>
        crée une archive contenant UNIQUEMENT les Parquet, le rapport qualité,
        la sortie de check_env et un manifeste SHA-256 (pas les fichiers bruts).
    python scripts/transfer.py import <archive.zip>
        (côté cloud) vérifie l'archive membre par membre puis l'importe.
"""
from __future__ import annotations

import json
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nexus.data.integrity import build_manifest, safe_import_zip, verify_dukascopy_cache  # noqa: E402


def main(a):
    if a[0] == "verify":
        rep = verify_dukascopy_cache(a[1], date.fromisoformat(a[2]), date.fromisoformat(a[3]),
                                     delete_corrupt="--repair" in a)
        print(json.dumps({k: (v if not isinstance(v, list) else {"n": len(v), "exemples": v[:10]}) for k, v in rep.items()},
                         indent=2, ensure_ascii=False))
        if rep["missing"] or rep["corrupt"]:
            print("Relancer le téléchargement pour compléter / réparer (reprise automatique).")
    elif a[0] == "pack":
        sym, out = a[1], Path(a[2])
        files = sorted((ROOT / "data" / "bars" / sym).glob("*.parquet"))
        files += [p for p in (ROOT / "reports" / "data_quality" / f"{sym}.json", ROOT / "reports" / "check_env_windows.txt") if p.exists()]
        if not files:
            raise SystemExit("aucun fichier Parquet : lancer d'abord build_bars.py")
        man = build_manifest(files, ROOT)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                z.write(f, f.relative_to(ROOT).as_posix())
            z.writestr("manifest.json", json.dumps(man, indent=2))
        print(f"archive : {out} ({out.stat().st_size / 1e6:.1f} Mo, {len(files)} fichiers)")
    elif a[0] == "import":
        print(safe_import_zip(Path(a[1])))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:] or ["help"])

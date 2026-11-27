"""Fenêtres de session en fuseaux IANA (gestion automatique des changements d'heure)."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SessionHypothesis:
    """Hypothèse de session : range [range_start, range_end) puis fenêtre d'entrée
    [range_end, entry_end) et sortie forcée à exit_time, toutes en heure locale `tz`.

    Chaque hypothèse est un essai distinct dans le registre (comparaisons multiples).
    """
    name: str
    tz: str
    range_start: str
    range_end: str
    entry_end: str
    exit_time: str
    rationale: str


SESSION_HYPOTHESES = {
    # Le document SBA indique 00:00–09:00 / 09:00–13:00 / 20:00 sans fuseau.
    "paris": SessionHypothesis(
        "paris", "Europe/Paris", "00:00", "09:00", "13:00", "20:00",
        "Lecture littérale des horaires SBA en heure de Paris (vidéaste francophone) — hypothèse non confirmée.",
    ),
    "london": SessionHypothesis(
        "london", "Europe/London", "00:00", "08:00", "12:00", "19:00",
        "Range nocturne jusqu'à l'ouverture de Londres (08:00 locale), principal centre du Forex.",
    ),
    "utc": SessionHypothesis(
        "utc", "UTC", "00:00", "07:00", "11:00", "18:00",
        "Définition fixe en UTC, sans changement d'heure (contrôle de robustesse).",
    ),
    "newyork": SessionHypothesis(
        "newyork", "America/New_York", "00:00", "09:30", "11:30", "15:55",
        "Range avant l'ouverture des actions US (09:30 New York).",
    ),
}


def local_to_utc(day: pd.Timestamp, hhmm: str, tz: str) -> pd.Timestamp:
    """Convertit (jour calendaire local, heure locale) en instant UTC."""
    h, m = map(int, hhmm.split(":"))
    local = pd.Timestamp(year=day.year, month=day.month, day=day.day, hour=h, minute=m).tz_localize(
        tz, nonexistent="shift_forward", ambiguous=False
    )
    return local.tz_convert("UTC")


def session_bounds(days, hyp: SessionHypothesis) -> pd.DataFrame:
    """Pour chaque jour local, les bornes UTC de la session."""
    rows = []
    for d in days:
        rows.append(
            {
                "day": d,
                "range_start": local_to_utc(d, hyp.range_start, hyp.tz),
                "range_end": local_to_utc(d, hyp.range_end, hyp.tz),
                "entry_end": local_to_utc(d, hyp.entry_end, hyp.tz),
                "exit_time": local_to_utc(d, hyp.exit_time, hyp.tz),
            }
        )
    return pd.DataFrame(rows)

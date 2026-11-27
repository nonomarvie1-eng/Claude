"""Registre permanent des hypothèses et des essais (SQLite).

Chaque hypothèse est enregistrée AVANT exécution (pré-enregistrement) avec sa
justification, ses paramètres autorisés, ses données, ses métriques, ses
critères de rejet, la version du code et le nombre d'essais déjà réalisés.
Chaque essai (variante × actif × période) est journalisé, y compris les échecs.
Le registre ne s'efface jamais : aucune commande de suppression n'est fournie.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from datetime import datetime, timezone

from ..config import REGISTRY_PATH, ROOT

SCHEMA = """
CREATE TABLE IF NOT EXISTS hypotheses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    family TEXT NOT NULL,
    statement TEXT NOT NULL,
    rationale TEXT NOT NULL,
    params_json TEXT NOT NULL,
    data_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    rejection_json TEXT NOT NULL,
    spec_hash TEXT NOT NULL,
    code_version TEXT NOT NULL,
    trials_before INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS trials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis_key TEXT NOT NULL REFERENCES hypotheses(key),
    variant_json TEXT NOT NULL,
    symbol TEXT NOT NULL,
    period TEXT NOT NULL,
    cost_multiplier REAL NOT NULL,
    config_hash TEXT NOT NULL,
    code_version TEXT NOT NULL,
    status TEXT NOT NULL,
    n_trades INTEGER,
    mean_r REAL,
    p_value REAL,
    result_json TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT
);
CREATE TABLE IF NOT EXISTS budgets (
    family TEXT PRIMARY KEY,
    max_trials INTEGER NOT NULL,
    justification TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS budget_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family TEXT NOT NULL,
    old_max INTEGER,
    new_max INTEGER NOT NULL,
    reason TEXT NOT NULL,
    ts TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS strategy_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis_key TEXT NOT NULL,
    variant_json TEXT NOT NULL,
    symbol TEXT NOT NULL,
    status TEXT NOT NULL,          -- rejected | insufficient | candidate | archived
    verdict TEXT NOT NULL,
    reason TEXT NOT NULL,
    trial_id INTEGER,
    ts TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS validation_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    reason TEXT NOT NULL,
    code_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS final_test_access (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    reason TEXT NOT NULL,
    code_version TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def code_version() -> str:
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "nexus"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return rev + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def stable_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


class Registry:
    def __init__(self, path=REGISTRY_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(path)
        self.con.executescript(SCHEMA)
        cols = {r[1] for r in self.con.execute("PRAGMA table_info(trials)")}
        for col, typ in (("data_hash", "TEXT"), ("seed", "INTEGER"), ("purpose", "TEXT")):
            if col not in cols:
                self.con.execute(f"ALTER TABLE trials ADD COLUMN {col} {typ}")
        self.con.commit()

    # -- budgets d'expériences ------------------------------------------------
    def set_budget(self, family: str, max_trials: int, justification: str) -> None:
        row = self.con.execute("SELECT max_trials FROM budgets WHERE family=?", (family,)).fetchone()
        if row is None:
            self.con.execute("INSERT INTO budgets VALUES (?,?,?,?)", (family, max_trials, justification, now()))
        elif row[0] != max_trials:
            # Toute extension est documentée et conservée (correction des comparaisons multiples)
            self.con.execute("INSERT INTO budget_changes (family,old_max,new_max,reason,ts) VALUES (?,?,?,?,?)",
                             (family, row[0], max_trials, justification, now()))
            self.con.execute("UPDATE budgets SET max_trials=? WHERE family=?", (max_trials, family))
        self.con.commit()

    def family_trials(self, family: str) -> int:
        return self.con.execute(
            "SELECT COUNT(*) FROM trials t JOIN hypotheses h ON t.hypothesis_key=h.key WHERE h.family=?",
            (family,)).fetchone()[0]

    def set_status(self, key, variant, symbol, status, verdict, reason, trial_id=None) -> None:
        self.con.execute("INSERT INTO strategy_status (hypothesis_key,variant_json,symbol,status,verdict,reason,trial_id,ts)"
                         " VALUES (?,?,?,?,?,?,?,?)",
                         (key, json.dumps(variant, sort_keys=True), symbol, status, verdict, reason, trial_id, now()))
        self.con.commit()

    # -- hypothèses ---------------------------------------------------------
    def n_trials(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM trials").fetchone()[0]

    def register_hypothesis(self, spec: dict) -> str:
        required = ["key", "family", "statement", "rationale", "params", "data", "metrics", "rejection"]
        missing = [k for k in required if k not in spec]
        if missing:
            raise ValueError(f"pré-enregistrement incomplet : {missing}")
        h = stable_hash({k: spec[k] for k in required})
        row = self.con.execute("SELECT spec_hash FROM hypotheses WHERE key=?", (spec["key"],)).fetchone()
        if row:
            if row[0] != h:
                raise ValueError(
                    f"L'hypothèse {spec['key']} a déjà été enregistrée avec une autre spécification. "
                    "Une hypothèse modifiée doit recevoir une nouvelle clé (nouvel essai)."
                )
            return h
        self.con.execute(
            "INSERT INTO hypotheses (key,family,statement,rationale,params_json,data_json,metrics_json,"
            "rejection_json,spec_hash,code_version,trials_before,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (spec["key"], spec["family"], spec["statement"], spec["rationale"], json.dumps(spec["params"]),
             json.dumps(spec["data"]), json.dumps(spec["metrics"]), json.dumps(spec["rejection"]), h,
             code_version(), self.n_trials(), now()),
        )
        self.con.commit()
        return h

    # -- essais ---------------------------------------------------------------
    def start_trial(self, key: str, variant: dict, symbol: str, period: str, cost_multiplier: float,
                    *, data_hash: str | None = None, seed: int | None = None, purpose: str = "selection") -> int:
        row = self.con.execute("SELECT family FROM hypotheses WHERE key=?", (key,)).fetchone()
        if not row:
            raise PermissionError(f"hypothèse {key} non pré-enregistrée : exécution refusée")
        b = self.con.execute("SELECT max_trials FROM budgets WHERE family=?", (row[0],)).fetchone()
        if b is not None and self.family_trials(row[0]) >= b[0]:
            raise PermissionError(f"budget d'expériences épuisé pour la famille {row[0]} ({b[0]} essais)")
        cfg = stable_hash({"key": key, "variant": variant, "symbol": symbol, "period": period, "cost": cost_multiplier})
        cur = self.con.execute(
            "INSERT INTO trials (hypothesis_key,variant_json,symbol,period,cost_multiplier,config_hash,code_version,"
            "status,started_at,data_hash,seed,purpose) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (key, json.dumps(variant, sort_keys=True), symbol, period, cost_multiplier, cfg, code_version(), "running",
             now(), data_hash, seed, purpose),
        )
        self.con.commit()
        return cur.lastrowid

    def finish_trial(self, trial_id: int, *, status: str, n_trades=None, mean_r=None, p_value=None, result=None):
        self.con.execute(
            "UPDATE trials SET status=?, n_trades=?, mean_r=?, p_value=?, result_json=?, finished_at=? WHERE id=?",
            (status, n_trades, mean_r, p_value, json.dumps(result, default=str) if result else None, now(), trial_id),
        )
        self.con.commit()

    def log_validation_access(self, reason: str) -> None:
        self.con.execute("INSERT INTO validation_access (ts,reason,code_version) VALUES (?,?,?)", (now(), reason, code_version()))
        self.con.commit()

    def log_final_access(self, reason: str) -> None:
        self.con.execute("INSERT INTO final_test_access (ts,reason,code_version) VALUES (?,?,?)", (now(), reason, code_version()))
        self.con.commit()

    def trials_df(self):
        import pandas as pd
        return pd.read_sql("SELECT * FROM trials", self.con)

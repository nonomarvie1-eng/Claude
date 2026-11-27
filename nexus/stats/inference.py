"""Inférence statistique tenant compte de la dépendance temporelle et des
comparaisons multiples."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Taille d'échantillon
# ---------------------------------------------------------------------------
def required_trades(mu: float, sigma: float, *, alpha: float = 0.05, power: float = 0.8,
                    n_tests: int = 1, rho_sum: float = 0.0, two_sided: bool = False) -> int:
    """Nombre de trades pour détecter une espérance `mu` (en R) d'écart-type `sigma`.

    n = ((z_{1-a'} + z_{power}) * sigma / mu)^2 * (1 + 2*rho_sum)
    - a' = alpha / n_tests (Bonferroni, conservateur) ; unilatéral par défaut
      (on ne cherche que mu > 0).
    - (1 + 2*sum rho_k) : inflation de variance due à l'autocorrélation des
      résultats (taille effective n_eff = n / (1 + 2*sum rho_k)).
    """
    a = alpha / n_tests
    za = stats.norm.ppf(1 - a / (2 if two_sided else 1))
    zb = stats.norm.ppf(power)
    return int(math.ceil(((za + zb) * sigma / mu) ** 2 * (1 + 2 * rho_sum)))


def binary_trade_sigma(rr: float, p: float | None = None) -> float:
    """Écart-type d'un trade -1R / +rr ; p par défaut = point mort 1/(1+rr)."""
    p = 1 / (1 + rr) if p is None else p
    mean = p * rr - (1 - p)
    return math.sqrt(p * rr ** 2 + (1 - p) - mean ** 2)


# ---------------------------------------------------------------------------
# Bootstrap par blocs (dépendance temporelle)
# ---------------------------------------------------------------------------
def block_bootstrap_mean(values: np.ndarray, groups: np.ndarray, *, n_boot: int = 5000, seed: int = 0):
    """Bootstrap par blocs naturels (ex. semaines ISO) : on rééchantillonne des
    blocs entiers avec remise. Renvoie (moyenne, IC95 bas, IC95 haut, p unilatéral H0: mu<=0)."""
    values = np.asarray(values, float)
    uniq, inv = np.unique(groups, return_inverse=True)
    sums = np.bincount(inv, weights=values)
    counts = np.bincount(inv)
    rng = np.random.default_rng(seed)
    nb = len(uniq)
    idx = rng.integers(0, nb, size=(n_boot, nb))
    boot = sums[idx].sum(axis=1) / counts[idx].sum(axis=1)
    m = values.mean()
    lo, hi = np.percentile(boot, [2.5, 97.5])
    # p-valeur par recentrage de la distribution bootstrap sous H0 (mu = 0)
    p = float((np.sum(boot - m >= m) + 1) / (n_boot + 1))
    return float(m), float(lo), float(hi), p


def autocorr_sum(x: np.ndarray, max_lag: int = 10) -> float:
    x = np.asarray(x, float) - np.mean(x)
    if len(x) < 3 * max_lag or x.var() == 0:
        return 0.0
    s = 0.0
    for k in range(1, max_lag + 1):
        s += np.corrcoef(x[:-k], x[k:])[0, 1]
    return float(s)


# ---------------------------------------------------------------------------
# Comparaisons multiples
# ---------------------------------------------------------------------------
def benjamini_hochberg(pvals) -> np.ndarray:
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.minimum(adj, 1.0)
    return out


def deflated_sharpe(sr: float, n_obs: int, skew: float, kurt: float, n_trials: int, sr_var_trials: float) -> float:
    """Deflated Sharpe Ratio (Bailey & López de Prado, 2014), SR non annualisé.
    Probabilité que le vrai SR soit > au maximum attendu de n_trials essais nuls."""
    if n_trials < 2 or n_obs < 3:
        sr0 = 0.0
    else:
        g = 0.5772156649
        sr0 = math.sqrt(max(sr_var_trials, 1e-12)) * ((1 - g) * stats.norm.ppf(1 - 1 / n_trials)
                                                      + g * stats.norm.ppf(1 - 1 / (n_trials * math.e)))
    den = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr ** 2, 1e-12))
    return float(stats.norm.cdf((sr - sr0) * math.sqrt(n_obs - 1) / den))


# ---------------------------------------------------------------------------
# Verdict en quatre catégories
# ---------------------------------------------------------------------------
CATEGORIES = (
    "Avantage statistique démontré",
    "Résultats prometteurs mais preuves insuffisantes",
    "Absence d'avantage démontré",
    "Résultats incompatibles avec une exploitation rentable",
)


def verdict(mean_r: float, ci_lo: float, ci_hi: float, p_adj: float, *, mean_r_2x_costs: float,
            p_random_adj: float, phase: str) -> str:
    """Règles fixées AVANT les résultats.
    - « démontré » n'est atteignable qu'après validation ET test final (phase="final").
    - Sur les données de développement, le meilleur verdict possible est « prometteur ».
    """
    if ci_hi < 0:
        return CATEGORIES[3]
    strong = ci_lo > 0 and p_adj < 0.05 and p_random_adj < 0.05 and mean_r_2x_costs > 0
    if strong and phase == "final":
        return CATEGORIES[0]
    if strong or (mean_r > 0 and p_adj < 0.25 and mean_r_2x_costs > 0):
        return CATEGORIES[1]
    if mean_r <= 0 and ci_hi < 0.05 and mean_r_2x_costs < 0:
        # Même dans le meilleur cas plausible, l'espérance reste trop faible pour couvrir des coûts réalistes
        return CATEGORIES[3]
    return CATEGORIES[2]


def week_groups(times: pd.Series) -> np.ndarray:
    t = pd.DatetimeIndex(times).tz_convert("UTC")
    iso = t.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).to_numpy()

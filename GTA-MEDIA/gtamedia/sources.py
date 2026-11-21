"""Registre des sources et contrôle des droits.

Chaque extrait utilisé dans un montage doit venir d'une source inscrite dans
sources/registry.yaml, avec un statut de droits. Le montage est BLOQUÉ si un
extrait n'a pas un statut autorisé ; le système produit alors la liste des
plans à filmer sur Xbox pour le remplacer.

Statuts :
  capture_perso      vos captures Xbox (gameplay publié selon la politique Rockstar)
  cc_by              vidéo sous licence Creative Commons Attribution (YouTube) : crédit obligatoire
  autorisation_ecrite  accord écrit de l'auteur (preuve à conserver dans sources/autorisations/)
  domaine_public     œuvre sans droits
  officiel_rockstar  contenu officiel Rockstar (bandes-annonces, captures) : BLOQUÉ par défaut,
                     tant que la politique Rockstar n'a pas été relue (réglage rights.allow_official)
  demande_envoyee    autorisation demandée, en attente : BLOQUÉ
  non_autorise       tous droits réservés, sans accord : BLOQUÉ
  inconnu            non vérifié : BLOQUÉ
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import re
from pathlib import Path

import yaml

from .utils import ROOT, PipelineError, log

REGISTRY = ROOT / "sources" / "registry.yaml"
ALLOWED = {"capture_perso", "cc_by", "autorisation_ecrite", "domaine_public"}
NEEDS_CREDIT = {"cc_by", "autorisation_ecrite"}
STATUSES = ALLOWED | {"officiel_rockstar", "demande_envoyee", "non_autorise", "inconnu", "cc_by_sa"}


# ------------------------------------------------------------------ registre
def load() -> dict:
    if not REGISTRY.exists():
        return {}
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    return data.get("sources", {}) or {}


def save(sources: dict) -> None:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    head = ("# Registre des sources GTA-MEDIA : une entrée par vidéo ou capture utilisée.\n"
            "# Statuts autorisés au montage : " + ", ".join(sorted(ALLOWED)) + "\n"
            "# Ne changez un statut qu'avec une preuve (licence visible, message d'accord…).\n")
    REGISTRY.write_text(head + yaml.safe_dump({"sources": sources}, allow_unicode=True, sort_keys=True),
                        encoding="utf-8")


def add(sid: str, **fields) -> dict:
    sources = load()
    entry = sources.get(sid, {})
    entry.update({k: v for k, v in fields.items() if v is not None})
    entry.setdefault("status", "inconnu")
    entry.setdefault("added", dt.date.today().isoformat())
    if entry["status"] not in STATUSES:
        raise PipelineError(f"Statut inconnu : {entry['status']} ({', '.join(sorted(STATUSES))})")
    sources[sid] = entry
    save(sources)
    return entry


def register_library(index: dict) -> int:
    """Inscrit automatiquement les captures importées comme capture_perso."""
    sources, n = load(), 0
    for name, e in index.items():
        sid = "xbox_" + Path(name).stem
        if sid not in sources:
            sources[sid] = {"status": "capture_perso", "file": e["file"], "platform": "Xbox (capture perso)",
                            "author": "nous", "date": e.get("captured", "")[:10],
                            "added": dt.date.today().isoformat()}
            n += 1
    if n:
        save(sources)
    return n


# ------------------------------------------------------------- vérification
def _clip_refs(proj: dict) -> list[dict]:
    """Toutes les références d'extraits d'un projet (clips, beats, compare)."""
    refs = []
    items = [b.get("clip", {}) | {"_beat": i, "_say": b.get("say", ""), "_fallback": b.get("fallback")}
             for i, b in enumerate(proj.get("beats") or [])]
    items += [dict(c, _clip=i) for i, c in enumerate(proj.get("clips") or [])]
    for it in items:
        if it.get("layout") == "compare":
            for side in ("top", "bottom"):
                refs.append(dict(it[side], _where=f"plan {it.get('_clip', it.get('_beat'))} ({side})",
                                 _fallback=it.get("_fallback")))
        else:
            where = f"beat {it['_beat'] + 1}" if "_beat" in it else f"plan {it['_clip'] + 1}"
            refs.append(dict(it, _where=where))
    return refs


def check_project(proj: dict, cfg: dict) -> dict:
    """Vérifie les droits de chaque extrait. Renvoie {ok, problems, credits, to_film, tags}."""
    sources = load()
    allow_official = bool((cfg.get("rights") or {}).get("allow_official", False))
    allowed = ALLOWED | ({"officiel_rockstar"} if allow_official else set())
    problems, credits, to_film = [], {}, []
    for ref in _clip_refs(proj):
        sid = ref.get("source")
        if not sid:
            f = str(ref.get("file", ""))
            if f.replace("\\", "/").startswith("library/"):
                continue                                   # capture importée par ingest = capture perso
            problems.append(f"{ref['_where']} : fichier « {f} » sans source déclarée")
            to_film.append(ref)
            continue
        src = sources.get(sid)
        if not src:
            problems.append(f"{ref['_where']} : source « {sid} » absente du registre")
            to_film.append(ref)
            continue
        st = src.get("status", "inconnu")
        if st not in allowed:
            problems.append(f"{ref['_where']} : « {sid} » statut {st} → NON UTILISABLE")
            to_film.append(ref)
            continue
        if st == "autorisation_ecrite" and not src.get("proof"):
            problems.append(f"{ref['_where']} : « {sid} » autorisation sans preuve (champ proof)")
            to_film.append(ref)
            continue
        if not src.get("file"):
            problems.append(f"{ref['_where']} : « {sid} » autorisé mais fichier local manquant (champ file)")
            continue
        if st in NEEDS_CREDIT or st == "officiel_rockstar":
            credits[sid] = src
    return {"ok": not problems, "problems": problems, "credits": credits, "to_film": to_film}


def credit_line(sid: str, src: dict) -> str:
    lic = {"cc_by": "licence CC BY", "autorisation_ecrite": "avec l'autorisation de l'auteur",
           "officiel_rockstar": "© Rockstar Games"}.get(src.get("status"), src.get("status"))
    who = src.get("author", "auteur inconnu")
    return f"{src.get('title', sid)} — {who} ({lic}) {src.get('url', '')}".strip()


def short_tag(src: dict) -> str:
    """Texte court affiché à l'écran pendant l'extrait (crédit visible)."""
    who = src.get("author", "")
    lic = {"cc_by": "CC BY", "autorisation_ecrite": "avec accord", "officiel_rockstar": "Rockstar Games"}
    return f"Source : {who} · {lic.get(src.get('status'), '')}".strip(" ·")


def write_reports(proj_dir: Path, name: str, res: dict, out_dir: Path) -> None:
    if res["credits"]:
        lines = ["Crédits des extraits utilisés :"] + [f"- {credit_line(k, v)}" for k, v in res["credits"].items()]
        (out_dir / f"{name}_credits.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if res["to_film"]:
        rows = ["# Plans à filmer sur Xbox pour remplacer les extraits non autorisés", ""]
        for r in res["to_film"]:
            what = r.get("_fallback") or "plan de gameplay illustrant : " + (r.get("_say") or "(voir le script)")
            rows.append(f"- **{r['_where']}** — {what}")
        rows += ["", "Après capture : `python gta.py ingest`, puis remplacez `source:` par la capture "
                 "(`python gta.py sources` liste les captures inscrites)."]
        (proj_dir / "A_FILMER.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


# --------------------------------------------------------------- recherche
def youtube_search(query: str, cc_only: bool = True, max_results: int = 25, lang: str = "fr") -> list[dict]:
    """Recherche YouTube via l'API officielle (clé gratuite : variable YOUTUBE_API_KEY).
    Avec cc_only, ne renvoie que les vidéos sous licence Creative Commons."""
    import requests
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key:
        raise PipelineError("Clé YOUTUBE_API_KEY absente (clé gratuite Google Cloud, voir docs/MULTISOURCE.md).")
    params = {"part": "snippet", "q": query, "type": "video", "maxResults": max_results,
              "relevanceLanguage": lang, "key": key, "videoDuration": "any"}
    if cc_only:
        params["videoLicense"] = "creativeCommon"
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=30)
    if r.status_code != 200:
        raise PipelineError(f"YouTube API : HTTP {r.status_code} {r.text[:200]}")
    ids = [it["id"]["videoId"] for it in r.json().get("items", [])]
    if not ids:
        return []
    r2 = requests.get("https://www.googleapis.com/youtube/v3/videos",
                      params={"part": "snippet,contentDetails,status,statistics", "id": ",".join(ids), "key": key},
                      timeout=30)
    if r2.status_code != 200:
        raise PipelineError(f"YouTube API : HTTP {r2.status_code} {r2.text[:200]}")
    out = []
    for v in r2.json().get("items", []):
        lic = v["status"].get("license")                    # "creativeCommon" ou "youtube"
        out.append({
            "id": "yt_" + v["id"], "url": f"https://www.youtube.com/watch?v={v['id']}",
            "title": v["snippet"]["title"], "author": v["snippet"]["channelTitle"],
            "date": v["snippet"]["publishedAt"][:10], "duration": v["contentDetails"]["duration"],
            "views": v.get("statistics", {}).get("viewCount"),
            "status": "cc_by" if lic == "creativeCommon" else "non_autorise",
            "license_raw": lic, "platform": "YouTube",
        })
    return out


def save_candidates(query: str, rows: list[dict]) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")[:50]
    path = ROOT / "research" / f"candidats_{dt.date.today():%Y%m%d}_{slug}.csv"
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(rows)
    sources = load()
    for r in rows:                                   # inscription au registre, statut issu de l'API
        sources.setdefault(r["id"], {k: r[k] for k in ("url", "title", "author", "date", "status", "platform")}
                           | {"added": dt.date.today().isoformat(), "note": f"licence API : {r['license_raw']}"})
    save(sources)
    return path


PERMISSION_TEMPLATE = """Bonjour {author},

Je lance {channel}, un média francophone sur GTA (TikTok et YouTube Shorts) qui analyse le jeu avec
une narration originale. Votre vidéo « {title} » ({url}) illustre parfaitement un sujet que je prépare.

Accepteriez-vous que j'en utilise un court passage (de {tin} à {tout}), dans une vidéo monétisée,
avec votre nom crédité à l'écran et en description ? Je peux vous envoyer la vidéo avant publication.

Une simple réponse « oui, j'autorise » à ce message me suffit. Merci beaucoup !
"""


def permission_message(sid: str, cfg: dict, tin: str = "…", tout: str = "…") -> str:
    src = load().get(sid)
    if not src:
        raise PipelineError(f"Source « {sid} » absente du registre")
    brand = (cfg.get("brand") or {})
    return PERMISSION_TEMPLATE.format(author=src.get("author", ""), channel=brand.get("name") or "ma chaîne",
                                      title=src.get("title", sid), url=src.get("url", ""), tin=tin, tout=tout)

"""
clean_ottoman_battles.py
========================
Nettoyage du dataset brut des batailles ottomanes dans les Balkans (1354–1683).
Données source : Wikidata via SPARQL (outil wikidata_ottoman_extractor.html)

Usage :
    python clean_ottoman_battles.py                              # utilise le fichier par défaut
    python clean_ottoman_battles.py --input mon_fichier.csv      # fichier personnalisé
    python clean_ottoman_battles.py --output resultat.csv        # sortie personnalisée
    python clean_ottoman_battles.py --no-filter-scope            # garder toutes les batailles

Étapes de nettoyage :
    1. Résolution des labels non résolus (QID bruts)
    2. Suppression des batailles hors périmètre ottoman-balkanique
    3. Déduplication (même bataille, plusieurs lieux ou plusieurs part_of)
    4. Résolution des conflits de dates (date approx. vs date précise)
    5. Ajout de la colonne date_precision (day / month / year)
    6. Harmonisation des noms de guerres/campagnes (part_ofLabel)
    7. Rapport de nettoyage
"""

import csv
import argparse
import sys
from collections import defaultdict, Counter
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# 1. CORRECTIONS MANUELLES DE LABELS NON RÉSOLUS
# ──────────────────────────────────────────────────────────────────────────────
# Wikidata retourne parfois un QID brut quand le libellé anglais/français
# n'est pas renseigné. On les corrige ici manuellement.
LABEL_FIXES = {
    # Batailles
    "Q115732142": "Battle of Sântimbru (March 27)",
    "Q136033321": "Battle of Schladming",
    # Lieux
    "Q9333973":   "Sasiv Horn",  # lieu en Ukraine, sera filtré ensuite
}


# ──────────────────────────────────────────────────────────────────────────────
# 2. BATAILLES HORS PÉRIMÈTRE
# ──────────────────────────────────────────────────────────────────────────────
# Ces guerres/campagnes ne concernent pas l'expansion ottomane dans les Balkans.
# Elles ont atterri dans le dataset à cause du filtre géographique large.
# Une bataille est supprimée seulement si elle appartient à l'une de ces guerres
# ET ne contient aucun mot-clé ottoman dans ses champs.
OUT_OF_SCOPE_WARS = {
    "First Anglo-Dutch War",
    "Franco-Dutch War",
    "Aragonese conquest of Naples",
    "War of Chioggia",
    "Venetian–Genoese Wars",
    "Messina revolt",
    "Mediterranean campaign of Alfonso V of Aragon",
    "Moldavian campaign of Tymofiy Khmelnytsky",
}

OTTOMAN_KEYWORDS = [
    "ottoman", "turk", "dardanelles", "gallipoli", "osmanlı"
]


def is_ottoman_related(row: dict) -> bool:
    """Vérifie si une bataille a un lien avec les Ottomans."""
    combined = " ".join([
        row.get("battleLabel", ""),
        row.get("part_ofLabel", ""),
        row.get("locationLabel", ""),
    ]).lower()
    return any(kw in combined for kw in OTTOMAN_KEYWORDS)


# ──────────────────────────────────────────────────────────────────────────────
# 3. HARMONISATION DES NOMS DE GUERRES
# ──────────────────────────────────────────────────────────────────────────────
# Wikidata utilise parfois plusieurs variantes pour la même guerre.
# On les normalise vers une forme canonique.
WAR_HARMONIZATION = {
    "Byzantine–Ottoman wars":          "Byzantine–Ottoman Wars",
    "Hungarian–Ottoman War":           "Ottoman–Hungarian Wars",
    "Venetian–Ottoman Wars":           "Ottoman–Venetian Wars",
    "Cretan War of 1645-1669":         "Cretan War (1645–1669)",
    "Austro-Turkish War of 1663–1664": "Austro-Turkish War (1663–1664)",
    "Polish–Ottoman War of 1683–99":   "Great Turkish War (1683–1699)",
    "Great Turkish War":               "Great Turkish War (1683–1699)",
}


# ──────────────────────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ──────────────────────────────────────────────────────────────────────────────

def date_precision(date_str: str) -> str:
    """
    Indique la précision d'une date ISO (YYYY-MM-DD).
    Wikidata retourne souvent YYYY-01-01 quand seule l'année est connue,
    et YYYY-MM-01 quand seul le mois est connu.
    """
    if not date_str or date_str == "?":
        return "unknown"
    parts = date_str.split("-")
    if len(parts) < 3:
        return "year"
    if parts[1] == "01" and parts[2] == "01":
        return "year"
    if parts[2] == "01":
        return "month"
    return "day"


def location_specificity_score(location: str) -> int:
    """
    Score de spécificité géographique (plus bas = plus précis).
    Utilisé pour choisir la meilleure coordonnée quand plusieurs existent.
    Les noms génériques (mer, fleuve, golfe) sont moins précis.
    """
    generic_terms = [
        "sea", "ocean", "gulf", "river", "ionian", "aegean",
        "adriatic", "mediterranean", "strait", "coast", "waters",
    ]
    loc_lower = location.lower()
    return sum(1 for term in generic_terms if term in loc_lower)


def resolve_labels(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Étape 1 : corriger les QID bruts dans battleLabel et locationLabel."""
    log = []
    for row in rows:
        for field in ("battleLabel", "locationLabel"):
            original = row[field]
            if original in LABEL_FIXES:
                row[field] = LABEL_FIXES[original]
                log.append(f"  Label corrigé : {original!r} → {row[field]!r}")
    return rows, log


def filter_out_of_scope(rows: list[dict], apply: bool) -> tuple[list[dict], list[dict], list[str]]:
    """Étape 2 : supprimer les batailles hors périmètre."""
    if not apply:
        return rows, [], ["  (filtre périmètre désactivé)"]

    kept, removed, log = [], [], []
    for row in rows:
        if row.get("part_ofLabel") in OUT_OF_SCOPE_WARS and not is_ottoman_related(row):
            removed.append(row)
            log.append(f"  Supprimé : {row['date'][:4]} | {row['battleLabel']} | {row['part_ofLabel']}")
        else:
            kept.append(row)
    return kept, removed, log


def deduplicate(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Étape 3 : déduplication.
    Même bataille (wikidata_url) + même date → garder 1 seule ligne,
    en préférant le lieu le plus spécifique.
    Même bataille + même date + plusieurs part_of → fusionner les part_of.
    """
    log = []
    # Grouper par (url, date)
    groups = defaultdict(list)
    for row in rows:
        groups[(row["wikidata_url"], row["date"])].append(row)

    result = []
    for (url, date), group in groups.items():
        if len(group) == 1:
            result.append(group[0])
            continue

        # Plusieurs lignes : choisir le meilleur lieu
        best = min(group, key=lambda r: location_specificity_score(r["locationLabel"]))

        # Fusionner les part_of distincts
        all_parts = sorted({r["part_ofLabel"] for r in group if r["part_ofLabel"]})
        best = dict(best)  # copie pour ne pas modifier l'original
        best["part_ofLabel"] = " | ".join(all_parts) if all_parts else ""

        result.append(best)
        if len(group) > 1:
            log.append(
                f"  Dédupliqué : {date[:4]} {best['battleLabel']} "
                f"({len(group)} lignes → 1, lieu retenu : {best['locationLabel']})"
            )

    return result, log


def resolve_multi_dates(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Étape 4 : résoudre les conflits de dates.
    Même bataille avec date approximative (YYYY-01-01) ET date précise
    → garder uniquement la date précise.
    Même bataille avec plusieurs dates précises distinctes
    → ce sont des événements réellement distincts, on garde tous.
    """
    log = []
    groups = defaultdict(list)
    for row in rows:
        groups[row["wikidata_url"]].append(row)

    result = []
    for url, group in groups.items():
        if len(group) == 1:
            result.append(group[0])
            continue

        precise = [r for r in group if date_precision(r["date"]) == "day"]
        approx  = [r for r in group if date_precision(r["date"]) != "day"]

        if precise:
            precise_dates = {r["date"] for r in precise}
            if len(precise_dates) == 1:
                # Une seule date précise : on la garde, on ignore les approx
                result.append(precise[0])
                if approx:
                    log.append(
                        f"  Date résolue : {precise[0]['battleLabel']} "
                        f"{approx[0]['date']} → {precise[0]['date']}"
                    )
            else:
                # Plusieurs dates précises différentes : événements distincts
                result.extend(precise)
                log.append(
                    f"  Événements distincts conservés : {group[0]['battleLabel']} "
                    f"({', '.join(sorted(precise_dates))})"
                )
        else:
            # Que des dates approx : garder la première
            result.append(approx[0])

    return result, log


def add_date_precision(rows: list[dict]) -> list[dict]:
    """Étape 5 : ajouter la colonne date_precision."""
    for row in rows:
        row["date_precision"] = date_precision(row["date"])
    return rows


def harmonize_wars(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Étape 6 : normaliser les noms de guerres."""
    log = []
    for row in rows:
        original = row.get("part_ofLabel", "")
        normalized = WAR_HARMONIZATION.get(original, original)
        if normalized != original:
            row["part_ofLabel"] = normalized
            log.append(f"  Guerre normalisée : {original!r} → {normalized!r}")
    return rows, log


# ──────────────────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

OUTPUT_FIELDS = [
    "battleLabel", "date", "date_precision", "locationLabel",
    "lat", "lon", "sultan", "sultan_wikidata", "part_ofLabel", "wikidata_url",
]


def clean(input_path: str, output_path: str, filter_scope: bool = True) -> None:
    # Lecture
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n_raw = len(rows)
    print(f"\n{'='*60}")
    print(f"  NETTOYAGE : {Path(input_path).name}")
    print(f"{'='*60}")
    print(f"\n  Lignes brutes : {n_raw}\n")

    # Étape 1 — Labels
    print("── Étape 1 : Résolution des labels non résolus")
    rows, log1 = resolve_labels(rows)
    print("\n".join(log1) if log1 else "  Aucun label à corriger.")

    # Étape 2 — Périmètre
    print("\n── Étape 2 : Filtre périmètre ottoman-balkanique")
    rows, removed, log2 = filter_out_of_scope(rows, filter_scope)
    print("\n".join(log2) if log2 else "  Aucune bataille supprimée.")
    print(f"  → {len(removed)} batailles supprimées")

    # Étape 3 — Déduplication
    print("\n── Étape 3 : Déduplication")
    rows, log3 = deduplicate(rows)
    print("\n".join(log3) if log3 else "  Aucun doublon détecté.")

    # Étape 4 — Dates
    print("\n── Étape 4 : Résolution des conflits de dates")
    rows, log4 = resolve_multi_dates(rows)
    print("\n".join(log4) if log4 else "  Aucun conflit de dates.")

    # Étape 5 — Précision des dates
    print("\n── Étape 5 : Ajout colonne date_precision")
    rows = add_date_precision(rows)
    prec = Counter(r["date_precision"] for r in rows)
    print(f"  day: {prec['day']}  month: {prec['month']}  year: {prec['year']}")

    # Étape 6 — Harmonisation guerres
    print("\n── Étape 6 : Harmonisation des noms de guerres")
    rows, log6 = harmonize_wars(rows)
    unique_log6 = sorted(set(log6))
    print("\n".join(unique_log6) if unique_log6 else "  Aucune harmonisation nécessaire.")

    # Export
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    # Résumé final
    print(f"\n{'='*60}")
    print(f"  RÉSUMÉ")
    print(f"{'='*60}")
    print(f"  Brut    : {n_raw:>4} lignes")
    print(f"  Nettoyé : {len(rows):>4} lignes  (−{n_raw - len(rows)})")
    print(f"\n  Distribution par sultan :")
    for sultan, count in sorted(Counter(r["sultan"] for r in rows).items(), key=lambda x: -x[1]):
        bar = "█" * (count // 2)
        print(f"    {sultan:<20} {count:>3}  {bar}")
    print(f"\n  Fichier écrit : {output_path}\n")


# ──────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nettoyage du dataset ottoman balkans")
    parser.add_argument(
        "--input", "-i",
        default="ottoman_balkans_battles_raw.csv",
        help="Fichier CSV brut (défaut : ottoman_balkans_battles_raw.csv)",
    )
    parser.add_argument(
        "--output", "-o",
        default="ottoman_balkans_battles_clean.csv",
        help="Fichier CSV nettoyé (défaut : ottoman_balkans_battles_clean.csv)",
    )
    parser.add_argument(
        "--no-filter-scope",
        action="store_false",
        dest="filter_scope",
        help="Désactiver le filtre périmètre (garder toutes les batailles)",
    )
    args = parser.parse_args()

    try:
        clean(args.input, args.output, args.filter_scope)
    except FileNotFoundError as e:
        print(f"\nErreur : fichier introuvable — {e}", file=sys.stderr)
        sys.exit(1)

# -*- coding: utf-8 -*-
"""Module de correction des expressions regulieres dans les fichiers Python."""

import re
import json
import logging
from pathlib import Path
from typing import List

# === Configuration
IGNORES = {"__pycache__", ".venv", "env", "venv", "site-packages"}
rapport: List[str] = []

# Expression reguliere : re.compile("(a|b|c)")  [abc]
alternance_pattern = re.compile(
    r're\.compile\(\s*["\']\((?:[a-zA-Z0-9]\|)+[a-zA-Z0-9]\)["\']\s*\)'
)

logging.basicConfig(level=logging.INFO, format="[CORRECTION] %(message)s")

# === Fonctions
def transformer_alternance(expr: re.Match) -> str:
    """Transforme une alternance (a|b|c) en classe [abc]."""
    contenu = expr.group(0)
    lettres = re.findall(r'\((.*?)\)', contenu)[0].split('|')
    compact = f"[{''.join(lettres)}]"
    return re.sub(r'\(.*?\)', compact, contenu)

def corriger_fichier(filepath: Path) -> int:
    """Corrige les expressions regulieres dans un fichier Python."""
    try:
        contenu = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logging.warning(f"Encodage non pris en charge : {filepath}")
        return 0
    except Exception as err:
        logging.error(f"Erreur lecture : {filepath}  {type(err).__name__}")
        return 0

    matches = list(alternance_pattern.finditer(contenu))
    if not matches:
        return 0

    nouveau_contenu = alternance_pattern.sub(transformer_alternance, contenu)

    try:
        filepath.write_text(nouveau_contenu, encoding="utf-8")
        rapport.append(str(filepath))
        logging.info(f"Alternance corrigee dans : {filepath} ({len(matches)} remplacement(s))")
        return len(matches)
    except Exception as err:
        logging.error(f"Erreur ecriture : {filepath}  {type(err).__name__}")
        return 0

def parcourir_dossier(dossier: Path) -> int:
    """Parcourt recursivement le dossier pour corriger les fichiers .py."""
    total_corrections = 0
    for path in dossier.rglob("*.py"):
        if any(ignored in path.parts for ignored in IGNORES):
            continue
        total_corrections += corriger_fichier(path)
    return total_corrections

def afficher_rapport() -> None:
    """Affiche le rapport des fichiers corrigés."""
    if rapport:
        logging.info("\nFichiers corriges :")
        for f in rapport:
            logging.info(f" - {f}")
    else:
        logging.info("Aucune correction necessaire.")

def sauvegarder_rapport_json(dossier: Path) -> None:
    """Sauvegarde le rapport dans un fichier JSON."""
    if not rapport:
        return
    rapport_path = dossier / "rapport_corrections.json"
    try:
        with rapport_path.open("w", encoding="utf-8") as f:
            json.dump({"corriges": rapport}, f, indent=2, ensure_ascii=False)
        logging.info(f"Rapport JSON sauvegarde : {rapport_path}")
    except Exception as e:
        logging.error(f"Erreur sauvegarde JSON : {e}")

def corriger_expressions(dossier: Path) -> None:
    """Fonction principale à appeler depuis assistant_pdg."""
    logging.info(f"Analyse des expressions regulieres dans : {dossier}")
    try:
        total = parcourir_dossier(dossier)
        afficher_rapport()
        sauvegarder_rapport_json(dossier)
        logging.info(f"Total de corrections effectuees : {total}")
    except Exception as e:
        logging.error(f"Erreur inattendue : {type(e).__name__} - {e}")


# Orchestration centralisée
from assistant_pdg import AssistantPDG

def run():
    print("Module exécuté via AssistantPDG")

AssistantPDG.register("chemin_universel", run)

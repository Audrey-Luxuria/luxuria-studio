# -*- coding: utf-8 -*-
"""Extraction automatique de vocabulaire depuis les scripts Python - Luxuria Studio"""

import os
import re
import logging
from pathlib import Path
from typing import Set

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DICTIONNAIRE_PATH = BASE_DIR / "dictionnaire_personnel.txt"
IGNORES = {"__pycache__", ".venv", "env", "venv", "site-packages"}

logging.basicConfig(level=logging.INFO, format="[DICTIONNAIRE] %(message)s")

def charger_dictionnaire() -> Set[str]:
    """Charge les mots deja enregistrés dans le dictionnaire."""
    if DICTIONNAIRE_PATH.exists():
        return set(DICTIONNAIRE_PATH.read_text(encoding="utf-8").splitlines())
    return set()

def extraire_mots_depuis_fichier(fichier_cible: Path) -> Set[str]:
    """Extrait les mots de trois lettres ou plus depuis un fichier source."""
    try:
        contenu = fichier_cible.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        logging.warning("Erreur lecture : {} ({})".format(fichier_cible, type(err).__name__))
        return set()

    # Expression reguliere etendue pour inclure lettres accentuees
    mots_detectes = re.findall(r"\b[\wA-y]{3,}\b", contenu)
    return set(mots_detectes)

def collecter_fichiers_python() -> Set[Path]:
    """Collecte tous les fichiers .py à analyser, sauf ce script et les dossiers ignorés."""
    fichiers = set()
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORES]
        for file in files:
            if file.endswith(".py") and file != Path(__file__).name:
                fichiers.add(Path(root) / file)
    return fichiers

def mettre_a_jour_dictionnaire() -> None:
    """Analyse les fichiers et met à jour le dictionnaire personnel."""
    fichiers_python = collecter_fichiers_python()
    mots_enregistres = charger_dictionnaire()
    nouveaux_mots: Set[str] = set()

    for fichier_source in fichiers_python:
        mots_du_fichier = extraire_mots_depuis_fichier(fichier_source)
        mots_inconnus = mots_du_fichier - mots_enregistres
        nouveaux_mots.update(mots_inconnus)

    if nouveaux_mots:
        try:
            with open(DICTIONNAIRE_PATH, "a", encoding="utf-8") as dict_file:
                for mot in sorted(nouveaux_mots):
                    dict_file.write(mot + "\n")
            logging.info("{} nouveau(x) mot(s) ajoute(s) au dictionnaire.".format(len(nouveaux_mots)))
        except OSError as err:
            logging.error("Erreur ecriture dictionnaire ({})".format(type(err).__name__))
    else:
        logging.info("Aucun nouveau mot a ajouter. Le dictionnaire est a jour.")

def main() -> None:
    logging.info("Analyse des fichiers Python en cours...")
    mettre_a_jour_dictionnaire()

# Bloc __main__ supprimé pour modularisation

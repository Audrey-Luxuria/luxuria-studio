# -*- coding: utf-8 -*-
"""Luxuria SQL Manager  Desactive les appels SQL dans les scripts Python."""

import re
import logging
from pathlib import Path

# === Dossier racine du projet
BASE_DIR = Path(__file__).resolve().parent

# === Expressions a desactiver
SQL_IMPORTS = [
    r'^import\s+sqlite3',
    r'^import\s+mysql.*',
    r'^import\s+psycopg2.*'
]

SQL_CALLS = [
    r'\.execute\(',
    r'\.connect\(',
    r'\.cursor\(',
    r'\.fetch.*\('
]

# === Rapport des fichiers modifiés
fichiers_modifies = []

def nettoyer_sql(filepath: Path) -> None:
    """Commente les imports et appels SQL dans un fichier Python."""
    try:
        contenu = filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        logging.warning(f"Fichier introuvable : {filepath}")
        return
    except PermissionError:
        logging.warning(f"Acces refuse : {filepath}")
        return
    except UnicodeDecodeError:
        logging.warning(f"Encodage non pris en charge : {filepath}")
        return

    original = contenu

    for pattern in SQL_IMPORTS:
        contenu = re.sub(
            pattern,
            lambda m: f"# {m.group(0)}  # SQL desactive",
            contenu,
            flags=re.MULTILINE
        )

    for pattern in SQL_CALLS:
        contenu = re.sub(
            pattern,
            lambda m: f"# {m.group(0)}  # SQL desactive",
            contenu,
            flags=re.MULTILINE
        )

    if contenu != original:
        try:
            filepath.write_text(contenu, encoding="utf-8")
            fichiers_modifies.append(str(filepath))
        except OSError as e:
            logging.error(f"Erreur ecriture fichier {filepath.name} : {e}")

def parcourir_dossier(dossier: Path) -> None:
    """Parcourt tous les fichiers .py du dossier et nettoie le SQL."""
    for path in dossier.rglob("*.py"):
        if path.resolve() != Path(__file__).resolve():
            nettoyer_sql(path)

def afficher_rapport() -> None:
    """Affiche les fichiers modifiés ou un message si aucun n'est touché."""
    if fichiers_modifies:
        logging.info(" Fichiers modifies :")
        for f in fichiers_modifies:
            logging.info(f" - {f}")
    else:
        logging.info(" Aucun fichier contenant du SQL detecte.")

# === Fonction orchestrable depuis assistant_pdg.py
def desactiver_sql_global() -> None:
    """Desactive les appels SQL dans tous les scripts du projet."""
    logging.info(" Desactivation des requetes SQL en cours...")
    parcourir_dossier(BASE_DIR)
    afficher_rapport()

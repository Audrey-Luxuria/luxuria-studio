# -*- coding: utf-8 -*-
"""Audit et correction des clauses 'except :' et des imports racines dans les fichiers Python."""

import os
import re
import logging
from pathlib import Path
from typing import List
from assistant_pdg import AssistantPDG

# === Configuration
IGNORES = {"__pycache__", ".venv", "env", "venv", "site-packages"}
EXCEPT_PATTERN = re.compile(r'^\s*except\s*:\s*$', re.MULTILINE)
RACINE_MODULES = ['charger_clients', 'run_audit', 'run_diagnostic', 'start_gui']
IMPORT_PATTERN = re.compile(rf'^import\s+({"|".join(RACINE_MODULES)})\b', re.MULTILINE)

rapport_except: List[str] = []
rapport_imports: List[str] = []

logging.basicConfig(level=logging.INFO, format="[AUDIT] %(message)s")

def nettoyer_typographie(contenu: str) -> str:
    return contenu.replace('\u00A0', ' ')

def corriger_exceptions(filepath: str, contenu: str) -> str:
    if EXCEPT_PATTERN.search(contenu):
        contenu = EXCEPT_PATTERN.sub("except Exception:", contenu)
        rapport_except.append(filepath)
        logging.info(f"  Clause 'except:' corrigée dans : {filepath}")
    return contenu

def corriger_imports(filepath: str, contenu: str) -> str:
    if IMPORT_PATTERN.search(contenu):
        header = (
            "import sys\nimport os\n"
            "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n\n"
        )
        contenu = header + contenu
        rapport_imports.append(filepath)
        logging.info(f"  Import racine corrigé dans : {filepath}")
    return contenu

def traiter_fichier(filepath: str, dry_run: bool = False) -> None:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenu = f.read()
    except (OSError, UnicodeDecodeError) as err:
        logging.warning(f"  Erreur lecture : {filepath} ({type(err).__name__})")
        return

    contenu = nettoyer_typographie(contenu)
    original = contenu

    contenu = corriger_exceptions(filepath, contenu)
    contenu = corriger_imports(filepath, contenu)

    if contenu != original and not dry_run:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(contenu)
        except (OSError, IOError) as err:
            logging.error(f"  Erreur écriture : {filepath} ({type(err).__name__})")

def parcourir_dossier(dossier: str, dry_run: bool = False) -> None:
    for root, dirs, files in os.walk(dossier):
        dirs[:] = [d for d in dirs if d not in IGNORES]
        for filename in files:
            if filename.endswith(".py") and filename != os.path.basename(__file__):
                chemin = os.path.join(root, filename)
                traiter_fichier(chemin, dry_run=dry_run)

def afficher_rapport() -> None:
    if rapport_except:
        logging.info("\n Clauses 'except:' corrigées :")
        for f in rapport_except:
            logging.info(f" - {f}")
    else:
        logging.info(" Aucune clause 'except:' à corriger.")

    if rapport_imports:
        logging.info("\n Imports racine corrigés :")
        for f in rapport_imports:
            logging.info(f" - {f}")
    else:
        logging.info(" Aucun import racine à corriger.")

# === Orchestration centralisée
def run():
    dossier = str(Path(__file__).resolve().parent)
    logging.info(f"🔍 Audit en cours dans : {dossier}")
    parcourir_dossier(dossier, dry_run=False)
    afficher_rapport()

AssistantPDG.register("correcteur_imports", run)

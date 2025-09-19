# -*- coding: utf-8 -*-
"""Module de localisation du fichier logo.png - Luxuria Studio"""

import sys
import logging
from pathlib import Path
from assistant_pdg import AssistantPDG  # ✅ Orchestrateur principal

# === Configuration du logging
logging.basicConfig(level=logging.INFO, format="[LOGO] %(message)s")

# === Répertoire de base
BASE_DIR = Path(__file__).resolve().parent

def get_resource_path(filename: str) -> Path:
    """
    Retourne le chemin absolu vers une ressource,
    compatible avec PyInstaller sans accès direct à _MEIPASS.
    """
    base = getattr(sys, "_MEIPASS", BASE_DIR)
    return Path(base) / filename

def verifier_logo_existant() -> Path | None:
    """
    Vérifie si le fichier logo.png est présent et retourne son chemin.
    """
    logo_path = get_resource_path("logo.png")
    if logo_path.is_file():
        logging.info(f"✅ Fichier trouvé : {logo_path}")
        return logo_path
    else:
        logging.warning("❌ Fichier logo.png introuvable.")
        return None

# === Orchestration centralisée
def run():
    verifier_logo_existant()

AssistantPDG.register("localisation_logo", run)

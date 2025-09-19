# -*- coding: utf-8 -*-
"""Configuration centrale pour Luxuria Studio."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from assistant_pdg import AssistantPDG  # ✅ Correction ici

# === Initialisation
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.is_file():
    logging.warning(f"[CONFIG] Fichier .env introuvable à la racine : {ENV_PATH}")
load_dotenv(dotenv_path=ENV_PATH)

# === Logging
logging.basicConfig(level=logging.INFO, format="[CONFIG] %(message)s")

# === Répertoires
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
PROJECT_ROOT = Path(__file__).resolve().parent
MODULES_PATH = PROJECT_ROOT / "luxuria_modules"
HTML_PATH = PROJECT_ROOT / "interface"

# === Variables d'environnement
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_HASH = os.getenv("ADMIN_HASH")
SECRET_KEY = os.getenv("SECRET_KEY")

# === Fonctions utilitaires
def afficher_config() -> None:
    """Affiche les chemins et variables de configuration."""
    logging.info(f" BASE_DIR  : {BASE_DIR}")
    logging.info(f" DATA_DIR  : {DATA_DIR}")
    logging.info(f" MODEL_DIR : {MODEL_DIR}")

    logging.info(f" ADMIN_ID     : {ADMIN_ID or '❌ non défini'}")
    logging.info(f" ADMIN_HASH   : {ADMIN_HASH or '❌ non défini'}")
    logging.info(f" SECRET_KEY   : {SECRET_KEY or '❌ non défini'}")

def get_config() -> dict:
    """Retourne la configuration sous forme de dictionnaire."""
    return {
        "ADMIN_ID": ADMIN_ID,
        "ADMIN_HASH": ADMIN_HASH,
        "SECRET_KEY": SECRET_KEY,
        "FILES": {
            "journal": BASE_DIR / "journal.log",
            "ca": BASE_DIR / "ca.json",
            "keys": BASE_DIR / "keys.json",
            "clients": BASE_DIR / "clients",
            "conversations": BASE_DIR / "conversations.json"
        }
    }

def verifier_chemins() -> None:
    """Vérifie l'existence des dossiers essentiels."""
    for path in [DATA_DIR, MODEL_DIR]:
        if not path.exists():
            logging.warning(f"📁 Dossier manquant : {path}")
        else:
            logging.info(f"📁 Dossier présent : {path}")

# === Orchestration
def main() -> None:
    logging.info("🔧 Chargement de la configuration Luxuria...")
    afficher_config()
    verifier_chemins()

# === Orchestration centralisée
def run():
    main()

# ✅ Vérifie que la méthode register existe avant de l'appeler
if hasattr(AssistantPDG, "register"):
    AssistantPDG.register("config", run)
else:
    logging.warning("[CONFIG] AssistantPDG ne contient pas de méthode 'register'.")

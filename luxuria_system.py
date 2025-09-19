# -*- coding: utf-8 -*-
"""Orchestrateur système Luxuria IA"""

import logging
import subprocess
import sys
from pathlib import Path
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration du logging
BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "log_activites.txt"

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# === Modules à orchestrer
MODULES = {
    "checker": BASE_DIR / "luxuria_modules_checker.py",
    "organizer": BASE_DIR / "luxuria_modules_organizer.py",
    "audit": BASE_DIR / "audit_python_script.py"
}

# === Exécution sécurisée d’un module
def executer_module(nom: str, chemin: Path) -> None:
    if not chemin.exists():
        logging.warning(f"[{nom}] Script introuvable : {chemin.name}")
        return
    try:
        logging.info(f"[{nom}] Démarrage...")
        subprocess.run([sys.executable, str(chemin)], check=True)
        logging.info(f"[{nom}] Terminé avec succès.")
    except subprocess.CalledProcessError as e:
        logging.error(f"[{nom}] Échec d'exécution : {e}")

# === Orchestration complète
def orchestrer_luxuria() -> None:
    logging.info("Orchestration Luxuria IA lancée")
    for nom, chemin in MODULES.items():
        executer_module(nom, chemin)
    logging.info("Orchestration terminée")

# === Étape de vérification technique
def executer_verificateur() -> None:
    verificateur_path = BASE_DIR / "luxuria_verificateur.py"
    if not verificateur_path.exists():
        logging.warning(f"[verificateur] Fichier introuvable : {verificateur_path.name}")
        return
    logging.info("[verificateur] Lancement du vérificateur Luxuria...")
    try:
        subprocess.run([sys.executable, str(verificateur_path)], check=True)
        logging.info("[verificateur] Vérification terminée avec succès.")
    except subprocess.CalledProcessError as e:
        logging.error(f"[verificateur] Échec de la vérification : {e}")

# === Point d’entrée principal
def main() -> None:
    orchestrer_luxuria()
    executer_verificateur()

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_system", run)

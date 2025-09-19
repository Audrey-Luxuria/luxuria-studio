# -*- coding: utf-8 -*-
"""Scanner de fichiers Python - Luxuria IA"""

import logging
from pathlib import Path
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Répertoire de base
BASE_DIR = Path(__file__).resolve().parent

def scanner_fichiers(source: Path) -> None:
    logging.info("Scan des fichiers Python en cours...\n")

    for fichier in source.glob("**/*"):
        if fichier.suffix in [".py", ".pyc"]:
            try:
                fichier.stat()  # Vérifie l'accessibilité
                logging.info(f"Accessible : {fichier.relative_to(source)}")
            except Exception as e:
                logging.warning(f"Bloqué : {fichier.relative_to(source)}  {e}")

# === Point d’entrée modulaire
def main() -> None:
    scanner_fichiers(BASE_DIR)

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("scanner", run)

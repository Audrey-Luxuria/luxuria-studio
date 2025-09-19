# -*- coding: utf-8 -*-
"""Orchestrateur de correction - Luxuria Studio"""

import subprocess
import logging
from pathlib import Path
from typing import List
from assistant_pdg import AssistantPDG

# === Configuration
logging.basicConfig(level=logging.INFO, format="[STRUCTURE] %(message)s")

class CorrecteurStructure:
    def __init__(self, base_dir: Path, scripts: List[str]):
        self.base_dir = base_dir.resolve()
        self.scripts = scripts

    @staticmethod
    def lancer_script(script_path: Path, dry_run: bool = False) -> bool:
        if not script_path.exists():
            logging.warning(f"Script introuvable : {script_path.name}")
            return False

        logging.info(f"📂 Exécution du script : {script_path.name}")
        if dry_run:
            logging.info("🔍 Simulation uniquement")
            return True

        try:
            subprocess.run(["python", str(script_path)], check=True)
            logging.info(f"✅ Script terminé avec succès : {script_path.name}")
            return True
        except subprocess.CalledProcessError as error:
            logging.error(f"❌ Erreur d'exécution : {script_path.name} ({error})")
            return False

    def corriger(self, dry_run: bool = False, selection: List[str] = None) -> None:
        logging.info("🧠 Démarrage du correcteur de structure")
        scripts_cibles = selection if selection else self.scripts
        total = len(scripts_cibles)
        succes = 0

        for nom_script in scripts_cibles:
            chemin_script = self.base_dir / nom_script
            if self.lancer_script(chemin_script, dry_run=dry_run):
                succes += 1

        logging.info(f"📊 Résumé : {succes} sur {total} script(s) exécutés avec succès")
        logging.info("🏁 Correction terminée")

# === Orchestration centralisée
def run():
    dossier = Path(__file__).resolve().parent
    scripts = [
        "correcteur_imports.py",
        "correcteur_eval.py",
        "correcteur_indentation.py",
        "correcteur_os.py",
        "correcteur_print_logging.py",
        "correcteur_ASCII_syntaxe.py"
    ]
    correcteur = CorrecteurStructure(dossier, scripts)
    correcteur.corriger(dry_run=False)

AssistantPDG.register("correcteur_structure", run)

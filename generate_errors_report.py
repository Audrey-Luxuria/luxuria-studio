# -*- coding: utf-8 -*-
"""Analyse des erreurs dans les scripts Python - Luxuria Studio"""

import os
import json
import logging
import runpy
from pathlib import Path
from datetime import datetime
from assistant_pdg import AssistantPDG

# === Configuration
logging.basicConfig(level=logging.INFO, format="[ERRORS] %(message)s")
BASE_PATH = Path(__file__).resolve().parent
THIS_FILE = Path(__file__).name
EXCLUDED_FILES = {THIS_FILE, "assistant_pdg.py"}

def scan_scripts_and_log_errors() -> dict:
    """Exécute tous les scripts Python du dossier courant (sauf exclusions) et retourne un rapport d'erreurs."""
    report = {}
    py_files = [f for f in os.listdir(BASE_PATH) if f.endswith(".py") and f not in EXCLUDED_FILES]

    for file_name in py_files:
        file_path = BASE_PATH / file_name
        logging.info(f"📂 Exécution du script : {file_name}")
        try:
            runpy.run_path(str(file_path))
            report[file_name] = {"status": "OK", "error": None}
            logging.info(f"✅ Script exécuté sans erreur : {file_name}")
        except Exception as e:
            report[file_name] = {
                "status": "ERROR",
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            logging.warning(f"❌ Erreur dans {file_name} : {type(e).__name__} - {e}")

    return report

def save_report(report: dict) -> Path:
    """Sauvegarde le rapport d'erreurs dans un fichier JSON horodaté."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = BASE_PATH / f"error_report_{timestamp}.json"
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        logging.info(f"📄 Rapport généré : {output_file.name}")
    except Exception as e:
        logging.error(f"❌ Échec de l'écriture du rapport : {type(e).__name__} - {e}")
    return output_file

def transmettre_rapport(report_path: Path) -> None:
    """Transmet le rapport à assistant_pdg via son interface dédiée."""
    try:
        AssistantPDG.register("error_report", lambda: logging.info(f"📨 Rapport disponible : {report_path.name}"))
        logging.info("✅ Rapport enregistré dans l'orchestrateur.")
    except Exception as e:
        logging.error(f"❌ Échec de l'enregistrement du rapport : {e}")

# === Orchestration centralisée
def run():
    rapport = scan_scripts_and_log_errors()
    fichier = save_report(rapport)
    transmettre_rapport(fichier)

AssistantPDG.register("generate_errors_report", run)

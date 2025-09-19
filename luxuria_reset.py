# -*- coding: utf-8 -*-
"""Réinitialisation des modules Luxuria Studio"""

import shutil
import logging
from pathlib import Path
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Dossiers de base
BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR / "modules"
LOG_DIR = BASE_DIR / "logs"

# === Nettoyage des anciens dossiers
for path in [MODULE_DIR, LOG_DIR]:
    if path.exists():
        shutil.rmtree(path)
        logging.info(f"Dossier supprimé : {path}")

# === Reconstruction des dossiers
MODULE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.info("Dossiers recréés.")

# === Modules à créer
modules = {
    "run_audit.py": [
        "import logging",
        "",
        "def run_audit():",
        "    logging.info(\"[Audit] Vérification des modules...\")"
    ],
    "run_diagnostic.py": [
        "import logging",
        "",
        "def run_diagnostic():",
        "    logging.info(\"[Diagnostic] Analyse du système...\")"
    ],
    "start_gui.py": [
        "import logging",
        "# import main  # À définir ailleurs",
        "",
        "def start_gui():",
        "    logging.info(\"[GUI] Lancement de l'interface...\")",
        "    # main()  # Appel à définir"
    ]
}

for name, lines in modules.items():
    path = MODULE_DIR / name
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logging.info(f"Module créé : {name}")

# === Log initial
log_path = LOG_DIR / "log_activites.txt"
with log_path.open("w", encoding="utf-8") as f:
    f.write("=== Journal d'activités Luxuria ===\n")
logging.info(f"Journal initial créé : {log_path}")

# === Fin
logging.info("Luxuria réinitialisé. Tu peux lancer l'orchestrateur.")

# === Fonction main modulaire
def main():
    """Point d'entrée optionnel pour Luxuria Reset."""
    pass

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_reset", run)

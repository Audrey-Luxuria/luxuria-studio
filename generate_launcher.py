# -*- coding: utf-8 -*-
"""Générateur du lanceur principal Luxuria Studio"""

import re
import logging
from pathlib import Path
from typing import Dict, List

# === Configuration du logging
logging.basicConfig(level=logging.INFO, format="[LAUNCHER] %(message)s")

# === Répertoires et fichiers
BASE_DIR = Path(__file__).resolve().parent
MAIN_PATH = BASE_DIR / "main.py"
BAT_PATH = BASE_DIR / "Luxuria.bat"

EXCLUSIONS = {"main.py", "assistant_pdg.py"}
PY_FILES = [
    f for f in BASE_DIR.glob("*.py")
    if f.name not in EXCLUSIONS and "generate" not in f.name and "injecteur" not in f.name
]
HTML_FILES = list(BASE_DIR.glob("*.html"))

# === Extraction des fonctions d’un module
def extraire_fonctions(path: Path) -> List[str]:
    try:
        contenu = path.read_text(encoding="utf-8")
        return re.findall(r"^def (\w+)\(", contenu, re.MULTILINE)
    except Exception as e:
        logging.warning(f"Erreur lecture {path.name} : {e}")
        return []

# === Génération du fichier main.py
def generer_main(modules: Dict[str, List[str]], html_files: List[Path]) -> None:
    lignes = [
        "# -*- coding: utf-8 -*-",
        "import logging",
        "from assistant_pdg import app, AssistantPDG",
        "",
        "logging.basicConfig(level=logging.INFO)",
        "",
        "def main():",
        "    logging.info('[Luxuria] Serveur en cours de lancement...')",
        "    AssistantPDG.coordonner()",
        ""
    ]

    if modules:
        lignes.append("    logging.info('Modules détectés :')")
        for nom in modules:
            lignes.append(f"    logging.info(' - {nom}')")

    if html_files:
        lignes.append("    logging.info('Fichiers HTML détectés :')")
        for html in html_files:
            lignes.append(f"    logging.info(' - {html.name}')")

    lignes.append("")
    lignes.append("    app.run(debug=False, port=5000, use_reloader=False, debug=False, use_reloader=False, debug=False, use_reloader=False, debug=False, use_reloader=False)")
    lignes.append("")
    lignes.append("if __name__ == '__main__':")
    lignes.append("    main()")

    MAIN_PATH.write_text("\n".join(lignes), encoding="utf-8")
    logging.info(f"main.py généré avec succès à : {MAIN_PATH.resolve()}")

# === Génération du fichier Luxuria .bat
def generer_bat() -> None:
    lignes = [
        "@echo off",
        "cd /d \"%~dp0\"",
        "echo [Luxuria] Initialisation...",
        "python main.py",
        "pause"
    ]
    BAT_PATH.write_text("\n".join(lignes), encoding="utf-8")
    logging.info(f"Luxuria.bat généré avec succès à : {BAT_PATH.resolve()}")

# === Analyse globale et génération
def analyser_et_generer() -> None:
    modules = {}
    for py in PY_FILES:
        nom_module = py.stem
        fonctions = extraire_fonctions(py)
        if fonctions:
            modules[nom_module] = fonctions

    generer_main(modules, HTML_FILES)
    generer_bat()

# === Point d’entrée
# Bloc __main__ supprimé pour modularisation

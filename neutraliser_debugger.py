# -*- coding: utf-8 -*-
"""Neutralisation du debugger Flask dans tous les scripts Luxuria"""

from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
EXCLUSIONS = {"__init__.py", "requirements.py", "config.py"}

def corriger_app_run(contenu: str) -> str:
    pattern = r"app\.run\((.*?)\)"
    matches = re.finditer(pattern, contenu, re.DOTALL)

    for match in matches:
        params = match.group(1)
        original_call = match.group(0)

        # Nettoyage des paramètres
        new_params = params

        # Remplace debug=True par debug=False
        new_params = re.sub(r"debug\s*=\s*True", "debug=False", new_params)

        # Ajoute debug=False si absent
        if "debug=" not in new_params:
            new_params += ", debug=False"

        # Ajoute use_reloader=False si absent
        if "use_reloader=" not in new_params:
            new_params += ", use_reloader=False"

        corrected_call = f"app.run({new_params}, debug=False, use_reloader=False, debug=False, use_reloader=False, debug=False, use_reloader=False, debug=False, use_reloader=False)"
        contenu = contenu.replace(original_call, corrected_call)

    return contenu

def traiter_fichier(script_path: Path) -> None:
    if script_path.name in EXCLUSIONS:
        return

    contenu = script_path.read_text(encoding="utf-8")
    nouveau_contenu = corriger_app_run(contenu)

    if contenu != nouveau_contenu:
        script_path.write_text(nouveau_contenu, encoding="utf-8")
        print(f"✅ Debug désactivé dans : {script_path.relative_to(BASE_DIR)}")
    else:
        print(f"⏩ Aucun changement : {script_path.relative_to(BASE_DIR)}")

def corriger_tous_les_scripts():
    print("🔍 Analyse de tous les fichiers Python du projet...")
    for script in BASE_DIR.rglob("*.py"):
        traiter_fichier(script)

# Bloc __main__ supprimé pour modularisation

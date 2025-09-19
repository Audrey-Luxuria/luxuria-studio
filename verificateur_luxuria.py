# -*- coding: utf-8 -*-
"""Vérificateur syntaxique des modules Luxuria"""

import ast
import logging
from pathlib import Path
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration du journal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Dossier racine et scripts à analyser
BASE_DIR = Path(__file__).resolve().parent
scripts = [f for f in BASE_DIR.glob("*.py") if f.name != Path(__file__).name]

# === Analyse syntaxique
def extraire_imports(tree: ast.AST) -> list[str]:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.extend(alias.name for alias in node.names)
    return imports

def extraire_noms_utilises(tree: ast.AST) -> set[str]:
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

def detecter_shadowing(noms: list[str]) -> set[str]:
    return {nom for nom in noms if noms.count(nom) > 1}

# === Analyse d’un script
def analyser_script(script_path: Path) -> None:
    logging.info(f"\nAnalyse de : {script_path.name}")
    try:
        contenu = script_path.read_text(encoding="utf-8")
        tree = ast.parse(contenu)
    except Exception as e:
        logging.error(f"Erreur de lecture ou de parsing : {e}")
        return

    # Chemin universel
    if "Path(__file__).resolve().parent" in contenu:
        logging.info("Chemin universel détecté")
    else:
        logging.warning("Chemin universel manquant")

    # Bloc d’exécution autonome
    if "__name__" in contenu and "__main__" in contenu:
        logging.info("Bloc if __name__ == '__main__' détecté")
    else:
        logging.warning("Bloc d’exécution autonome manquant")

    # Imports inutilisés
    imports = extraire_imports(tree)
    noms_utilises = extraire_noms_utilises(tree)
    imports_inutiles = [imp for imp in imports if imp not in noms_utilises]
    if imports_inutiles:
        logging.warning(f"Imports inutilisés : {', '.join(imports_inutiles)}")
    else:
        logging.info("Aucun import inutile")

    # Shadowing
    noms = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
    doublons = detecter_shadowing(noms)
    if doublons:
        logging.warning(f"Variables réutilisées plusieurs fois : {', '.join(sorted(doublons))}")
    else:
        logging.info("Pas de shadowing détecté")

# === Analyse globale
def analyser_tous_les_scripts() -> None:
    for script in scripts:
        analyser_script(script)

# === Point d’entrée modulaire
def main() -> None:
    analyser_tous_les_scripts()

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("verificateur_luxuria", run)

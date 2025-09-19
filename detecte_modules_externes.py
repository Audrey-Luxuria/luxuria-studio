# -*- coding: utf-8 -*-
"""Detection et installation automatique des modules externes - Luxuria Studio"""

import os
import sys
import importlib.util
import logging
import subprocess
import argparse
from pathlib import Path
from typing import Union, Dict, List, Set

# Configuration
BASE_DIR = Path(__file__).resolve().parent
external_modules_by_file: Dict[str, List[str]] = {}
modules_to_install: Set[str] = set()

logging.basicConfig(level=logging.INFO, format="[MODULES] %(message)s")

def extract_imports(source_file: Union[str, Path]) -> List[str]:
    """Extrait les noms de modules importés dans un fichier Python."""
    try:
        with open(str(source_file), "r", encoding="utf-8") as file:
            return [
                line.split()[1].split(".")[0]
                for line in file
                if line.strip().startswith(("import ", "from "))
                and len(line.split()) >= 2
            ]
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError):
        return []

def is_external_module(module_name: str) -> bool:
    """Determine si un module est externe (non standard)."""
    if module_name in sys.builtin_module_names:
        return False
    spec = importlib.util.find_spec(module_name)
    return spec is None or "site-packages" in (spec.origin or "")

def scan_directory_for_externals(target_dir: Union[str, Path]) -> None:
    """Parcourt les fichiers .py et detecte les modules externes utilises."""
    for root, _, files in os.walk(str(target_dir)):
        for file_name in files:
            if file_name.endswith(".py") and file_name != "__init__.py":
                file_path = os.path.join(root, file_name)
                imported = extract_imports(file_path)
                externals = [name for name in imported if is_external_module(name)]
                if externals:
                    external_modules_by_file[file_path] = sorted(set(externals))
                    modules_to_install.update(externals)

def installer_modules(modules: Set[str], dry_run: bool = False) -> None:
    """Installe les modules externes detectes et genere requirements.txt."""
    if not modules:
        logging.info("Aucun module a installer.")
        return

    logging.info("Installation des modules externes...")
    installed = []

    for module in sorted(modules):
        if dry_run:
            logging.info("Module detecte (simulation) : {}".format(module))
            continue
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)
            logging.info("Installe : {}".format(module))
            installed.append(module)
        except subprocess.CalledProcessError:
            logging.warning("Echec installation : {}".format(module))

    if installed and not dry_run:
        requirements_path = BASE_DIR / "requirements.txt"
        try:
            requirements_path.write_text("\n".join(installed) + "\n", encoding="utf-8")
            logging.info("requirements.txt genere avec {} module(s)".format(len(installed)))
        except OSError as err:
            logging.error("Erreur ecriture requirements.txt ({})".format(type(err).__name__))

def afficher_rapport() -> None:
    """Affiche les modules externes detectes par fichier."""
    if external_modules_by_file:
        logging.info("Modules externes detectes :")
        for script_path, modules in external_modules_by_file.items():
            logging.info("Fichier : {}".format(script_path))
            for external in modules:
                logging.info("  - {}".format(external))
    else:
        logging.info("Aucun module externe detecte.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Detecte et installe les modules externes utilises dans les scripts Python.")
    parser.add_argument("path", nargs="?", default=str(BASE_DIR),
                        help="Chemin du dossier a analyser (defaut : dossier du script)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simule l'installation sans modifier le systeme")
    args = parser.parse_args()

    logging.info("Analyse du dossier : {}".format(args.path))
    scan_directory_for_externals(args.path)
    afficher_rapport()
    installer_modules(modules_to_install, dry_run=args.dry_run)

# Bloc __main__ supprime pour modularisation


# Orchestration centralisée
from assistant_pdg import AssistantPDG

def run():
    print("Module exécuté via AssistantPDG")

AssistantPDG.register("detecte_modules_externes", run)

# -*- coding: utf-8 -*-
"""Luxuria Requirements Manager — Génère un fichier requirements.txt fiable à partir des imports réels."""

import re
import subprocess
import logging
import sys
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from importlib.metadata import distributions

# === Configuration ===
BASE_DIR = Path(__file__).resolve().parent
REQUIREMENTS_PATH = BASE_DIR / "requirements.txt"
EXCLUDED_MODULES = {"assistant_pdg", "main", "config", "luxuria_web"}
DRY_RUN = False  # True = simulation sans installation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Détection des modules standards
def est_module_standard(nom: str) -> bool:
    try:
        return nom in sys.stdlib_module_names
    except AttributeError:
        # Fallback pour versions de Python < 3.10
        import sysconfig
        stdlib_path = sysconfig.get_paths()["stdlib"]
        return (Path(stdlib_path) / nom).exists()


# === Vérifie si le module est disponible sur PyPI
def module_existe_sur_pypi(nom: str) -> bool:
    url = f"https://pypi.org/pypi/{nom}/json"
    try:
        with urlopen(url) as response:
            return response.status == 200
    except (HTTPError, URLError):
        return False

# === Analyse des imports dans tous les fichiers .py
def extraire_modules_importes() -> set[str]:
    modules = set()
    for script in BASE_DIR.rglob("*.py"):
        if script.name == Path(__file__).name:
            continue
        try:
            lignes = script.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            logging.warning(f"Erreur lecture fichier {script.name} : {e}")
            continue

        for ligne in lignes:
            match = re.match(r"^\s*(?:import|from)\s+([a-zA-Z0-9_.]+)", ligne)
            if match:
                nom_complet = match.group(1)
                nom_base = nom_complet.split('.')[0]
                if nom_base not in EXCLUDED_MODULES and not est_module_standard(nom_base):
                    modules.add(nom_base)
    return modules

# === Installation des modules manquants
def installer_modules(modules: set[str]) -> None:
    for module in sorted(modules):
        if not module_existe_sur_pypi(module):
            logging.warning(f"⛔ Module introuvable sur PyPI : {module} — ignoré.")
            continue
        try:
            __import__(module)
            logging.info(f"✅ Module déjà présent : {module}")
        except ImportError:
            if DRY_RUN:
                logging.info(f"🔎 Simulation — module à installer : {module}")
            else:
                logging.info(f"📦 Installation du module : {module}")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)
                except subprocess.CalledProcessError as e:
                    logging.error(f"❌ Échec installation : {module} — {e}")

# === Collecte des packages installés
def lister_packages_installes() -> list[str]:
    packages = []
    for dist in distributions():
        try:
            nom = dist.metadata["Name"]
            version = dist.version
            if nom and version:
                packages.append(f"{nom}=={version}")
        except KeyError:
            continue
    return sorted(packages)

# === Écriture du fichier requirements.txt
def ecrire_requirements(packages: list[str]) -> None:
    try:
        timestamp = f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        REQUIREMENTS_PATH.write_text(timestamp + "\n".join(packages) + "\n", encoding="utf-8")
        logging.info(f"📝 requirements.txt mis à jour ({len(packages)} packages).")
    except OSError as e:
        logging.error(f"❌ Erreur écriture requirements.txt : {e}")

# === Fonction principale
def generer_requirements() -> None:
    logging.info("🔍 Analyse des scripts Python en cours...")
    modules = extraire_modules_importes()
    installer_modules(modules)
    packages = lister_packages_installes()
    ecrire_requirements(packages)

# === Exécution directe
if __name__ == "__main__":
    generer_requirements()

import logging
from typing import Union, List, Dict
from pathlib import Path
from assistant_pdg import AssistantPDG

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

# Dictionnaire des imports par fichier
imports_map: Dict[str, List[str]] = {}

def extract_imports(file_path: Union[str, Path]) -> List[str]:
    """Extrait les modules importés dans un fichier Python."""
    found_modules: List[str] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('import '):
                    parts = stripped.split()
                    if len(parts) >= 2:
                        found_modules.append(parts[1].split('.')[0])
                elif stripped.startswith('from '):
                    parts = stripped.split()
                    if len(parts) >= 2:
                        found_modules.append(parts[1].split('.')[0])
    except FileNotFoundError:
        logging.warning(f"Fichier introuvable : {file_path}")
    except PermissionError:
        logging.warning(f"Permission refusée : {file_path}")
    except UnicodeDecodeError:
        logging.warning(f"Encodage illisible : {file_path}")
    return found_modules

def scan_imports(directory: Union[str, Path]) -> None:
    """Scanne tous les fichiers .py du dossier pour extraire les imports."""
    directory = Path(directory)
    for file_path in directory.rglob("*.py"):
        if file_path.name != "__init__.py":
            found = extract_imports(file_path)
            if found:
                imports_map[str(file_path)] = found

def afficher_resultats() -> None:
    """Affiche les résultats de l'analyse."""
    if imports_map:
        logging.info("📦 Modules importés par fichier :")
        for path, mods in imports_map.items():
            logging.info(f"\n{path}")
            for mod in sorted(set(mods)):
                logging.info(f"     {mod}")
    else:
        logging.info("Aucun import détecté.")

# Orchestration centralisée
def run():
    logging.info("🔍 Analyse des imports en cours...")
    scan_imports(Path(__file__).resolve().parent)
    afficher_resultats()

AssistantPDG.register("analyse_imports", run)

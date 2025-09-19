# -*- coding: utf-8 -*-
"""Simulation des préférences PyCharm avec export YAML - Luxuria Studio."""

import logging
from pathlib import Path
import yaml
from assistant_pdg import AssistantPDG

# === Logging
logging.basicConfig(level=logging.INFO, format="[CONFIG] %(message)s")

# === Préférences simulées
def generer_preferences() -> dict:
    """Génère un dictionnaire simulant les préférences PyCharm."""
    return {
        "Appearance & Behavior > System Settings": {
            "Save files when switching to a different application": True,
            "Save files if the IDE is idle for": 5
        },
        "Editor > General > Editor Tabs": {
            "Mark modified": True
        },
        "Tools > Actions on Save": {
            "Reformat code": True,
            "Optimize imports": True,
            "Rearrange code": False,
            "Run code cleanup": False,
            "Upload to default server": False
        }
    }

# === Export YAML
def exporter_yaml(data: dict, nom_fichier: str = "automatly_save.yaml", dossier: Path = None) -> bool:
    """Exporte les préférences dans un fichier YAML."""
    dossier = dossier or Path(__file__).resolve().parent
    chemin = dossier / nom_fichier
    try:
        with chemin.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        logging.info(f"📄 Fichier YAML exporté : {chemin.name}")
        return True
    except (OSError, IOError, yaml.YAMLError) as err:
        logging.error(f"❌ Erreur export YAML : {type(err).__name__}")
        return False

# === Configuration principale
def configurer_preferences(exporter: bool = True, dossier: Path = None) -> dict:
    """Configure les préférences et les affiche. Retourne le dictionnaire."""
    prefs = generer_preferences()

    logging.info("🧠 Préférences simulées PyCharm :")
    for section, options in prefs.items():
        logging.info(f" {section}")
        for option, value in options.items():
            if isinstance(value, bool):
                status = "Activé" if value else "Désactivé"
                logging.info(f"   - {option}: {status}")
            else:
                logging.info(f"   - {option}: {value} sec")

    if exporter:
        exporter_yaml(prefs, dossier=dossier)

    logging.info("✅ Sauvegarde automatique configurée avec élégance par Luxuria.")
    return prefs

# === Orchestration centralisée
def run():
    dossier = Path(__file__).resolve().parent
    configurer_preferences(exporter=True, dossier=dossier)

AssistantPDG.register("config_sauvegarde_auto", run)

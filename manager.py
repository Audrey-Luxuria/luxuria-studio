# -*- coding: utf-8 -*-
"""Module central de gestion Luxuria"""

import os
import json
import logging
import hashlib
from typing import Dict, Callable, Any, List
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration
BASE_DIR = os.path.join(os.getcwd(), "luxuria_data")
os.makedirs(BASE_DIR, exist_ok=True)

LOG_PATH = os.path.join(BASE_DIR, "manager.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def log_activite(message: str) -> None:
    logging.info(message)

# === Classe centrale
class LuxuriaManager:
    def __init__(self) -> None:
        self._registry: Dict[str, str] = {}
        self._actions: Dict[str, Callable[[Any], Dict[str, Any]]] = {}

    def register(self, key: str, value: str) -> None:
        self._registry[key] = value

    def unregister(self, key: str) -> None:
        self._registry.pop(key, None)

    def get(self, key: str) -> str:
        return self._registry.get(key, "")

    def list_keys(self) -> List[str]:
        return list(self._registry.keys())

    def clear(self) -> None:
        self._registry.clear()

    def export_registry(self) -> Dict[str, str]:
        return dict(self._registry)

    def hash_registry(self) -> str:
        data = json.dumps(self._registry, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def define_action(self, name: str, func: Callable[[Any], Dict[str, Any]]) -> None:
        self._actions[name] = func

    def execute_action(self, name: str, data: Any = None) -> Dict[str, Any]:
        action = self._actions.get(name)
        if action:
            return action(data)
        log_activite(f"Aucune action définie pour : {name}")
        return {"error": "Action inconnue"}

# === Initialisation du manager
manager = LuxuriaManager()

# === Action : export JSON
def action_export_json(_: Any) -> Dict[str, Any]:
    try:
        path = os.path.join(BASE_DIR, "export.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manager.export_registry(), f, indent=4)
        log_activite(f"Export JSON effectué : {path}")
        return {"status": "Export JSON réussi"}
    except Exception as e:
        log_activite(f"Erreur export JSON : {e}")
        return {"error": str(e)}

manager.define_action("btn_export_json", action_export_json)

# === Action : nettoyage
def action_clean(_: Any) -> Dict[str, Any]:
    fichiers = ["export.json", "rapport.pdf", "graphique.html"]
    resultats = {}
    for nom in fichiers:
        chemin = os.path.join(BASE_DIR, nom)
        try:
            if os.path.exists(chemin):
                os.remove(chemin)
                log_activite(f"Fichier supprimé : {chemin}")
                resultats[nom] = "supprimé"
            else:
                resultats[nom] = "absent"
        except Exception as e:
            resultats[nom] = f"erreur : {str(e)}"
    return {"nettoyage": resultats}

manager.define_action("btn_clean", action_clean)

# === Action : résumé des clés
def action_resume(_: Any) -> Dict[str, Any]:
    resume = {
        "total": len(manager.list_keys()),
        "hash": manager.hash_registry(),
        "cles": manager.list_keys()
    }
    log_activite("Résumé du registre généré")
    return resume

manager.define_action("btn_resume", action_resume)

# === Fonction main modulaire
def main() -> None:
    log_activite("Manager Luxuria initialisé")

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_manager", run)

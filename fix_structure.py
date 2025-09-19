# -*- coding: utf-8 -*-
"""Gestion des fiches clients - Luxuria Studio"""

import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from assistant_pdg import AssistantPDG

# === Configuration
BASE = Path(__file__).resolve().parent
DOSSIER_CLIENT = BASE.parent / "interface_client"
CLIENTS_FILE = DOSSIER_CLIENT / "clients.json"
STYLES_FILE = DOSSIER_CLIENT / "styles.json"
CHARGER_SCRIPT = BASE / "clients" / "charger_fiche_client.py"
CLE_VALIDITE_JOURS = 7

logging.basicConfig(level=logging.INFO, format="[CLIENT] %(message)s")

def charger_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        logging.warning(f"Fichier introuvable : {path.name}")
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as err:
        logging.error(f"Erreur chargement {path.name} : {type(err).__name__}")
        return {}

def chercher_client(recherche: str) -> Optional[Dict[str, Any]]:
    base_clients = charger_json(CLIENTS_FILE)
    recherche = recherche.strip().lower()

    if recherche in base_clients:
        return base_clients[recherche]

    for fiche in base_clients.values():
        if fiche.get("cle_acces", "").lower() == recherche or fiche.get("nom", "").lower() == recherche:
            return fiche
    return None

def est_cle_valide(fiche: Dict[str, Any]) -> bool:
    date_str = fiche.get("date_cle", "")
    try:
        date_cle = datetime.strptime(date_str, "%Y-%m-%d")
        return datetime.now() <= date_cle + timedelta(days=CLE_VALIDITE_JOURS)
    except ValueError:
        return False

def format_fiche_client(fiche: Dict[str, Any]) -> str:
    if not fiche:
        return "Aucune donnée client disponible."

    lignes = []
    nom = fiche.get("nom", "").title()
    prenom = fiche.get("prenom", "").title()
    lignes.append(f"Fiche client : {prenom} {nom}")
    lignes.append("-" * 40)

    for champ, valeur in fiche.items():
        if champ not in ["historique_achats", "style_prefere", "cle_acces", "date_cle"]:
            lignes.append(f"{champ:<20}: {valeur}")

    if "date_cle" in fiche:
        if est_cle_valide(fiche):
            expiration = datetime.strptime(fiche["date_cle"], "%Y-%m-%d") + timedelta(days=CLE_VALIDITE_JOURS)
            lignes.append(f"Clé valide jusqu'au : {expiration.strftime('%d/%m/%Y')}")
        else:
            lignes.append("Clé expirée ou invalide.")

    achats = fiche.get("historique_achats", [])
    if achats:
        lignes.append("\nAchats récents :")
        lignes.extend(f"- {item}" for item in achats)

    style_nom = fiche.get("style_prefere", "")
    styles = charger_json(STYLES_FILE)
    style_data = styles.get(style_nom, {})
    if style_data:
        lignes.append(f"\nStyle préféré : {style_nom}")
        lignes.append("-" * 40)
        for champ, valeur in style_data.items():
            lignes.append(f"{champ:<20}: {valeur}")
    elif style_nom:
        lignes.append(f"\nStyle '{style_nom}' non reconnu.")

    return "\n".join(lignes)

def get_client_fiche(nom_client: str) -> Dict[str, Any]:
    if not CHARGER_SCRIPT.is_file():
        raise FileNotFoundError(f"Script introuvable : {CHARGER_SCRIPT.name}")

    try:
        result = subprocess.run(
            ["python", str(CHARGER_SCRIPT), nom_client],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Échec d'exécution du script : {e}")
    except json.JSONDecodeError:
        raise ValueError("Sortie JSON invalide.")

# === Orchestration centralisée
def run():
    nom_test = "alice"
    fiche = chercher_client(nom_test)
    texte = format_fiche_client(fiche)
    logging.info(texte)

AssistantPDG.register("fiche_client", run)

# -*- coding: utf-8 -*-
"""Vérificateur de clés Luxuria Studio"""

from pathlib import Path
from typing import Dict, Any
import json
import logging
from datetime import datetime
from assistant_pdg import AssistantPDG  # ✅ Orchestration activée

# === Setup logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# === Define path to JSON file
SCRIPT_DIR = Path(__file__).resolve().parent
KEYS_PATH = SCRIPT_DIR / "luxuria_keys.json"

# === Chargement des données
def load_keys_file(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Fichier JSON invalide : {e}")

# === Extraction d'une clé
def get_key_info(client_identifier: str, keys_data: Dict[str, Any]) -> Dict[str, Any]:
    access_entries = keys_data.get("acces", [])
    if not isinstance(access_entries, list):
        raise ValueError("Le champ 'acces' doit être une liste.")

    for entry in access_entries:
        if entry.get("identifiant") == client_identifier:
            return entry.get("cle", {})

    raise KeyError(f"Aucune clé trouvée pour l'identifiant : {client_identifier}")

# === Évaluation de la validité
def evaluate_key_status(key_info: Dict[str, Any]) -> Dict[str, Any]:
    expiration_str = key_info.get("expiration")
    if not expiration_str:
        raise ValueError("Champ 'expiration' manquant dans la clé.")

    try:
        expiration_date = datetime.fromisoformat(expiration_str)
    except Exception as e:
        raise ValueError(f"Format de date invalide : {expiration_str}") from e

    now = datetime.now()
    is_active = now < expiration_date

    return {
        "status": key_info.get("status", "inconnu"),
        "paid": bool(key_info.get("paid")),
        "expiration": expiration_str,
        "post_expiration_action": key_info.get("action_apres_expiration", "non définie"),
        "temporal_state": "active" if is_active else "expirée"
    }

# === Rapport texte
def format_key_report(client_identifier: str, key_status: Dict[str, Any]) -> str:
    return (
        f"\nClient : {client_identifier}\n"
        f"===========================\n"
        f"Statut : {key_status['status']}\n"
        f"Payé : {'Oui' if key_status['paid'] else 'Non'}\n"
        f"Expiration : {key_status['expiration']}\n"
        f"Action après expiration : {key_status['post_expiration_action']}\n"
        f"État actuel : {'ACTIVE' if key_status['temporal_state'] == 'active' else 'EXPIREE'}\n"
    )

# === Rapport HTML
def generate_html_report(client_identifier: str, key_status: Dict[str, Any], output_path: Path) -> None:
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Rapport de Clé - {client_identifier}</title>
</head>
<body>
    <h2>Client : {client_identifier}</h2>
    <ul>
        <li><strong>Statut :</strong> {key_status['status']}</li>
        <li><strong>Payé :</strong> {'Oui' if key_status['paid'] else 'Non'}</li>
        <li><strong>Expiration :</strong> {key_status['expiration']}</li>
        <li><strong>Action après expiration :</strong> {key_status['post_expiration_action']}</li>
        <li><strong>État actuel :</strong> {'ACTIVE' if key_status['temporal_state'] == 'active' else 'EXPIREE'}</li>
    </ul>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")
    logging.info(f"Rapport HTML généré : {output_path.name}")

# === Point d'entrée
def main() -> None:
    client_identifier = input("Entrez l'identifiant du client : ").strip()

    try:
        keys_data = load_keys_file(KEYS_PATH)
        key_info = get_key_info(client_identifier, keys_data)
        key_status = evaluate_key_status(key_info)
        report = format_key_report(client_identifier, key_status)
        logging.info(report)

        html_path = SCRIPT_DIR / f"{client_identifier}_rapport.html"
        generate_html_report(client_identifier, key_status, html_path)

    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as error:
        logging.error(f"Erreur : {error}")

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_keys_checker", run)

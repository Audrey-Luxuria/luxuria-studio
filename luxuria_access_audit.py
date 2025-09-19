# -*- coding: utf-8 -*-
"""Audit des accès Luxuria Studio."""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from assistant_pdg import AssistantPDG  # ✅ Orchestrateur principal

# === Configuration du logging ===
logging.basicConfig(
    level=logging.INFO,
    format="[AUDIT] %(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Constantes ===
ACCESS_DURATION = timedelta(days=30)
RENEWAL_WINDOW = timedelta(days=37)
COMMUNAL_GALLERY_DURATION = timedelta(days=30)
KEYS_FILE = Path(__file__).parent / "luxuria_keys.json"

# === Chargement des données
def load_keys(filepath: Path) -> dict:
    if not filepath.exists():
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")
    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)

def parse_date(date_str: str, label: str, client_id: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise ValueError(f"{client_id} : Date invalide pour {label} ({date_str})")

# === Audit principal
def audit_access() -> dict:
    try:
        data = load_keys(KEYS_FILE)
    except Exception as e:
        logging.error(str(e))
        return {"error": str(e)}

    now = datetime.now()
    stats = {"total": 0, "valid": 0, "expired": 0, "renewable": 0}
    alerts = []

    for client in data.get("access", []):
        stats["total"] += 1
        client_id = client.get("id", "inconnu")
        key = client.get("key", {})

        try:
            gen_date = parse_date(key["generation_date"], "génération", client_id)
            pay_date = parse_date(key["payment_date"], "paiement", client_id)
        except Exception as e:
            alerts.append(str(e))
            continue

        expiration = pay_date + ACCESS_DURATION
        renewal_deadline = gen_date + RENEWAL_WINDOW
        paid = key.get("paid") is True

        if paid and now <= expiration:
            stats["valid"] += 1
        elif paid and expiration < now <= renewal_deadline:
            stats["renewable"] += 1
            alerts.append(f"{client_id} : accès expiré mais renouvelable jusqu'au {renewal_deadline.date()}")
        else:
            stats["expired"] += 1
            alerts.append(f"{client_id} : accès expiré ou non payé")

        # Galerie commune
        if "communal_gallery_payment" in key:
            try:
                gallery_date = parse_date(key["communal_gallery_payment"], "galerie commune", client_id)
                if now > gallery_date + COMMUNAL_GALLERY_DURATION:
                    alerts.append(f"{client_id} : accès galerie commune expiré")
            except Exception as e:
                alerts.append(str(e))

        # Communauté
        if "community_payment" in key:
            try:
                community_date = parse_date(key["community_payment"], "communauté", client_id)
                if now > community_date + ACCESS_DURATION:
                    alerts.append(f"{client_id} : accès communauté expiré")
            except Exception as e:
                alerts.append(str(e))

        # Identifiants manquants
        if not key.get("community_id") or not key.get("community_password"):
            alerts.append(f"{client_id} : identifiants communauté manquants")
        if not key.get("communal_gallery_id") or not key.get("communal_gallery_password"):
            alerts.append(f"{client_id} : identifiants galerie commune manquants")

    return {
        "timestamp": now.isoformat(),
        "stats": stats,
        "alerts": alerts
    }

# === Récupération sécurisée des identifiants
def retrieve_credentials(client_id: str, authorized_by_pdg: bool) -> dict:
    if not authorized_by_pdg:
        return {"error": "Accès refusé : autorisation PDG requise."}

    try:
        data = load_keys(KEYS_FILE)
    except Exception as e:
        return {"error": str(e)}

    client = next((c for c in data.get("access", []) if c.get("id") == client_id), None)
    if not client:
        return {"error": f"Client '{client_id}' introuvable."}

    key = client.get("key", {})
    try:
        pay_date = parse_date(key["payment_date"], "paiement", client_id)
    except Exception as e:
        return {"error": str(e)}

    if datetime.now() > pay_date + ACCESS_DURATION:
        return {"error": f"Accès expiré pour '{client_id}'."}

    credentials = {}
    if key.get("community_id") and key.get("community_password"):
        credentials["communaute"] = {
            "id": key["community_id"],
            "mot_de_passe": key["community_password"]
        }
    if key.get("communal_gallery_id") and key.get("communal_gallery_password"):
        credentials["galerie_commune"] = {
            "id": key["communal_gallery_id"],
            "mot_de_passe": key["communal_gallery_password"]
        }

    return credentials if credentials else {"info": f"Aucun identifiant actif pour '{client_id}'."}

# === Orchestration centralisée
def run():
    logging.info("🔍 Lancement de l'audit des accès Luxuria...")
    rapport = audit_access()
    if "error" in rapport:
        logging.error(rapport["error"])
    else:
        logging.info(f"Audit terminé : {rapport['stats']}")
        for alert in rapport["alerts"]:
            logging.warning(f"⚠️ {alert}")

AssistantPDG.register("luxuria_access_audit", run)

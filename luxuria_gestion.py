# -*- coding: utf-8 -*-
"""Module de gestion Luxuria Studio : abonnements, contrats, facturation"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta, date
from assistant_pdg import AssistantPDG

# === Répertoires
BASE_DIR = Path(__file__).resolve().parent.parent
ADMIN_DIR = BASE_DIR / "admin_private"
PRIVATE_DIR = BASE_DIR / "private"

ADMIN_DIR.mkdir(parents=True, exist_ok=True)
PRIVATE_DIR.mkdir(parents=True, exist_ok=True)

# === Fichiers
PATH_KEYS = ADMIN_DIR / "luxuria_keys.json"
PATH_CONTRACTS = ADMIN_DIR / "luxuria_contrats.json"
PATH_INVOICES = PRIVATE_DIR / "facturation.json"
PATH_LOG = PRIVATE_DIR / "journal_activite.txt"

# === Journalisation
logging.basicConfig(
    filename=str(PATH_LOG),
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log(msg: str) -> None:
    try:
        with PATH_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")
    except OSError as e:
        logging.error(f"Erreur journalisation : {e}")
    logging.info(msg)

# === Abonnements
def load_keys() -> Dict[str, Any]:
    if not PATH_KEYS.exists():
        return {"acces": [], "meta": {"dernier_update": None}}
    try:
        return json.loads(PATH_KEYS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log(f"Erreur lecture clés : {e}")
        return {"acces": [], "meta": {"dernier_update": None}}

def save_keys(data: Dict[str, Any]) -> None:
    try:
        PATH_KEYS.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        log(f"Erreur sauvegarde clés : {e}")

def add_subscription(id_: str, name: str, role: str, duration_days: int = 365) -> None:
    now = datetime.now()
    expiration = now + timedelta(days=duration_days)
    data = load_keys()
    data["acces"].append({
        "identifiant": id_,
        "client": {"nom": name, "role": role},
        "cle": {
            "status": "actif",
            "paid": True,
            "start": now.isoformat(),
            "expiration": expiration.isoformat(),
            "action_apres_expiration": "bloquer"
        },
        "mise_a_jour": {
            "responsable": "assistant",
            "dossier": str(ADMIN_DIR),
            "date_migration": now.isoformat()
        }
    })
    data["meta"]["dernier_update"] = now.isoformat()
    save_keys(data)
    log(f"Abonnement activé pour {name} ({id_}) jusqu'au {expiration:%d/%m/%Y}")
    AssistantPDG.notifier_connexion(id_)

def deactivate_expired_subscriptions() -> List[str]:
    data = load_keys()
    now = datetime.now()
    expired = []
    for entry in data["acces"]:
        try:
            exp_date = datetime.fromisoformat(entry["cle"]["expiration"])
            if exp_date < now and entry["cle"]["status"] == "actif":
                entry["cle"]["status"] = "expiré"
                entry["cle"]["paid"] = False
                entry["mise_a_jour"]["date_migration"] = now.isoformat()
                expired.append(entry["identifiant"])
        except (KeyError, ValueError) as e:
            log(f"Date invalide pour {entry.get('identifiant', 'inconnu')} : {e}")
    if expired:
        save_keys(data)
        log(f"Abonnements expirés : {', '.join(expired)}")
    return expired

# === Contrats
def load_contracts() -> Dict[str, Any]:
    if not PATH_CONTRACTS.exists():
        return {"contrats": [], "meta": {"dernier_update": None}}
    try:
        return json.loads(PATH_CONTRACTS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log(f"Erreur lecture contrats : {e}")
        return {"contrats": [], "meta": {"dernier_update": None}}

def save_contracts(data: Dict[str, Any]) -> None:
    try:
        PATH_CONTRACTS.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        log(f"Erreur sauvegarde contrats : {e}")

def add_contract(id_: str, name: str, role: str, country: str, text: str) -> None:
    data = load_contracts()
    data["contrats"].append({
        "identifiant": id_,
        "client": {"nom": name, "role": role, "pays": country},
        "contenu": {"contrat": text, "avenants": []},
        "mise_a_jour": {
            "responsable": "assistant",
            "dossier": str(ADMIN_DIR),
            "horodatage": datetime.now().isoformat()
        }
    })
    data["meta"]["dernier_update"] = datetime.now().isoformat()
    save_contracts(data)
    log(f"Contrat ajouté pour {name} ({id_})")

def add_amendment(id_: str, title: str, type_: str, date_: str = None) -> None:
    data = load_contracts()
    contract = next((c for c in data["contrats"] if c["identifiant"] == id_), None)
    if not contract:
        log(f"Contrat introuvable pour avenant {id_}")
        return
    contract["contenu"]["avenants"].append({
        "titre": title,
        "type": type_,
        "date": date_ or date.today().isoformat()
    })
    contract["mise_a_jour"]["horodatage"] = datetime.now().isoformat()
    save_contracts(data)
    log(f"Avenant ajouté au contrat {id_}")

# === Facturation
def load_invoices() -> Dict[str, Any]:
    if not PATH_INVOICES.exists():
        return {"factures": [], "meta": {}}
    try:
        return json.loads(PATH_INVOICES.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log(f"Erreur lecture facturation : {e}")
        return {"factures": [], "meta": {}}

def save_invoices(data: Dict[str, Any]) -> None:
    data["meta"]["dernier_update"] = datetime.now().isoformat()
    data["meta"].setdefault("structure", "Luxuria IA - Facturation Client")
    data["meta"].setdefault("source", str(PATH_INVOICES))
    try:
        PATH_INVOICES.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        log(f"Erreur sauvegarde facturation : {e}")

def add_invoice(client_id: str, name: str, amount: float = 49.0, currency: str = "EUR", method: str = "Stripe") -> None:
    if not AssistantPDG.verifier_paiement(client_id):
        log(f"Paiement non validé pour {client_id}")
        return

    data = load_invoices()
    today = date.today()
    due = today + timedelta(days=30)
    ref = f"FAC-{client_id}-{today:%Y%m%d}"

    data["factures"].append({
        "code": client_id,
        "client": {"nom": name},
        "paiement": {
            "montant": amount,
            "devise": currency,
            "mode": method,
            "etat": "en attente",
            "reference": ref
        },
        "dates": {
            "facture": today.isoformat(),
            "echeance": due.isoformat()
        }
    })
    save_invoices(data)

    contract_text = (
        f"Contrat généré automatiquement pour {name}.\n"
        f"Montant : {amount} {currency} via {method}.\n"
        f"Date de facturation : {today.isoformat()}.\n"
        f"Échéance : {due.isoformat()}.\n"
        f"Référence : {ref}."
    )
    add_contract(client_id, name, "client", "FR", contract_text)
    add_amendment(client_id, "Facturation mensuelle", "automatique", today.isoformat())
    log(f"Facture enregistrée pour {name}")
    AssistantPDG.notifier_connexion(client_id)

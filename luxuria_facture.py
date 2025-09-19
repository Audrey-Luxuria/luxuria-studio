# -*- coding: utf-8 -*-
"""Luxuria Facture Gestion des factures clients (module orchestre)."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from json.decoder import JSONDecodeError

# === Chemins
BASE_DIR = Path(__file__).resolve().parent
DIRS = {
    "config": BASE_DIR / "config",
    "private": BASE_DIR / "private",
    "admin": BASE_DIR / "admin_private",
    "fiches": BASE_DIR / "luxuria_fiches",
    "factures": BASE_DIR / "luxuria_fiches" / "factures",
    "journal": BASE_DIR / "admin_private" / "luxuria_journal.log",
    "clients": BASE_DIR / "config" / "clients.json"
}

# === Creation des dossiers
for chemin in DIRS.values():
    if chemin.suffix == "":
        chemin.mkdir(parents=True, exist_ok=True)

# === Logger
logging.basicConfig(
    filename=str(DIRS["journal"]),
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_event(message: str, niveau: str = "info") -> None:
    if hasattr(logging, niveau):
        getattr(logging, niveau)(message)

# === Validations
STATUTS_VALIDES = {"en attente", "payee", "refusee", "remboursee", "gratuit", "paye"}

def email_valide(email: str) -> bool:
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

def date_valide(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def statut_valide(statut: str) -> bool:
    return statut.lower() in STATUTS_VALIDES

# === Clients
def charger_clients() -> dict:
    path = DIRS["clients"]
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log_event("Fichier clients introuvable", "warning")
    except PermissionError:
        log_event("Acces refuse au fichier clients", "error")
    except JSONDecodeError as e:
        log_event(f"JSON invalide dans clients.json : {e}", "error")
    return {}

def enregistrer_clients(clients: dict) -> None:
    path = DIRS["clients"]
    try:
        path.write_text(json.dumps(clients, indent=2, ensure_ascii=True), encoding="utf-8")
    except OSError as e:
        log_event(f"Erreur systeme lors de l'enregistrement des clients : {e}", "error")

def ajouter_client_demo() -> None:
    clients = charger_clients()
    if "luxuria_demo" not in clients:
        clients["luxuria_demo"] = {
            "nom": "Audrey",
            "email": "audrey@example.com",
            "ville": "Bellac",
            "date_acces": datetime.now().strftime("%Y-%m-%d"),
            "expiration": "2025-12-31",
            "statut": "actif"
        }
        enregistrer_clients(clients)
        log_event("Client demo ajoute : luxuria_demo")

# === Factures
def charger_factures(nom: str) -> list:
    path = DIRS["factures"] / f"{nom.strip().lower()}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log_event(f"Aucune facture trouvee pour {nom}", "info")
    except JSONDecodeError:
        log_event(f"Factures corrompues pour {nom}", "warning")
    return []

def sauvegarder_factures(nom: str, factures: list) -> bool:
    path = DIRS["factures"] / f"{nom.strip().lower()}.json"
    try:
        path.write_text(json.dumps(factures, indent=2, ensure_ascii=True), encoding="utf-8")
        return True
    except OSError as e:
        log_event(f"Erreur systeme lors de la sauvegarde des factures : {e}", "error")
        return False

def generer_facture_auto(nom: str, montant: float = 99.0, statut: str = "en attente", label: str = "Service IA") -> None:
    if montant <= 0 or not statut_valide(statut):
        log_event(f"Parametres invalides pour {nom}", "warning")
        return

    nom_clean = nom.strip().title()
    factures = charger_factures(nom_clean)
    numero = f"F{datetime.now().year}-{len(factures) + 1:03d}"
    date_facture = datetime.now().strftime("%Y-%m-%d")

    facture = {
        "numero": numero,
        "date": date_facture,
        "montant": montant,
        "statut": statut,
        "label": label
    }

    factures.append(facture)
    if sauvegarder_factures(nom_clean, factures):
        log_event(f"Facture enregistree : {nom_clean} #{numero} ({montant:.2f} EUR)")
    else:
        log_event(f"Echec enregistrement facture : {nom_clean}", "error")

# === Fonction orchestrable depuis assistant_pdg.py
def traitement_facturation_automatique(nom_client: str = None) -> None:
    log_event(" Demarrage du module de facturation")
    ajouter_client_demo()
    clients = charger_clients()
    for key, data in clients.items():
        if data.get("statut", "").lower() == "actif":
            if nom_client and data["nom"].lower() != nom_client.lower():
                continue
            generer_facture_auto(data["nom"])
    log_event(" Fin du traitement de facturation")

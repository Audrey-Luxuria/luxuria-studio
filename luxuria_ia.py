# -*- coding: utf-8 -*-
"""Module IA Luxuria Studio"""

from flask import Flask, request, render_template_string
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import colorama
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Initialisation
colorama.init(autoreset=True)
app = Flask(__name__)

# === Répertoires et fichiers
BASE = Path(__file__).resolve().parent
FICHES = BASE / "luxuria_fiches"
PRIVATE = BASE / "admin_private"
CLIENTS_GALLERY = FICHES / "galleries_clients"

FICHES.mkdir(exist_ok=True)
PRIVATE.mkdir(exist_ok=True)
CLIENTS_GALLERY.mkdir(parents=True, exist_ok=True)

CLIENTS_PATH = FICHES / "clients.json"
KEYS_PATH = FICHES / "luxuria_keys.json"
FACTURES_PATH = FICHES / "factures.json"
PRICING_FILE = BASE / "luxuria_pricing.json"
GALLERY_GLOBAL = BASE / "fiche.json"
LOG_PATH = PRIVATE / "luxuria_journal.log"

# === Journalisation
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)

def log(msg: str):
    logging.info(msg)

# === Utilitaires JSON
def charger_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        log(f"[ERREUR] Fichier JSON mal formé : {path.name}")
        return {}

def sauvegarder_json(path: Path, data: Dict[str, Any]) -> None:
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        log(f"[ERREUR] Impossible d'écrire dans {path.name} : {e}")

# === Fonctions métier
def ajouter_client(nom: str, email: str, role: str, localisation: str):
    identifiant = f"{nom.strip().lower().replace(' ', '_')}_{role.lower()}"
    clients = charger_json(CLIENTS_PATH)
    clients[identifiant] = {
        "nom": nom,
        "email": email,
        "role": role,
        "localisation": localisation,
        "date_acces": datetime.now().isoformat(),
        "statut": "actif"
    }
    sauvegarder_json(CLIENTS_PATH, clients)
    log(f"[CLIENT] Ajout : {nom} ({role})")
    return identifiant

def ajouter_cle(nom: str, statut: str = "actif", expiration: Optional[str] = None):
    identifiant = f"key_{nom.lower().replace(' ', '_')}"
    keys = charger_json(KEYS_PATH)
    expiration = expiration or (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    keys[identifiant] = {
        "nom": nom,
        "statut": statut,
        "expiration": expiration,
        "date_creation": datetime.now().isoformat()
    }
    sauvegarder_json(KEYS_PATH, keys)
    log(f"[ACCES] Clé ajoutée : {nom} (expire le {expiration})")

def generer_facture(nom: str, produit: str, montant: float = 0.0, statut: str = "gratuit"):
    facture = {
        "client": nom,
        "produit": produit,
        "montant": montant,
        "statut": statut,
        "date": datetime.now().isoformat()
    }
    data = charger_json(FACTURES_PATH)
    factures = data.get("factures", [])
    factures.append(facture)
    data["factures"] = factures
    data["meta"] = {"dernier_update": datetime.now().isoformat()}
    sauvegarder_json(FACTURES_PATH, data)
    log(f"[FACTURE] Générée : {nom} / {produit} ({statut})")

def client_a_acces(client_id: str) -> bool:
    keys = charger_json(KEYS_PATH)
    for k, v in keys.items():
        if k.startswith(f"key_{client_id}") and v.get("statut") in ["actif", "renouvele"]:
            return True
    return False

def afficher_galerie(path: Path) -> str:
    data = charger_json(path)
    creations = data.get("creations", [])
    if not creations:
        return "<p>Galerie vide.</p>"
    html = "<ul>"
    for item in creations:
        nom = item.get("nom", "Sans titre")
        desc = item.get("description", "Aucune description")
        pdf = item.get("pdf", "Non disponible")
        html += f"<li><strong>{nom}</strong> - {desc} - PDF : {pdf}</li>"
    html += "</ul>"
    return html

# === Interface Flask
@app.route("/")
def accueil():
    return render_template_string("""
    <h2>Bienvenue chez Luxuria IA</h2>
    <form method='POST' action='/espace-client'>
        <label>Clé client :</label><br>
        <input type='text' name='cle' required><br>
        <button type='submit'>Accéder</button>
    </form>
    """)

@app.route("/espace-client", methods=["POST"])
def espace_client():
    cle = request.form.get("cle", "").strip()
    clients = charger_json(CLIENTS_PATH)
    client = clients.get(cle)
    if not client:
        return "<h3>Clé invalide</h3><p>Aucun client trouvé.</p>"

    factures = charger_json(FACTURES_PATH).get("factures", [])
    galerie_privee = afficher_galerie(CLIENTS_GALLERY / f"{cle}.json")
    galerie_globale = afficher_galerie(GALLERY_GLOBAL) if client_a_acces(cle) else "<p>Accès refusé.</p>"

    html_factures = "<ul>"
    for f in factures:
        if f.get("client") == cle:
            produit = f.get("produit", "Inconnu")
            montant = f.get("montant", 0.0)
            statut = f.get("statut", "inconnu")
            html_factures += f"<li>{produit} - {montant} EUR - {statut}</li>"
    html_factures += "</ul>"

    return render_template_string(f"""
    <h2>Espace client : {client['nom']}</h2>
    <h3>Factures</h3>{html_factures}
    <h3>Galerie privée</h3>{galerie_privee}
    <h3>Galerie globale</h3>{galerie_globale}
    """)

# === Orchestration centrale
def run():
    identifiant = ajouter_client("Audrey", "audrey@luxuria.fr", "admin", "Nouvelle-Aquitaine")
    ajouter_cle("Audrey")
    generer_facture(identifiant, "Consultation IA")
    log("Initialisation automatique terminée.")

AssistantPDG.register("luxuria_ia", run)

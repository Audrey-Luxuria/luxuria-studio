# -*- coding: utf-8 -*-
"""Structure ajoutée automatiquement."""

import os
import sys
import json
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Initialisation
logging.basicConfig(level=logging.INFO)
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY or not API_KEY.startswith("sk-"):
    logging.error("Clé API manquante ou invalide dans .env.")
    sys.exit()

# === Chemins universels
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR.parent / "config"
STYLE_DIR = BASE_DIR.parent / "luxuria_fiches"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
STYLE_DIR.mkdir(parents=True, exist_ok=True)

CLIENTS_FILE = CONFIG_DIR / "clients.json"

# === Chargement ou création du fichier clients.json
if not CLIENTS_FILE.exists():
    logging.info("Création du fichier clients.json...")
    with CLIENTS_FILE.open("w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)

with CLIENTS_FILE.open("r", encoding="utf-8") as f:
    clients = json.load(f)

# === Saisie de la clé Luxuria
logging.info("Bienvenue dans Luxuria Pro")
cle_client = input("Entrez votre clé Luxuria : ").strip()

# === Vérification ou création du profil
if cle_client in clients:
    client = clients[cle_client]
    logging.info(f"Bonjour {client['nom']} ! Bienvenue dans ton atelier Luxuria.")
else:
    logging.info("Clé inconnue. Créons ton profil...")
    nom = input("Ton prénom : ").strip()
    email = input("Ton e-mail : ").strip()
    client = {
        "nom": nom,
        "email": email,
        "historique": [],
        "requetes": 0
    }
    clients[cle_client] = client
    logging.info(f"Profil créé pour {nom} avec la clé {cle_client}.")

# === Enregistrement de la session
client["requetes"] += 1
client["historique"].append({
    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "action": "Connexion à Luxuria"
})

with CLIENTS_FILE.open("w", encoding="utf-8") as f:
    json.dump(clients, f, indent=4, ensure_ascii=False)

# === Génération fictive du style Luxuria
logging.info("Préparation de ton style signature avec Luxuria...")
style = {
    "client": cle_client,
    "palette": ["#ff3cac", "#784ba0", "#2b86c5"],
    "typographie": "Luxuria Serif",
    "ambiance": "futuriste romantique"
}

description = (
    f"\nStyle généré pour {client['nom']} :\n"
    f"- Palette : {', '.join(style['palette'])}\n"
    f"- Typographie : {style['typographie']}\n"
    f"- Ambiance : {style['ambiance']}\n"
)
logging.info(description)

# === Export du style
STYLE_FILE = STYLE_DIR / f"{cle_client}_style.json"
with STYLE_FILE.open("w", encoding="utf-8") as f:
    json.dump(style, f, indent=4, ensure_ascii=False)

logging.info(f"Style enregistré dans : {STYLE_FILE}")

# === Fonction main
def main():
    """Point d'entrée modulaire pour Luxuria Pro."""
    pass

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_pro", run)

# -*- coding: utf-8 -*-
"""Luxuria Studio  Generateur de fiches clients et galerie IA."""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from flask import Flask, send_from_directory, jsonify
import requests
import openai

# === Configuration ===
logging.basicConfig(level=logging.INFO, format="[LUXURIA] %(message)s")
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise EnvironmentError("Cle API OpenAI manquante. Definis-la avec : export OPENAI_API_KEY='ta_cle'")

BASE_DIR = Path(__file__).resolve().parent
GALERIE_FILE = BASE_DIR / "galerie_commune.json"
CLIENTS_FILE = BASE_DIR / "clients.json"

# === Chargement des profils clients
def charger_clients() -> Dict[str, Dict[str, str]]:
    if not CLIENTS_FILE.exists():
        raise FileNotFoundError("Fichier clients.json introuvable.")
    with CLIENTS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

# === Generation de signature poetique
def generer_signature(client: Dict[str, str]) -> str:
    prompt = (
        "Tu es un assistant creatif pour une maison de design de luxe.\n"
        f"Style : {client['style']}\n"
        f"Diamant : {client['diamant']}\n"
        f"Couleur : {client['couleur']}\n"
        f"Motif : {client['motif']}\n"
        f"Symbole : {client['symbole']}\n"
        "Genere une signature stylistique Luxuria en une phrase poetique."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.info(f"Erreur GPT : {e}")
        return "Signature non disponible"

# === Generation dimage stylisee
def generer_image(client: Dict[str, str], identifiant: str) -> Optional[str]:
    prompt = (
        f"Portrait stylise avec le style '{client['style']}', diamant '{client['diamant']}', "
        f"couleur '{client['couleur']}', motif '{client['motif']}', symbole '{client['symbole']}'."
    )
    try:
        response = openai.Image.create(prompt=prompt, n=1, size="512x512")
        url = response["data"][0]["url"]
        image_path = BASE_DIR / f"{identifiant}_portrait.png"
        image_data = requests.get(url).content
        with open(image_path, "wb") as f:
            f.write(image_data)
        return image_path.name
    except Exception as e:
        logging.info(f"Erreur image : {e}")
        return None

# === Ajout a la galerie commune
def ajouter_a_galerie(client_nom: str, image_path: str, signature: str) -> None:
    galerie = {}
    if GALERIE_FILE.exists():
        try:
            with GALERIE_FILE.open("r", encoding="utf-8") as f:
                galerie = json.load(f)
        except json.JSONDecodeError:
            galerie = {}

    galerie.setdefault(client_nom, []).append({
        "image": image_path,
        "signature": signature
    })

    with GALERIE_FILE.open("w", encoding="utf-8") as f:
        json.dump(galerie, f, indent=2, ensure_ascii=False)

# === Creation des fiches enrichies
def creer_fiches_clients() -> None:
    clients = charger_clients()
    for identifiant, profil in clients.items():
        fiche_path = BASE_DIR / f"{identifiant}_fiche.json"
        if fiche_path.exists():
            logging.info(f"Fiche deja existante : {identifiant}")
            continue

        signature = generer_signature(profil)
        image_path = generer_image(profil, identifiant)

        fiche = profil.copy()
        fiche["signature_ia"] = signature
        fiche["image_ia"] = image_path or "non generee"
        fiche["intelligence_stylistique"] = "GPT-4 Luxuria Studio"

        with fiche_path.open("w", encoding="utf-8") as f:
            json.dump(fiche, f, indent=4, ensure_ascii=False)

        if image_path:
            ajouter_a_galerie(profil["nom"], image_path, signature)

        logging.info(f"Fiche enrichie + image generee : {identifiant}")

# === Interface Flask
app = Flask(__name__)

@app.route("/")
def accueil() -> str:
    clients = charger_clients()
    html = "<h1>Luxuria Studio  Portail client</h1><ul>"
    html += "<li><a href='/galerie-commune'>Galerie commune</a></li>"
    for identifiant in clients:
        html += f"<li><a href='/galerie-personnelle/{identifiant}'>Galerie personnelle : {identifiant.capitalize()}</a></li>"
    html += "</ul>"
    return html

@app.route("/galerie-personnelle/<identifiant>")
def galerie_personnelle(identifiant: str) -> str:
    clients = charger_clients()
    if identifiant not in clients:
        return "<h3>Client inconnu.</h3>"

    image_file = BASE_DIR / f"{identifiant}_portrait.png"
    if not image_file.exists():
        return "<h3>Aucune galerie personnelle trouvee.</h3>"

    return f"""
    <h2>Galerie personnelle de {identifiant.capitalize()}</h2>
    <img src='/{image_file.name}' width='200'>
    <br><a href="/"><button>Retour</button></a>
    """

@app.route("/galerie-commune")
def galerie_commune() -> str:
    if not GALERIE_FILE.exists():
        return "<h3>Aucune galerie commune disponible.</h3>"

    try:
        with GALERIE_FILE.open("r", encoding="utf-8") as f:
            galerie = json.load(f)
    except json.JSONDecodeError:
        return "<h3>Erreur de lecture de la galerie commune.</h3>"

    html = "<h2>Galerie commune Luxuria</h2>"
    for nom, creations in galerie.items():
        html += f"<h3>{nom}</h3>"
        for item in creations:
            image = item["image"]
            signature = item["signature"]
            html += f"<img src='/{image}' width='200'><p>{signature}</p>"

    html += "<br><a href='/'><button>Retour</button></a>"
    return html

@app.route("/<path:filename>")
def fichier_statique(filename):
    return send_from_directory(BASE_DIR, filename)

@app.route("/api/fiche/<identifiant>")
def api_fiche(identifiant: str):
    fiche_path = BASE_DIR / f"{identifiant}_fiche.json"
    if not fiche_path.exists():
        return jsonify({"error": "Fiche introuvable"}), 404
    with fiche_path.open("r", encoding="utf-8") as f:
        return jsonify(json.load(f))

# === Lancement
# Bloc __main__ supprimé pour modularisation

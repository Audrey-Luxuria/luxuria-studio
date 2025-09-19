# -*- coding: utf-8 -*-
"""Module de signature de charte et accès à la galerie commune - Luxuria Studio"""

from flask import Flask, request, render_template_string
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Dict
from assistant_pdg import AssistantPDG

app = Flask(__name__)
SIGNATURES_FILE = Path(__file__).resolve().parent / "signatures_charte.json"

logging.basicConfig(level=logging.INFO, format="[GALERIE] %(message)s")

def load_signatures() -> Dict[str, Dict[str, str]]:
    if not SIGNATURES_FILE.is_file():
        logging.info("Fichier de signatures non trouvé. Initialisation.")
        return {}
    try:
        with SIGNATURES_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.warning("Fichier de signatures corrompu.")
        return {}

def save_signature(client_key: str, ip: str) -> None:
    signatures = load_signatures()
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")
    signatures[client_key] = {
        "horodatage": horodatage,
        "ip": ip
    }
    try:
        with SIGNATURES_FILE.open("w", encoding="utf-8") as f:
            json.dump(signatures, f, indent=4, ensure_ascii=False)
        logging.info(f"Signature enregistrée pour {client_key} ({ip})")
    except OSError as e:
        logging.error(f"Erreur d'enregistrement : {e}")

@app.route("/galerie_commune")
def galerie_commune():
    client_key = request.args.get("client_key", "").strip()
    if not client_key:
        return "Clé client manquante", 400

    ip = request.remote_addr or "inconnue"
    signatures = load_signatures()

    if client_key not in signatures:
        save_signature(client_key, ip)
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")
        charte_html = f"""
        <div style="background-color:#f9f9f9; padding:15px; border:1px solid #ccc;">
            <h2>Charte d'utilisation de la galerie commune</h2>
            <ul>
                <li>Les visuels sont visibles uniquement par les membres autorisés.</li>
                <li>Ils ne doivent pas être copiés ou diffusés hors du cadre Luxuria.</li>
                <li>Chaque visuel est marqué par une signature électronique.</li>
                <li>Le dépôt vaut acceptation de la charte.</li>
            </ul>
            <p style="font-size:12px; color:#666;">
              Signature : {client_key} - {horodatage} - IP : {ip}
            </p>
        </div>
        """
        return render_template_string(charte_html)

    return render_template_string("<h2>Bienvenue dans la galerie commune</h2>")

@app.route("/interface_admin")
def interface_admin():
    signatures = load_signatures()
    html = "<h2>Signatures de la charte</h2><ul>"
    for client, data in signatures.items():
        html += f"<li>{client} - {data['horodatage']} - IP : {data['ip']}</li>"
    html += "</ul>"
    return render_template_string(html)

# === Orchestration centralisée
def run():
    logging.info("Lancement du serveur Flask pour la galerie commune...")
    app.run(debug=False, port=5000, use_reloader=False)


AssistantPDG.register("galerie_commune", run)

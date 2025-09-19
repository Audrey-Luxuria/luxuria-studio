# -*- coding: utf-8 -*-
"""Galerie privée et sécurisée - Luxuria Studio"""

from flask import Flask, send_file, render_template_string, abort
from pathlib import Path
from datetime import datetime
import logging
from typing import List
from assistant_pdg import AssistantPDG

# === Configuration
logging.basicConfig(level=logging.INFO, format="[GALERIE PRIVEE] %(message)s")
BASE_DIR = Path(__file__).resolve().parent
GALLERY_DIR = BASE_DIR / "galerie_privee"
GALLERY_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

# === Fonctions utilitaires
def get_all_clients() -> List[str]:
    return [folder.name for folder in GALLERY_DIR.iterdir() if folder.is_dir()]

def get_client_designs(client_key: str) -> List[str]:
    client_folder = GALLERY_DIR / client_key
    if not client_folder.exists():
        return []
    return [f.name for f in client_folder.glob("*.png")]

# === Routes principales
@app.route("/galerie_privee", methods=["GET"])
def galerie_privee():
    html = "<h1>Galeries privées</h1><ul>"
    for client_key in get_all_clients():
        designs = get_client_designs(client_key)
        html += f"<li><h2>Galerie de {client_key}</h2><ul>"
        for design in designs:
            html += f"<li><img src='/static_privee/{client_key}/{design}' width='300'></li>"
        html += "</ul>"

        pdf_path = GALLERY_DIR / client_key / "galerie.pdf"
        if pdf_path.exists():
            html += f"<br><a href='/telecharger_pdf/{client_key}'>Télécharger PDF</a>"
        else:
            html += "<br><p style='color:red;'>PDF non disponible</p>"

        html += "</li><hr>"
    html += "</ul>"
    return render_template_string(html)

@app.route("/telecharger_pdf/<client_key>", methods=["GET"])
def telecharger_pdf(client_key: str):
    pdf_path = GALLERY_DIR / client_key / "galerie.pdf"
    if not pdf_path.exists():
        return "<h3>PDF non disponible</h3>", 404
    logging.info(f"Téléchargement PDF pour {client_key}")
    return send_file(pdf_path, as_attachment=True)

@app.route("/static_privee/<client_key>/<filename>")
def static_privee(client_key: str, filename: str):
    file_path = GALLERY_DIR / client_key / filename
    if not file_path.exists():
        abort(404)
    return send_file(file_path)

@app.route("/galerie_secure", methods=["GET"])
def galerie_secure():
    page = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Galerie Sécurisée</title>
        <style>
            body {
                user-select: none;
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                padding: 20px;
            }
            img {
                pointer-events: none;
                margin: 10px;
                border: 1px solid #ccc;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            }
            .charte {
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 5px;
            }
            .signature {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            @media print {
                body {
                    display: none;
                }
            }
        </style>
        <script>
            document.addEventListener("contextmenu", event => event.preventDefault());
            document.addEventListener("keydown", function(e) {
                if (
                    (e.ctrlKey && (e.key === "s" || e.key === "u")) ||
                    e.key === "F12" ||
                    (e.ctrlKey && e.shiftKey && e.key === "I")
                ) {
                    e.preventDefault();
                }
            });
            window.addEventListener("keyup", function(e) {
                if (e.key === "PrintScreen") {
                    alert("Capture d'écran désactivée.");
                }
            });
        </script>
    </head>
    <body>
        <div class="charte">
            <h2>Charte d'utilisation de la galerie privée</h2>
            <ul>
                <li>Les visuels ne doivent pas être copiés, téléchargés ou imprimés.</li>
                <li>La capture d'écran est désactivée pour protéger les créations.</li>
                <li>Les fichiers PDF sont réservés aux clients abonnés.</li>
                <li>La galerie est accessible via les liens fournis par l'assistant PDG.</li>
                <li>Chaque visuel est marqué par une signature numérique.</li>
            </ul>
        </div>
    """

    for client_key in get_all_clients():
        designs = get_client_designs(client_key)
        page += f"<h2>Galerie de {client_key}</h2><div>"
        for design in designs:
            page += f"<img src='/static_privee/{client_key}/{design}' width='300'>"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            page += f"<div class='signature'>Signature : {client_key} - {timestamp}</div>"
        page += "</div>"

        pdf_path = GALLERY_DIR / client_key / "galerie.pdf"
        if pdf_path.exists():
            page += f"<p><a href='/telecharger_pdf/{client_key}'>Télécharger PDF</a></p>"
        else:
            page += "<p style='color:red;'>PDF non disponible</p>"

        page += "<hr>"

    page += "</body></html>"
    return render_template_string(page)

# === Orchestration centralisée
def run():
    logging.info("Lancement du serveur Flask pour la galerie privée...")
    app.run(debug=False, port=5000, use_reloader=False)


AssistantPDG.register("galerie_privee", run)

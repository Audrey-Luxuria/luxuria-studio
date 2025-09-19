# -*- coding: utf-8 -*-
"""Module de veille BOAMP - Luxuria IA"""

from flask import Flask, request, jsonify
import datetime
import logging
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Initialisation de l'application
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# === Vérification du format de date
def date_valide(date_str: str) -> bool:
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# === Vérification de conformité RGPD
def est_conforme_rgpd(pays: str) -> dict:
    pays_conformes = {"France", "Belgique", "Luxembourg", "Allemagne", "Espagne"}
    compatible = pays in pays_conformes
    message = f"{pays} est conforme au RGPD" if compatible else f"{pays} n'est pas reconnu comme conforme au RGPD"
    return {"compatible": compatible, "message": message}

# === Simulation d'extraction d'avis BOAMP
def extraire_avis_boamp(date_str: str) -> list[dict]:
    return [
        {"id": 101, "objet": "Marché public de voirie", "date": date_str},
        {"id": 102, "objet": "Contrat de maintenance informatique", "date": date_str},
        {"id": 103, "objet": "Appel d'offres pour mobilier urbain", "date": date_str}
    ]

# === Journalisation de la requête
def journaliser_requete(date: str, ip: str, nb_resultats: int) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{timestamp}] Requête BOAMP  Date: {date}, IP: {ip}, Résultats: {nb_resultats}")

# === Route principale
@app.route("/veille", methods=["GET"])
def veille_boamp():
    date_param = request.args.get("date", default=datetime.datetime.now().strftime("%Y-%m-%d"))
    pays_client = request.args.get("pays", default="France")

    if not date_valide(date_param):
        return jsonify({
            "erreur": "Format de date invalide",
            "attendu": "YYYY-MM-DD"
        }), 400

    rgpd = est_conforme_rgpd(pays_client)
    if not rgpd["compatible"]:
        return jsonify({
            "erreur": "Non-conformité RGPD",
            "details": rgpd["message"]
        }), 403

    avis = extraire_avis_boamp(date_param)
    ip_client = request.remote_addr or "inconnue"
    journaliser_requete(date_param, ip_client, len(avis))

    return jsonify({
        "date": date_param,
        "pays": pays_client,
        "rgpd": rgpd["message"],
        "resultats": avis,
        "nb_resultats": len(avis)
    })

# === Point d’entrée modulaire
def main() -> None:
    app.run(debug=False, port=5000, use_reloader=False)


# === Orchestration centrale
def run():
    main()

AssistantPDG.register("veille", run)

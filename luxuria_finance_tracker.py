# -*- coding: utf-8 -*-
"""Luxuria Finance Tracker  Suivi des transactions clients (module orchestre)."""

import json
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from json.decoder import JSONDecodeError

# === Chemins
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "luxuria_fiches"
FINANCE_DIR = DATA_DIR / "finance_clients"
DASHBOARD_PATH = ROOT_DIR / "admin_private" / "admin.html"
LOG_PATH = ROOT_DIR / "admin_private" / "luxuria_finance.log"

FINANCE_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# === Logger
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_activite(message: str, niveau: str = "info") -> None:
    if hasattr(logging, niveau):
        getattr(logging, niveau)(message)

# === Enregistrement de transaction
def enregistrer_transaction(client_id: str, fonction: str, montant: float) -> str:
    if not client_id.strip():
        return " Identifiant client invalide."
    if montant <= 0:
        return " Montant invalide. Doit etre positif."

    fichier = FINANCE_DIR / f"{client_id}.json"
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    registre = {"solde_total": 0.0, "transactions": []}
    if fichier.exists():
        try:
            registre = json.loads(fichier.read_text(encoding="utf-8"))
        except JSONDecodeError:
            log_activite(f" Fichier corrompu pour {client_id}", "warning")

    transaction = {
        "date": horodatage,
        "fonction": fonction,
        "montant": montant
    }

    registre["transactions"].append(transaction)
    registre["solde_total"] += montant

    try:
        fichier.write_text(json.dumps(registre, indent=2, ensure_ascii=True), encoding="utf-8")
        log_activite(f" Transaction enregistree : {client_id} / {fonction} / +{montant:.2f}")
        return f" Transaction enregistree pour {client_id} (+{montant:.2f})"
    except OSError as e:
        log_activite(f" Erreur ecriture fichier : {e}", "error")
        return f" Echec enregistrement pour {client_id}"

# === Analyse globale
def collecter_transactions() -> list:
    donnees = []
    for fichier in FINANCE_DIR.glob("*.json"):
        try:
            registre = json.loads(fichier.read_text(encoding="utf-8"))
            donnees.extend(registre.get("transactions", []))
        except JSONDecodeError:
            log_activite(f" Fichier illisible : {fichier.name}", "warning")
    return donnees

def analyser_par_mois(transactions: list):
    par_mois = defaultdict(float)
    par_annee = defaultdict(float)

    for t in transactions:
        try:
            dt = datetime.strptime(t["date"], "%Y-%m-%d %H:%M:%S")
            cle_mois = dt.strftime("%Y-%m")
            cle_annee = dt.strftime("%Y")
            montant = float(t["montant"])
            par_mois[cle_mois] += montant
            par_annee[cle_annee] += montant
        except (KeyError, ValueError):
            continue

    return par_mois, par_annee

def estimer_revenu_suivant(par_mois: dict) -> float:
    mois_tries = sorted(par_mois.keys())[-3:]
    if not mois_tries:
        return 0.0
    total = sum(par_mois[m] for m in mois_tries)
    return round(total / len(mois_tries), 2)

# === Generation du dashboard HTML interactif
def generer_dashboard() -> None:
    transactions = collecter_transactions()
    par_mois, par_annee = analyser_par_mois(transactions)
    estimation = estimer_revenu_suivant(par_mois)

    mois_labels = sorted(par_mois.keys())
    mois_values = [round(par_mois[m], 2) for m in mois_labels]

    annee_labels = sorted(par_annee.keys())
    annee_values = [round(par_annee[a], 2) for a in annee_labels]

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dashboard Luxuria</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1> Dashboard Financier Luxuria</h1>

    <h2> Montants par mois</h2>
    <canvas id="chartMois" width="600" height="300"></canvas>

    <h2> Montants par annee</h2>
    <canvas id="chartAnnee" width="600" height="300"></canvas>

    <h2> Estimation du mois suivant</h2>
    <p>Moyenne des 3 derniers mois : <strong>{estimation:.2f} EUR</strong></p>

    <script>
        const ctxMois = document.getElementById('chartMois').getContext('2d');
        new Chart(ctxMois, {{
            type: 'bar',
            data: {{
                labels: {mois_labels},
                datasets: [{{
                    label: 'Montants mensuels (EUR)',
                    data: {mois_values},
                    backgroundColor: 'rgba(54, 162, 235, 0.6)'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        const ctxAnnee = document.getElementById('chartAnnee').getContext('2d');
        new Chart(ctxAnnee, {{
            type: 'line',
            data: {{
                labels: {annee_labels},
                datasets: [{{
                    label: 'Montants annuels (EUR)',
                    data: {annee_values},
                    borderColor: 'rgba(255, 99, 132, 1)',
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    try:
        DASHBOARD_PATH.write_text(html, encoding="utf-8")
        log_activite(" Dashboard HTML interactif genere avec succes.")
    except OSError as e:
        log_activite(f" Erreur ecriture dashboard : {e}", "error")

# === Fonction orchestrable depuis assistant_pdg.py
def suivi_financier_automatique() -> None:
    log_activite(" Lancement du suivi financier automatise")
    generer_dashboard()
    log_activite(" Suivi financier termine")

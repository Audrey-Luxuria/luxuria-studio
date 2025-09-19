# -*- coding: utf-8 -*-
"""Déclaration URSSAF mensuelle - Luxuria IA"""

import json
import logging
from datetime import datetime
from pathlib import Path
from fpdf import FPDF
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Répertoires
ROOT = Path(__file__).resolve().parent
PRIVATE_DIR = ROOT / "admin_private"
DECLARATIONS_DIR = ROOT / "LuxuriaProject" / "autonomie_ia" / "declarations_urssaf"
ADMIN_HTML = ROOT / "LuxuriaProject" / "admin.html"

PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
DECLARATIONS_DIR.mkdir(parents=True, exist_ok=True)

# === Fichiers clés
RAPPORT_JSON = PRIVATE_DIR / "rapport_urssaf.json"
LOG_FILE = PRIVATE_DIR / "luxuria_journal.log"

# === Journalisation
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)

def log(message: str, level: str = "info") -> None:
    getattr(logging, level)(message)

# === Gestion JSON
def charger_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception as e:
        log(f"Erreur lecture JSON : {e}", "error")
        return {}

def sauvegarder_json(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log(f"Erreur sauvegarde JSON : {e}", "error")

# === Paramètres fiscaux
REGIME_FISCAL = {
    "statut": "EI",
    "activite": "SaaS",
    "taux": 0.22,
    "seuil_max": 1800.00
}

# === Calcul URSSAF
def calculer_urssaf(revenus: float) -> dict:
    taux = REGIME_FISCAL["taux"]
    cotisations = round(revenus * taux, 2)
    net = round(revenus - cotisations, 2)

    if cotisations > REGIME_FISCAL["seuil_max"]:
        log(f"Cotisations bloquées : {cotisations:.2f} EUR dépassent le seuil", "warning")
        return {
            "Revenus déclarés": revenus,
            "Taux URSSAF": f"{taux * 100:.1f}%",
            "Cotisations": "Blocage automatique",
            "Net après cotisation": "Non calculé",
            "Statut": "Déclaration suspendue"
        }

    return {
        "Revenus déclarés": revenus,
        "Taux URSSAF": f"{taux * 100:.1f}%",
        "Cotisations": cotisations,
        "Net après cotisation": net,
        "Statut": "Déclaration validée"
    }

# === Génération PDF
def generer_pdf(donnees: dict, mois: str) -> str:
    fichier = DECLARATIONS_DIR / f"declaration_urssaf_{mois}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Déclaration URSSAF mensuelle", ln=1, align="C")
    pdf.ln(5)
    pdf.cell(0, 10, f"Mois : {mois}", ln=1)
    pdf.ln(5)

    for k, v in donnees.items():
        ligne = f"{k} : {v if isinstance(v, str) else f'{v:.2f} EUR'}"
        pdf.cell(0, 10, ligne, ln=1)

    try:
        pdf.output(str(fichier))
        log(f"PDF généré : {fichier.resolve()}")
        return str(fichier)
    except Exception as e:
        log(f"Erreur génération PDF : {e}", "error")
        return ""

# === Notifications HTML
def notifier_admin(mois: str, chemin_pdf: str) -> None:
    horodatage = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nom = Path(chemin_pdf).name
    lien = f"./autonomie_ia/declarations_urssaf/{nom}"

    bloc = (
        f"<div class='notification'>\n"
        f"  <p><strong>{horodatage}</strong> Déclaration URSSAF générée pour <em>{mois}</em>. "
        f"<a href='{lien}' download>Télécharger le PDF</a> (à signer manuellement).</p>\n"
        f"</div>\n"
    )

    try:
        with open(ADMIN_HTML, "a", encoding="utf-8") as f:
            f.write(bloc)
        log("Notification ajoutée à admin.html")
    except Exception as e:
        log(f"Erreur notification admin : {e}", "error")

def ajouter_tableau_admin(mois: str, donnees: dict) -> None:
    lignes = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>\n" for k, v in donnees.items()])
    tableau = (
        f"<h3>Déclaration URSSAF {mois}</h3>\n"
        f"<table border='1' cellpadding='5'>\n"
        f"<thead><tr><th>Élément</th><th>Valeur</th></tr></thead>\n"
        f"<tbody>\n{lignes}</tbody>\n</table>\n"
    )

    try:
        with open(ADMIN_HTML, "a", encoding="utf-8") as f:
            f.write(tableau)
        log("Tableau URSSAF ajouté à admin.html")
    except Exception as e:
        log(f"Erreur ajout tableau admin : {e}", "error")

# === Déclaration mensuelle
def declarer_urssaf(mois: str, revenus: float) -> None:
    donnees = calculer_urssaf(revenus)
    chemin_pdf = generer_pdf(donnees, mois)
    notifier_admin(mois, chemin_pdf)
    ajouter_tableau_admin(mois, donnees)

# === Création du rapport JSON
def creer_rapport(mois: str) -> None:
    data = charger_json(RAPPORT_JSON)
    rapports = data.get("rapports", [])

    if any(r.get("mois") == mois for r in rapports):
        log(f"Rapport déjà existant pour {mois}")
        return

    revenus = 4200.00  # Valeur par défaut
    donnees = calculer_urssaf(revenus)
    chemin_pdf = generer_pdf(donnees, mois)

    rapport = {
        "mois": mois,
        "pdf_bilan": Path(chemin_pdf).name,
        "envoye": False,
        "horodatage": datetime.now().isoformat(),
        "status": "en attente de signature"
    }

    rapports.append(rapport)
    data["rapports"] = rapports
    data["meta"] = {
        "structure": "Luxuria IA - Rapports URSSAF mensuels",
        "source": str(RAPPORT_JSON),
        "dernier_update": datetime.now().isoformat(),
        "notes": "Généré automatiquement. Signature manuelle requise."
    }

    sauvegarder_json(RAPPORT_JSON, data)
    notifier_admin(mois, chemin_pdf)
    log(f"Rapport URSSAF créé pour {mois}")

# === Point d’entrée modulaire
def main():
    mois = datetime.now().strftime("%m-%Y")
    log(f"Initialisation de la déclaration URSSAF pour {mois}")
    creer_rapport(mois)

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("module_declaration_urssaf", run)

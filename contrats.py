# -*- coding: utf-8 -*-
"""Gestion des contrats SaaS Luxuria — version statique et robuste."""

import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from deep_translator import GoogleTranslator
from fpdf import FPDF

logging.basicConfig(level=logging.INFO, format="[CONTRAT] %(message)s")

LEGAL_PROFILES = {
    "FR": {
        "juridiction": "Conformément au droit français et au RGPD",
        "remboursement": "non-remboursable après 7 jours d’essai gratuit",
        "renouvellement": "automatique sauf résiliation 15 jours avant échéance"
    },
    "US": {
        "juridiction": "Conformément aux lois de l’État du Delaware",
        "remboursement": "non-remboursable après période d’essai",
        "renouvellement": "automatique sauf résiliation 30 jours avant échéance"
    },
    "CA": {
        "juridiction": "Conformément à la loi canadienne sur la protection des renseignements personnels",
        "remboursement": "non-remboursable après 7 jours d’essai",
        "renouvellement": "automatique sauf résiliation 20 jours avant échéance"
    }
}

class PDFContrat(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path

    def header(self):
        if self.logo_path and Path(self.logo_path).exists():
            self.image(self.logo_path, x=10, y=8, w=30)
        self.set_font("Arial", size=14)
        self.cell(0, 10, "Contrat SaaS Luxuria", ln=1)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, "Luxuria - Confidential", ln=1, align="C")

class ContratManager:
    def __init__(self, dossier_base: Path, fichier_db="contrats.json", dossier_pdf="pdfs", fichier_html="client.html"):
        self.base = dossier_base.resolve()
        self.db_path = self.base / fichier_db
        self.pdf_dir = self.base / dossier_pdf
        self.html_path = self.base / fichier_html
        self.codes_envoyes = {}
        self.pdf_dir.mkdir(exist_ok=True)

    @staticmethod
    def generer_contrat(nom: str, prenom: str, email: str, pays: str, langue: str = "fr") -> str:
        date_signature = datetime.now().strftime("%Y-%m-%d")
        profil = LEGAL_PROFILES.get(pays.upper(), LEGAL_PROFILES["FR"])

        texte = f"""
Contrat SaaS Luxuria
Client : {prenom} {nom}
Email : {email}
Date de signature : {date_signature}

1. Objet du contrat
Ce contrat encadre l’utilisation des services SaaS de Luxuria.

2. Durée et résiliation
Durée initiale de 12 mois, {profil['renouvellement']}.

3. Essai gratuit et politique de remboursement
Le client bénéficie d’un essai gratuit de 7 jours. Passé ce délai, le service est {profil['remboursement']}.

4. Confidentialité
Les données du client sont confidentielles et ne sont ni revendues ni partagées.

5. Protection des données personnelles
{profil['juridiction']}

6. Signature électronique
Ce contrat est signé électroniquement et enregistré dans le registre sécurisé de Luxuria.
"""
        if langue.lower() != "fr":
            return GoogleTranslator(source="fr", target=langue).translate(texte)
        return texte

    def enregistrer_contrat(self, contrat_data: dict) -> None:
        contrats = []
        if self.db_path.exists():
            try:
                with self.db_path.open("r", encoding="utf-8") as f:
                    contrats = json.load(f)
            except json.JSONDecodeError:
                logging.warning("Fichier JSON mal formé.")
        contrats.append(contrat_data)
        with self.db_path.open("w", encoding="utf-8") as f:
            json.dump(contrats, f, indent=2, ensure_ascii=False)
        logging.info("Contrat enregistré.")

    @staticmethod
    def exporter_pdf(texte_contrat: str, chemin_pdf: Path, logo_path: Path = None) -> None:
        pdf = PDFContrat(logo_path=logo_path)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for ligne in texte_contrat.split("\n"):
            pdf.multi_cell(0, 10, ligne)
        pdf.output(str(chemin_pdf))
        logging.info(f"PDF exporté : {chemin_pdf.name}")

    def envoyer_code_sms(self, tel: str) -> str:
        code = str(random.randint(100000, 999999))
        self.codes_envoyes[tel] = {"code": code, "timestamp": time.time()}
        logging.info(f"[SIMULATION SMS] Code envoyé à {tel} : {code}")
        return code

    def verifier_code(self, tel: str, code_saisi: str) -> bool:
        infos = self.codes_envoyes.get(tel)
        if not infos or time.time() - infos["timestamp"] > 300:
            return False
        return infos["code"] == code_saisi

    def ajouter_notification_client(self, nom: str, prenom: str) -> None:
        bloc = f"""
<div class="notification-renouvellement">
  <h3>Bonjour {prenom} {nom},</h3>
  <p>Votre contrat Luxuria sera automatiquement renouvelé dans 30 jours.</p>
  <p>Vous pouvez le modifier ou le résilier depuis votre espace client.</p>
</div>
"""
        self.html_path.parent.mkdir(exist_ok=True)
        with self.html_path.open("a", encoding="utf-8") as f:
            f.write(bloc)

    @staticmethod
    def afficher_historique(historique: list) -> None:
        for contrat in historique:
            logging.info(f"Contrat du {contrat['date']} — {contrat['statut']}")

# === Orchestration centralisée
def run():
    dossier = Path(__file__).resolve().parent
    manager = ContratManager(dossier)
    contrat = manager.generer_contrat("Dupont", "Audrey", "audrey@example.com", "FR")
    pdf_path = manager.pdf_dir / "contrat_demo.pdf"
    manager.exporter_pdf(contrat, pdf_path)
    manager.enregistrer_contrat({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "statut": "généré",
        "client": "Audrey Dupont",
        "contenu": contrat
    })
    manager.ajouter_notification_client("Dupont", "Audrey")

# Enregistrement dans l’orchestrateur
from assistant_pdg import AssistantPDG
AssistantPDG.register("contrats", run)

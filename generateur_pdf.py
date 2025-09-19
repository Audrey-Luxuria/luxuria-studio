# -*- coding: utf-8 -*-
"""Générateur de contrat PDF - Luxuria Studio"""

import logging
from pathlib import Path
from typing import Optional
from fpdf import FPDF
from assistant_pdg import AssistantPDG

logging.basicConfig(level=logging.INFO, format="[PDF] %(message)s")

class GenerateurPDF:
    def __init__(self, dossier_pdf: str = "pdfs", logo_path: Optional[str] = None) -> None:
        self.dossier = Path(dossier_pdf)
        self.dossier.mkdir(exist_ok=True)
        self.logo_path = Path(logo_path) if logo_path else None

    def creer_pdf(self, prenom: str, nom: str, texte_contrat: str) -> Optional[Path]:
        nom_fichier = f"{prenom}_{nom}_contrat.pdf"
        chemin = self.dossier / nom_fichier

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Logo en haut à gauche
        if self.logo_path and self.logo_path.is_file():
            try:
                pdf.image(str(self.logo_path), x=10, y=8, w=30)
                pdf.ln(20)
                logging.info("Logo inséré dans le PDF.")
            except RuntimeError:
                logging.warning("Logo invalide ou introuvable.")

        # Titre
        pdf.cell(0, 10, "Contrat SaaS Luxuria", ln=1)
        pdf.ln(5)

        # Texte du contrat
        for ligne in texte_contrat.split("\n"):
            pdf.multi_cell(0, 10, ligne)

        # Filigrane discret en bas
        pdf.set_y(-15)
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(180, 180, 180)
        pdf.cell(0, 10, "Luxuria - Confidential", ln=1)

        try:
            pdf.output(str(chemin))
            logging.info(f"✅ PDF généré avec succès : {chemin.name}")
            return chemin
        except Exception as err:
            logging.error(f"❌ Erreur lors de la création du PDF : {err}")
            return None

# === Orchestration centralisée
def run():
    prenom = "Audrey"
    nom = "Dupont"
    texte = (
        "Contrat SaaS Luxuria\n"
        "Client : Audrey Dupont\n"
        f"Date : {Path(__file__).stat().st_mtime_ns // 1_000_000_000}\n"
        "Conditions :\n"
        "- Accès sécurisé à la galerie privée\n"
        "- Génération de visuels personnalisés\n"
        "- Assistance stylistique IA\n"
        "- Clause de confidentialité renforcée"
    )

    pdf_gen = GenerateurPDF(logo_path="assets/luxuria_logo.png")
    pdf_gen.creer_pdf(prenom, nom, texte)

AssistantPDG.register("generateur_pdf", run)

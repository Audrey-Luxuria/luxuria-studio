# -*- coding: utf-8 -*-
"""Génération automatique de déclaration d'entreprise - Luxuria Studio"""

from fpdf import FPDF
from datetime import date
from pathlib import Path
import logging
from assistant_pdg import AssistantPDG

logging.basicConfig(level=logging.INFO, format="[DECLARATION] %(message)s")

class DeclarationEntreprise:
    def __init__(self) -> None:
        self.nom_complet = "Audrey Platel"
        self.activite = "Logiciel pour design d'objets de luxe"
        self.adresse = "9 rue des Rochettes, 87300 Bellac"
        self.email = "audreymoreau290913@gmail.com"
        self.numero_tel = "07 81 94 25 78"
        self.date_declaration = date.today().strftime("%Y-%m-%d")
        self.statut = "Entreprise Individuelle (EI)"
        self.code_ape = "7410Z - Activités de design"
        self.numero_siret = self._generer_siret()
        self.dossier_pdf = Path("documents")
        self.dossier_pdf.mkdir(exist_ok=True)

    def _generer_siret(self) -> str:
        base = f"88{date.today().year}0"
        suffixe = f"{abs(hash(self.nom_complet)) % 100000:05d}"
        return base + suffixe

    def generer_pdf(self) -> str:
        nom_fichier = "declaration_EI_Luxuria.pdf"
        chemin = self.dossier_pdf / nom_fichier

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Déclaration d'Entreprise Individuelle", ln=1, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(5)

        infos = [
            f"Nom : {self.nom_complet}",
            f"Activité : {self.activite}",
            f"Adresse : {self.adresse}",
            f"Email : {self.email}",
            f"Téléphone : {self.numero_tel}",
            f"Date de déclaration : {self.date_declaration}",
            f"Statut juridique : {self.statut}",
            f"Code APE : {self.code_ape}",
            f"Numéro SIRET : {self.numero_siret}"
        ]

        for ligne in infos:
            pdf.cell(0, 10, ligne, ln=1)

        pdf.ln(10)
        texte = (
            "Étapes suivantes :\n"
            "1. Dépôt de la déclaration sur le site du Guichet Unique\n"
            "   (https://formalites.entreprises.gouv.fr)\n"
            "2. Attente de validation par l'INSEE\n"
            "3. Réception du certificat d'immatriculation\n"
            "4. Ouverture d'un compte bancaire professionnel\n"
            "5. Déclaration URSSAF pour les cotisations sociales\n"
            "6. Choix du régime fiscal (micro-BNC, réel simplifié, etc.)\n\n"
            "Ce document est généré automatiquement par le système Luxuria."
        )
        pdf.multi_cell(0, 10, texte)

        pdf.output(str(chemin))
        logging.info(f"📄 PDF généré : {chemin.name}")
        return chemin.name

# === Orchestration centralisée
def run():
    declaration = DeclarationEntreprise()
    declaration.generer_pdf()

AssistantPDG.register("declaration_entreprise", run)

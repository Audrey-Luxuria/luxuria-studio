# -*- coding: utf-8 -*-
"""Générateur de processus de fabrication PDF - Luxuria Design"""

from fpdf import FPDF
from datetime import date
from pathlib import Path
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

class ProcessusFabricationPDF:
    def __init__(self, dossier_pdf: str = "processus_design", logo_path: str = None) -> None:
        self.dossier = Path(dossier_pdf)
        self.dossier.mkdir(parents=True, exist_ok=True)
        self.logo_path = Path(logo_path) if logo_path else None

    def generer_pdf(self, client_nom: str, type_design: str, materiaux: list, paiement_valide: bool) -> Path | None:
        if not paiement_valide:
            print(f"Accès refusé : le client {client_nom} n’a pas encore réglé.")
            return None

        nom_fichier = f"{client_nom.replace(' ', '_')}_processus_design.pdf"
        chemin_pdf = self.dossier / nom_fichier

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        # Logo
        if self.logo_path and self.logo_path.is_file():
            try:
                pdf.image(str(self.logo_path), x=10, y=8, w=30)
                pdf.ln(25)
            except Exception as e:
                print(f"Erreur lors de l’ajout du logo : {e}")

        # Titre principal
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Processus de Fabrication du Design", ln=1, align="C")
        pdf.ln(5)

        # Informations client
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Client : {client_nom}", ln=1)
        pdf.cell(0, 10, f"Type de design : {type_design}", ln=1)
        pdf.cell(0, 10, f"Date : {date.today().strftime('%d/%m/%Y')}", ln=1)
        pdf.ln(5)

        # Étapes du processus
        etapes = [
            ("1. Brief créatif", "Échange approfondi avec le client pour cerner les attentes, les inspirations et les contraintes techniques."),
            ("2. Moodboard & esquisses", "Création d’un univers visuel cohérent avec croquis, palettes de couleurs et textures."),
            ("3. Modélisation 3D", "Réalisation d’un modèle 3D pour valider les proportions, volumes et rendus."),
            ("4. Sélection des matériaux", "Matériaux choisis pour ce projet :\n" + "\n".join(f"- {m}" for m in materiaux)),
            ("5. Prototype physique", "Fabrication d’un prototype pour tester l’ergonomie, la solidité et l’esthétique."),
            ("6. Ajustements & validation", "Modifications selon les retours client avant validation finale."),
            ("7. Fabrication finale", "Production dans nos ateliers partenaires avec contrôle qualité à chaque étape."),
            ("8. Inspection & livraison", "Inspection minutieuse avant expédition. Livraison avec certificat d’authenticité."),
        ]

        for titre, contenu in etapes:
            pdf.set_font("Arial", 'B', 13)
            pdf.cell(0, 10, titre, ln=1)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, contenu)
            pdf.ln(3)

        # Signature visuelle
        pdf.set_y(-30)
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, "Luxuria Design  •  Élégance & précision sur mesure", ln=1, align="C")

        try:
            pdf.output(str(chemin_pdf))
            print(f"PDF généré avec succès : {chemin_pdf}")
            return chemin_pdf
        except Exception as e:
            print(f"Erreur lors de la création du PDF : {e}")
            return None

# === Exemple d’utilisation
def main() -> None:
    client = "Audrey Dupont"
    design = "Table basse en marbre et laiton"
    materiaux = ["Marbre noir Marquina", "Laiton poli", "Verre trempé"]
    paiement = True  # À vérifier dynamiquement dans ton système

    generateur = ProcessusFabricationPDF(logo_path="assets/luxuria_logo.png")
    generateur.generer_pdf(client_nom=client, type_design=design, materiaux=materiaux, paiement_valide=paiement)

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("processus_design", run)

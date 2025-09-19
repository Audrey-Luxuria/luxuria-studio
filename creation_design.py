# -*- coding: utf-8 -*-
"""Module de création de design personnalisé - Luxuria Studio"""

import uuid
from datetime import datetime
import logging
from typing import Optional
from assistant_pdg import AssistantPDG

logging.basicConfig(level=logging.INFO, format="[DESIGN] %(message)s")

class CreationDesign:
    def __init__(self, client_nom: str) -> None:
        self.client_nom = client_nom
        self.design_id = str(uuid.uuid4())
        self.instructions = ""
        self.croquis_genere = None
        self.touche_personnelle = ""
        self.design_final = None
        self.date_creation = datetime.now().strftime("%Y-%m-%d %H:%M")

    def ajouter_instructions(self, texte: str) -> None:
        self.instructions = texte.strip()
        logging.info(f"Instructions enregistrées : {self.instructions}")

    def generer_croquis(self) -> Optional[str]:
        if not self.instructions:
            logging.warning("Veuillez fournir des instructions avant de générer un croquis.")
            return None
        self.croquis_genere = f"Croquis généré selon les instructions : {self.instructions}"
        logging.info(f"Croquis généré : {self.croquis_genere}")
        return self.croquis_genere

    def ajouter_touche_personnelle(self, ajout: str) -> Optional[str]:
        if not self.croquis_genere:
            logging.warning("Aucun croquis généré à personnaliser.")
            return None
        self.touche_personnelle = ajout.strip()
        self.design_final = f"{self.croquis_genere}\n+ Touche personnelle : {self.touche_personnelle}"
        logging.info(f"Design final personnalisé : {self.design_final}")
        return self.design_final

    def enregistrer_design(self) -> Optional[dict]:
        if not self.design_final:
            logging.warning("Aucun design final à enregistrer.")
            return None
        design_data = {
            "id": self.design_id,
            "client": self.client_nom,
            "instructions": self.instructions,
            "croquis": self.croquis_genere,
            "personnalisation": self.touche_personnelle,
            "design_final": self.design_final,
            "date": self.date_creation
        }
        logging.info(f"Design enregistré : {design_data}")
        return design_data

# === Orchestration centralisée
def run():
    designer = CreationDesign("Audrey")
    designer.ajouter_instructions("Créer un logo élégant avec des courbes dorées et un fond noir.")
    designer.generer_croquis()
    designer.ajouter_touche_personnelle("Ajout d’un motif floral discret en bas à droite.")
    designer.enregistrer_design()

AssistantPDG.register("creation_design", run)

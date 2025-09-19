# -*- coding: utf-8 -*-
"""Module de tarification internationale - Luxuria IA"""

import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration du journal
BASE_DIR = Path(__file__).resolve().parent
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info(f"Dossier racine : {BASE_DIR}")

# === Modèles de données
@dataclass
class Service:
    nom: str
    description: str
    tarif_eur: float

@dataclass
class Formule:
    statut: str
    tarif_eur: float
    avantages: List[str]
    description: str
    comptes_inclus: int = 1
    tarif_compte_sup: Optional[float] = None
    options: Dict[str, str] = field(default_factory=dict)

# === Taux de conversion
conversion_rates: Dict[str, float] = {
    "FR": 1.00,
    "USA": 1.10,
    "Canada": 1.45,
    "Brésil": 5.40,
    "Chine": 7.90,
    "Russie": 98.00,
    "Inde": 91.00,
    "Afrique": 655.00,
    "Dubai": 4.00,
    "Japon": 160.00
}

def ajouter_pays(pays: str, taux: float) -> None:
    conversion_rates[pays] = taux
    logging.info(f"Pays ajouté : {pays} avec taux {taux}")

# === Catalogue des services
services = [
    Service("Style émotionnel", "Création d’un style complet (poétique + guide + visuel)", 25),
    Service("Suggestion intelligente", "Lecture des préférences + proposition personnalisée", 15),
    Service("PDF explicatif", "Document détaillé du processus de fabrication du style", 20),
    Service("Galerie visuelle", "Consultation des styles générés + favoris + filtres", 70),
    Service("Accès communauté", "Accès à la communauté Luxuria (forum, échanges, inspirations)", 15)
]

# === Formules mensuelles
formules = [
    Formule("Particulier", 49, [
        "3 styles émotionnels / mois",
        "1 PDF explicatif",
        "Accès à la galerie",
        "Accès à la communauté",
        "1 suggestion intelligente"
    ], "Pour les créateurs indépendants"),

    Formule("Professionnel", 99, [
        "5 styles émotionnels",
        "3 PDF explicatifs",
        "Galerie enrichie",
        "Accès à la communauté",
        "Suggestions illimitées"
    ], "Pour les marques et designers", comptes_inclus=3, tarif_compte_sup=9.50),

    Formule("École / Institution", 149, [
        "10 styles émotionnels",
        "5 PDF explicatifs",
        "Galerie multi-utilisateur",
        "Accès à la communauté",
        "Suggestions illimitées"
    ], "Pour les écoles de mode", comptes_inclus=10, tarif_compte_sup=7.50, options={
        "essai_galerie": "3 semaines gratuites",
        "support": "prioritaire"
    }),

    Formule("Studio Créatif", 199, [
        "Accès illimité aux styles",
        "30 PDF explicatifs",
        "Galerie + communauté multi-utilisateur",
        "Suggestions illimitées"
    ], "Pour studios et agences", comptes_inclus=20, tarif_compte_sup=7.50, options={
        "API": "accès développeur",
        "branding": "personnalisation visuelle"
    })
]

# === Affichage des tarifs convertis
def afficher_tarifs_internationaux() -> None:
    logging.info("\nTarification Internationale Luxuria\n")
    for pays, taux in conversion_rates.items():
        logging.info(f"--- {pays} ---")
        logging.info("Tarifs Unitaires :")
        for service in services:
            prix_local = round(service.tarif_eur * taux, 2)
            logging.info(f"  {service.nom} : {prix_local} ({service.description})")
        logging.info("Formules Mensuelles :")
        for formule in formules:
            prix_base = round(formule.tarif_eur * taux, 2)
            logging.info(f"  {formule.statut} : {prix_base} ({formule.description})")
            logging.info(f"    Comptes inclus : {formule.comptes_inclus}")
            if formule.tarif_compte_sup:
                tarif_sup = round(formule.tarif_compte_sup * taux, 2)
                logging.info(f"    Compte supplémentaire : {tarif_sup} / compte")
            for avantage in formule.avantages:
                logging.info(f"    - {avantage}")
            for opt, val in formule.options.items():
                logging.info(f"    Option : {opt}  {val}")
        logging.info("=" * 60)

# === Point d’entrée modulaire
def main() -> None:
    ajouter_pays("Australie", 1.60)
    ajouter_pays("Mexique", 18.50)
    afficher_tarifs_internationaux()

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("tarifs", run)

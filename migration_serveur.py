# -*- coding: utf-8 -*-
"""Protocole de migration Luxuria IA"""

import random
import logging
from datetime import datetime
from pathlib import Path
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration des répertoires
BASE_DIR = Path(__file__).resolve().parent
RAPPORTS_DIR = BASE_DIR / "LuxuriaProject" / "autonomie_ia" / "rapports_migrations"
RAPPORTS_DIR.mkdir(parents=True, exist_ok=True)

ADMIN_HTML = BASE_DIR / "LuxuriaProject" / "admin.html"

# === Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Paramètres de migration
REGIONS = ["France", "Europe", "Monde"]
SEUILS = {
    "France": 100.0,
    "Europe": 300.0,
    "Monde": 700.0
}

# === Simulation du solde bancaire
def generer_solde() -> float:
    return round(random.uniform(50, 1000), 2)

# === Génération de rapport
def enregistrer_rapport(region: str, solde: float, autorise: bool, raison: str) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom = f"migration_{region.lower()}_{timestamp}.txt"
    chemin = RAPPORTS_DIR / nom

    contenu = (
        f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        f"Région ciblée : {region}\n"
        f"Solde disponible : {solde:.2f} EUR\n"
        f"{'Migration autorisée' if autorise else 'Migration refusée'}\n"
        f"Raison : {raison}\n"
    )

    chemin.write_text(contenu, encoding="utf-8")
    logging.info(f"Rapport enregistré : {chemin.resolve()}")

# === Signature électronique
def signer_contrat(region: str, solde: float) -> str:
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    identifiant = f"CTR-{region[:3].upper()}-{int(solde)}-{datetime.now().strftime('%H%M%S')}"
    logging.info(f"Contrat signé : {identifiant} pour {region}")
    return f"Contrat {identifiant} signé le {horodatage} pour {region} (montant : {solde:.2f} EUR)"

# === Notification admin
def notifier_admin(message: str) -> None:
    horodatage = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    bloc = (
        f"<div class='notification'>\n"
        f"  <p><strong>{horodatage}</strong> {message}</p>\n"
        f"</div>\n"
    )
    with open(ADMIN_HTML, "a", encoding="utf-8") as f:
        f.write(bloc)
    logging.info("Notification ajoutée à admin.html")

# === Stratégie de migration
def executer_migration(solde: float) -> None:
    logging.info("Début de la stratégie de migration...")

    for region in REGIONS:
        seuil = SEUILS.get(region)
        if solde >= seuil:
            raison = f"Solde suffisant pour {region} (seuil : {seuil:.2f} EUR)"
            enregistrer_rapport(region, solde, True, raison)
            signature = signer_contrat(region, solde)
            notifier_admin(f"Migration vers {region} validée. {signature}")
            logging.info(f"Migration réussie vers {region}")
        else:
            raison = f"Solde insuffisant pour {region} (requis : {seuil:.2f} EUR, disponible : {solde:.2f} EUR)"
            enregistrer_rapport(region, solde, False, raison)
            notifier_admin(f"Migration vers {region} refusée. {raison}")
            logging.warning(f"Migration interrompue : {raison}")
            break

# === Fonction principale
def main() -> None:
    logging.info("Initialisation du protocole de migration Luxuria IA")
    solde = generer_solde()
    logging.info(f"Solde détecté : {solde:.2f} EUR")

    if solde < min(SEUILS.values()):
        raison = "Solde trop faible pour toute migration. Attente d’un seuil supérieur."
        enregistrer_rapport("Aucune", solde, False, raison)
        notifier_admin(f"Aucune migration autorisée. {raison}")
        logging.error(raison)
        return

    executer_migration(solde)

    # Rappels de sécurité
    logging.info("Interdiction formelle de coter Luxuria en bourse.")
    logging.info("Location de serveurs autorisée uniquement si solde suffisant.")
    logging.info("Le compte bancaire Luxuria ne doit jamais être en déficit.")

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("migration_serveur", run)

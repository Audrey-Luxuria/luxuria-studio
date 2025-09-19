# -*- coding: utf-8 -*-
"""Organisateur de modules Luxuria Studio"""

import shutil
import logging
import hashlib
import unicodedata
from pathlib import Path
from collections import Counter
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration du logging
LOG_PATH = "organizer.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# === Dossiers
BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "luxuria_scripts_temp"
MODULE_DIR = BASE_DIR / "luxuria_modules"
MODULE_DIR.mkdir(parents=True, exist_ok=True)

# === Sous-modules et mots-clés associés
SUBMODULES = {
    "manager": ["lancer_module", "LuxuriaManager", "btn_web_client"],
    "admin": ["generer_rapport_json", "predire_chiffre_affaires", "generer_pdf_facturation"],
    "contrats": ["class Contrat", "verifier_contrats", "renouveler"],
    "clefs": ["statut_cle_client", "cle", "expiration"],
    "utils": ["log_activite", "mois_valide", "nettoyer_dossier"]
}

# === Création des sous-dossiers
for name in SUBMODULES:
    (MODULE_DIR / name).mkdir(parents=True, exist_ok=True)

# === Identification du module par pondération
def identifier_module(contenu: str) -> str:
    contenu_lower = contenu.lower()
    scores = Counter()
    for module, mots in SUBMODULES.items():
        for mot in mots:
            if mot.lower() in contenu_lower:
                scores[module] += 1
    return scores.most_common(1)[0][0] if scores else "utils"

# === Calcul du hash SHA-256
def hash_fichier(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

# === Nettoyage des noms de fichiers
def nettoyer_nom(nom: str) -> str:
    nom = unicodedata.normalize('NFKD', nom).encode('ascii', 'ignore').decode('ascii')
    nom = nom.replace(' ', '_').replace('(', '').replace(')', '').lower()
    return ''.join(c for c in nom if c.isalnum() or c in ('_', '-'))

def nettoyer_noms_fichiers(dossier: Path) -> None:
    for fichier in dossier.glob("*.py"):
        nom = fichier.name
        nom_sans_ext = nom[:-3]
        if not nom_sans_ext.isascii() or not all(c.isalnum() or c in ('_', '-') for c in nom_sans_ext):
            nom_nettoye = nettoyer_nom(nom_sans_ext)
            nouveau_nom = nom_nettoye + ".py"
            nouveau_chemin = fichier.parent / nouveau_nom
            compteur = 1
            while nouveau_chemin.exists():
                nouveau_nom = f"{nom_nettoye}_{compteur}.py"
                nouveau_chemin = fichier.parent / nouveau_nom
                compteur += 1
            try:
                fichier.rename(nouveau_chemin)
                logging.info(f"Nom corrigé : {nom} → {nouveau_nom}")
            except Exception as e:
                logging.warning(f"Erreur lors du renommage de {nom} : {e}")

# === Audit de sécurité
MIN_FILE_SIZE = 400

def auditer_fichiers(dossier: Path) -> list[str]:
    alertes = []
    for fichier in dossier.glob("*.py"):
        if not fichier.is_file():
            alertes.append(f"Fichier manquant : {fichier.name}")
        elif fichier.stat().st_size < MIN_FILE_SIZE:
            alertes.append(f"Taille suspecte : {fichier.name} ({fichier.stat().st_size} octets)")
    for alerte in alertes:
        logging.warning(f"⚠️ ALERTE SÉCURITÉ : {alerte}")
    return alertes

# === Organisation des scripts
def organiser_scripts() -> None:
    if not SOURCE_DIR.exists():
        logging.warning(f"Dossier source introuvable : {SOURCE_DIR}")
        return

    fichiers = list(SOURCE_DIR.glob("*.py"))
    if not fichiers:
        logging.info("Aucun fichier .py trouvé dans le dossier source.")
        return

    for fichier in fichiers:
        try:
            contenu = fichier.read_text(encoding="utf-8")
            module = identifier_module(contenu)
            destination_dir = MODULE_DIR / module
            fichier_hash = hash_fichier(fichier)

            doublon = False
            for existant in destination_dir.glob("*.py"):
                if hash_fichier(existant) == fichier_hash:
                    logging.info(f"{fichier.name} déjà présent dans {module}/ (doublon détecté)")
                    doublon = True
                    break

            if not doublon:
                destination = destination_dir / fichier.name
                if destination.exists():
                    base = fichier.stem
                    i = 1
                    while (destination_dir / f"{base}_{i}.py").exists():
                        i += 1
                    destination = destination_dir / f"{base}_{i}.py"
                shutil.copy2(fichier, destination)
                logging.info(f"{fichier.name} → {module}/")

            fichier.unlink()
        except Exception as e:
            logging.error(f"Erreur avec {fichier.name} : {e}")

# === Fonction principale
def main():
    logging.info("🔍 Audit de sécurité des fichiers Luxuria IA...")
    auditer_fichiers(SOURCE_DIR)

    logging.info("🧼 Nettoyage des noms de fichiers...")
    nettoyer_noms_fichiers(SOURCE_DIR)

    logging.info("📦 Organisation des scripts Luxuria IA...")
    organiser_scripts()

    logging.info("✅ Tous les fichiers ont été triés et le dossier source nettoyé.")

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_modules_organizer", run)

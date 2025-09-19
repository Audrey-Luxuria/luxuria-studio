# -*- coding: utf-8 -*-
"""Luxuria Deduplicator Nettoyage intelligent des doublons et fichiers vides."""

import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# === Configuration du logger ===
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "nettoyage_luxuria.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# === Parametres globaux ===
DOSSIERS_EXCLUS = {".git", "__pycache__", "venv", "env", "logs"}
SUPPRIMER_VIDES = True

# === Suivi des operations ===
hash_index: Dict[str, Path] = {}
fichiers_vides: List[Path] = []
fichiers_doublons: List[Path] = []
fichiers_erreurs: List[str] = []

# === Fonctions principales ===
def calculer_hash(chemin: Path) -> Optional[str]:
    """Calcule le hash SHA256 dun fichier donne."""
    sha256 = hashlib.sha256()
    try:
        with chemin.open("rb") as fichier:
            for bloc in iter(lambda: fichier.read(4096), b""):
                sha256.update(bloc)
        return sha256.hexdigest()
    except FileNotFoundError:
        fichiers_erreurs.append(f"Fichier introuvable : {chemin}")
    except PermissionError:
        fichiers_erreurs.append(f"Permission refusee : {chemin}")
    except OSError as e:
        fichiers_erreurs.append(f"Erreur systeme : {chemin}  {e.strerror}")
    return None

def nettoyer_dossier(racine: Path) -> None:
    """Analyse recursivement le dossier et supprime doublons et fichiers vides."""
    for chemin in racine.rglob("*"):
        if chemin.is_dir() and chemin.name in DOSSIERS_EXCLUS:
            continue
        if chemin.is_file():
            try:
                if SUPPRIMER_VIDES and chemin.stat().st_size == 0:
                    chemin.unlink()
                    fichiers_vides.append(chemin)
                    continue

                hash_val = calculer_hash(chemin)
                if hash_val:
                    if hash_val in hash_index:
                        chemin.unlink()
                        fichiers_doublons.append(chemin)
                    else:
                        hash_index[hash_val] = chemin
            except FileNotFoundError:
                fichiers_erreurs.append(f"Fichier introuvable lors du traitement : {chemin}")
            except PermissionError:
                fichiers_erreurs.append(f"Acces refuse lors du traitement : {chemin}")
            except OSError as e:
                fichiers_erreurs.append(f"Erreur systeme : {chemin}  {e.strerror}")
            except Exception as e:
                # Dernier recours : journaliser sans interrompre
                fichiers_erreurs.append(f"Erreur inattendue : {chemin}  {type(e).__name__}: {e}")

def afficher_resultats() -> None:
    """Affiche un resume complet du nettoyage effectue."""
    logging.info("\n Nettoyage termine")
    logging.info("-" * 50)
    logging.info(f" Fichiers vides supprimes : {len(fichiers_vides)}")
    logging.info(f" Doublons supprimes : {len(fichiers_doublons)}")
    logging.info(f" Erreurs rencontrees : {len(fichiers_erreurs)}")
    logging.info(f" Date : {datetime.now().strftime('%d %B %Y a %H:%M:%S')}")

    if fichiers_vides:
        logging.info("\n Fichiers vides supprimes :")
        for f in sorted(fichiers_vides):
            logging.info(f"  - {f}")

    if fichiers_doublons:
        logging.info("\n Doublons supprimes :")
        for f in sorted(fichiers_doublons):
            logging.info(f"  - {f}")

    if fichiers_erreurs:
        logging.info("\n Erreurs :")
        for e in fichiers_erreurs:
            logging.info(f"  - {e}")

# === Integration dans assistant_pdg.py ou autre
def lancer_nettoyage(chemin_base: Optional[Path] = None) -> None:
    """Fonction à appeler depuis un autre script pour lancer le nettoyage."""
    racine = chemin_base or Path(__file__).parent.resolve()
    logging.info(f"\n Lancement du nettoyage dans : {racine}")
    nettoyer_dossier(racine)
    afficher_resultats()

# === Fonction main pour execution directe
# Bloc __main__ supprimé pour modularisation

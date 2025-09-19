# -*- coding: utf-8 -*-
"""Générateur de fiches clients - Luxuria Studio"""

import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
from assistant_pdg import AssistantPDG

logging.basicConfig(level=logging.INFO, format="[GENERATION] %(message)s")

BASE_DIR = Path(__file__).resolve().parent
DOSSIER_CLIENTS = BASE_DIR / "clients_data"
DOSSIER_CLIENTS.mkdir(exist_ok=True)

CHARGER_SCRIPT = BASE_DIR / "charger_fiche_client.py"
ASSISTANT_SCRIPT = BASE_DIR / "assistant_pdg.py"

EXEMPLES: Dict[str, Dict[str, Any]] = {
    "alice": {
        "nom": "Alice Dupont",
        "email": "alice.dupont@example.com",
        "style_prefere": "minimalisme",
        "diamant_favori": "emeraude"
    },
    "marc": {
        "nom": "Marc Lemoine",
        "email": "marc.lemoine@example.com",
        "style_prefere": "baroque",
        "diamant_favori": "saphir"
    }
}

def enrichir_fiche(identifiant: str, fiche: Dict[str, Any]) -> Dict[str, Any]:
    fiche["cle_acces"] = identifiant
    fiche["date_cle"] = datetime.now().strftime("%Y-%m-%d")
    fiche.setdefault("historique_achats", [])
    return fiche

def generer_style_signature(fiche: Dict[str, Any]) -> str:
    motif = fiche.get("motif_prefere", "")
    couleur = fiche.get("couleur_favorite", "")
    symbole = fiche.get("symbole_fetiche", "")
    return f"{motif} / {couleur} / {symbole}"

def enrichir_fiche_avancee(identifiant: str, fiche: Dict[str, Any]) -> Dict[str, Any]:
    fiche = enrichir_fiche(identifiant, fiche)
    fiche["style_signature"] = generer_style_signature(fiche)
    return fiche

def sauvegarder_fiche(identifiant: str, fiche: Dict[str, Any]) -> Path:
    chemin = DOSSIER_CLIENTS / f"{identifiant}.json"
    fiche_enrichie = enrichir_fiche(identifiant, fiche)

    try:
        if chemin.is_file():
            with chemin.open("r", encoding="utf-8") as f:
                existante = json.load(f)
            fusion = fusionner_fiches(existante, fiche_enrichie)
            with chemin.open("w", encoding="utf-8") as f:
                json.dump(fusion, f, indent=4, ensure_ascii=False)
            logging.info(f"Fiche mise à jour : {identifiant}")
        else:
            with chemin.open("w", encoding="utf-8") as f:
                json.dump(fiche_enrichie, f, indent=4, ensure_ascii=False)
            logging.info(f"Fiche créée : {identifiant}")
    except Exception as err:
        logging.warning(f"Erreur pour {identifiant} : {err}")

    return chemin

def synchroniser_avec_assistant_pdg(chemin_fiche: Path) -> None:
    try:
        subprocess.run(["python", str(ASSISTANT_SCRIPT), str(chemin_fiche)], check=True)
        logging.info(f"Fiche transmise à l'assistant PDG : {chemin_fiche.name}")
    except subprocess.CalledProcessError as err:
        logging.warning(f"Erreur de synchronisation : {err}")

def afficher_fiches_existantes() -> None:
    fichiers = list(DOSSIER_CLIENTS.glob("*.json"))
    if not fichiers:
        logging.info("Aucune fiche client enregistrée.")
        return
    for fichier in fichiers:
        try:
            with fichier.open("r", encoding="utf-8") as f:
                fiche = json.load(f)
            nom = fiche.get("nom", "Inconnu")
            signature = fiche.get("style_signature", "")
            logging.info(f"{fichier.name} | {nom} | Style : {signature}")
        except Exception as err:
            logging.warning(f"Erreur lecture {fichier.name} : {err}")

def synchroniser_toutes_les_fiches() -> None:
    for fichier in DOSSIER_CLIENTS.glob("*.json"):
        try:
            subprocess.run(["python", str(ASSISTANT_SCRIPT), str(fichier)], check=True)
            logging.info(f"Fiche transmise : {fichier.name}")
        except Exception as err:
            logging.warning(f"Erreur de synchronisation : {err}")

def charger_fiche_client(nom: str) -> Dict[str, Any]:
    if not CHARGER_SCRIPT.is_file():
        raise FileNotFoundError(f"Script introuvable : {CHARGER_SCRIPT}")
    if not nom or not isinstance(nom, str):
        raise ValueError("Nom client invalide ou vide.")
    try:
        result = subprocess.run(
            ["python", str(CHARGER_SCRIPT), nom],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout.strip())
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f"Échec d'exécution : {err.stderr.strip()}")
    except json.JSONDecodeError:
        raise ValueError("Sortie JSON invalide.")

def fusionner_fiches(fiche_existante: Dict[str, Any], nouvelle_fiche: Dict[str, Any]) -> Dict[str, Any]:
    fusion = fiche_existante.copy()
    for cle, valeur in nouvelle_fiche.items():
        if cle == "historique_achats":
            anciens = set(fusion.get(cle, []))
            nouveaux = set(valeur)
            fusion[cle] = sorted(anciens.union(nouveaux))
        elif not fusion.get(cle):
            fusion[cle] = valeur
    return fusion

def creer_clients_exemple() -> None:
    for identifiant, fiche_client in EXEMPLES.items():
        chemin = sauvegarder_fiche(identifiant, fiche_client)
        synchroniser_avec_assistant_pdg(chemin)

# === Orchestration centralisée
def run():
    logging.info("🚀 Lancement du générateur de fiches clients...")
    creer_clients_exemple()
    afficher_fiches_existantes()
    synchroniser_toutes_les_fiches()
    logging.info("✅ Opérations terminées.")

AssistantPDG.register("generateur_clients", run)

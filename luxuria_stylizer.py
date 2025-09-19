# -*- coding: utf-8 -*-
"""Module de stylisation Luxuria IA"""

import json
import random
import unicodedata
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Configuration
BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "admin_private" / "log_activites.txt"
STYLES_DIR = BASE_DIR / "luxuria_fiches" / "clients" / "styles"
PRICING_PATH = BASE_DIR / "admin_private" / "luxuria_pricing.json"

STYLES_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === Utilitaires
def log_activite(message: str) -> None:
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"[{horodatage}] {message}\n")

def normaliser(texte: str) -> str:
    return unicodedata.normalize("NFKD", texte).encode("ASCII", "ignore").decode().lower()

# === Chargement des styles client
def charger_styles(client_id: str) -> List[str]:
    fichier = STYLES_DIR / f"{client_id}.json"
    if not fichier.is_file():
        return []
    try:
        with fichier.open("r", encoding="utf-8") as f:
            contenu = json.load(f)
        styles = contenu.get("styles", [])
        return [s.get("theme", "") for s in styles if isinstance(s, dict) and "theme" in s]
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return []

# === Comparaison des affinités
def comparer_affinites(client_id: str) -> List[Dict[str, Any]]:
    themes_client = set(charger_styles(client_id))
    suggestions = []
    for fichier in STYLES_DIR.glob("*.json"):
        autre_id = fichier.stem
        if autre_id == client_id:
            continue
        themes_autre = set(charger_styles(autre_id))
        communs = themes_client.intersection(themes_autre)
        if communs:
            suggestions.append({
                "autre_client": autre_id,
                "styles_communs": sorted(communs),
                "niveau_affinite": len(communs)
            })
    return sorted(suggestions, key=lambda x: x["niveau_affinite"], reverse=True)

# === Offres par segment
def offres_par_segment(segment: str, afficher_prix: bool = False) -> List[str]:
    segment = segment.strip().lower()
    if not PRICING_PATH.is_file():
        return []
    try:
        with PRICING_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        raw_tarifs = data.get("tarifs", [])
        if not isinstance(raw_tarifs, list):
            return []
        offres = []
        for item in raw_tarifs:
            if item.get("segment", "").strip().lower() == segment:
                offre = item.get("offre", "offre inconnue")
                prix = item.get("prix", "N/A")
                offres.append(f"{offre} ({prix})" if afficher_prix else offre)
        return offres
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return []

# === Générateur de styles libres
class LuxuriaStylizerInfini:
    def __init__(self) -> None:
        self.motifs_poetiques = {
            "arabesque": "la danse des courbes infinies",
            "geometrique": "l'ordre secret des formes",
            "organique": "la respiration de la nature",
            "mystique": "les murmures de l'invisible",
            "chaotique": "le tumulte des âmes libres",
            "ethere": "la trace des rêves oubliés"
        }
        self.symboles_inspirants = {
            "lune": "la lumière douce des rêves",
            "serpent": "la sagesse ondoyante",
            "clé": "l'ouverture vers l'inconnu",
            "papillon": "la métamorphose éternelle",
            "miroir": "le reflet des vérités cachées",
            "fenêtre": "l'appel vers l'ailleurs"
        }
        self.textures_sensorielles = [
            "velours", "soie", "écorce", "brume",
            "poussière d'étoiles", "verre craquelé"
        ]
        self.couleurs_evocatrices = [
            "noir", "bleu nuit", "ivoire", "rouge cendre",
            "vert absinthe", "or liquide"
        ]
        self.emotions_connues = [
            "joie", "colère", "sérénité",
            "mystère", "désir", "rêverie"
        ]

    def interpret_emotion(self, emotion: str) -> str:
        mapping = {
            "joie": "arabesque",
            "colère": "geometrique",
            "sérénité": "organique",
            "mystère": "mystique",
            "désir": "chaotique",
            "rêverie": "ethere"
        }
        return mapping.get(emotion.lower(), random.choice(list(self.motifs_poetiques.keys())))

    def generate_style(self, emotion: str, texture: str, couleur: str, symbole: str) -> Dict[str, Any]:
        motif = self.interpret_emotion(emotion)
        signature = f"{motif}-{texture}-{couleur}-{symbole}-{random.randint(1000, 9999)}"
        return {
            "composition": {"motifs": [motif], "textures": [texture]},
            "visuel": {"couleurs": [couleur], "symbole": symbole},
            "signature_luxuria": signature
        }

# === Offre personnalisée automatisée
def generer_offre_personnalisee(client_id: str) -> Dict[str, Any]:
    stylizer = LuxuriaStylizerInfini()
    themes = charger_styles(client_id)
    affinites = comparer_affinites(client_id)

    if not themes:
        emotion = random.choice(stylizer.emotions_connues)
        texture = random.choice(stylizer.textures_sensorielles)
        couleur = random.choice(stylizer.couleurs_evocatrices)
        symbole = random.choice(list(stylizer.symboles_inspirants.keys()))
        style = stylizer.generate_style(emotion, texture, couleur, symbole)
        theme = style["composition"]["motifs"][0]
        tarif = 30
        segment = "decouverte"
        offre = f"Croquis IA '{theme}' à tarif découverte : {tarif}"
        message = "Aucun style enregistré. Luxuria propose une création libre."
    else:
        theme = max(set(themes), key=themes.count)
        base_tarif = 75
        reduction = min(5 * len(affinites), 45)
        tarif = max(30, base_tarif - reduction)
        segment = "premium" if tarif >= 60 else "decouverte"
        offre = f"Design IA premium '{theme.title()}' + certificat : {tarif}"
        message = f"Le style '{theme}' est récurrent. Luxuria propose une variation exclusive."

    recommandations = [a["autre_client"] for a in affinites[:3]]
    offres_complementaires = offres_par_segment(segment, afficher_prix=True)

    log_activite(f"[COMMERCIALE] Offre générée pour {client_id} / Thème : {theme} / Tarif : {tarif}")

    return {
        "client": client_id,
        "theme": theme,
        "offre": offre,
        "tarif": tarif,
        "message": message,
        "segment": segment,
        "recommandations": recommandations,
        "offres_complementaires": offres_complementaires,
        "date": datetime.now().isoformat()
    }

# === Point d'entrée modulaire
def main():
    """Point d'entrée optionnel pour Luxuria Stylizer."""
    pass

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_stylizer", run)

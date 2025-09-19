# -*- coding: utf-8 -*-
"""Générateur de logo Luxuria Studio"""

import os
import logging
from PIL import Image, ImageDraw, ImageFont
from assistant_pdg import AssistantPDG

# === Configuration du logging
logging.basicConfig(level=logging.INFO, format="[LOGO] %(message)s")

# === Répertoires
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# === Paramètres du logo
TAILLE = 300
FOND = "#f4f4f4"
OR = "#d4af37"
TEXTE = "L"
MARGE = 30
FICHIER_IMAGE = os.path.join(ASSETS_DIR, "logo.png")
FICHIER_POLICE = os.path.join(BASE_DIR, "arial.ttf")

def generer_logo() -> str:
    """Génère le logo Luxuria et le sauvegarde dans assets/logo.png"""
    try:
        img = Image.new("RGB", (TAILLE, TAILLE), FOND)
        draw = ImageDraw.Draw(img)

        # Cercle doré
        draw.ellipse((MARGE, MARGE, TAILLE - MARGE, TAILLE - MARGE), outline=OR, width=6)

        # Chargement de la police
        try:
            font = ImageFont.truetype(FICHIER_POLICE, 120)
        except OSError:
            font = ImageFont.load_default()
            logging.info("Police personnalisée introuvable, police par défaut utilisée.")

        # Position du texte
        bbox = draw.textbbox((0, 0), TEXTE, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (TAILLE - text_width) // 2
        y = (TAILLE - text_height) // 2

        draw.text((x, y), TEXTE, font=font, fill=OR)

        # Sauvegarde
        img.save(FICHIER_IMAGE)
        logging.info(f"✅ Logo généré : {FICHIER_IMAGE}")
        return FICHIER_IMAGE

    except Exception as err:
        logging.warning(f"❌ Erreur de génération du logo : {err}")
        return ""

def injecter_logo_pdf(canvas, x=40, y=750, taille=60) -> None:
    """Insère le logo dans un PDF via ReportLab canvas"""
    try:
        canvas.drawImage(FICHIER_IMAGE, x, y, width=taille, height=taille, mask='auto')
        logging.info("Logo inséré dans le PDF.")
    except Exception as err:
        logging.warning(f"Erreur insertion logo PDF : {err}")

# === Orchestration centralisée
def run():
    logging.info("🚀 Lancement du générateur de logo Luxuria...")
    generer_logo()

AssistantPDG.register("generateur_logo", run)

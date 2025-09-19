# -*- coding: utf-8 -*-
"""Luxuria Converter  Convertisseur de scripts Python en executables (.exe)"""

import subprocess
import sys
import logging
from pathlib import Path
import platform

# === Configuration du logger ===
logging.basicConfig(
    level=logging.INFO,
    format="[Luxuria Converter] %(levelname)s : %(message)s"
)

def est_windows():
    return platform.system() == "Windows"

def pyinstaller_disponible():
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def convertir(script_py: str):
    """Convertit un fichier .py en executable .exe via PyInstaller."""
    chemin_script = Path(script_py).resolve()

    if not est_windows():
        logging.error("Ce convertisseur ne fonctionne que sous Windows.")
        return

    if not pyinstaller_disponible():
        logging.error("PyInstaller n'est pas disponible. Installez-le avec : pip install pyinstaller")
        return

    if not chemin_script.exists():
        logging.error(f"Fichier introuvable : {chemin_script}")
        return

    logging.info(f" Conversion du script : {chemin_script.name}")
    commande = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--clean",
        "--distpath", "dist",
        "--workpath", "build",
        "--name", chemin_script.stem,
        str(chemin_script)
    ]

    try:
        subprocess.run(commande, check=True)
        exe_path = Path("dist") / f"{chemin_script.stem}.exe"
        if exe_path.exists():
            logging.info(f" Conversion reussie : {exe_path}")
        else:
            logging.warning(" Conversion terminee, mais le fichier .exe n'a pas ete trouve.")
    except subprocess.CalledProcessError as e:
        logging.error(" Echec de la conversion.")
        logging.debug(e)

def interface():
    """Interface utilisateur en ligne de commande."""
    print("\n Luxuria Converter  Generateur d'executables (.exe)")
    print("Assurez-vous que PyInstaller est installe (pip install pyinstaller)")
    script = input("Entrez le chemin du fichier .py a convertir : ").strip()
    convertir(script)

# === Point dentree autonome ===
# Bloc __main__ supprimé pour modularisation

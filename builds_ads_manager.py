# -*- coding: utf-8 -*-
"""Script de build pour LuxuriaAdsManager."""

import logging
import sys
from pathlib import Path
import PyInstaller.__main__
from assistant_pdg import AssistantPDG

# === Configuration du logging
logging.basicConfig(level=logging.INFO, format="[BUILD] %(message)s")

# === Fichiers et dossiers requis
REQUIRED_ITEMS = [
    ("campagne_publicite.py", "file"),
    ("logo.ico", "file"),
    ("visuels", "dir")
]

# === Détection du séparateur pour --add-data
DATA_SEPARATOR = ";" if sys.platform.startswith("win") else ":"


def check_required_paths(base_dir: Path) -> bool:
    """Vérifie que tous les fichiers/dossiers requis sont présents."""
    missing = []
    for name, expected_type in REQUIRED_ITEMS:
        path = base_dir / name
        if expected_type == "file" and not path.is_file():
            missing.append(str(path))
        elif expected_type == "dir" and not path.is_dir():
            missing.append(str(path))
    if missing:
        logging.error("❌ Éléments manquants :")
        for m in missing:
            logging.error(f" - {m}")
        return False
    return True


def build_executable(base_dir: Path) -> None:
    """Compile le gestionnaire de publicités en exécutable."""
    try:
        logging.info("🔧 Compilation de LuxuriaAdsManager...")
        PyInstaller.__main__.run([
            str(base_dir / "campagne_publicite.py"),
            "--name=LuxuriaAdsManager",
            "--onefile",
            "--windowed",
            f"--icon={base_dir / 'logo.ico'}",
            f"--add-data=visuels{DATA_SEPARATOR}visuels",
            "--clean",
            "--noconfirm"
        ])
        logging.info("✅ Build terminé avec succès.")
    except Exception as e:
        logging.error(f"❌ Échec du build : {type(e).__name__} - {e}")


def run_build() -> None:
    """Point d'entrée principal pour lancer le build."""
    base_dir = Path(__file__).resolve().parent
    logging.info(f"📁 Dossier de travail : {base_dir}")

    if not check_required_paths(base_dir):
        logging.error("⛔ Build annulé : fichiers requis manquants.")
        return

    build_executable(base_dir)

# === Orchestration centralisée
def run():
    run_build()

AssistantPDG.register("build_ads_manager", run)

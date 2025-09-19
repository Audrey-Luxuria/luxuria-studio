# -*- coding: utf-8 -*-
"""Script de compilation pour LuxuriaAssistantPDG."""

import logging
from pathlib import Path
import PyInstaller.__main__
from assistant_pdg import AssistantPDG

# === Configuration du logging
logging.basicConfig(level=logging.INFO, format="[BUILD] %(message)s")

def build_assistant():
    """Compile assistant_pdg.py en exécutable standalone."""
    base_dir = Path(__file__).resolve().parent
    script_path = base_dir / "assistant_pdg.py"
    icon_path = base_dir / "logo.ico"

    if not script_path.is_file():
        logging.error(f"❌ Fichier introuvable : {script_path}")
        return

    logging.info("🔧 Compilation de LuxuriaAssistantPDG...")

    args = [
        str(script_path),
        "--name=LuxuriaAssistantPDG",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm"
    ]

    if icon_path.is_file():
        args.append(f"--icon={icon_path}")

    try:
        PyInstaller.__main__.run(args)
        logging.info("✅ Build terminé avec succès.")
    except Exception as e:
        logging.error(f"❌ Échec du build : {type(e).__name__} - {e}")

def run_build():
    build_assistant()

# === Orchestration centralisée
def run():
    run_build()

AssistantPDG.register("build_assistant_pdg", run)

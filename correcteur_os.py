# -*- coding: utf-8 -*-
"""Ajoute 'import os' aux fichiers Python qui utilisent le module sans l'importer."""

import logging
from pathlib import Path
from typing import List

IGNORES = {"__pycache__", ".venv", "env", "venv", "site-packages"}
rapport: List[str] = []

logging.basicConfig(level=logging.INFO, format="[OS] %(message)s")

class CorrecteurOS:
    @staticmethod
    def fichier_utilise_os(contenu: str) -> bool:
        for line in contenu.splitlines():
            line = line.strip()
            if line.startswith(("#", '"', "'")):
                continue
            if "os." in line:
                return True
        return False

    @staticmethod
    def corriger_fichier(filepath: Path, dry_run: bool = False) -> bool:
        try:
            contenu = filepath.read_text(encoding="utf-8")
        except FileNotFoundError:
            logging.warning(f" Fichier introuvable : {filepath}")
            return False
        except UnicodeDecodeError:
            logging.warning(f" Encodage non pris en charge : {filepath}")
            return False

        if not CorrecteurOS.fichier_utilise_os(contenu):
            return False

        if "import os" in contenu:
            logging.info(f" Deja correct : {filepath}")
            return False

        logging.info(f" Correction : {filepath}")
        lignes = contenu.splitlines()
        index_insertion = next(
            (i + 1 for i, ligne in enumerate(lignes)
             if ligne.startswith("#!") or "coding" in ligne),
            0
        )
        lignes.insert(index_insertion, "import os")
        nouveau_contenu = "\n".join(lignes) + "\n"

        if not dry_run:
            try:
                filepath.write_text(nouveau_contenu, encoding="utf-8")
            except OSError:
                logging.error(f" Erreur decriture : {filepath}")
                return False

        rapport.append(str(filepath))
        return True

    @staticmethod
    def corriger_dossier(dossier: Path, dry_run: bool = False, exclude: Path = None) -> None:
        for fichier in dossier.rglob("*.py"):
            if any(part in IGNORES for part in fichier.parts):
                continue
            if exclude and fichier.resolve() == exclude.resolve():
                continue
            CorrecteurOS.corriger_fichier(fichier, dry_run=dry_run)

    @staticmethod
    def afficher_rapport() -> None:
        if rapport:
            logging.info(f"\n {len(rapport)} fichier(s) corrige(s) :")
            for f in rapport:
                logging.info(f" - {f}")
        else:
            logging.info(" Aucun fichier a corriger.")


# Orchestration centralisée
from assistant_pdg import AssistantPDG

def run():
    print("Module exécuté via AssistantPDG")

AssistantPDG.register("correcteur_os", run)

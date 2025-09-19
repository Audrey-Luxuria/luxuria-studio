# -*- coding: utf-8 -*-
"""Correction des indentations (tabulations espaces) dans les fichiers Python."""

import logging
from pathlib import Path
from typing import List

IGNORES = {"__pycache__", ".venv", "env", "venv", "site-packages"}
report: List[str] = []

logging.basicConfig(level=logging.INFO, format="[INDENT] %(message)s")

class CorrecteurIndentation:
    @staticmethod
    def nettoyer_typographie(texte: str) -> str:
        return texte.replace('\u00A0', ' ')

    @staticmethod
    def corriger_indentation(filepath: Path, dry_run: bool = False) -> bool:
        try:
            contenu = filepath.read_text(encoding="utf-8")
        except FileNotFoundError:
            logging.warning(f" Fichier introuvable : {filepath}")
            return False
        except UnicodeDecodeError:
            logging.warning(f" Encodage non pris en charge : {filepath}")
            return False

        lignes = contenu.splitlines(keepends=True)
        modifie = False
        lignes_corrigees = []

        for ligne in lignes:
            nettoyee = CorrecteurIndentation.nettoyer_typographie(ligne)
            if '\t' in nettoyee:
                lignes_corrigees.append(nettoyee.replace('\t', '    '))
                modifie = True
            else:
                lignes_corrigees.append(nettoyee)

        if modifie:
            if not dry_run:
                try:
                    filepath.write_text("".join(lignes_corrigees), encoding="utf-8")
                    logging.info(f" Indentation corrigee dans : {filepath}")
                except OSError:
                    logging.error(f" Erreur decriture : {filepath}")
                    return False
            report.append(str(filepath))
        return modifie

    @staticmethod
    def parcourir_dossier(dossier: Path, dry_run: bool = False, exclude: Path = None) -> None:
        for fichier in dossier.rglob("*.py"):
            if any(part in IGNORES for part in fichier.parts):
                continue
            if exclude and fichier.resolve() == exclude.resolve():
                continue
            CorrecteurIndentation.corriger_indentation(fichier, dry_run=dry_run)

    @staticmethod
    def afficher_rapport() -> None:
        if report:
            logging.info(f"\n {len(report)} fichier(s) corrige(s) :")
            for path in report:
                logging.info(f" - {path}")
        else:
            logging.info(" Aucun probleme d'indentation detecte.")


# Orchestration centralisée
from assistant_pdg import AssistantPDG

def run():
    print("Module exécuté via AssistantPDG")

AssistantPDG.register("correcteur_indentation", run)

# -*- coding: utf-8 -*-
"""Remplacement securise de eval() par ast.literal_eval() dans les scripts Python."""

import re
import logging
from pathlib import Path
from typing import Union

# === Configuration
logging.basicConfig(level=logging.INFO, format="[EVAL] %(message)s")
report: list[str] = []

class CorrecteurEval:
    @staticmethod
    def replace_eval(file_path: Path, dry_run: bool = False) -> bool:
        """Remplace les appels a eval() par ast.literal_eval() dans un fichier Python."""
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
        except FileNotFoundError:
            logging.warning(f"Fichier introuvable : {file_path}")
            return False
        except UnicodeDecodeError:
            logging.warning(f"Encodage non pris en charge : {file_path}")
            return False

        modified_lines = []
        changed = False
        ast_imported = any(re.match(r'\s*import\s+ast', line) for line in lines)

        for line in lines:
            if 'eval(' in line:
                indent = line[:len(line) - len(line.lstrip())]
                new_line = indent + line.replace('eval(', 'ast.literal_eval(', 1)
                modified_lines.append(new_line)
                changed = True
            else:
                modified_lines.append(line)

        if changed:
            if not ast_imported:
                insert_index = next(
                    (i + 1 for i, line in enumerate(modified_lines)
                     if line.strip().startswith(('import ', 'from '))),
                    0
                )
                modified_lines.insert(insert_index, 'import ast\n')

            if not dry_run:
                try:
                    file_path.write_text("".join(modified_lines), encoding="utf-8")
                except OSError:
                    logging.warning(f"Erreur decriture : {file_path}")
                    return False

            report.append(str(file_path))
            return True

        return False

    @staticmethod
    def scan_directory(root: Union[str, Path], dry_run: bool = False, exclude: Path = None) -> None:
        """Parcourt le repertoire et corrige les fichiers contenant eval()."""
        root_path = Path(root).resolve()
        for file in root_path.rglob("*.py"):
            if exclude and file.resolve() == exclude.resolve():
                continue
            CorrecteurEval.replace_eval(file, dry_run=dry_run)

    @staticmethod
    def afficher_rapport() -> None:
        if report:
            logging.info(f"\n {len(report)} fichier(s) modifie(s) :")
            for path in report:
                logging.info(f" - {path}")
        else:
            logging.info(" Aucun appel a eval() trouve.")


# Orchestration centralisée
from assistant_pdg import AssistantPDG

def run():
    print("Module exécuté via AssistantPDG")

AssistantPDG.register("correcteur_eval", run)

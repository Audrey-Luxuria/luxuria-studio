# -*- coding: utf-8 -*-
"""Injecteur de structure minimale dans les scripts Python - Luxuria Studio"""

import os
import logging
from pathlib import Path
from typing import Union

logging.basicConfig(level=logging.INFO, format="[STRUCTURE] %(message)s")

BASE_DIR = Path(__file__).resolve().parent
SCRIPT_NAME = Path(__file__).name

def has_structure(file_path: Union[str, os.PathLike]) -> bool:
    """Verifie si un fichier Python contient une structure (fonction ou classe)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("def ") or stripped.startswith("class "):
                    return True
        return False
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError):
        return False

def inject_structure(file_path: Union[str, os.PathLike]) -> None:
    """Injecte une docstring et une fonction placeholder dans un fichier Python."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        new_lines = []

        # Docstring absente
        if not lines or not lines[0].strip().startswith(('"""', "'''")):
            new_lines.append('"""Structure ajoutee automatiquement."""')
            new_lines.append('')

        # Fonction placeholder absente
        if "def placeholder()" not in content:
            new_lines.append("def placeholder():")
            new_lines.append("    pass")
            new_lines.append('')

        new_lines.extend(lines)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        logging.info("Structure injectee dans : {}".format(Path(file_path).name))
    except Exception as err:
        logging.error("Erreur sur {} : {}".format(Path(file_path).name, err))

def correct_structure(directory: Union[str, os.PathLike]) -> None:
    """Parcourt les fichiers Python et injecte une structure minimale si necessaire."""
    directory = Path(directory).resolve()
    for path in directory.rglob("*.py"):
        if path.name in {"__init__.py", SCRIPT_NAME}:
            continue
        if not has_structure(path):
            inject_structure(path)

def main() -> None:
    logging.info("Injection de structure dans les fichiers Python vides...")
    correct_structure(BASE_DIR)
    logging.info("Tous les fichiers ont maintenant une structure minimale.")

# Bloc __main__ supprimé pour modularisation


# -*- coding: utf-8 -*-
"""Audit et correction ASCII + syntaxe Python  Luxuria Studio."""

import sys
import re
import py_compile
import unicodedata
import logging
from pathlib import Path
from typing import List

# === Configuration
BASE_DIR = Path(__file__).resolve().parent
logging.basicConfig(level=logging.INFO, format="[AUDIT] %(message)s")

# === Fonctions ASCII
def normalize_ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

def fix_non_ascii(path: Path) -> str:
    try:
        original = path.read_text(encoding="utf-8")
        cleaned = normalize_ascii(original)
        if original != cleaned:
            path.write_text(cleaned, encoding="utf-8")
            return " ASCII corrige"
        return " ASCII OK"
    except (OSError, UnicodeDecodeError) as err:
        return f" Erreur lecture/ecriture : {type(err).__name__}"

# === Verification de syntaxe
def check_syntax(path: Path) -> str:
    try:
        py_compile.compile(str(path), doraise=True)
        return " Syntaxe OK"
    except py_compile.PyCompileError as err:
        return f" Erreur de syntaxe : {err.msg}"
    except Exception as err:
        return f" Erreur compilation : {type(err).__name__}"

def attempt_fix_syntax(path: Path) -> str:
    try:
        code = path.read_text(encoding="utf-8")
        code = re.sub(r"^\s+\n", "\n", code, flags=re.MULTILINE)
        if code.count("(") > code.count(")"):
            code += ")" * (code.count("(") - code.count(")"))
        path.write_text(code, encoding="utf-8")
        return " Correction syntaxe appliquee"
    except Exception as err:
        return f" Echec correction : {type(err).__name__}"

# === Fichiers
def list_py_files(root: Path) -> List[Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]

def find_ghost_files(root: Path, known_files: List[Path]) -> List[Path]:
    all_py = [p for p in root.rglob("*.py")]
    return [p for p in all_py if p not in known_files]

# === Audit principal
def audit_and_fix(root: Path) -> None:
    py_files = list_py_files(root)
    ghost_files = find_ghost_files(root, py_files)
    report_lines: List[str] = []

    logging.info(f" Audit en cours dans : {root}\n")

    for path in py_files:
        logging.info(f" Fichier : {path.name}")
        ascii_result = fix_non_ascii(path)
        syntax_result = check_syntax(path)

        logging.info(f"   {ascii_result}")
        logging.info(f"   {syntax_result}")

        if "Erreur de syntaxe" in syntax_result:
            fix_result = attempt_fix_syntax(path)
            syntax_result_post = check_syntax(path)
            logging.info(f"   {fix_result}")
            logging.info(f"   Apres correction : {syntax_result_post}")
            report_lines.append(
                f"{path}\n   {ascii_result}\n   {syntax_result}\n   {fix_result}\n   {syntax_result_post}"
            )
        else:
            report_lines.append(f"{path}\n   {ascii_result}\n   {syntax_result}")

    if ghost_files:
        report_lines.append("\n Fichiers fantomes detectes :")
        for ghost in ghost_files:
            report_lines.append(f"   - {ghost}")

    report_path = BASE_DIR / "python_audit_report.txt"
    try:
        report_path.write_text("\n\n".join(report_lines), encoding="utf-8")
        logging.info(f"\n Rapport genere : {report_path.name}")
    except (OSError, IOError) as err:
        logging.error(f" Erreur ecriture du rapport : {type(err).__name__}")

# === Orchestration
def main() -> None:
    try:
        target = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR
        if not target.exists():
            logging.error(f" Chemin invalide : {target}")
            return
        audit_and_fix(target)
    except Exception as e:
        logging.error(f" Erreur inattendue : {type(e).__name__} - {e}")

# Bloc __main__ supprime pour modularisation


# Orchestration centralisée
from assistant_pdg import AssistantPDG

def run():
    print("Module exécuté via AssistantPDG")

AssistantPDG.register("correcteur_ASCII_syntaxe", run)

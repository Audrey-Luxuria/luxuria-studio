# -*- coding: utf-8 -*-
import ast
from pathlib import Path

MODULE = "assistant_pdg"
INJECTION = f"import {MODULE}\n"
BASE_DIR = Path(__file__).resolve().parent

def already_imported(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == MODULE for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == MODULE:
                return True
    return False

def inject(script_path):
    try:
        content = script_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        print(f" {script_path.name} : erreur de lecture ou de parsing")
        return

    if already_imported(tree):
        print(f" {script_path.name} : deja importe")
        return

    script_path.write_text(INJECTION + content, encoding="utf-8")
    print(f" {script_path.name} : injection reussie")

def main():
    for script in BASE_DIR.glob("*.py"):
        if script.name != Path(__file__).name:
            inject(script)

# Bloc __main__ supprimé pour modularisation

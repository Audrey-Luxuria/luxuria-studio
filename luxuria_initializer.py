# -*- coding: utf-8 -*-
"""Initialiseur structurel Luxuria Studio"""

import os
import sys
import re
import shutil
import importlib
import traceback
import logging
from datetime import datetime
from pathlib import Path
from typing import List
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Base directory
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# === Configuration
DRY_RUN = False
EXCLUDED_DIRS = {'.venv', '__pycache__', 'venv', '.vscode'}
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# === Logging
LOG_FILE = BACKUP_DIR / "initializer.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M"
)

# === Regex patterns
pattern_import = re.compile(r'from\s+LuxuriaProject(\.[\w.]+)?\s+import')
pattern_sys_path = re.compile(r'sys\.path\.append\([^)]+\)')
pattern_file_access = re.compile(r'(open|read_csv|read_excel|load|save|to_csv|to_excel)\((["\'])(.+?)(["\'])')

# === Utilities
def create_backup(filepath: Path) -> Path:
    rel_path = filepath.relative_to(BASE_DIR)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"{rel_path}.{timestamp}.bak"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, backup_path)
    logging.info(f"Backup created: {backup_path}")
    return backup_path

def clean_imports(line: str) -> str:
    return re.sub(r'from\s+LuxuriaProject\.', 'from ', line)

def fix_file(filepath: Path) -> bool:
    try:
        content = filepath.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError as e:
        logging.warning(f"Read error: {filepath}\n{e}")
        return False

    modified = False
    new_content = []

    for line in content:
        if pattern_import.search(line):
            line = clean_imports(line)
            modified = True
        elif pattern_sys_path.search(line):
            logging.info(f"Removed sys.path from {filepath}")
            modified = True
            continue
        new_content.append(line)

    if modified:
        logging.info(f"Modified: {filepath}")
        if not DRY_RUN:
            create_backup(filepath)
            try:
                filepath.write_text("".join(new_content), encoding="utf-8")
            except OSError as e:
                logging.error(f"Write error: {filepath}\n{e}")
        return True
    return False

def inject_base_path(filepath: Path) -> bool:
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        logging.warning(f"Read error: {filepath}\n{e}")
        return False

    if 'BASE_PATH' in content:
        logging.info(f"{filepath.name} already configured")
        return False

    matches = list(re.finditer(pattern_file_access, content))
    if not matches:
        logging.info(f"No path detected in {filepath.name}")
        return False

    base_code = 'from pathlib import Path\nBASE_PATH = Path(__file__).resolve().parent\n'
    content = base_code + content

    for match in matches:
        old_path = match.group(3)
        if '/' not in old_path and '\\' not in old_path:
            continue
        new_call = f'{match.group(1)}(BASE_PATH / "{old_path}"'
        content = content.replace(match.group(0), new_call)

    logging.info(f"Injected BASE_PATH in {filepath.name}")
    if not DRY_RUN:
        create_backup(filepath)
        try:
            filepath.write_text(content, encoding="utf-8")
        except OSError as e:
            logging.error(f"Write error: {filepath}\n{e}")
    return True

def scan_and_fix(directory: Path) -> int:
    logging.info(f"Scanning: {directory}")
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith('.py'):
                path = Path(root) / file
                if fix_file(path):
                    count += 1
                inject_base_path(path)
    logging.info(f"Files modified: {count}")
    return count

def find_modules(folder: Path) -> List[str]:
    modules = []
    for f in folder.glob("*.py"):
        if f.name != "__init__.py":
            rel = f.relative_to(BASE_DIR).with_suffix("")
            modules.append(".".join(rel.parts))
    return modules

def test_internal_modules() -> int:
    logging.info("Testing internal modules")
    tested = 0
    for folder in BASE_DIR.iterdir():
        if folder.is_dir() and folder.name not in EXCLUDED_DIRS:
            modules = find_modules(folder)
            for module in modules:
                try:
                    importlib.import_module(module)
                    logging.info(f"Import OK: {module}")
                except ModuleNotFoundError:
                    logging.warning(f"Module not found: {module}")
                except Exception as e:
                    logging.error(f"Import error {module}: {e}")
                    traceback.print_exc()
                tested += 1
    return tested

def check_structure() -> bool:
    logging.info("Checking project structure")
    folders = [d for d in BASE_DIR.iterdir() if d.is_dir() and d.name not in EXCLUDED_DIRS]
    if not folders:
        logging.warning("No folders found.")
        return False
    for d in folders:
        py_files = list(d.glob("*.py"))
        if not py_files:
            logging.info(f"Empty folder: {d}")
    return True

def run_diagnostic():
    logging.info("Starting Luxuria IA diagnostic")
    logging.info("---------------------------------------------------------")
    if check_structure():
        module_count = test_internal_modules()
        file_count = scan_and_fix(BASE_DIR)
        logging.info(f"Résumé : {file_count} fichiers modifiés | {module_count} modules testés")
    else:
        logging.warning("Structure incomplète : aucun fichier Python trouvé.")
    logging.info("Diagnostic terminé.")

# === Orchestration centrale
def run():
    run_diagnostic()

AssistantPDG.register("luxuria_initializer", run)

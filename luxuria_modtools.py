# -*- coding: utf-8 -*-
"""Module d'outils de modification Luxuria Studio"""

import os
import shutil
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from assistant_pdg import AssistantPDG  # ✅ Orchestration centrale

# === Logger global
logging.basicConfig(level=logging.INFO, format="[%Y-%m-%d %H:%M:%S] %(message)s")

# === Logging utilitaire
def log(message: str, log_file: Optional[Path] = None) -> None:
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}"
    logging.info(full_message)
    if log_file:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(full_message + "\n")

# === Backup
def backup_file(file_path: Path, backup_dir: Path, log_file: Optional[Path] = None) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / file_path.name
    shutil.copy2(file_path, backup_path)
    log(f"Backup created: {backup_path}", log_file)

# === Unicode cleanup
def clean_unicode_file(file_path: Path, log_file: Optional[Path] = None) -> None:
    try:
        content = file_path.read_text(encoding="utf-8")
        cleaned = content.replace("\u2028", "").replace("\u2029", "")
        file_path.write_text(cleaned, encoding="utf-8")
        log(f"Cleaned Unicode characters in: {file_path}", log_file)
    except Exception as e:
        log(f"Error cleaning {file_path}: {e}", log_file)

# === Signature
def update_signature(file_path: Path, sig_path: Path, author: str = "unknown", log_file: Optional[Path] = None) -> None:
    sig_path.parent.mkdir(parents=True, exist_ok=True)
    hash_val = hashlib.sha256(file_path.read_bytes()).hexdigest()
    signature = {
        "file": str(file_path),
        "hash": hash_val,
        "author": author,
        "timestamp": datetime.now().isoformat()
    }

    if sig_path.exists():
        data = json.loads(sig_path.read_text(encoding="utf-8"))
    else:
        data = {}

    data[str(file_path)] = signature
    sig_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log(f"Signature updated for: {file_path}", log_file)

def check_integrity(file_path: Path, sig_path: Path) -> str:
    if not sig_path.exists():
        return "Signature file missing"
    data = json.loads(sig_path.read_text(encoding="utf-8"))
    sig = data.get(str(file_path))
    if not sig:
        return "No signature found"
    current_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return "Valid" if current_hash == sig["hash"] else "Tampered"

# === UTF-8 audit
def audit_utf8(file_list: List[Path], log_file: Optional[Path] = None) -> None:
    for f in file_list:
        try:
            f.read_text(encoding="utf-8")
            log(f"UTF-8 OK: {f}", log_file)
        except UnicodeDecodeError:
            log(f"UTF-8 ERROR: {f}", log_file)

# === Requirements
def extract_modules(req_path: Path) -> List[str]:
    return [
        line.strip().split("==")[0]
        for line in req_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

def install_modules(modules: List[str], log_file: Optional[Path] = None) -> None:
    for module in modules:
        try:
            subprocess.run(["pip", "install", module], check=True)
            log(f"Installed: {module}", log_file)
        except subprocess.CalledProcessError:
            log(f"Failed to install: {module}", log_file)

# === Environment
def load_env(env_path: Path, log_file: Optional[Path] = None) -> None:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, val = line.strip().split("=", 1)
            os.environ[key] = val
            log(f"Env loaded: {key}", log_file)

# === HTML report
def generate_html_report(report_path: Path, log_file: Optional[Path] = None) -> None:
    if not log_file or not log_file.exists():
        return
    lines = log_file.read_text(encoding="utf-8")
    html = f"""<!DOCTYPE html>
<html><head><title>Audit Report</title></head><body>
<h1>Audit Log</h1><pre>{lines}</pre>
</body></html>"""
    report_path.write_text(html, encoding="utf-8")
    log(f"HTML report generated: {report_path}", log_file)

# === Main audit runner
def run_audit(
    root: Path,
    backup_dir: Optional[Path] = None,
    log_file: Optional[Path] = None,
    sig_path: Optional[Path] = None,
    req_path: Optional[Path] = None,
    env_path: Optional[Path] = None,
    html_report_path: Optional[Path] = None,
    module_prefix: Optional[str] = None
) -> None:
    log_file = Path(log_file) if log_file else None
    py_files = list(root.rglob("*.py"))
    if module_prefix:
        py_files = [f for f in py_files if module_prefix in f.name]

    for f in py_files:
        if backup_dir:
            backup_file(f, Path(backup_dir), log_file)
        clean_unicode_file(f, log_file)
        if sig_path:
            update_signature(f, Path(sig_path), author="automated", log_file=log_file)

    audit_utf8(py_files, log_file)

    data_files = list(root.rglob("*.txt")) + list(root.rglob("*.csv"))
    audit_utf8(data_files, log_file)

    if sig_path:
        for f in py_files:
            status = check_integrity(f, Path(sig_path))
            log(f"Integrity {f.name}: {status}", log_file)

    if req_path:
        modules = extract_modules(Path(req_path))
        install_modules(modules, log_file)

    if env_path:
        load_env(Path(env_path), log_file)

    if html_report_path:
        generate_html_report(Path(html_report_path), log_file)

    log("Audit completed", log_file=log_file)

# === Point d'entrée
def main():
    run_audit(
        root=Path("."),
        backup_dir=Path("backups"),
        log_file=Path("audit.log"),
        sig_path=Path("signatures.json"),
        req_path=Path("requirements.txt"),
        env_path=Path(".env"),
        html_report_path=Path("audit_report.html")
    )

# === Orchestration centrale
def run():
    main()

AssistantPDG.register("luxuria_modtools", run)

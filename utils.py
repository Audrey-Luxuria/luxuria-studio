# -*- coding: utf-8 -*-
"""Module utilitaire pour journalisation, affichage et execution securisee."""

import os
import logging
import datetime
import traceback
from typing import Callable, Any

# === Configuration du fichier de log ===
LOG_FILE = "debug.log"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as log_init:
        log_init.write("=== LOG INITIALISE ===\n")

# === Configuration du logger ===
logger = logging.getLogger("luxuria")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

# === Journalisation manuelle ===
def log(message: str) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

# === Execution securisee ===
def safe_run(func: Callable, *args, **kwargs) -> Any:
    try:
        return func(*args, **kwargs)
    except ZeroDivisionError:
        afficher_erreur("Division par zero detectee.")
        log("ERREUR: Division par zero")
        return None
    except (TypeError, ValueError) as err:
        afficher_erreur(f"Erreur de type ou de valeur : {err}")
        log(f"ERREUR: {err}")
        return None
    except Exception as err:
        trace = traceback.format_exc()
        log(f"ERREUR: {str(err)}")
        log("TRACE:")
        log(trace)
        afficher_erreur("Une erreur inattendue est survenue.")
        logger.error(trace)
        return None

# === Affichage stylise ===
def afficher_banner(titre: str) -> None:
    ligne = "=" * (len(titre) + 8)
    logger.info(f"\n{ligne}\n=== {titre} ===\n{ligne}\n")

def afficher_info(message: str) -> None:
    logger.info(f"[INFO] {message}")

def afficher_warning(message: str) -> None:
    logger.warning(f"[ATTENTION] {message}")

def afficher_erreur(message: str) -> None:
    logger.error(f"[ERREUR] {message}")
    log(f"ERREUR: {message}")

def afficher_succes(message: str) -> None:
    logger.info(f"[SUCCES] {message}")

# === Auto-test integre ===
def test_auto() -> None:
    afficher_banner("Test automatique utils.py")
    afficher_info("Affichage d'information")
    afficher_warning("Affichage d'avertissement")
    afficher_erreur("Affichage d'erreur simulee")
    afficher_succes("Affichage de succes")

    def division(a: float, b: float) -> float:
        return a / b

    afficher_info("Test safe_run : division valide")
    safe_run(division, 10, 2)

    afficher_info("Test safe_run : division par zero")
    safe_run(division, 10, 0)

    afficher_info("Test safe_run : erreur de type")
    safe_run(division, "dix", 2)

# === Point dentree ===
def main() -> None:
    test_auto()

# Bloc __main__ supprimé pour modularisation

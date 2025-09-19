# -# -*- coding: utf-8 -*-
# """Assistant PDG - Luxuria Studio"""
#
# import logging
# import subprocess
# import webbrowser
# from pathlib import Path
# from assistant_pdg import AssistantPDG
#
# logging.basicConfig(level=logging.INFO, format="[ASSISTANT] %(message)s")
#
# BASE_DIR = Path(__file__).resolve().parent
#
# def detecter_interfaces() -> dict[str, Path]:
#     """Détecte les interfaces disponibles dans le projet."""
#     mapping = {}
#     for script in BASE_DIR.glob("interface_*.py"):
#         nom = script.stem.replace("interface_", "")
#         mapping[nom] = script
#     if (BASE_DIR / "galerie_privee.py").is_file():
#         mapping["galerie"] = BASE_DIR / "galerie_privee.py"
#     if (BASE_DIR / "galerie_commune.py").is_file():
#         mapping["commune"] = BASE_DIR / "galerie_commune.py"
#     return mapping
#
# INTERFACES = detecter_interfaces()
#
# class IAssistant:
#     """Interface d'action pour le PDG Luxuria."""
#
#     @staticmethod
#     def verifier_client(cle: str) -> bool:
#         """Vérifie la validité d'une clé client via AssistantPDG."""
#         verifier = getattr(AssistantPDG, "verifier_cle_client", None)
#         if callable(verifier):
#             try:
#                 return bool(verifier(cle))
#             except Exception as err:
#                 logging.warning(f"Erreur de vérification : {err}")
#         else:
#             logging.warning("Fonction verifier_cle_client non disponible.")
#         return False
#
#     @staticmethod
#     def inscrire_nouveau_client() -> None:
#         """Inscrit un nouveau client via AssistantPDG."""
#         inscrire = getattr(AssistantPDG, "inscrire_client", None)
#         if callable(inscrire):
#             try:
#                 inscrire()
#                 logging.info("✅ Nouveau client inscrit.")
#             except Exception as err:
#                 logging.error(f"Échec d'inscription : {err}")
#         else:
#             logging.warning("Fonction inscrire_client non disponible.")
#
#     @staticmethod
#     def ouvrir_interface(nom: str) -> None:
#         """Lance une interface Python spécifique."""
#         chemin = INTERFACES.get(nom)
#         if not chemin or not chemin.is_file():
#             logging.warning(f"Interface '{nom}' introuvable.")
#             return
#         try:
#             subprocess.run(["python", str(chemin)], check=True)
#             logging.info(f"Interface '{nom}' lancée.")
#         except subprocess.CalledProcessError as err:
#             logging.error(f"Échec du lancement de '{nom}' : {err}")
#
#     @staticmethod
#     def ouvrir_galerie_web(mode: str = "secure") -> None:
#         """Ouvre la galerie dans le navigateur (mode 'secure' ou 'commune')."""
#         ports = {"secure": 5001, "commune": 5000}
#         url = f"http://127.0.0.1:{ports.get(mode, 5000)}/galerie_{mode}"
#         try:
#             webbrowser.open(url)
#             logging.info(f"Galerie '{mode}' ouverte dans le navigateur.")
#         except Exception as err:
#             logging.error(f"Impossible d'ouvrir la galerie : {err}")
#
# # === Orchestration centralisée
# def run():
#     logging.info("🧠 Assistant PDG initialisé.")
#     IAssistant.ouvrir_interface("client")
#     IAssistant.ouvrir_galerie_web("secure")
#
# AssistantPDG.register("IAssistant", run)

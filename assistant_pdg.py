# -*- coding: utf-8 -*-
"""Orchestrateur principal de Luxuria Studio."""
print("🧠 AssistantPDG initialisé")

import os
import sys
import logging
import subprocess
from pathlib import Path

# === Configuration de base
BASE_PATH = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_PATH))
(Path(BASE_PATH) / "logs").mkdir(exist_ok=True)
from pathlib import Path
import sys

BASE_PATH = Path(__file__).resolve().parent
LIB_PATH = BASE_PATH / "libs"
sys.path.insert(0, str(LIB_PATH))

logging.basicConfig(
    level=logging.INFO,
    format="[AssistantPDG] %(message)s",
    handlers=[
        logging.FileHandler(BASE_PATH / "logs" / "execution.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# === Identifiants administrateur
ADMIN_ID = "Audreyplatel"
ADMIN_MDP = "Borderlands87"
API_KEY = "proj_4Yals6jrsWZnr8wXrLrDRgkj"

# === Fichiers à exclure
EXCLUSIONS = {"assistant_pdg.py", "generate_assistant_pdg.py", "__init__.py"}

class AssistantPDG:
    """Classe centrale pour orchestrer tous les modules et interfaces Luxuria."""

    ADMIN_ID = ADMIN_ID
    ADMIN_MDP = ADMIN_MDP
    API_KEY = API_KEY

    @classmethod
    def register(cls, nom: str, fonction: callable) -> None:
        logging.info(f"📌 Module enregistré : {nom}")
        fonction()

    @classmethod
    def lister_scripts(cls) -> dict[str, list[str]]:
        scripts_py, scripts_html = [], []
        for path in BASE_PATH.rglob("*"):
            if path.is_file():
                rel = path.relative_to(BASE_PATH).as_posix()
                if path.name.startswith(".") or path.suffix not in {".py", ".html"}:
                    continue
                if path.suffix == ".py" and path.name not in EXCLUSIONS:
                    scripts_py.append(rel)
                elif path.suffix == ".html":
                    scripts_html.append(rel)
        return {"py": sorted(scripts_py), "html": sorted(scripts_html)}

    @classmethod
    def executer_script(cls, nom_script: str) -> None:
        chemin = BASE_PATH / nom_script
        if not chemin.is_file():
            logging.warning(f"Fichier introuvable : {nom_script}")
            return
        logging.info(f"Exécution du script : {nom_script}")
        result = subprocess.run([sys.executable, str(chemin)], capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"❌ Échec du script : {nom_script}")
            logging.error(f"Code retour : {result.returncode}")
            logging.error(f"Erreur : {result.stderr.strip()}")
        else:
            logging.info(f"✅ Script terminé : {nom_script}")
            if result.stdout.strip():
                logging.debug(result.stdout.strip())

    @classmethod
    def afficher_html(cls, nom_fichier: str) -> None:
        chemin = BASE_PATH / nom_fichier
        if not chemin.is_file():
            logging.warning(f"Fichier HTML introuvable : {nom_fichier}")
            return
        logging.info(f"Affichage du fichier HTML : {nom_fichier}")
        os.system(f'start "" "{chemin}"')

    @classmethod
    def coordonner(cls, mode="normal") -> None:
        logging.info("→ Coordination automatique des modules Luxuria")
        scripts = cls.lister_scripts()
        for script in scripts["py"]:
            logging.info(f"→ Traitement : {script}")
            cls.executer_script(script)
            if mode == "diagnostic":
                logging.info("Diagnostic post-script terminé")
        for html in scripts["html"]:
            cls.afficher_html(html)

    @classmethod
    def orchestrer(cls, audit: callable, diagnostic: callable) -> None:
        logging.info("→ Orchestration personnalisée")
        try:
            audit()
            logging.info("Audit terminé")
        except Exception as audit_err:
            logging.error(f"Échec audit : {audit_err}")
        try:
            diagnostic()
            logging.info("Diagnostic terminé")
        except Exception as diag_err:
            logging.error(f"Échec diagnostic : {diag_err}")
        logging.info("Orchestration terminée")

    # === Fonctions métier
    @staticmethod
    def verifier_acces(user_id: str, mot_de_passe: str) -> bool:
        return user_id == ADMIN_ID and mot_de_passe == ADMIN_MDP

    @staticmethod
    def notifier_connexion(user_id: str) -> None:
        logging.info(f"Connexion réussie pour : {user_id}")

    @staticmethod
    def demarrer_inscription() -> None:
        logging.info("Processus d'inscription lancé.")

    @staticmethod
    def enregistrer_nouvelle_inscription(data: dict) -> bool:
        logging.info(f"Enregistrement des données : {data}")
        return True

    @staticmethod
    def get_client_fiche(client_id: str) -> dict:
        logging.info(f"Récupération fiche client : {client_id}")
        return {"id": client_id, "nom": "Client Exemple", "status": "actif"}

    @staticmethod
    def get_client_details(client_id: str) -> dict:
        logging.info(f"Détails client : {client_id}")
        return {"id": client_id, "nom": "Client Exemple", "email": "client@luxuria.com"}

    @staticmethod
    def get_section_client(client_id: str) -> str:
        logging.info(f"Section active pour : {client_id}")
        return "profil"

    @staticmethod
    def get_style_details(client_id: str) -> dict:
        logging.info(f"Récupération style client : {client_id}")
        return {"couleur": "bleu", "police": "Roboto"}

    @staticmethod
    def generer_design_client(client_id: str) -> str:
        style = AssistantPDG.get_style_details(client_id)
        logging.info(f"Génération design pour {client_id} avec {style}")
        return f"Design_{client_id}.html"

    @staticmethod
    def generer_image(client_id: str) -> str:
        logging.info(f"Génération image pour : {client_id}")
        return f"{client_id}_image.png"

    @staticmethod
    def modifier_image(image_path: str, filtre: str) -> str:
        logging.info(f"Application filtre '{filtre}' sur : {image_path}")
        return f"{image_path}_modifié"

    @staticmethod
    def verifier_paiement(client_id: str) -> bool:
        logging.info(f"Vérification paiement pour : {client_id}")
        return True

    @staticmethod
    def generer_pdg_protege(client_id: str) -> str:
        logging.info(f"Génération profil PDG protégé pour : {client_id}")
        return f"PDG_{client_id}_secure.json"

    @staticmethod
    def generer_pdf_protege(client_id: str) -> str:
        logging.info(f"Génération PDF sécurisé pour : {client_id}")
        return f"{client_id}_secure.pdf"

    @staticmethod
    def section_est_valide(section: str) -> bool:
        return section in ["accueil", "profil", "paiement", "communauté"]

    @staticmethod
    def valider_acces_communaute(user_id: str, mot_de_passe: str) -> bool:
        return user_id.startswith("lux_") and mot_de_passe == "motdepasse_test"

    @staticmethod
    def ouvrir_interface(nom: str) -> None:
        AssistantPDG.afficher_html(f"{nom}.html")

    @staticmethod
    def executer_modules() -> None:
        logging.info("Exécution manuelle des modules")
        AssistantPDG.coordonner()

# === Fonctions d'accès externes
def get_admin_credentials() -> dict:
    return {"id": AssistantPDG.ADMIN_ID, "password": AssistantPDG.ADMIN_MDP}

def get_api_key() -> str:
    return AssistantPDG.API_KEY

def verifier_admin(id_admin: str, mdp_admin: str) -> bool:
    return id_admin == AssistantPDG.ADMIN_ID and mdp_admin == AssistantPDG.ADMIN_MDP

# === Fonctions exposées pour les interfaces
def verifier_access(role: str, identifiant: str, cle: str = "", mot_de_passe: str = "") -> bool:
    if role == "client":
        return identifiant.startswith("lux_") and cle == API_KEY
    elif role == "admin":
        return identifiant == ADMIN_ID and mot_de_passe == ADMIN_MDP
    elif role == "communaute":
        return AssistantPDG.valider_acces_communaute(identifiant, mot_de_passe)
    return False

def demarrer_inscription(role: str) -> None:
    logging.info(f"Inscription lancée pour le rôle : {role}")
    AssistantPDG.demarrer_inscription()

# === Fonctions accessibles via import assistant_pdg
notifier_connexion = AssistantPDG.notifier_connexion
ouvrir_interface = AssistantPDG.ouvrir_interface
valider_acces_communaute = AssistantPDG.valider_acces_communaute
get_client_fiche = AssistantPDG.get_client_fiche
get_style_details = AssistantPDG.get_style_details
generer_design_client = AssistantPDG.generer_design_client
section_est_valide = AssistantPDG.section_est_valide

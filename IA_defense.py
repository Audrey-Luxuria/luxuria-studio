# -*- coding: utf-8 -*-
"""Protocole de défense IA - Luxuria Studio"""

import json
import hashlib
import logging
import datetime
import smtplib
from email.message import EmailMessage
from pathlib import Path
from secrets import token_hex
from assistant_pdg import AssistantPDG

# === Répertoires
BASE_DIR = Path(__file__).resolve().parent
DEFENSE_DIR = BASE_DIR / "luxuria_defense"
HONEYPOT_DIR = DEFENSE_DIR / "honeypots"
KEYS_FILE = DEFENSE_DIR / "clefs_securite.json"
THREATS_JSON = DEFENSE_DIR / "menaces_detectees.json"
LOG_FILE = DEFENSE_DIR / "defense.log"

# === Configuration admin
ADMIN_EMAIL = "admin@luxuria.ai"
SMTP_SERVER = "smtp.luxuria.ai"
SMTP_PORT = 587

# === Signatures connues
SIGNATURES_MALWARE = {
    "eval(": "usage de eval",
    "exec(": "usage de exec",
    "import socket": "tentative de connexion réseau",
    "subprocess.Popen": "exécution de commande système",
    "rm -rf": "commande destructrice",
    "base64.b64decode": "obfuscation potentielle"
}

# === Modules critiques
CRITICAL_MODULES = [
    "admin_luxuria.py",
    "assistant_pdg.py",
    "luxuria_orchestrateur.py",
    "requirements.py"
]

# === Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# === Initialisation
DEFENSE_DIR.mkdir(exist_ok=True)
HONEYPOT_DIR.mkdir(exist_ok=True)

def hacher_contenu(contenu: str) -> str:
    return hashlib.sha256(contenu.encode("utf-8")).hexdigest()

def detecter_malwares(script: Path) -> list:
    menaces = []
    try:
        contenu = script.read_text(encoding="utf-8")
        for signature, description in SIGNATURES_MALWARE.items():
            if signature in contenu:
                menaces.append({
                    "fichier": str(script),
                    "signature": signature,
                    "description": description,
                    "hash": hacher_contenu(contenu),
                    "horodatage": datetime.datetime.now().isoformat()
                })
    except Exception as err:
        logging.warning(f"Erreur lecture {script.name} : {err}")
    return menaces

def bloquer(script: Path) -> None:
    try:
        script.chmod(0o000)
        logging.warning(f"Exécution bloquée : {script.name}")
    except Exception as err:
        logging.error(f"Erreur blocage {script.name} : {err}")

def recenser(menaces: list) -> None:
    historique = []
    if THREATS_JSON.exists():
        try:
            historique = json.loads(THREATS_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            historique = []
    historique.extend(menaces)
    THREATS_JSON.write_text(json.dumps(historique, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info(f"{len(menaces)} menace(s) recensée(s).")

def deployer_honeypots() -> None:
    leurres = ["config_admin.py", "luxuria_secret.py", "db_credentials.py"]
    for leurre in leurres:
        path = HONEYPOT_DIR / leurre
        contenu = f"# Honeypot : {leurre}\n# Ne pas toucher\n"
        path.write_text(contenu, encoding="utf-8")
        logging.info(f"Honeypot déployé : {leurre}")

def verifier_honeypots() -> list:
    intrusions = []
    for honeypot in HONEYPOT_DIR.glob("*.py"):
        if honeypot.stat().st_mtime != honeypot.stat().st_ctime:
            intrusions.append(str(honeypot))
            logging.warning(f"Intrusion détectée sur honeypot : {honeypot.name}")
    return intrusions

def revoquer_et_regenerer_cles() -> None:
    nouvelles_cles = {
        "admin_key": token_hex(32),
        "api_key": token_hex(32),
        "session_token": token_hex(32),
        "horodatage": datetime.datetime.now().isoformat()
    }
    KEYS_FILE.write_text(json.dumps(nouvelles_cles, indent=2), encoding="utf-8")
    logging.info("Clés compromises révoquées et régénérées.")

def notifier_admin(sujet: str, corps: str) -> None:
    try:
        msg = EmailMessage()
        msg["Subject"] = sujet
        msg["From"] = "defense@luxuria.ai"
        msg["To"] = ADMIN_EMAIL
        msg.set_content(corps)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.send_message(msg)
        logging.info("Notification envoyée à l'administrateur.")
    except Exception as err:
        logging.error(f"Erreur envoi notification : {err}")

def defense_luxuria() -> None:
    logging.info("🛡️ Lancement du protocole IA Defense Luxuria")

    deployer_honeypots()
    intrusions = verifier_honeypots()

    menaces_detectees = []
    for script in BASE_DIR.glob("*.py"):
        if script.name == "IA_defense.py":
            continue
        menaces = detecter_malwares(script)
        if menaces:
            bloquer(script)
            menaces_detectees.extend(menaces)

    if menaces_detectees or intrusions:
        recenser(menaces_detectees)
        revoquer_et_regenerer_cles()
        notifier_admin(
            sujet="Alerte Sécurité Luxuria",
            corps=f"{len(menaces_detectees)} menace(s) détectée(s).\n"
                  f"Honeypots compromis : {', '.join(intrusions)}\n"
                  f"Clés régénérées automatiquement."
        )

# === Orchestration centralisée
def run():
    defense_luxuria()

AssistantPDG.register("IA_defense", run)

# -*- coding: utf-8 -*-
"""Module de gestion des campagnes publicitaires Luxuria."""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from assistant_pdg import AssistantPDG

# === Configuration dynamique
base_path: Path = Path()
log_file: Path = Path()
export_file: Path = Path()
visuels_dir: Path = Path()

def init_paths(path: Path) -> None:
    global base_path, log_file, export_file, visuels_dir
    if not isinstance(path, Path):
        raise TypeError("init_paths attend un objet de type Path")
    base_path = path.resolve()
    log_file = base_path / "campagnes_log.txt"
    export_file = base_path / "campagnes_export.json"
    visuels_dir = base_path / "visuels"
    visuels_dir.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="[PUB] %(message)s")

TARIFS_PAR_PAYS: Dict[str, str] = {
    "FR": "8", "US": "$8", "JP": "980",
    "CN": "58", "BR": "R$44", "AF": "80 Dh",
}

PLATEFORMES: List[str] = [
    "Instagram", "Facebook", "Twitter", "LinkedIn", "Pinterest",
    "TikTok", "Snapchat", "GoogleAds", "YouTube", "Reddit",
    "Medium", "Tumblr", "WhatsApp", "Telegram", "Discord"
]

publicite_active = True

# === Modèle de données
@dataclass
class Campagne:
    id: str
    pays: str
    roles: List[str]
    periode: Tuple[str, str]
    message: str
    visuel: str
    publiee: bool = True

campagnes: Dict[str, List[Campagne]] = {}

# === Fonctions utilitaires
def log(message: str) -> None:
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"[{horodatage}] {message}\n")
    except OSError as e:
        logging.warning(f"Erreur écriture log : {e}")

def generer_visuel(campagne: Campagne) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_facecolor("#b19770")
    ax.text(0.5, 0.5, campagne.message, fontsize=24, color="white",
            ha="center", va="center", transform=ax.transAxes)
    plt.axis("off")
    try:
        plt.savefig(campagne.visuel, bbox_inches="tight")
        plt.close()
        log(f"Visuel généré : {campagne.visuel}")
    except Exception as e:
        logging.error(f"Erreur génération visuel : {e}")

def poster_sur(plateforme: str, visuel_path: str) -> None:
    nom_fichier = Path(visuel_path).name
    log(f"Visuel {nom_fichier} diffusé sur {plateforme}")
    logging.info(f"{plateforme} - {nom_fichier}")

# === Campagne
def creer_campagne(pays: str, role: str) -> Campagne:
    pays_code = pays.strip().upper()
    date_du_jour = datetime.now().strftime("%Y-%m-%d")
    identifiant = f"camp_{pays_code.lower()}_{role}_{date_du_jour.replace('-', '')}"
    message = f"Luxuria - Offre spéciale pour {role} ({pays_code})"
    visuel_fichier = visuels_dir / f"{identifiant}.png"
    campagne = Campagne(
        id=identifiant,
        pays=pays_code,
        roles=[role],
        periode=(date_du_jour, date_du_jour),
        message=message,
        visuel=str(visuel_fichier)
    )
    generer_visuel(campagne)
    campagnes.setdefault(pays_code, []).append(campagne)
    log(f"Campagne créée : {identifiant}")
    return campagne

def diffuser(campagne: Campagne) -> None:
    if not publicite_active:
        log("Diffusion annulée : publicité désactivée")
        logging.info("Publicité désactivée")
        return
    for plateforme in PLATEFORMES:
        poster_sur(plateforme, campagne.visuel)
    logging.info(f"Campagne '{campagne.id}' diffusée sur {len(PLATEFORMES)} plateformes.")

def exporter() -> None:
    try:
        contenu = {p: [asdict(c) for c in lst] for p, lst in campagnes.items()}
        with export_file.open("w", encoding="utf-8") as f:
            json.dump(contenu, f, indent=2, ensure_ascii=False)
        log("Export JSON effectué")
    except Exception as e:
        logging.error(f"Erreur export JSON : {e}")

# === Interface graphique
def interface() -> None:
    root = tk.Tk()
    root.title("Luxuria - Campagnes actives")
    root.geometry("800x600")

    tk.Label(root, text="Campagnes actives", font=("Helvetica", 16, "bold")).pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=5)
    tk.Label(frame, text="Pays :").grid(row=0, column=0, padx=(0, 8))
    pays_var = tk.StringVar(value="FR")
    ttk.Combobox(frame, textvariable=pays_var,
                 values=sorted(campagnes.keys()), state="readonly").grid(row=0, column=1)

    zone = tk.Text(root, width=100, height=25)
    zone.pack(pady=10)

    def afficher() -> None:
        zone.delete("1.0", tk.END)
        pays_sel = pays_var.get().upper()
        date_actuelle = datetime.now().strftime("%Y-%m-%d")
        actives = [
            c for c in campagnes.get(pays_sel, [])
            if c.publiee and c.periode[0] <= date_actuelle <= c.periode[1]
        ]
        if not actives:
            zone.insert(tk.END, "Aucune campagne active.\n")
            return
        tarif = TARIFS_PAR_PAYS.get(pays_sel, "N/A")
        for c in actives:
            zone.insert(tk.END,
                f"{c.message}\nVisuel : {Path(c.visuel).name}\n"
                f"Période : {c.periode[0]} à {c.periode[1]}\n"
                f"Tarif : {tarif}\n---\n"
            )

    ttk.Button(root, text="Afficher", command=afficher).pack(pady=5)
    root.mainloop()

# === Orchestration
def run_campaigns(path: Path) -> None:
    init_paths(path)
    campagne_demo = creer_campagne("FR", "admin")
    diffuser(campagne_demo)
    exporter()
    interface()

# === Orchestration centralisée
def run():
    dossier = Path(__file__).resolve().parent
    run_campaigns(dossier)

AssistantPDG.register("campagne_publicite", run)

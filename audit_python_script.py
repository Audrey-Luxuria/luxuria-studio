import logging
from pathlib import Path
from assistant_pdg import AssistantPDG

# === Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

def ranger_fichier(dossier: Path, nom_fichier: str) -> None:
    """
    Vérifie la présence du fichier dans chaque sous-dossier et le déplace si nécessaire.
    Le dossier et le nom du fichier sont injectés dynamiquement.
    """
    if not dossier.is_dir():
        logging.error(f"Dossier invalide : {dossier}")
        return

    fichier_source = dossier / nom_fichier
    if not fichier_source.is_file():
        logging.warning(f"Fichier source introuvable à la racine : {nom_fichier}")
        return

    sous_dossiers = [d for d in dossier.iterdir() if d.is_dir()]
    for sous_dossier in sous_dossiers:
        cible = sous_dossier / nom_fichier
        if cible.is_file():
            logging.info(f"✅ Présent : {sous_dossier.name}/{nom_fichier}")
        else:
            try:
                fichier_source.rename(cible)
                logging.info(f"📦 Déplacé vers : {sous_dossier.name}/{nom_fichier}")
                break  # On ne déplace qu'une fois
            except PermissionError:
                logging.error(f"⛔ Permission refusée pour déplacer vers : {sous_dossier}")
            except FileNotFoundError:
                logging.error(f"❌ Fichier source introuvable pendant le déplacement.")
            except OSError as e:
                logging.error(f"⚠️ Erreur système : {e}")

def main(dossier_cible: Path, fichier_recherche: str) -> None:
    logging.info("🧹 Lancement du rangement pour l'assistant-PDG...")
    ranger_fichier(dossier_cible, fichier_recherche)

# === Orchestration centralisée
def run():
    dossier_test = Path(__file__).resolve().parent / "test_rangement"
    fichier_test = "rapport.json"
    main(dossier_test, fichier_test)

AssistantPDG.register("assistant_technique", run)

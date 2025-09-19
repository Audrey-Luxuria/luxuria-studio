# -*- coding: utf-8 -*-
"""Point d’entrée principal de Luxuria Studio."""

import logging
from assistant_pdg import AssistantPDG
from flask import Flask

# === Initialisation minimale du serveur Flask
app = Flask(__name__)

# === Configuration du logging
logging.basicConfig(level=logging.INFO, format="[Luxuria] %(message)s")

def main():
    logging.info("🧠 Lancement du serveur Luxuria Studio...")
    AssistantPDG.coordonner()

    logging.info("📦 Modules détectés :")
    modules = [
        "access_manager", "admin_private", "analyse_imports", "api_veille", "assistant_technique",
        "audit_python_script", "builds_ads_manager", "build_assistant_pdg", "camapagne_publicite",
        "chemin_universel", "config", "config_sauvegarde_auto", "contrats", "coordinateur",
        "correcteur_ASCII_syntaxe", "correcteur_eval", "correcteur_imports", "correcteur_indentation",
        "correcteur_os", "correcteur_print_logging", "correcteur_strucutre", "creation_design",
        "declaration_entreprise", "detecte_modules_externes", "dictionnaire_auto", "diffuseur_universel",
        "faq_assistant", "fiche_client", "fix_structure", "galerie_commune", "galerie_privee",
        "IA_defense", "interface", "interface_admin", "interface_client", "interface_communaute",
        "interface_creation", "interface_inscription", "logo_png", "luxuria_access_audit", "luxuria_admin",
        "luxuria_client_access", "luxuria_community", "luxuria_conformite", "luxuria_contrats",
        "luxuria_converter", "luxuria_deduplicator", "luxuria_facture", "luxuria_finance_tracker",
        "luxuria_gestion", "luxuria_ia", "luxuria_initializer", "luxuria_keys_checker", "luxuria_manager",
        "luxuria_modtools", "luxuria_modules_organizer", "luxuria_pro", "luxuria_reset",
        "luxuria_sql_manager", "luxuria_stylizer", "luxuria_system", "luxuria_utils", "luxuria_web",
        "manager", "migration_serveur", "modules", "module_declaration_urssaf", "neutraliser_debugger",
        "processus_design", "requirements", "run_audit", "run_diagnostic", "scanner", "stat_gui",
        "surveillance_reponse_mail", "tarifs", "utils", "veille", "verificateur_luxuria"
    ]
    for mod in modules:
        logging.info(f" - {mod}")

    logging.info("🖼️ Fichiers HTML détectés :")
    html_files = [
        "404.html", "acceuil.html", "admin.html", "clause.html", "cles.html", "client.html",
        "communaute.html", "conversations.html", "creation.html", "dashboard.html", "galeriecommune.html",
        "galerieprivee.html", "logging.html", "navbar.html", "notifications.html", "nouveauclient.html",
        "paiement.html", "publicite.html", "signature.html", "stats_card.html"
    ]
    for html in html_files:
        logging.info(f" - {html}")

    logging.info("🚀 Démarrage du serveur Flask...")
    app.run(debug=False, port=5000, use_reloader=False)

# === Bloc d’exécution autonome
if __name__ == "__main__":
    main()

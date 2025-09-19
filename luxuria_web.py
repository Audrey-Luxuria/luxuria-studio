# luxuria_web.py - Interface web centralisée pour Luxuria Studio

from flask import Flask, render_template_string, send_file, abort
from assistant_pdg import AssistantPDG, BASE_PATH
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="[LUXURIA WEB] %(message)s")

# === Route d'accueil
@app.route("/")
def accueil():
    modules = AssistantPDG.lister_modules().get("modules", [])
    html = "<h1>Luxuria Studio</h1><ul>"
    for mod in modules:
        html += f"<li><a href='/executer/{mod}'>{mod}</a></li>"
    html += "</ul>"
    return render_template_string(html)

# === Exécution d’un module
@app.route("/executer/<nom_module>")
def executer_module(nom_module):
    try:
        AssistantPDG.executer_module(nom_module)
        return f"<h3>Module '{nom_module}' exécuté avec succès.</h3>"
    except Exception as e:
        return f"<h3>Erreur lors de l'exécution de '{nom_module}' : {e}</h3>", 500

# === Affichage d’un fichier HTML
@app.route("/interface/<nom_fichier>")
def afficher_interface(nom_fichier):
    chemin = BASE_PATH / nom_fichier
    if not chemin.is_file():
        abort(404)
    return send_file(chemin)

# === Lancement manuel via Flask
def run():
    logging.info("Lancement de l'interface web Luxuria...")
    app.run(debug=False, use_reloader=False, port=5000)

AssistantPDG.register("luxuria_web", run)

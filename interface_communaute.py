from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import json, os
import assistant_pdg  # Orchestrateur passif

communaute_bp = Blueprint("communaute", __name__, template_folder="templates")

# === Configuration
FICHIER_MESSAGES = "messages.json"
SALONS_TEXTUELS = ["art_emotionnel", "pierres_rares", "galerie_mystique"]
SALONS_VOCAUX = ["salon_vocal_1", "salon_vocal_2"]

# === Initialisation
def charger_messages():
    if not os.path.exists(FICHIER_MESSAGES):
        with open(FICHIER_MESSAGES, "w", encoding="utf-8") as f:
            json.dump({salon: [] for salon in SALONS_TEXTUELS}, f)

    with open(FICHIER_MESSAGES, "r", encoding="utf-8") as f:
        return json.load(f)

def enregistrer_message(salon, auteur, contenu):
    messages = charger_messages()
    nouveau = {"nom": auteur, "contenu": contenu}
    messages[salon].append(nouveau)

    with open(FICHIER_MESSAGES, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

# === Authentification
@communaute_bp.route("/communaute/login", methods=["GET", "POST"])
def login_communaute():
    if request.method == "POST":
        identifiant = request.form.get("identifiant")
        mot_de_passe = request.form.get("mot_de_passe")

        if assistant_pdg.valider_acces_communaute(identifiant, mot_de_passe):
            session["communaute_user"] = identifiant
            return redirect(url_for("communaute.salon_textuel", nom_salon=SALONS_TEXTUELS[0]))
        else:
            flash("Accès refusé à la communauté.", "error")
            return redirect(url_for("communaute.login_communaute"))

    return render_template("communaute_login.html")

# === Salon textuel
@communaute_bp.route("/communaute/textuel/<nom_salon>", methods=["GET", "POST"])
def salon_textuel(nom_salon):
    if "communaute_user" not in session:
        return redirect(url_for("communaute.login_communaute"))

    if nom_salon not in SALONS_TEXTUELS:
        flash("Salon inexistant.", "error")
        return redirect(url_for("communaute.salon_textuel", nom_salon=SALONS_TEXTUELS[0]))

    messages = charger_messages().get(nom_salon, [])

    if request.method == "POST":
        contenu = request.form.get("message")
        if contenu:
            enregistrer_message(nom_salon, session["communaute_user"], contenu)
            return redirect(url_for("communaute.salon_textuel", nom_salon=nom_salon))

    return render_template(
        "communaute_salon.html",
        salon=nom_salon,
        messages=messages,
        salons_textuels=SALONS_TEXTUELS,
        salons_vocaux=SALONS_VOCAUX,
        user=session["communaute_user"]
    )

# === Salon vocal
@communaute_bp.route("/communaute/vocal/<nom_salon>")
def salon_vocal(nom_salon):
    if "communaute_user" not in session:
        return redirect(url_for("communaute.login_communaute"))

    if nom_salon not in SALONS_VOCAUX:
        flash("Salon vocal inexistant.", "error")
        return redirect(url_for("communaute.salon_vocal", nom_salon=SALONS_VOCAUX[0]))

    return render_template(
        "communaute_vocal.html",
        salon=nom_salon,
        user=session["communaute_user"]
    )

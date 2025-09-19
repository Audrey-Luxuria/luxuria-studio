from flask import Blueprint, render_template, request, redirect, url_for, flash
import assistant_pdg  # ✅ Orchestrateur principal

client_bp = Blueprint("client", __name__, template_folder="templates")

@client_bp.route("/client", methods=["GET", "POST"])
def espace_client():
    fiche = None
    style_info = None
    design_ia = None
    section = None

    if request.method == "POST":
        nom = request.form.get("nom", "").lower()
        action = request.form.get("action")

        fiche = assistant_pdg.get_client_fiche(nom)
        if not fiche:
            flash("Client introuvable.", "error")
            return redirect(url_for("client.espace_client"))

        style_info = assistant_pdg.get_style_details(nom)

        if action == "design":
            design_ia = assistant_pdg.generer_design_client(nom)
        elif action.startswith("section:"):
            section = action.split("section:")[1]
            if not assistant_pdg.section_est_valide(section):
                flash("Section inconnue.", "error")
                return redirect(url_for("client.espace_client"))

    return render_template(
        "client.html",
        fiche=fiche,
        style_info=style_info,
        design_ia=design_ia,
        section=section,
        menu_sections=["accueil", "profil", "paiement", "communauté"]  # Remplacement temporaire
    )

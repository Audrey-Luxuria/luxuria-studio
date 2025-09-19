from flask import Flask, render_template, request, redirect, flash, send_file, session
import assistant_pdg  # Orchestrateur passif
import io

app = Flask(__name__)
app.secret_key = "luxuria_creation_secret"

# Stockage temporaire en memoire
session_designs = {}

@app.route("/", methods=["GET", "POST"])
def creation():
    if request.method == "POST":
        client_nom = request.form.get("client_nom", "").strip()
        instructions = request.form.get("instructions", "").strip()
        touche = request.form.get("touche", "").strip()
        modifier = request.form.get("modifier", "").strip()

        if not client_nom or not instructions:
            flash("Le nom du client et les instructions sont obligatoires.", "error")
            return redirect("/")

        # Generation d'image via assistant
        image_bytes = assistant_pdg.generer_image(instructions, touche)

        # Modification si demandee
        if modifier:
            image_bytes = assistant_pdg.modifier_image(image_bytes, modifier)

        # Enregistrement
        design_id = f"{client_nom.lower()}_{len(session_designs)+1}"
        session_designs[design_id] = {
            "client": client_nom,
            "instructions": instructions,
            "touche": touche,
            "image_bytes": image_bytes
        }

        session["design_id"] = design_id
        flash(" Design genere avec succes.", "success")
        return redirect("/resultat")

    return render_template("creation.html")

@app.route("/resultat")
def resultat():
    design_id = session.get("design_id")
    if not design_id or design_id not in session_designs:
        flash("Aucun design a afficher.", "error")
        return redirect("/")

    design = session_designs[design_id]
    return render_template("resultat.html", design=design, design_id=design_id)

@app.route("/image/<design_id>")
def afficher_image(design_id):
    design = session_designs.get(design_id)
    if not design:
        flash("Image introuvable.", "error")
        return redirect("/")

    return send_file(
        io.BytesIO(design["image_bytes"]),
        mimetype="image/png",
        download_name=f"{design_id}.png"
    )

@app.route("/telecharger_pdf/<design_id>")
def telecharger_pdf(design_id):
    design = session_designs.get(design_id)
    if not design or not assistant_pdg.verifier_paiement(design["client"]):
        flash("Paiement requis pour acceder au PDF.", "error")
        return redirect("/resultat")

    pdf_buffer = assistant_pdg.generer_pdf_protege(design["image_bytes"], design["client"])
    return send_file(pdf_buffer, mimetype="application/pdf", download_name=f"{design_id}.pdf")

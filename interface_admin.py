from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify, flash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pathlib import Path
import io
import json
import logging
import assistant_pdg  # Orchestrateur passif

admin_bp = Blueprint("admin", __name__, template_folder="templates")
ROOT = Path(__file__).resolve().parent
logging.basicConfig(level=logging.INFO, format="[ADMIN] %(message)s")

# === Identifiants verrouillés
ADMIN_ID = "Audreyplatel"
ADMIN_MDP = "Borderlands87"

# === Utilitaires
def generer_pdf(titre: str, contenu: str = "Contenu généré automatiquement.") -> send_file:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, titre)
    pdf.drawString(100, 730, contenu)
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    nom_fichier = f"{titre.replace(' ', '_')}.pdf"
    logging.info(f"PDF généré : {nom_fichier}")
    return send_file(buffer, mimetype="application/pdf", download_name=nom_fichier)

def charger_json(nom_fichier: str):
    path = ROOT / nom_fichier
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# === Routes
@admin_bp.route("/admin", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifiant = request.form.get("identifiant")
        mot_de_passe = request.form.get("mot_de_passe")

        if identifiant == ADMIN_ID and mot_de_passe == ADMIN_MDP:
            session["user"] = "admin"
            assistant_pdg.notifier_connexion(identifiant)
            return redirect(url_for("admin.dashboard_ca"))
        else:
            flash("Accès refusé.", "error")
            return redirect(url_for("admin.login"))

    return render_template("admin_login.html")

@admin_bp.route("/admin/dashboard")
def dashboard_ca():
    if session.get("user") != "admin":
        return redirect(url_for("admin.login"))

    sections = [
        {"titre": "Déclaration URSSAF Mensuelle", "url": url_for("admin.urssaf_mensuelle")},
        {"titre": "Déclaration URSSAF Annuelle", "url": url_for("admin.urssaf_annuelle")},
        {"titre": "Dossier de Déclaration Entreprise", "url": url_for("admin.declaration_entreprise")},
        {"titre": "Historique des Paiements", "url": url_for("admin.paiements")},
        {"titre": "Export PDF", "url": url_for("admin.export_section", section="global")},
        {"titre": "Conversations de la communauté", "url": url_for("admin.conversations")},
        {"titre": "Signatures de la charte", "url": url_for("admin.signatures_charte")},
        {"titre": "Clés d'accès", "url": url_for("admin.cles_acces")},
        {"titre": "Notifications", "url": url_for("admin.notifications")}
    ]

    return render_template("admin_dashboard.html", sections=sections)

@admin_bp.route("/admin/urssaf-mensuelle")
def urssaf_mensuelle():
    return generer_pdf("Déclaration URSSAF Mensuelle")

@admin_bp.route("/admin/urssaf-annuelle")
def urssaf_annuelle():
    return generer_pdf("Déclaration URSSAF Annuelle")

@admin_bp.route("/admin/declaration-entreprise")
def declaration_entreprise():
    return generer_pdf("Dossier de Déclaration Entreprise")

@admin_bp.route("/admin/paiements")
def paiements():
    return generer_pdf("Historique des Paiements")

@admin_bp.route("/admin/export/<section>")
def export_section(section: str):
    return generer_pdf(f"Export PDF - Section : {section}")

@admin_bp.route("/admin/conversations")
def conversations():
    return render_template("admin_section.html", titre="Conversations de la communauté", contenu="Historique à venir...")

@admin_bp.route("/admin/signatures-charte")
def signatures_charte():
    signatures = charger_json("signatures.json")
    return render_template("admin_section.html", titre="Signatures de la charte", contenu=signatures)

@admin_bp.route("/admin/cles-acces")
def cles_acces():
    cles = charger_json("cles_acces.json")
    return render_template("admin_section.html", titre="Clés d'accès", contenu=cles)

@admin_bp.route("/admin/notifications")
def notifications():
    return render_template("admin_section.html", titre="Notifications", contenu="Aucune alerte pour le moment.")

@admin_bp.route("/admin/assistant-pdg")
def assistant_pdg_view():
    return jsonify({
        "role": "assistant",
        "mode": "orchestration passive",
        "droits": "lecture uniquement",
        "identifiant_admin": ADMIN_ID
    })

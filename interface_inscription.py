import os, json, hashlib, datetime, smtplib
from email.message import EmailMessage
import assistant_pdg  # ✅ Orchestrateur principal

# === Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FICHIER_CLIENTS = os.path.join(BASE_DIR, "clients_inscrits.json")
CATEGORIES = ["Particulier", "Professionnel", "Studio", "Ecole", "Assistant-PDG"]

EMAIL_EXPEDITEUR = "luxuria.system@example.com"
EMAIL_MDP = "TON_MOT_DE_PASSE"
SMTP_SERVEUR = "smtp.example.com"
SMTP_PORT = 587

def initialiser_fichier():
    if not os.path.exists(FICHIER_CLIENTS):
        with open(FICHIER_CLIENTS, "w", encoding="utf-8") as f:
            json.dump({cat: [] for cat in CATEGORIES}, f, indent=2, ensure_ascii=False)

def generer_cle_acces(prenom, nom, naissance):
    base = f"{prenom}{nom}{naissance}{datetime.datetime.now().timestamp()}"
    return hashlib.sha256(base.encode()).hexdigest()[:12].upper()

def envoyer_email(destinataire, cle):
    msg = EmailMessage()
    msg["Subject"] = "Votre clé d'accès Luxuria"
    msg["From"] = EMAIL_EXPEDITEUR
    msg["To"] = destinataire
    msg.set_content(f"""Bonjour,

Votre inscription à Luxuria est confirmée.

Voici votre clé d'accès personnelle (valable 30 jours) :
{cle}

Cette clé vous permet d'accéder à la galerie et à la communauté après validation.

Bien à vous,
L'équipe Luxuria""")

    with smtplib.SMTP(SMTP_SERVEUR, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_EXPEDITEUR, EMAIL_MDP)
        smtp.send_message(msg)

def traiter_inscription(form):
    initialiser_fichier()

    prenom = form.get("prenom", "").strip().title()
    nom = form.get("nom", "").strip().title()
    naissance = form.get("naissance", "").strip().replace(" ", "").replace("/", "-")
    adresse = form.get("adresse", "").strip()
    tel = form.get("tel", "").strip()
    email = form.get("email", "").strip()
    categorie = form.get("categorie", "")
    identifiant = form.get("identifiant", "").strip()

    if not all([prenom, nom, naissance, adresse, tel, email, categorie]):
        raise ValueError("Tous les champs doivent être remplis.")

    if categorie not in ["Particulier", "Assistant-PDG"] and not identifiant:
        raise ValueError("Un identifiant est requis pour cette catégorie.")

    try:
        datetime.datetime.strptime(naissance, "%Y-%m-%d")
    except ValueError:
        raise ValueError("La date de naissance doit être au format AAAA-MM-JJ.")

    cle = generer_cle_acces(prenom, nom, naissance)
    date_inscription = datetime.datetime.today()
    date_expiration = date_inscription + datetime.timedelta(days=30)

    client = {
        "prenom": prenom,
        "nom": nom,
        "date_naissance": naissance,
        "adresse": adresse,
        "telephone": tel,
        "email": email,
        "categorie": categorie,
        "identifiant": identifiant if identifiant else None,
        "cle_acces": cle,
        "date_inscription": date_inscription.strftime("%Y-%m-%d"),
        "date_expiration": date_expiration.strftime("%Y-%m-%d"),
        "acces_limite": {
            "galerie": categorie == "Assistant-PDG",
            "pdf": categorie == "Assistant-PDG",
            "communaute": categorie == "Assistant-PDG"
        }
    }

    # === Orchestration centrale
    assistant_pdg.enregistrer_nouvelle_inscription(client)

    if categorie != "Assistant-PDG":
        envoyer_email(email, cle)

    return f"Inscription réussie. Clé envoyée à {email}"

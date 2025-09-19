import json
import requests
import datetime
import logging
from pathlib import Path
from typing import List, Dict
from flask import Flask, request, render_template_string, send_file
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from assistant_pdg import AssistantPDG

# === Setup
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
base_path: Path = Path()  # Initialisé par l’orchestrateur

# === RGPD
def load_rgpd() -> Dict[str, Dict]:
    rgpd_file = base_path / "rgpd_cache.json"
    if not rgpd_file.exists():
        logging.warning("Fichier RGPD introuvable")
        return {}
    try:
        return json.loads(rgpd_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logging.warning("Erreur de décodage JSON RGPD")
        return {}
    except OSError as e:
        logging.warning(f"Erreur lecture RGPD : {e}")
        return {}

def check_rgpd(country: str) -> Dict:
    data = load_rgpd()
    info = data.get(country)
    if not info:
        return {"ok": False, "msg": f"Aucune info RGPD pour {country}"}
    if info.get("compatible"):
        return {"ok": True, "msg": f"{country} est conforme"}
    return {"ok": False, "msg": f"{country} n'est pas conforme"}

# === BOAMP
def get_boamp(date: str) -> List[Dict[str, str]]:
    url = f"https://www.boamp.fr/api/xml?datePublication={date}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, "xml")
        avis = soup.find_all("avis")
        return [
            {
                "title": a.find("titre").text.strip() if a.find("titre") else "Sans titre",
                "subject": a.find("objet").text.strip() if a.find("objet") else "Objet non précisé"
            }
            for a in avis
        ]
    except requests.RequestException as e:
        logging.error(f"Erreur requête BOAMP : {e}")
        return [{"error": str(e)}]

# === Graphiques
def make_rgpd_chart(data: Dict[str, Dict]) -> Path:
    labels = list(data.keys())
    values = [1 if d.get("compatible") else 0 for d in data.values()]
    colors = ["green" if v else "red" for v in values]
    plt.bar(labels, values, color=colors)
    plt.xticks(rotation=45)
    chart_path = base_path / "rgpd_chart.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def make_boamp_chart(avis: List[Dict[str, str]], date: str) -> Path:
    titles = [a.get("title", "Sans titre") for a in avis]
    plt.barh(titles, [1] * len(titles))
    plt.title(f"BOAMP {date}")
    chart_path = base_path / f"boamp_chart_{date}.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# === API
@app.route("/rgpd")
def rgpd_view():
    data = load_rgpd()
    chart = make_rgpd_chart(data)
    return render_template_string(f"<h2>RGPD</h2><img src='/img/{chart.name}' width='600'>")

@app.route("/boamp")
def boamp_view():
    date = request.args.get("date", datetime.datetime.now().strftime("%Y-%m-%d"))
    avis = get_boamp(date)
    chart = make_boamp_chart(avis, date)
    return render_template_string(f"<h2>BOAMP {date}</h2><img src='/img/{chart.name}' width='600'>")

@app.route("/img/<name>")
def serve_image(name):
    image_path = base_path / name
    if not image_path.exists():
        return f"<p>Image introuvable : {name}</p>", 404
    return send_file(image_path, mimetype="image/png")

# === Fonctions appelables
def start_api(path: Path):
    global base_path
    base_path = path.resolve()
    app.run(debug=False, port=5000, use_reloader=False)


def run_cli(path: Path, date: str, country: str = "France"):
    global base_path
    base_path = path.resolve()

    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Format de date invalide. Utiliser YYYY-MM-DD.")
        return

    rgpd = check_rgpd(country)
    print(rgpd["msg"])
    if not rgpd["ok"]:
        return

    avis = get_boamp(date)
    print(f"{len(avis)} avis trouvés pour {date}")
    for a in avis[:5]:
        print("-", a.get("title", "Sans titre"))

# === Orchestration centralisée
def run():
    global base_path
    base_path = Path(__file__).resolve().parent
    logging.info("🧠 Lancement de l'API RGPD + BOAMP")
    run_cli(base_path, datetime.datetime.now().strftime("%Y-%m-%d"), "France")

AssistantPDG.register("api_veille", run)

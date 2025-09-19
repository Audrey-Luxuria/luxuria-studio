import json
import bcrypt
from datetime import datetime
from flask import Flask, request, session, redirect, url_for, render_template_string
from pathlib import Path
from assistant_pdg import AssistantPDG

# === Configuration interne ===
BASE_DIR = Path(__file__).resolve().parent
FILES = {
    "log": BASE_DIR / "admin_log.txt",
    "data": BASE_DIR / "admin_data.json",
    "clients": BASE_DIR / "admin_clients.json",
    "conversations": BASE_DIR / "admin_conversations.json"
}
CONFIG = {
    "secret_key": "luxuria_secret_key",
    "admin_id": "admin",
    "admin_hash": "$2b$12$examplehash"  # bcrypt hash simulé
}

# === Flask setup ===
app = Flask(__name__)
app.secret_key = CONFIG["secret_key"]

# === Initialisation des fichiers ===
def init_files():
    defaults = {
        FILES["log"]: "Log initialized\n",
        FILES["data"]: {"monthly_stats": {}},
        FILES["clients"]: {},
        FILES["conversations"]: {"conversations": []}
    }
    for path, content in defaults.items():
        if not path.exists():
            with path.open("w", encoding="utf-8") as f:
                if isinstance(content, dict):
                    json.dump(content, f, indent=2)
                else:
                    f.write(content)

# === Utilitaires ===
def read_json(path, key=None):
    if not path.exists():
        return {} if key else []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return {} if key else []
    return data.get(key, []) if key else data

def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""

def log_event(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with FILES["log"].open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

# === Authentification ===
def is_admin():
    return session.get("admin") is True

def require_admin():
    return redirect(url_for("login")) if not is_admin() else None

# === Routes ===
@app.route("/")
def home():
    return render_template_string("<h2>Luxuria Studio</h2><a href='/login'><button>Admin Login</button></a>")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ident = request.form.get("identifiant")
        pwd = request.form.get("mot_de_passe", "").encode("utf-8")
        if ident == CONFIG["admin_id"] and bcrypt.checkpw(pwd, CONFIG["admin_hash"].encode("utf-8")):
            session["admin"] = True
            log_event("Admin login successful")
            return redirect(url_for("admin"))
        return render_template_string("<p>Invalid credentials</p><a href='/login'><button>Retry</button></a>")
    return render_template_string("""
        <h3>Admin Login</h3>
        <form method='post'>
            <label>Username:</label><br>
            <input name='identifiant'><br><br>
            <label>Password:</label><br>
            <input name='mot_de_passe' type='password'><br><br>
            <button type='submit'>Login</button>
        </form>
    """)

@app.route("/admin")
def admin():
    if require_admin(): return require_admin()

    month = datetime.now().strftime("%m-%Y")
    stats = read_json(FILES["data"], "monthly_stats")
    total = sum(stats.get(role, {}).get(month, 0.0) for role in stats)

    clients = read_json(FILES["clients"])
    convs = read_json(FILES["conversations"], "conversations")
    log_lines = read_text(FILES["log"]).splitlines()
    last_action = log_lines[-1] if log_lines else "No activity recorded"

    analysis_result = f"{len(clients)} clients, {len(convs)} conversations"

    return render_template_string(f"""
        <h3>Admin Dashboard</h3><ul>
            <li><strong>Revenue ({month}):</strong> {total:.2f}</li>
            <li><strong>Active clients:</strong> {len(clients)}</li>
            <li><strong>Conversations:</strong> {len(convs)}</li>
            <li><strong>Last log entry:</strong> {last_action}</li>
            <li><strong>AI Analysis:</strong> {analysis_result}</li>
        </ul>
        <a href='/logout'><button>Logout</button></a>
    """)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    log_event("Admin logout")
    return redirect(url_for("home"))

# === Orchestration centralisée
def run():
    init_files()
    log_event("Admin server started")
    print("[Luxuria Admin] Server running at http://localhost:5000")
    app.run(debug=False, port=5000, use_reloader=False)


AssistantPDG.register("admin_private", run)

from pathlib import Path

# === Configuration ===
BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR / "luxuria_modules"
EXCLUSIONS = {"__init__.py", "requirements.py", "assistant_pdg.py"}
ORCHESTRATEUR_IMPORT = "from assistant_pdg import AssistantPDG"
REGISTRATION_TEMPLATE = "\n\n# Orchestration centralisée\n{import_line}\n\ndef run():\n    print(\"Module exécuté via AssistantPDG\")\n\nAssistantPDG.register(\"{module_name}\", run)\n"

def module_est_orchestre(contenu: str) -> bool:
    return "AssistantPDG.register" in contenu and "def run" in contenu

def injecter_si_absent(module_path: Path) -> None:
    contenu = module_path.read_text(encoding="utf-8")
    module_name = module_path.stem

    if module_est_orchestre(contenu):
        print(f"✅ Déjà orchestré : {module_name}")
        return

    bloc = REGISTRATION_TEMPLATE.format(import_line=ORCHESTRATEUR_IMPORT, module_name=module_name)
    contenu += bloc
    module_path.write_text(contenu, encoding="utf-8")
    print(f"🔧 Orchestration ajoutée à : {module_name}")

def verifier_et_corriger_modules():
    print("🔍 Vérification des modules Luxuria...")
    for module_file in MODULE_DIR.glob("*.py"):
        if module_file.name in EXCLUSIONS:
            continue
        injecter_si_absent(module_file)
    print("🏁 Vérification terminée. Tous les modules sont maintenant exécutables via AssistantPDG.")

# Bloc __main__ supprimé pour modularisation

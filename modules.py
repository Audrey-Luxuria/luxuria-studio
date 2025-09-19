import shutil
from pathlib import Path
import re

# === Configuration ===
BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR / "luxuria_modules"
EXCLUSIONS = {"requirements.py", "__init__.py"}

def nettoyer_main(script_path: Path) -> None:
    contenu = script_path.read_text(encoding="utf-8")
    nouveau_contenu = re.sub(
        r"\nif\s+__name__\s*==\s*['\"]__main__['\"]:\s*\n(.*\n?)+",
        "\n# Bloc __main__ supprimé pour modularisation\n",
        contenu,
        flags=re.MULTILINE
    )
    script_path.write_text(nouveau_contenu, encoding="utf-8")

def transformer_en_modules():
    MODULE_DIR.mkdir(exist_ok=True)
    init_path = MODULE_DIR / "__init__.py"
    init_path.touch()

    for script in BASE_DIR.glob("*.py"):
        if script.name in EXCLUSIONS or script.name == Path(__file__).name:
            continue

        nouveau_path = MODULE_DIR / script.name
        shutil.move(str(script), str(nouveau_path))
        nettoyer_main(nouveau_path)
        print(f"✅ Module créé : {nouveau_path.name}")

    print(f"\n📦 Tous les scripts ont été transformés en modules dans '{MODULE_DIR.name}'.")

if __name__ == "__main__":
    transformer_en_modules()

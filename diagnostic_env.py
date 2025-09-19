import sys
import site
import os

print("🧠 Interpréteur utilisé :", sys.executable)
print("📦 Dossiers site-packages :", site.getsitepackages())
print("🔍 sys.path :")
for p in sys.path:
    print("   ", p)
print("✅ Environnement virtuel activé :", 'VIRTUAL_ENV' in os.environ)

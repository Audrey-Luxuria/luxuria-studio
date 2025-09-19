# === Luxuria Environment Reset Script (local, sans emojis ni accents) ===
# À exécuter dans PowerShell en tant qu'administratrice

Write-Host "`n[Luxuria] Réinitialisation locale de l'environnement..."

# 1. Se placer dans le dossier principal
$projectPath = "C:\Users\ASUS\Desktop\IALuxuriaDesign"
Set-Location $projectPath

# 2. Supprimer l'ancien environnement s'il existe
if (Test-Path ".venv") {
    Remove-Item ".venv" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Ancien environnement supprimé"
}

# 3. Créer un nouvel environnement virtuel
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
Write-Host "Environnement virtuel activé"

# 4. Installer les modules nécessaires
pip install --upgrade pip setuptools wheel
pip install flask rich requests pigment jinja2

# 5. Vérifier les imports
$testScript = @'
import flask, rich, requests, pigment, jinja2
print("Tous les modules sont importés avec succès.")
'@
$testPath = "$projectPath\test_imports.py"
$testScript | Out-File -Encoding UTF8 $testPath
python $testPath
Remove-Item $testPath -Force

# 6. Message final
Write-Host "`n[Luxuria] Environnement prêt. Tu peux maintenant exécuter : python assistant_pdg.py"

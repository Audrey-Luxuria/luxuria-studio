@echo off
cd /d "%~dp0"
echo [Luxuria] Initialisation de l'orchestrateur principal...

REM === Activation de l'environnement virtuel
call .venv\Scripts\activate.bat

REM === Lancement de l'orchestrateur principal
python assistant_pdg.py

pause

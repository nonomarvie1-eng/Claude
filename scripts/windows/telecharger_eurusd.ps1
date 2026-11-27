# NEXUS QUANT — Téléchargement des données EUR/USD sur Windows (lecture seule, gratuit)
#
# Ce script :
#   1. vérifie que Python est installé ;
#   2. crée un environnement Python isolé dans le dossier du projet (.venv) ;
#   3. installe numpy, pandas, pyarrow (bibliothèques open source) ;
#   4. télécharge les bougies 1 minute EUR/USD (bid et ask) depuis le flux
#      historique public de Dukascopy, à un rythme lent (le serveur limite le débit) ;
#   5. construit les fichiers Parquet et un rapport qualité ;
#   6. crée une archive ZIP sur votre Bureau, à me transmettre.
#
# Il ne passe AUCUN ordre, ne se connecte à aucun courtier et n'envoie rien
# d'autre que des demandes de téléchargement de fichiers historiques publics.
# Le téléchargement peut être interrompu (fermer la fenêtre) et relancé :
# il reprend là où il s'était arrêté.
#
# Utilisation : clic droit sur ce fichier > « Exécuter avec PowerShell »,
# ou dans PowerShell, depuis le dossier du projet :
#     powershell -ExecutionPolicy Bypass -File scripts\windows\telecharger_eurusd.ps1

$ErrorActionPreference = "Stop"
$Projet = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Projet
Write-Host "Dossier du projet : $Projet"

# 1. Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python est introuvable. Installez Python 3.12 depuis https://www.python.org/downloads/ (cochez 'Add python.exe to PATH'), puis relancez ce script." -ForegroundColor Red
    exit 1
}
python --version

# 2-3. Environnement isolé
if (-not (Test-Path ".venv")) { python -m venv .venv }
$vpy = Join-Path $Projet ".venv\Scripts\python.exe"
& $vpy -m pip install --quiet --upgrade pip
& $vpy -m pip install --quiet "numpy>=1.26" "pandas>=2.1" "pyarrow>=14" "scipy>=1.11"

# Inspection de la machine (lecture seule)
& $vpy scripts\check_env.py | Tee-Object -FilePath "reports\check_env_windows.txt"

# 4. Téléchargement (période de développement d'abord, puis le reste)
& $vpy scripts\download_data.py dukascopy EURUSD 2019-12-01 2023-07-01
& $vpy scripts\download_data.py dukascopy EURUSD 2023-07-01 2026-07-01

# 5. Parquet + rapport qualité
& $vpy scripts\build_bars.py EURUSD 2019-12-01 2026-07-01

# 6. Archive à transmettre
$zip = Join-Path ([Environment]::GetFolderPath("Desktop")) "nexus_eurusd_bars.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path "data\bars\EURUSD", "reports\data_quality\EURUSD.json", "reports\check_env_windows.txt" -DestinationPath $zip
Write-Host "Terminé. Archive créée : $zip" -ForegroundColor Green
Write-Host "Transmettez ce fichier dans la conversation Claude (glisser-déposer)."

# =====================================================================
# GTA-MEDIA - Mise à jour du code depuis GitHub
# Récupère la dernière version (dossier source C:\GTA-SRC) puis copie le code
# dans C:\GTA-MEDIA. Vos réglages (config), captures, voix, .venv et vidéos
# ne sont PAS touchés.
# Usage : powershell -ExecutionPolicy Bypass -File C:\GTA-SRC\GTA-MEDIA\scripts\windows\update.ps1
# =====================================================================
param(
    [string]$Src = "C:\GTA-SRC",
    [string]$Dst = "C:\GTA-MEDIA",
    [string]$Branch = "claude/gta-vertical-video-pipeline-a6b3hl",
    [string]$Repo = "https://github.com/nonomarvie1-eng/Claude.git"
)
$ErrorActionPreference = "Stop"
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Host "Git introuvable : lancez install.ps1" -ForegroundColor Red; exit 1 }

if (Test-Path (Join-Path $Src ".git")) {
    Write-Host "Mise à jour de $Src ..." -ForegroundColor Cyan
    git -C $Src fetch origin $Branch
    git -C $Src checkout $Branch
    git -C $Src pull --ff-only origin $Branch
} else {
    Write-Host "Téléchargement initial dans $Src ..." -ForegroundColor Cyan
    git clone -b $Branch $Repo $Src
}
$from = Join-Path $Src "GTA-MEDIA"
foreach ($item in "gtamedia","scripts","docs","gta.py","README.md","requirements.txt") {
    Copy-Item -Path (Join-Path $from $item) -Destination $Dst -Recurse -Force
    Write-Host "  copié : $item"
}
# Crée les dossiers éventuellement manquants
foreach ($d in "inbox","library","output","work","assets\music","assets\sfx","assets\voices") {
    New-Item -ItemType Directory -Force -Path (Join-Path $Dst $d) | Out-Null
}
Get-ChildItem $Dst -Recurse -File -ErrorAction SilentlyContinue | Unblock-File
Write-Host "Code à jour : $(git -C $Src log -1 --format='%h %s')" -ForegroundColor Green

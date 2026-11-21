# =====================================================================
# GTA-MEDIA - Installation guidée et sécurisée (Windows 10/11)
# - Uniquement des logiciels GRATUITS, via winget (sources officielles).
# - Chaque installation demande votre accord (O/N). Aucun achat, aucun compte.
# Usage : powershell -ExecutionPolicy Bypass -File scripts\windows\install.ps1
# =====================================================================
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

function Ask($q) {
    $r = (Read-Host "$q [O/N]").Trim()
    # accepte O, o, Oui, Y, yes et aussi 0 (zéro, souvent tapé par erreur)
    $ok = ($r -match "^(o|oui|y|yes|0)$")
    if (-not $ok) { Write-Host "  (réponse '$r' comprise comme NON)" -ForegroundColor Yellow }
    return $ok
}
function Has($cmd) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    return ($c -and $c.Source -notlike "*WindowsApps*")
}
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget absent : installez 'App Installer' depuis le Microsoft Store puis relancez." -ForegroundColor Red
    exit 1
}

$pkgs = @(
    @{ cmd="python"; id="Python.Python.3.12"; name="Python 3.12 (requis)" },
    @{ cmd="ffmpeg"; id="Gyan.FFmpeg";        name="FFmpeg build complète gyan.dev (requis, inclut libass/zscale)" },
    @{ cmd="git";    id="Git.Git";            name="Git (recommandé, sauvegarde des projets)" },
    @{ cmd="node";   id="OpenJS.NodeJS.LTS";  name="Node.js LTS (optionnel, non utilisé pour l'instant)" }
)
foreach ($p in $pkgs) {
    if (Has $p.cmd) { Write-Host "[OK] $($p.name) déjà installé" -ForegroundColor Green; continue }
    if (Ask "Installer $($p.name) ? (winget id: $($p.id))") {
        winget install --id $p.id --exact --source winget --accept-package-agreements --accept-source-agreements
    } else { Write-Host "  -> ignoré" -ForegroundColor Yellow }
}
# Recharge le PATH sans redémarrer la session
$env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")

$venvPy = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    if (Ask "Créer l'environnement Python isolé .venv et installer les modules (PyYAML, numpy, requests, piper-tts) ?") {
        $base = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
        & $base -m venv .venv
        & $venvPy -m pip install --upgrade pip
        & $venvPy -m pip install -r requirements.txt
    }
}
if ((Test-Path $venvPy) -and -not (Test-Path "assets\voices\fr_FR-siwis-medium.onnx")) {
    if (Ask "Télécharger la voix française gratuite Piper fr_FR-siwis-medium (~60 Mo, licence CC BY 4.0) ?") {
        & $venvPy gta.py voices --download fr_FR-siwis-medium
    }
}
if (Test-Path $venvPy) { & $venvPy gta.py doctor }
Write-Host "`nTerminé. Fermez et rouvrez PowerShell si une commande reste introuvable." -ForegroundColor Cyan

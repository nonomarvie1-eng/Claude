# =====================================================================
# GTA-MEDIA - Raccourci : importer les captures puis monter un projet
# Usage : powershell -ExecutionPolicy Bypass -File scripts\windows\build.ps1 projects\demo\episode.yaml
# =====================================================================
param([Parameter(Mandatory=$true)][string]$Project, [string]$Tts = "")
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
& $py gta.py ingest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($Tts) { & $py gta.py build $Project --tts $Tts } else { & $py gta.py build $Project }
exit $LASTEXITCODE

# =====================================================================
# GTA-MEDIA - Audit du PC Windows (LECTURE SEULE : rien n'est installé ni modifié)
# Usage (PowerShell, dans le dossier GTA-MEDIA) :
#   powershell -ExecutionPolicy Bypass -File scripts\windows\audit.ps1
# Résultat affiché + enregistré dans audit-report.txt
# =====================================================================
$ErrorActionPreference = "SilentlyContinue"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$report = Join-Path $root "audit-report.txt"
$lines = New-Object System.Collections.Generic.List[string]
function Out-Line($status, $name, $detail) {
    $l = "[{0,-3}] {1,-24} {2}" -f $status, $name, $detail
    $lines.Add($l)
    $color = switch ($status) { "OK" {"Green"} "!!" {"Red"} "--" {"Yellow"} default {"Gray"} }
    Write-Host $l -ForegroundColor $color
}
function Get-Ver($cmd, $arg) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if (-not $c) { return $null }
    $out = & $c.Source $arg 2>&1 | Select-Object -First 1
    return "$out ($($c.Source))"
}

Write-Host "=== GTA-MEDIA : audit du PC ===" -ForegroundColor Cyan
$os = Get-CimInstance Win32_OperatingSystem
$build = [int]$os.BuildNumber
Out-Line ($(if ($build -ge 19045) {"OK"} else {"!!"})) "Windows" "$($os.Caption) $($os.Version) build $build ($($os.OSArchitecture))"
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Out-Line "i" "Processeur" "$($cpu.Name.Trim()) - $($cpu.NumberOfLogicalProcessors) threads"
$ram = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
Out-Line ($(if ($ram -ge 8) {"OK"} else {"!!"})) "Mémoire" "$ram Go (8 Go minimum, 16 conseillés)"
foreach ($g in Get-CimInstance Win32_VideoController) {
    $vram = if ($g.AdapterRAM -gt 0) { "{0:N1} Go" -f ($g.AdapterRAM / 1GB) } else { "?" }
    Out-Line "i" "Carte graphique" "$($g.Name) - pilote $($g.DriverVersion) - VRAM~$vram"
}
$drive = Get-PSDrive -Name ($root.Path.Substring(0,1))
$free = [math]::Round($drive.Free / 1GB)
Out-Line ($(if ($free -ge 20) {"OK"} else {"!!"})) "Disque $($drive.Name):" "$free Go libres (20 Go conseillés)"
Out-Line "i" "PowerShell" "$($PSVersionTable.PSVersion) - ExecutionPolicy $(Get-ExecutionPolicy)"
$lp = (Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem").LongPathsEnabled
Out-Line ($(if ($lp -eq 1) {"OK"} else {"--"})) "Chemins longs" ($(if ($lp -eq 1) {"activés"} else {"désactivés (facultatif)"}))

$wg = Get-Ver "winget" "--version"
Out-Line ($(if ($wg) {"OK"} else {"!!"})) "winget" ($(if ($wg) {$wg} else {"ABSENT - installez 'App Installer' depuis le Microsoft Store"}))

# Python : on ignore le faux python.exe du Microsoft Store (WindowsApps)
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py -and $py.Source -like "*WindowsApps*") { $py = $null }
$pyl = Get-Command py -ErrorAction SilentlyContinue
if ($py)      { Out-Line "OK" "Python" "$(& $py.Source --version 2>&1) ($($py.Source))" }
elseif ($pyl) { Out-Line "OK" "Python (py)" "$(& py --version 2>&1)" }
else          { Out-Line "!!" "Python" "ABSENT (3.10+ requis)" }

$ff = Get-Ver "ffmpeg" "-version"
Out-Line ($(if ($ff) {"OK"} else {"!!"})) "FFmpeg" ($(if ($ff) {$ff} else {"ABSENT - requis"}))
if ($ff) {
    $filters = & ffmpeg -hide_banner -filters 2>&1 | Out-String
    foreach ($f in "ass","zscale","loudnorm","sidechaincompress","xfade") {
        $has = $filters -match "\s$f\s"
        Out-Line ($(if ($has) {"OK"} else {"!!"})) "  filtre $f" ($(if ($has) {"présent"} else {"absent"}))
    }
    $enc = & ffmpeg -hide_banner -encoders 2>&1 | Out-String
    foreach ($e in "libx264","h264_nvenc","h264_qsv","h264_amf") {
        Out-Line ($(if ($enc -match $e) {"OK"} else {"--"})) "  encodeur $e" ($(if ($enc -match $e) {"compilé"} else {"absent"}))
    }
}
$fp = Get-Ver "ffprobe" "-version"
Out-Line ($(if ($fp) {"OK"} else {"!!"})) "FFprobe" ($(if ($fp) {"présent"} else {"ABSENT - requis"}))
$node = Get-Ver "node" "--version"
Out-Line ($(if ($node) {"OK"} else {"--"})) "Node.js" ($(if ($node) {$node} else {"absent (optionnel)"}))
$git = Get-Ver "git" "--version"
Out-Line ($(if ($git) {"OK"} else {"--"})) "Git" ($(if ($git) {$git} else {"absent (recommandé)"}))

$xbox = Get-AppxPackage -Name "Microsoft.GamingApp"
Out-Line ($(if ($xbox) {"OK"} else {"--"})) "Appli Xbox (PC)" ($(if ($xbox) {"installée v$($xbox.Version)"} else {"absente (utile pour récupérer les captures)"}))
$od = $env:OneDrive
Out-Line ($(if ($od) {"OK"} else {"--"})) "OneDrive" ($(if ($od) {$od} else {"non configuré"}))
$caps = Get-ChildItem -Path "$env:USERPROFILE\Videos","$od" -Recurse -Depth 3 -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "Captur|Xbox" } | Select-Object -First 5
foreach ($c in $caps) { Out-Line "i" "Dossier captures ?" $c.FullName }

$venv = Join-Path $root ".venv\Scripts\python.exe"
Out-Line ($(if (Test-Path $venv) {"OK"} else {"--"})) "Environnement .venv" ($(if (Test-Path $venv) {"présent"} else {"pas encore créé (install.ps1)"}))

$lines | Set-Content -Path $report -Encoding UTF8
Write-Host "`nRapport enregistré : $report" -ForegroundColor Cyan
Write-Host "Légende : OK = bon, !! = à corriger, -- = optionnel/absent, i = info"

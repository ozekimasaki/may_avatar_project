# Inochi Creator v0.8.6 (win32 zip = Win32 API, 64-bit).
# UAC for VC++ redist is the only human click.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Tools = Join-Path $Root "tools\inochi-creator"
$ZipUrl = "https://github.com/Inochi2D/inochi-creator/releases/download/v0.8.6/inochi-creator-win32.zip"
$Zip = Join-Path $env:TEMP "inochi-creator-win32-0.8.6.zip"
$Redist = "https://aka.ms/vs/17/release/vc_redist.x64.exe"

New-Item -ItemType Directory -Force -Path $Tools | Out-Null
Write-Host "Downloading Creator v0.8.6 zip..."
Invoke-WebRequest -Uri $ZipUrl -OutFile $Zip
Expand-Archive -Path $Zip -DestinationPath $Tools -Force

$exe = Get-ChildItem -Path $Tools -Filter inochi-creator.exe -Recurse | Select-Object -First 1
if (-not $exe) { throw "inochi-creator.exe not found after extract" }
Write-Host "Found $($exe.FullName)"

$pins = Join-Path $Root "08_repro\pins.yaml"
$line = "local_path: $($exe.FullName -replace '\\','/')"
Write-Host "Pin reminder: $line"

$vc = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64" -ErrorAction SilentlyContinue
if (-not $vc) {
  $redistPath = Join-Path $env:TEMP "vc_redist.x64.exe"
  Invoke-WebRequest -Uri $Redist -OutFile $redistPath
  Write-Host "Launching VC++ x64 redist. Approve the UAC dialog."
  Start-Process -FilePath $redistPath -Wait
}

Write-Host "Install complete. Human launches Creator GUI for Stage A."

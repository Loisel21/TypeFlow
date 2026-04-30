$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Virtuelle Umgebung nicht gefunden. Bitte zuerst im Projektordner 'python -m venv .venv' ausfuehren."
}

Set-Location $projectRoot
& $python "main.py"

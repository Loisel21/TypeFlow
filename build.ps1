$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Virtual environment not found. Please run 'python -m venv .venv' in the project folder first."
}

Set-Location $projectRoot

& $python ".\scripts\generate_assets.py"
& $python -m PyInstaller --noconfirm --clean ".\TypeFlow.spec"

Write-Host ""
Write-Host "Build completed."
Write-Host "Executable: $projectRoot\dist\TypeFlow.exe"

$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$venvPython = ".\venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    & $venvPython --version *> $null
    if ($LASTEXITCODE -eq 0) {
        & $venvPython run.py
        exit $LASTEXITCODE
    }

    Write-Host "El venv local no es usable. Ejecuta .\setup.ps1 para recrearlo."
}

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    py -3 run.py
    exit $LASTEXITCODE
}

python run.py

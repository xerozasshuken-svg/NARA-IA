$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$venvPython = ".\venv\Scripts\python.exe"

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    $pythonCommand = @("py", "-3")
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Error "No se encontro Python. Instala Python 3.11+ y vuelve a ejecutar setup.ps1."
    }
    $pythonCommand = @("python")
}

$venvUsable = $false
if (Test-Path -LiteralPath $venvPython) {
    & $venvPython --version *> $null
    $venvUsable = ($LASTEXITCODE -eq 0)
}

if ((Test-Path -LiteralPath "venv") -and -not $venvUsable) {
    Write-Host "El entorno virtual copiado no es usable en este equipo. Recreando venv..."
    Remove-Item -Recurse -Force -LiteralPath "venv"
}

if (-not (Test-Path -LiteralPath "venv")) {
    $pythonExe = $pythonCommand[0]
    $pythonArgs = @()
    if ($pythonCommand.Length -eq 2) {
        $pythonArgs += $pythonCommand[1]
    }

    & $pythonExe @pythonArgs -m venv venv
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "Entorno listo. Ejecuta: .\start.ps1"

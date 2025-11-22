# PowerShell script to activate venv and run Uvicorn in one step
$venvPath = "venv/Scripts/Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating venv..."
    & $venvPath
    Write-Host "Running Uvicorn..."
    uvicorn brain:app --host 0.0.0.0 --port 5000
} else {
    Write-Host "Venv not found. Please create it first."
}

# PowerShell script to run the Go backend in one step
$backendPath = "backend/main.go"
if (Test-Path $backendPath) {
    Write-Host "Starting PatentPulse Go Backend..."
    cd backend
    go run main.go
} else {
    Write-Host "main.go not found in backend/. Please check your setup."
}

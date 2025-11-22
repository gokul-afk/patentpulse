# PowerShell script to run both Go backend and Python AI service in separate terminals

# Start Go Backend in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; go run main.go"

# Start Python AI Service in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ai-service; .\venv\Scripts\Activate.ps1; uvicorn brain:app --host 0.0.0.0 --port 5000"

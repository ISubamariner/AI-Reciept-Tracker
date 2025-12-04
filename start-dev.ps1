# Development Server Startup Script
# Starts both backend and frontend servers in separate terminal windows

Write-Host "Starting development servers..." -ForegroundColor Green
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start Backend API
Write-Host "Launching Backend API..." -ForegroundColor Cyan
$backendPath = Join-Path $scriptDir "backend-api"
$venvPath = Join-Path (Split-Path $scriptDir -Parent) ".venv\Scripts\Activate.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendPath'; Write-Host 'Backend API starting...' -ForegroundColor Green; & '$venvPath'; python run.py"

# Wait a moment to ensure backend starts first
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Launching Frontend..." -ForegroundColor Cyan
$frontendPath = Join-Path $scriptDir "frontend\ai-receipt-ui"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; Write-Host 'Frontend starting...' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "Development servers are starting!" -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Two terminal windows have been opened." -ForegroundColor Gray
Write-Host "Close the terminal windows to stop the servers." -ForegroundColor Gray
Write-Host "Press Ctrl+C in each window to stop gracefully." -ForegroundColor Gray

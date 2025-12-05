# Verbose Development Server Startup Script
# More verbose version with better error checking and logging

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Development Environment Startup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Script Directory: $scriptDir" -ForegroundColor Gray

# === PRE-FLIGHT CHECKS ===
Write-Host ""
Write-Host "Running pre-flight checks..." -ForegroundColor Yellow

# Check virtual environment
$venvPath = Join-Path (Split-Path $scriptDir -Parent) ".venv\Scripts\Activate.ps1"
Write-Host "Checking virtual environment at: $venvPath" -ForegroundColor Gray
if (-not (Test-Path $venvPath)) {
    Write-Host "✗ FAIL: Virtual environment not found" -ForegroundColor Red
    Write-Host "  Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Virtual environment found" -ForegroundColor Green

# Check backend directory and run.py
$backendPath = Join-Path $scriptDir "backend-api"
$runPyPath = Join-Path $backendPath "run.py"
Write-Host "Checking backend at: $backendPath" -ForegroundColor Gray
if (-not (Test-Path $backendPath)) {
    Write-Host "✗ FAIL: Backend directory not found" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $runPyPath)) {
    Write-Host "✗ FAIL: run.py not found in backend directory" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Backend files found" -ForegroundColor Green

# Check Python dependencies
$requirementsPath = Join-Path $backendPath "requirements.txt"
Write-Host "Checking Python dependencies..." -ForegroundColor Gray
if (Test-Path $requirementsPath) {
    $checkImports = "try:`n    from app import create_app`n    print('OK')`nexcept ImportError as e:`n    print(f'MISSING: {e}')"
    $importCheck = & "$((Split-Path $scriptDir -Parent))\.venv\Scripts\python.exe" -c $checkImports 2>&1
    if ($importCheck -notmatch "OK") {
        Write-Host "✗ MISSING: Python dependencies not installed" -ForegroundColor Red
        Write-Host "Installing from requirements.txt..." -ForegroundColor Yellow
        & "$((Split-Path $scriptDir -Parent))\.venv\Scripts\python.exe" -m pip install -q -r $requirementsPath
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ FAIL: Could not install dependencies" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✓ Python dependencies are installed" -ForegroundColor Green
    }
} else {
    Write-Host "⚠ WARNING: requirements.txt not found" -ForegroundColor Yellow
}

# Check frontend directory
$frontendPath = Join-Path $scriptDir "frontend\ai-receipt-ui"
$packageJsonPath = Join-Path $frontendPath "package.json"
Write-Host "Checking frontend at: $frontendPath" -ForegroundColor Gray
if (-not (Test-Path $frontendPath)) {
    Write-Host "✗ FAIL: Frontend directory not found" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $packageJsonPath)) {
    Write-Host "✗ FAIL: package.json not found" -ForegroundColor Red
    Write-Host "  Please run 'npm install' in the frontend directory" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Frontend files found" -ForegroundColor Green

# Check if port 5000 is already in use
Write-Host "Checking if port 5000 is available..." -ForegroundColor Gray
$portInUse = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠ WARNING: Port 5000 is already in use" -ForegroundColor Yellow
    $response = Read-Host "Do you want to kill the process using port 5000? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        $procs = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | 
                 Select-Object -ExpandProperty OwningProcess -Unique | 
                 Where-Object { $_ -ne 0 }
        foreach ($p in $procs) {
            try {
                Stop-Process -Id $p -Force -ErrorAction Stop
                Write-Host "  ✓ Stopped process $p" -ForegroundColor Green
            } catch {
                Write-Host "  ✗ Could not stop process $p" -ForegroundColor Red
            }
        }
        Start-Sleep -Seconds 1
    } else {
        Write-Host "Backend may fail to start if port 5000 is in use" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ Port 5000 is available" -ForegroundColor Green
}

Write-Host ""
Write-Host "All pre-flight checks passed!" -ForegroundColor Green
Write-Host ""

# === START SERVERS ===
Write-Host "Starting servers..." -ForegroundColor Cyan
Write-Host ""

# Backend startup command with detailed logging
Write-Host "Launching Backend API in new window..." -ForegroundColor Yellow
$backendCommand = @"
Write-Host '========================================' -ForegroundColor Cyan
Write-Host 'BACKEND API SERVER' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

Set-Location '$backendPath'
Write-Host 'Working Directory: ' -NoNewline
Write-Host (Get-Location) -ForegroundColor Gray
Write-Host ''

Write-Host 'Activating virtual environment...' -ForegroundColor Yellow
if (Test-Path '$venvPath') {
    & '$venvPath'
    if (`$?) {
        Write-Host '✓ Virtual environment activated' -ForegroundColor Green
        Write-Host ''
        
        Write-Host 'Python Version:' -ForegroundColor Yellow
        python --version
        Write-Host ''
        
        Write-Host 'Starting Flask application...' -ForegroundColor Yellow
        Write-Host '----------------------------------------' -ForegroundColor Gray
        python run.py
        
        Write-Host '' -ForegroundColor Red
        Write-Host '========================================' -ForegroundColor Red
        Write-Host 'BACKEND SERVER STOPPED' -ForegroundColor Red
        Write-Host '========================================' -ForegroundColor Red
    } else {
        Write-Host '✗ FAILED to activate virtual environment' -ForegroundColor Red
    }
} else {
    Write-Host '✗ Virtual environment not found!' -ForegroundColor Red
}

Write-Host ''
Write-Host 'Press any key to close this window...' -ForegroundColor Yellow
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

# Wait for backend to initialize
Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 4

# Frontend startup command with detailed logging
Write-Host "Launching Frontend in new window..." -ForegroundColor Yellow
$frontendCommand = @"
Write-Host '========================================' -ForegroundColor Cyan
Write-Host 'FRONTEND DEVELOPMENT SERVER' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

Set-Location '$frontendPath'
Write-Host 'Working Directory: ' -NoNewline
Write-Host (Get-Location) -ForegroundColor Gray
Write-Host ''

Write-Host 'Node Version:' -ForegroundColor Yellow
node --version
Write-Host 'NPM Version:' -ForegroundColor Yellow
npm --version
Write-Host ''

Write-Host 'Starting Vite development server...' -ForegroundColor Yellow
Write-Host '----------------------------------------' -ForegroundColor Gray
npm run dev

Write-Host '' -ForegroundColor Red
Write-Host '========================================' -ForegroundColor Red
Write-Host 'FRONTEND SERVER STOPPED' -ForegroundColor Red
Write-Host '========================================' -ForegroundColor Red

Write-Host ''
Write-Host 'Press any key to close this window...' -ForegroundColor Yellow
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "SERVERS LAUNCHED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:  http://localhost:5000" -ForegroundColor Yellow
Write-Host "Frontend:     http://localhost:5173" -ForegroundColor Yellow
Write-Host "API Docs:     http://localhost:5000/api/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Two terminal windows have been opened." -ForegroundColor Gray
Write-Host "Check each window for detailed startup logs." -ForegroundColor Gray
Write-Host ""
Write-Host "To stop the servers:" -ForegroundColor Cyan
Write-Host "  1. Press Ctrl+C in each terminal window" -ForegroundColor Gray
Write-Host "  2. Or simply close the terminal windows" -ForegroundColor Gray
Write-Host ""

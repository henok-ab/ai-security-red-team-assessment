Write-Host ""
Write-Host "==============================================="
Write-Host "   AI SECURITY RED TEAM - ENVIRONMENT SETUP"
Write-Host "==============================================="
Write-Host ""

# Move to project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# -----------------------------------------------
# 1. Check Python
# -----------------------------------------------

Write-Host "===== Checking Python =====" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python was not found." -ForegroundColor Red
    Write-Host "Please install Python 3.11 or later."
    exit 1
}

python --version


# -----------------------------------------------
# 2. Create virtual environment
# -----------------------------------------------

Write-Host ""
Write-Host "===== Creating virtual environment =====" -ForegroundColor Cyan

if (Test-Path "venv") {
    Write-Host "venv already exists. Skipping creation."
}
else {
    python -m venv venv

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }

    Write-Host "Virtual environment created."
}


# -----------------------------------------------
# 3. Activate virtual environment
# -----------------------------------------------

Write-Host ""
Write-Host "===== Activating virtual environment =====" -ForegroundColor Cyan

& ".\venv\Scripts\Activate.ps1"


# -----------------------------------------------
# 4. Upgrade pip
# -----------------------------------------------

Write-Host ""
Write-Host "===== Updating pip =====" -ForegroundColor Cyan

python -m pip install --upgrade pip


# -----------------------------------------------
# 5. Install dependencies
# -----------------------------------------------

Write-Host ""
Write-Host "===== Installing dependencies =====" -ForegroundColor Cyan

if (Test-Path "requirements.txt") {

    python -m pip install -r requirements.txt

}
else {

    Write-Host "requirements.txt not found." -ForegroundColor Yellow
    Write-Host "Please create requirements.txt first."
}


# -----------------------------------------------
# 6. Finish
# -----------------------------------------------

Write-Host ""
Write-Host "==============================================="
Write-Host "       ENVIRONMENT SETUP COMPLETE"
Write-Host "==============================================="
Write-Host ""

Write-Host "Virtual environment:"
Write-Host "    .\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Next steps:"
Write-Host "    python model/inspect_model.py"
Write-Host "    python model/baseline.py"
Write-Host ""
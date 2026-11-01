# Setup and Test Script for Intelligent Medical System
# PowerShell script to set up the development environment and run tests

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Intelligent Medical System - Setup & Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check Python version
$versionMatch = python --version 2>&1 | Select-String '(\d+)\.(\d+)\.(\d+)'
$major = [int]$versionMatch.Matches.Groups[1].Value
$minor = [int]$versionMatch.Matches.Groups[2].Value

if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
    Write-Host "✗ Python 3.11+ is required (found $major.$minor)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠ Please edit .env file with your configuration" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}

Write-Host ""

# Run migrations
Write-Host "Creating migrations..." -ForegroundColor Yellow
python manage.py makemigrations accounts organizations
Write-Host "✓ Migrations created" -ForegroundColor Green

Write-Host ""

Write-Host "Applying migrations..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "✓ Migrations applied" -ForegroundColor Green

Write-Host ""

# Initialize system data
Write-Host "Initializing system data..." -ForegroundColor Yellow
python manage.py init_system
Write-Host "✓ System initialized" -ForegroundColor Green

Write-Host ""

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
Write-Host ""
python manage.py test apps.accounts apps.organizations --verbosity=2

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "2. Start server: python manage.py runserver" -ForegroundColor White
Write-Host "3. Access admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host "4. Access API docs: http://localhost:8000/api/docs/" -ForegroundColor White
Write-Host ""

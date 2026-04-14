# Crisis Response Center - Production Launcher
# Quick launcher with system validation

Write-Host "`n" -NoNewline
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host "  CRISIS RESPONSE CENTER" -ForegroundColor White
Write-Host "=" -ForegroundColor Cyan -NoNewline; Write-Host ("=" * 68) -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    $venvPath = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
    if (Test-Path $venvPath) {
        & $venvPath
        Write-Host "Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "Virtual environment not found!" -ForegroundColor Red
        Write-Host "  Run: python -m venv .venv" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "Virtual environment active" -ForegroundColor Green
}
Write-Host ""

# Start MCP Server
Write-Host "Starting MCP Server..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "start_mcp_server.ps1")

# Validate environment
Write-Host "Validating environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found!" -ForegroundColor Red
    Write-Host "  Create .env with: GOOGLE_API_KEY=your_api_key" -ForegroundColor Yellow
    exit 1
}

# Run system check
Write-Host "Running system validation..." -ForegroundColor Yellow
python tests\test_system_ready.py
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 68) -ForegroundColor Green
    Write-Host "  ALL SYSTEMS READY - Starting Application" -ForegroundColor White
    Write-Host "=" -ForegroundColor Green -NoNewline; Write-Host ("=" * 68) -ForegroundColor Green
    Write-Host ""
    Write-Host "Type your queries to interact with the crisis commander." -ForegroundColor Cyan
    Write-Host "Type 'exit' to quit." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "TIP: If 'exit' doesn't work, press Ctrl+C twice to stop." -ForegroundColor Yellow
    Write-Host ""
    
    # Start application
    python -m google.adk.cli run .
} else {
    Write-Host ""
    Write-Host "=" -ForegroundColor Red -NoNewline; Write-Host ("=" * 68) -ForegroundColor Red
    Write-Host "  SYSTEM CHECK FAILED" -ForegroundColor White
    Write-Host "=" -ForegroundColor Red -NoNewline; Write-Host ("=" * 68) -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the errors above before starting." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Application stopped." -ForegroundColor Cyan

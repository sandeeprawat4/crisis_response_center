# Start ERP MCP Server
# This script starts the MCP server on HTTP transport
# Configuration can be set via environment variables in .env file

Write-Host "Starting ERP MCP Server..." -ForegroundColor Cyan

# Load configuration from environment or use defaults
$ErpHost = if ($env:ERP_SERVER_HOST) { $env:ERP_SERVER_HOST } else { "127.0.0.1" }
$ErpPort = if ($env:ERP_SERVER_PORT) { $env:ERP_SERVER_PORT } else { "8000" }
$ErpUrl = if ($env:ERP_SERVER_URL) { $env:ERP_SERVER_URL } else { "http://${ErpHost}:${ErpPort}" }

Write-Host "[INFO] Server configuration: $ErpUrl" -ForegroundColor Gray

# Check if server is already running
$existingServer = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -and $_.CommandLine -match "erp_logistics\\server.py"
}

if ($existingServer) {
    Write-Host "[WARNING] MCP Server already running (PID: $($existingServer.Id))" -ForegroundColor Yellow
    Write-Host "Stopping existing server..." -ForegroundColor Yellow
    Stop-Process -Id $existingServer.Id -Force
    Start-Sleep -Seconds 2
}

# Start the server in a new window
Write-Host "[OK] Starting MCP Server on $ErpUrl" -ForegroundColor Green

$serverPath = Join-Path $PSScriptRoot "mcp_servers\erp_logistics\server.py"

Start-Process python -ArgumentList $serverPath -WindowStyle Normal

# Wait for server to start
Start-Sleep -Seconds 3

# Check if server is healthy
try {
    $response = Invoke-WebRequest -Uri "$ErpUrl/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] MCP Server is healthy and ready" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] MCP Server responded with status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Cannot connect to MCP Server. Please check if it started correctly." -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "MCP Server Endpoints:" -ForegroundColor Cyan
Write-Host "  Health: $ErpUrl/health" -ForegroundColor Gray
Write-Host "  Tools:  $ErpUrl/tools" -ForegroundColor Gray
Write-Host "  Call:   $ErpUrl/tools/call" -ForegroundColor Gray
Write-Host ""

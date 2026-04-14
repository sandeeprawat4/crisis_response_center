# Stop Crisis Response Center
# Emergency stop script for when normal exit doesn't work

Write-Host "`nStopping Crisis Response Center..." -ForegroundColor Yellow

# Find and stop Python processes running ADK or MCP servers
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python process(es)" -ForegroundColor White
    
    foreach ($proc in $pythonProcesses) {
        $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
        
        if ($cmdLine -like "*google.adk*" -or $cmdLine -like "*erp_logistics*") {
            Write-Host "Stopping: PID $($proc.Id) - $cmdLine" -ForegroundColor Cyan
            Stop-Process -Id $proc.Id -Force
            Write-Host "[OK] Process stopped" -ForegroundColor Green
        }
    }
} else {
    Write-Host "No Python processes found" -ForegroundColor Green
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host ""

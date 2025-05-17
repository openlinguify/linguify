# Minimal test build
Write-Host "Running minimal test build..." -ForegroundColor Green

# Clean .next
if (Test-Path ".next") {
    Write-Host "Removing .next directory..." -ForegroundColor Yellow
    cmd /c "rmdir /s /q .next" 2>$null
}

# Set minimal environment
$env:NODE_ENV = "production"
$env:NEXT_TELEMETRY_DISABLED = "1"

# Run build with output capture
Write-Host "Starting build..." -ForegroundColor Cyan

$buildProcess = Start-Process -FilePath "cmd" -ArgumentList "/c npm run build" `
    -NoNewWindow -PassThru -RedirectStandardOutput "build.log" -RedirectStandardError "error.log"

# Monitor progress
$counter = 0
while (-not $buildProcess.HasExited -and $counter -lt 300) {
    Start-Sleep -Seconds 1
    $counter++
    if ($counter % 10 -eq 0) {
        Write-Host "." -NoNewline
    }
    if ($counter % 60 -eq 0) {
        Write-Host " ($counter seconds)"
    }
}

if ($buildProcess.HasExited) {
    Write-Host "`nBuild completed with exit code: $($buildProcess.ExitCode)" -ForegroundColor Green
} else {
    Write-Host "`nBuild timeout after $counter seconds" -ForegroundColor Red
    $buildProcess.Kill()
}

# Show output
if (Test-Path "build.log") {
    Write-Host "`nBuild output:" -ForegroundColor Yellow
    Get-Content "build.log"
}

if (Test-Path "error.log" -and (Get-Item "error.log").Length -gt 0) {
    Write-Host "`nBuild errors:" -ForegroundColor Red
    Get-Content "error.log"
}

# Cleanup
Remove-Item "build.log", "error.log" -ErrorAction SilentlyContinue

Write-Host "`nTest complete." -ForegroundColor Green
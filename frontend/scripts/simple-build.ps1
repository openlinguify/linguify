# Simple build script for testing
Write-Host "Starting simple build test..." -ForegroundColor Green

# Clean .next
if (Test-Path ".next") {
    Remove-Item -Path ".next" -Recurse -Force -ErrorAction SilentlyContinue
}

# Run build with output
Write-Host "Running Next.js build..." -ForegroundColor Yellow

# Direct execution to see output
& npm run build

Write-Host "`nBuild script completed." -ForegroundColor Green
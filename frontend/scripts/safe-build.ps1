# Safe build script for Windows
Write-Host "Starting safe build process..." -ForegroundColor Green

# Try to stop any running Next.js processes
Write-Host "Stopping any running Next.js processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Clear Next.js cache if possible
try {
    if (Test-Path ".next/cache") {
        Remove-Item -Path ".next/cache" -Recurse -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "Could not clear cache" -ForegroundColor Yellow
}

# Run build with clean flag
Write-Host "Running build..." -ForegroundColor Yellow
try {
    npm run build
    Write-Host "Build completed!" -ForegroundColor Green
} catch {
    Write-Host "Build failed: $_" -ForegroundColor Red
}
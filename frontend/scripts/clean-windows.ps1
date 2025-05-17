# PowerShell script to clean node_modules on Windows
Write-Host "Cleaning project files..." -ForegroundColor Green

# Stop any running Node processes
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Try to remove node_modules
if (Test-Path "node_modules") {
    Write-Host "Removing node_modules..." -ForegroundColor Yellow
    try {
        # Use a more forceful approach
        cmd /c "rmdir /s /q node_modules"
    } catch {
        Write-Host "Failed to remove node_modules, trying alternative method..." -ForegroundColor Red
        # Alternative method using robocopy
        $empty = "$env:TEMP\empty_dir_$([System.Guid]::NewGuid())"
        New-Item -ItemType Directory -Path $empty -Force
        robocopy $empty node_modules /mir /r:1 /w:1
        Remove-Item $empty -Force
        Remove-Item node_modules -Force -Recurse -ErrorAction SilentlyContinue
    }
}

# Remove package-lock.json
if (Test-Path "package-lock.json") {
    Remove-Item "package-lock.json" -Force
}

# Remove .next directory
if (Test-Path ".next") {
    Write-Host "Removing .next directory..." -ForegroundColor Yellow
    try {
        cmd /c "rmdir /s /q .next"
    } catch {
        Write-Host "Failed to remove .next" -ForegroundColor Red
    }
}

Write-Host "Clean completed!" -ForegroundColor Green
Write-Host "Run 'npm install' to reinstall dependencies" -ForegroundColor Cyan
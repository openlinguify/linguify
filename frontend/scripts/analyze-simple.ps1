# Simple Windows bundle analyzer
Write-Host "Starting build analysis..." -ForegroundColor Green

# Clean .next directory
if (Test-Path ".next") {
    Write-Host "Cleaning .next directory..." -ForegroundColor Yellow
    Remove-Item -Path ".next" -Recurse -Force
}

# Create .next directory
New-Item -ItemType Directory -Path ".next" -Force

# Run build
Write-Host "Running build..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    
    # Find and display bundle sizes
    Write-Host "`nBundle Analysis:" -ForegroundColor Cyan
    Get-ChildItem -Path ".next" -Filter "*.js" -Recurse | 
        Select-Object Name, @{Name='SizeKB';Expression={[math]::Round($_.Length/1KB, 2)}} |
        Sort-Object SizeKB -Descending |
        Select-Object -First 10 |
        Format-Table -AutoSize
} else {
    Write-Host "Build failed!" -ForegroundColor Red
}
# Simple Windows bundle analyzer that handles common issues
Write-Host "Starting build and analysis..." -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Running npm install..." -ForegroundColor Yellow
    npm install
}

# Check if Next.js is available
$nextPath = "node_modules\.bin\next.cmd"
if (-not (Test-Path $nextPath)) {
    Write-Host "Next.js not found. Installing..." -ForegroundColor Yellow
    npm install next
}

# Clean .next directory
if (Test-Path ".next") {
    Write-Host "Cleaning .next directory..." -ForegroundColor Yellow
    try {
        Remove-Item -Path ".next" -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Host "Could not clean .next directory. This is usually fine." -ForegroundColor Yellow
    }
}

# Run build
Write-Host "Running build..." -ForegroundColor Yellow
$env:ANALYZE = "true"
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
    
    # Analyze bundle sizes
    Write-Host "`n=== Bundle Analysis ===" -ForegroundColor Cyan
    
    # Check static directory
    if (Test-Path ".next\static") {
        Write-Host "`nStatic files:" -ForegroundColor Yellow
        Get-ChildItem -Path ".next\static" -Recurse -Filter "*.js" | 
            Select-Object Name, @{Name='SizeKB';Expression={[math]::Round($_.Length/1KB, 2)}} |
            Sort-Object SizeKB -Descending |
            Format-Table -AutoSize
    }
    
    # Check server directory
    if (Test-Path ".next\server") {
        Write-Host "`nServer files:" -ForegroundColor Yellow
        Get-ChildItem -Path ".next\server" -Filter "*.js" | 
            Select-Object Name, @{Name='SizeKB';Expression={[math]::Round($_.Length/1KB, 2)}} |
            Sort-Object SizeKB -Descending |
            Select-Object -First 10 |
            Format-Table -AutoSize
    }
    
    # Total size
    Write-Host "`n=== Total Build Size ===" -ForegroundColor Cyan
    $totalSize = (Get-ChildItem -Path ".next" -Recurse | Measure-Object -Property Length -Sum).Sum
    Write-Host "Total: $([math]::Round($totalSize/1MB, 2)) MB" -ForegroundColor Green
    
} else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    Write-Host "Please check the errors above." -ForegroundColor Yellow
}
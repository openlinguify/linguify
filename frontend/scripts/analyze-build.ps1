# Windows-compatible build analyzer with error handling
Write-Host "Starting build analysis..." -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Please run 'npm install' first." -ForegroundColor Red
    exit 1
}

# Clean .next directory if it exists
if (Test-Path ".next") {
    Write-Host "Cleaning .next directory..." -ForegroundColor Yellow
    try {
        # Force stop any file locks
        Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Remove-Item -Path ".next" -Recurse -Force -ErrorAction Stop
        Write-Host ".next directory cleaned." -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not fully clean .next directory." -ForegroundColor Yellow
    }
}

# Set environment variable for Next.js
$env:ANALYZE = "true"
$env:NODE_ENV = "production"

Write-Host "`nRunning Next.js build..." -ForegroundColor Cyan

# Create a build process with timeout
try {
    $process = Start-Process -FilePath "npm" -ArgumentList "run", "build" -PassThru -NoNewWindow -RedirectStandardOutput "build-output.txt" -RedirectStandardError "build-error.txt"
    
    # Wait for process with timeout (5 minutes)
    $timeout = 300  # seconds
    $hasExited = $process.WaitForExit($timeout * 1000)
    
    if (-not $hasExited) {
        Write-Host "`nBuild timeout after $timeout seconds. Terminating..." -ForegroundColor Yellow
        $process.Kill()
        $exitCode = 1
    } else {
        $exitCode = $process.ExitCode
    }
    
    # Display output
    if (Test-Path "build-output.txt") {
        Write-Host "`nBuild Output:" -ForegroundColor Gray
        Get-Content "build-output.txt"
    }
    
    if (Test-Path "build-error.txt" -and (Get-Item "build-error.txt").Length -gt 0) {
        Write-Host "`nBuild Errors:" -ForegroundColor Red
        Get-Content "build-error.txt"
    }
    
    # Clean up log files
    Remove-Item "build-output.txt", "build-error.txt" -ErrorAction SilentlyContinue
    
    if ($exitCode -eq 0) {
        Write-Host "`nBuild completed successfully!" -ForegroundColor Green
        
        # Analyze bundle
        Write-Host "`n=== Bundle Analysis ===" -ForegroundColor Cyan
        
        # Check .next directory structure
        if (Test-Path ".next") {
            $totalSize = 0
            $fileCount = 0
            
            Write-Host "`nLargest JavaScript files:" -ForegroundColor Yellow
            Get-ChildItem -Path ".next" -Recurse -Filter "*.js" -ErrorAction SilentlyContinue | 
                ForEach-Object {
                    $totalSize += $_.Length
                    $fileCount++
                    $_
                } |
                Sort-Object Length -Descending |
                Select-Object -First 10 |
                Format-Table @{L='File';E={$_.Name}}, @{L='Size (KB)';E={[math]::Round($_.Length/1KB, 2)}} -AutoSize
            
            Write-Host "`nBundle Summary:" -ForegroundColor Cyan
            Write-Host "Total JS files: $fileCount" -ForegroundColor White
            Write-Host "Total size: $([math]::Round($totalSize/1MB, 2)) MB" -ForegroundColor White
            
            # Check specific directories
            @("static", "server", "pages") | ForEach-Object {
                $dirPath = Join-Path ".next" $_
                if (Test-Path $dirPath) {
                    $dirSize = (Get-ChildItem -Path $dirPath -Recurse -ErrorAction SilentlyContinue | 
                               Measure-Object -Property Length -Sum).Sum
                    Write-Host "$_ directory: $([math]::Round($dirSize/1MB, 2)) MB" -ForegroundColor White
                }
            }
        }
    } else {
        Write-Host "`nBuild failed with exit code: $exitCode" -ForegroundColor Red
    }
} catch {
    Write-Host "`nBuild process error: $_" -ForegroundColor Red
}

Write-Host "`nAnalysis complete." -ForegroundColor Green
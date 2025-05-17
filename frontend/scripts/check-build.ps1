# Build troubleshooting script
Write-Host "Build Troubleshooting Script" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# 1. Check Node version
Write-Host "`n1. Node.js version:" -ForegroundColor Yellow
node --version

# 2. Check npm version
Write-Host "`n2. npm version:" -ForegroundColor Yellow
npm --version

# 3. Check Next.js installation
Write-Host "`n3. Next.js installation:" -ForegroundColor Yellow
if (Test-Path "node_modules/next/package.json") {
    $nextVersion = (Get-Content "node_modules/next/package.json" | ConvertFrom-Json).version
    Write-Host "Next.js version: $nextVersion" -ForegroundColor Green
} else {
    Write-Host "Next.js not found!" -ForegroundColor Red
}

# 4. Check for .next directory issues
Write-Host "`n4. .next directory status:" -ForegroundColor Yellow
if (Test-Path ".next") {
    Write-Host ".next directory exists" -ForegroundColor Green
    $files = Get-ChildItem ".next" -Recurse | Measure-Object
    Write-Host "Files in .next: $($files.Count)" -ForegroundColor White
} else {
    Write-Host ".next directory does not exist" -ForegroundColor White
}

# 5. Try a basic build with verbose output
Write-Host "`n5. Attempting basic build with verbose output..." -ForegroundColor Yellow

# Set environment variables
$env:NODE_OPTIONS = "--max-old-space-size=4096"
$env:NEXT_TELEMETRY_DISABLED = "1"

# Create a simple next.config.js for testing
$testConfig = @"
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
"@

# Backup existing config
if (Test-Path "next.config.js") {
    Move-Item "next.config.js" "next.config.js.backup" -Force
}
if (Test-Path "next.config.ts") {
    Move-Item "next.config.ts" "next.config.ts.backup" -Force
}

# Write test config
Set-Content -Path "next.config.js" -Value $testConfig

Write-Host "Using simplified config for testing..." -ForegroundColor Yellow

# Try build
try {
    $result = & npm run build 2>&1
    Write-Host $result
} catch {
    Write-Host "Build error: $_" -ForegroundColor Red
}

# Restore original config
if (Test-Path "next.config.ts.backup") {
    Move-Item "next.config.ts.backup" "next.config.ts" -Force
}
if (Test-Path "next.config.js.backup") {
    Move-Item "next.config.js.backup" "next.config.js" -Force
}
Remove-Item "next.config.js" -ErrorAction SilentlyContinue

Write-Host "`nTroubleshooting complete." -ForegroundColor Green
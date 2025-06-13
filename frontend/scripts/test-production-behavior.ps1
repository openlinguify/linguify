# Script pour tester le comportement de production en local

Write-Host "🚀 Testing Production Behavior Locally" -ForegroundColor Blue
Write-Host ""

# Sauvegarder les fichiers .env actuels
if (Test-Path ".env.local") {
    Copy-Item ".env.local" ".env.local.backup" -Force
    Write-Host "✅ Backed up .env.local" -ForegroundColor Green
}

if (Test-Path ".env.production.local") {
    Copy-Item ".env.production.local" ".env.production.local.backup" -Force
    Write-Host "✅ Backed up .env.production.local" -ForegroundColor Green
}

# Copier .env.test-production vers .env.production.local
Copy-Item ".env.test-production" ".env.production.local" -Force
Write-Host "✅ Set up test production environment" -ForegroundColor Green

Write-Host ""
Write-Host "📦 Building with production settings..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Starting production server..." -ForegroundColor Yellow
    Write-Host "Access the app at: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "You should be redirected to /home when not authenticated" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    
    npm run start
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
}

# Restaurer les fichiers .env originaux
Write-Host ""
Write-Host "🔄 Restoring original environment files..." -ForegroundColor Yellow

if (Test-Path ".env.local.backup") {
    Copy-Item ".env.local.backup" ".env.local" -Force
    Remove-Item ".env.local.backup"
    Write-Host "✅ Restored .env.local" -ForegroundColor Green
}

if (Test-Path ".env.production.local.backup") {
    Copy-Item ".env.production.local.backup" ".env.production.local" -Force
    Remove-Item ".env.production.local.backup"
    Write-Host "✅ Restored .env.production.local" -ForegroundColor Green
}
@echo off
echo Building project...
npm run build

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b %ERRORLEVEL%
)

echo.
echo Build successful! Analyzing bundle...
echo.

echo Next.js Build Output:
echo ==========================================
dir .next /s | findstr /i ".js" | findstr /v node_modules
echo ==========================================

echo.
echo Total build size:
dir .next /s /a-d | find "File(s)"
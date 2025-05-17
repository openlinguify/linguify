# Windows Specific Commands

## Bundle Analysis on Windows

On Windows (PowerShell), you have several options to run the bundle analysis command:

### Option 1: Install cross-env (Recommended)
```powershell
npm install --save-dev cross-env
npm run analyze
```

### Option 2: PowerShell Direct
```powershell
$env:ANALYZE="true"; npm run build
```

### Option 3: Use the Windows Script
```powershell
npm run analyze:windows
```

### Option 4: Use the Batch File
```batch
scripts\analyze.bat
```

## Other Problematic Commands on Windows

### Clean Command
The `npm run clean` command uses `rm -rf`, which is not available on Windows by default.

Alternatives:
```powershell
# PowerShell
Remove-Item -Recurse -Force .next, node_modules

# Or use rimraf
npm install --save-dev rimraf
```

Then update your package.json:
```json
"clean": "rimraf .next node_modules"
```

### Dev:all Command
The `npm run dev:all` command uses Unix-style paths. For Windows, you can:

1. Install WSL (Windows Subsystem for Linux)
2. Use Git Bash
3. Modify the script for PowerShell

## General Recommendations for Windows

1. **Use Git Bash**: Most Unix commands will work
2. **Install cross-env**: For environment variables
3. **Use rimraf**: For deletion commands
4. **Create .bat or .ps1 scripts**: For complex commands

## Recommended Dependency Installation for Windows

```powershell
npm install --save-dev cross-env rimraf
```

This will solve most compatibility issues between Unix and Windows.
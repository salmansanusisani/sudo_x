param([switch]$BrowserTests)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed.' }
    }
    & .\.venv\Scripts\python.exe -m pip install -e '.[dev]'
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    Push-Location ui
    try {
        & npm.cmd ci --no-fund
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
        if ($BrowserTests) {
            & npx.cmd playwright install chromium
            if ($LASTEXITCODE -ne 0) { throw 'Test browser installation failed.' }
            & npm.cmd run test:e2e
            if ($LASTEXITCODE -ne 0) { throw 'Browser tests failed.' }
        }
    } finally { Pop-Location }
    Write-Host 'SUDO X is ready. Run .\launch.ps1 from a normal, non-administrator terminal.'
} finally { Pop-Location }

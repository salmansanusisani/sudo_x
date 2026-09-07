param(
    [ValidateRange(1, 65535)][int]$Port = 8765,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Missing Python environment. Run .\setup.ps1 first.'
}
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'ui\dist\index.html'))) {
    throw 'Missing UI build. Run .\setup.ps1 first.'
}
$launchArguments = @('-m', 'sudo_x', '--port', $Port)
if (-not $NoBrowser) { $launchArguments += '--app' }
& $pythonPath @launchArguments
exit $LASTEXITCODE

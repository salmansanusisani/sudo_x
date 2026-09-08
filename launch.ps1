param(
    [ValidateRange(1, 65535)][int]$Port = 8765,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath (Join-Path $PSScriptRoot '.env')) {
    $values = Get-Content -LiteralPath (Join-Path $PSScriptRoot '.env') | ConvertFrom-StringData
    foreach ($name in @('NEBIUS_API_KEY', 'TAVILY_API_KEY')) {
        if ($values.ContainsKey($name)) { Set-Item -Path "Env:$name" -Value $values[$name] }
    }
}
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

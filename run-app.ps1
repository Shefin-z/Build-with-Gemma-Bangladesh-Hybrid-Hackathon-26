Set-Location $PSScriptRoot

$apiListener = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $apiListener) {
    Start-Process -FilePath python -ArgumentList '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
}

$nodeRoot = Join-Path $PSScriptRoot '.codex-node\node-v22.23.1-win-x64'
$npmCommand = Join-Path $nodeRoot 'npm.cmd'
if (-not (Test-Path $npmCommand)) {
    $npmCommand = (Get-Command npm -ErrorAction Stop).Source
}

& $npmCommand run dev -- --host 127.0.0.1

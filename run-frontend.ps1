Set-Location $PSScriptRoot
$nodeRoot = Join-Path $PSScriptRoot '.codex-node\node-v22.23.1-win-x64'
$env:PATH = "$nodeRoot;$env:PATH"
& (Join-Path $nodeRoot 'npm.cmd') run dev -- --host 127.0.0.1

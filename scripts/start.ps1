$ErrorActionPreference = 'Stop'
$renalisRoot = Split-Path -Parent $PSScriptRoot
$renalisPython = Join-Path $renalisRoot '.venv\Scripts\python.exe'
$renalisVite = Join-Path $renalisRoot 'node_modules\vite\bin\vite.js'
if (-not (Test-Path -LiteralPath $renalisPython) -or -not (Test-Path -LiteralPath $renalisVite)) {
    throw 'Install Python and Node dependencies first; see README.md.'
}
$renalisLogFolder = Join-Path $renalisRoot 'data'
New-Item -ItemType Directory -Path $renalisLogFolder -Force | Out-Null
if (-not (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue)) {
    # A background Windows process has no reliable interactive console signal
    # channel for Uvicorn's reload worker. Use a stable API process here; the
    # README's interactive development command supports --reload separately.
    Start-Process -FilePath $renalisPython -ArgumentList '-m uvicorn backend.app:app --host 127.0.0.1 --port 8000' -WorkingDirectory $renalisRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $renalisLogFolder 'api.log') -RedirectStandardError (Join-Path $renalisLogFolder 'api-error.log')
}
if (-not (Get-NetTCPConnection -State Listen -LocalPort 5173 -ErrorAction SilentlyContinue)) {
    $renalisNode = (Get-Command node.exe -ErrorAction Stop).Source
    Start-Process -FilePath $renalisNode -ArgumentList ('"{0}" --host 127.0.0.1 --port 5173' -f $renalisVite) -WorkingDirectory $renalisRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $renalisLogFolder 'web.log') -RedirectStandardError (Join-Path $renalisLogFolder 'web-error.log')
}
Write-Output 'RENALIS local preview: http://127.0.0.1:5173/'
Write-Output 'If a port belongs to another application, use the manual commands in README.md.'

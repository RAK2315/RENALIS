$ErrorActionPreference = 'Stop'
$renalisDeliveryRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $renalisDeliveryRoot
$renalisDeliveryStarted = Get-Date
do {
    $renalisReady = $false
    if (Test-Path -LiteralPath 'artifacts/submission-v05/verification.json') {
        try { $renalisReady = (Get-Content -Raw 'artifacts/submission-v05/verification.json' | ConvertFrom-Json).passed } catch {}
    }
    if ($renalisReady) { break }
    if (((Get-Date) - $renalisDeliveryStarted).TotalMinutes -gt 20) { throw 'The master is not verified yet. Completed checkpoints are retained.' }
    Start-Sleep -Seconds 5
} while ($true)
& ./.venv/Scripts/python.exe scripts/prepare-submission.py
if ($LASTEXITCODE -ne 0) { throw 'Source packaging failed.' }
$renalisArtifactPython = 'C:\Users\rehtr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $renalisArtifactPython video/submission_v05/delivery.py --kit
if ($LASTEXITCODE -ne 0) { throw 'Submission kit packaging failed.' }
$env:NODE_PATH = 'C:\Users\rehtr\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
& node video/submission_v05/check-player.cjs
if ($LASTEXITCODE -ne 0) { throw 'Browser delivery checks failed.' }

$ErrorActionPreference = 'Stop'
$renalisFilmRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $renalisFilmRoot
$renalisVideoPython = Join-Path $renalisFilmRoot '.venv-video/Scripts/python.exe'
$renalisBundledModules = 'C:\Users\rehtr\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
if (Test-Path -LiteralPath $renalisBundledModules) { $env:NODE_PATH = $renalisBundledModules }
$renalisVideoNode = (Get-Command node.exe).Source
$renalisStarted = Get-Date
do {
    $renalisVoiceCount = (Get-ChildItem -LiteralPath 'artifacts/submission-v05/voice' -Filter '*.json').Count
    $renalisFootageCount = 0
    if (Test-Path -LiteralPath 'artifacts/submission-v05/footage.json') {
        $renalisFootage = Get-Content -Raw 'artifacts/submission-v05/footage.json' | ConvertFrom-Json
        $renalisFootageCount = @($renalisFootage.PSObject.Properties).Count
    }
    Write-Output "Checkpoint: $renalisVoiceCount/120 voice phrases, $renalisFootageCount/22 filmed views."
    if ($renalisVoiceCount -eq 120 -and $renalisFootageCount -eq 22) { break }
    if (((Get-Date) - $renalisStarted).TotalMinutes -gt 20) { throw 'Production inputs still incomplete; all existing checkpoints are retained.' }
    Start-Sleep -Seconds 10
} while ($true)
& $renalisVideoPython -m video.submission_v05.audio --assemble
if ($LASTEXITCODE -ne 0) { throw 'Audio assembly failed; voice caches retained.' }
& $renalisVideoNode video/submission_v05/render.cjs --preview
if ($LASTEXITCODE -ne 0) { throw 'Composition preview failed.' }
& $renalisVideoNode video/submission_v05/render.cjs
if ($LASTEXITCODE -ne 0) { throw 'Render failed; completed scenes and chapters retained.' }
& $renalisVideoPython -m video.submission_v05.verify
if ($LASTEXITCODE -ne 0) { throw 'Media verification failed; review before delivery.' }

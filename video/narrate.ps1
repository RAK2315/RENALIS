param([string]$OutputDirectory)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Speech
$renalisStory=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'storyboard.json') -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$renalisSpeech=New-Object System.Speech.Synthesis.SpeechSynthesizer
$renalisSpeech.SelectVoice('Microsoft Zira Desktop')
$renalisSpeech.Rate=1
$renalisSpeech.Volume=100
foreach($renalisScene in $renalisStory){
    $renalisWave=Join-Path $OutputDirectory ($renalisScene.id+'.wav')
    $renalisSpeech.SetOutputToWaveFile($renalisWave)
    $renalisSpeech.Speak($renalisScene.voice)
    $renalisSpeech.SetOutputToNull()
    Write-Output ('Narrated '+$renalisScene.id)
}
$renalisSpeech.Dispose()

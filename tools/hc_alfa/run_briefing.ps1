param(
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Join-Path $PSScriptRoot '..' '..')

Write-Host "[run_briefing] Running HC Alfa briefing..."
if ($DryRun) {
  python -m tools.hc_alfa.briefing --out planning/briefings
} else {
  python -m tools.hc_alfa.briefing --out planning/briefings
}

Write-Host "[run_briefing] Done."


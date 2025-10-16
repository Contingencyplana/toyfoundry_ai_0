param(
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Join-Path $PSScriptRoot '..' '..')

if ($DryRun) {
  Write-Host "[update_ledger] Dry-run: preview index"
  python tools/ledger_indexer.py --dry-run
} else {
  Write-Host "[update_ledger] Rebuilding exchange/ledger/index.json"
  python tools/ledger_indexer.py --write
}

Write-Host "[update_ledger] Done."


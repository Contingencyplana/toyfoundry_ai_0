param(
  [string]$ExitOnError = '1'
)
$ErrorActionPreference = 'Stop'
$errors = @()

function Test-JsonFile($path, $requiredKeys) {
  try {
    $obj = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json -AsHashtable
  } catch {
    $script:errors += ("Invalid JSON: {0}: {1}" -f $path, $_)
    return
  }
  foreach ($k in $requiredKeys) {
    if (-not $obj.ContainsKey($k)) {
      $script:errors += "Missing key '$k' in $path"
    }
  }
}

# Validate change-as-order templates
Test-JsonFile 'exchange/orders/templates/change-order.template.json' @('schema','order_id','issued_by','target','directives')
Test-JsonFile 'exchange/acknowledgements/templates/change-ack.template.json' @('schema','ack_id','referenced_id','status')
Test-JsonFile 'exchange/reports/templates/change-report.template.json' @('schema','report_id','referenced_order','pipeline','safety')

# Validate lanes config
try {
  $lanes = Get-Content -Raw -LiteralPath 'tools/telemetry/canary_sandbox.sample.json' | ConvertFrom-Json -AsHashtable
  if (-not $lanes.ContainsKey('lanes')) { $errors += 'Lanes config missing lanes[]' }
  if (-not $lanes.ContainsKey('telemetry')) { $errors += 'Lanes config missing telemetry{}' }
} catch {
  $errors += "Invalid JSON: tools/telemetry/canary_sandbox.sample.json: $_"
}

if ($errors.Count) {
  Write-Host "Template validation FAILED:" -ForegroundColor Red
  $errors | ForEach-Object { Write-Host " - $_" }
  if ($ExitOnError -ne '0') { exit 1 }
} else {
  Write-Host 'Template validation OK' -ForegroundColor Green
}

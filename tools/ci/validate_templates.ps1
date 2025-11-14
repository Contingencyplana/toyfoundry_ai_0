param(
  [string]$ExitOnError = '1'
)
$ErrorActionPreference = 'Stop'
$errors = @()

$toolsRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path $toolsRoot -Parent
$templateRoots = @(
  (Join-Path $repoRoot 'exchange')
  (Join-Path $repoRoot 'high_command_exchange')
  (Join-Path (Join-Path $repoRoot 'tools') 'ci/template_snapshots')
)

function ConvertToHashtable($obj) {
  if ($null -eq $obj) { return @{} }
  if ($obj -is [System.Collections.IDictionary]) { return $obj }
  $hash = @{}
  foreach ($prop in $obj.PSObject.Properties) {
    $hash[$prop.Name] = $prop.Value
  }
  return $hash
}

function Resolve-TemplatePath($relativePath) {
  foreach ($root in $script:templateRoots) {
    $candidate = Join-Path $root $relativePath
    if (Test-Path -LiteralPath $candidate) {
      return $candidate
    }
  }
  $script:errors += "Missing template file: $relativePath"
  return $null
}

function Test-JsonFile($path, $requiredKeys) {
  try {
    $obj = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    $obj = ConvertToHashtable $obj
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

function Test-Template($relativePath, $requiredKeys) {
  $path = Resolve-TemplatePath $relativePath
  if ($null -ne $path) {
    Test-JsonFile $path $requiredKeys
  }
}

# Validate change-as-order templates (fallback to snapshots if needed)
Test-Template 'orders/templates/change-order.template.json' @('schema','order_id','issued_by','target','directives')
Test-Template 'acknowledgements/templates/change-ack.template.json' @('schema','ack_id','referenced_id','status')
Test-Template 'reports/templates/change-report.template.json' @('schema','report_id','order_id','reported_by','status')

# Validate lanes config
try {
  $lanesPath = Join-Path (Join-Path $repoRoot 'tools') 'telemetry/canary_sandbox.sample.json'
  $lanes = Get-Content -Raw -LiteralPath $lanesPath | ConvertFrom-Json
  $lanes = ConvertToHashtable $lanes
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

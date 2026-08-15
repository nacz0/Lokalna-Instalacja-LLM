[CmdletBinding()]
param(
    [string]$EnvFile = ".env.k8s",
    [string]$Namespace = "local-llm"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ResolvedEnvFile = if ([System.IO.Path]::IsPathRooted($EnvFile)) {
    $EnvFile
} else {
    Join-Path $RepoRoot $EnvFile
}

if (-not (Test-Path -LiteralPath $ResolvedEnvFile)) {
    throw "Brak pliku $ResolvedEnvFile. Skopiuj .env.k8s.example jako .env.k8s i uzupelnij wartosci."
}

$RequiredKeys = @("PIPELINES_API_KEY", "WEBUI_SECRET_KEY")
$ConfiguredValues = @{}
Get-Content -LiteralPath $ResolvedEnvFile |
    Where-Object { $_ -match '^\s*[^#][^=]*=' } |
    ForEach-Object {
        $Parts = $_ -split '=', 2
        $ConfiguredValues[$Parts[0].Trim()] = $Parts[1].Trim()
    }

foreach ($Key in $RequiredKeys) {
    $Value = $ConfiguredValues[$Key]
    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "W pliku sekretow brakuje wartosci $Key."
    }
    if ($Value -in @("change-me", "replace-with-a-long-random-value")) {
        throw "Zastap przykladowa wartosc $Key wlasnym sekretem."
    }
}

kubectl apply -f (Join-Path $RepoRoot "k8s/base/namespace.yaml") | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Nie udalo sie utworzyc namespace $Namespace." }

kubectl create secret generic llm-secrets `
    --namespace $Namespace `
    --from-env-file=$ResolvedEnvFile `
    --dry-run=client `
    -o yaml |
    kubectl apply -f - | Out-Host

if ($LASTEXITCODE -ne 0) { throw "Nie udalo sie utworzyc Kubernetes Secret." }
Write-Host "Secret llm-secrets zostal zastosowany w namespace $Namespace." -ForegroundColor Green

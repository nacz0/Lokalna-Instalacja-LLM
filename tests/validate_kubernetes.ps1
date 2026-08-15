$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Overlays = @("local", "gpu")

foreach ($Overlay in $Overlays) {
    $ManifestLines = kubectl kustomize (Join-Path $RepoRoot "k8s/overlays/$Overlay")
    if ($LASTEXITCODE -ne 0) {
        throw "Nie udało się wyrenderować overlay $Overlay."
    }
    $Manifest = $ManifestLines -join "`n"

    foreach ($RequiredResource in @("name: ollama", "name: pipelines", "name: open-webui", "name: ollama-model-loader")) {
        if ($Manifest -notmatch [regex]::Escape($RequiredResource)) {
            throw "Overlay $Overlay nie zawiera zasobu $RequiredResource."
        }
    }

    Write-Host "Overlay ${Overlay}: OK" -ForegroundColor Green
}

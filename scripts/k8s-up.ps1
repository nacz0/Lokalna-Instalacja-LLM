[CmdletBinding()]
param(
    [ValidateSet("local", "gpu")]
    [string]$Overlay = "local",
    [ValidateSet("docker-desktop", "kind", "minikube")]
    [string]$ClusterType = "docker-desktop",
    [string]$KindClusterName = "kind",
    [switch]$SkipBuild,
    [switch]$SkipModelWait
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Namespace = "local-llm"
$OverlayPath = Join-Path $RepoRoot "k8s/overlays/$Overlay"

kubectl cluster-info | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Brak polaczenia z klastrem Kubernetes. Sprawdz biezacy kontekst kubectl."
}

kubectl get secret llm-secrets -n $Namespace 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    & (Join-Path $PSScriptRoot "k8s-create-secret.ps1")
}

if (-not $SkipBuild) {
    & (Join-Path $PSScriptRoot "k8s-build.ps1") -ClusterType $ClusterType -KindClusterName $KindClusterName
}

# Job jest bezpiecznie odtwarzany, aby uwzglednic zmiany listy modeli.
kubectl delete job ollama-model-loader -n $Namespace --ignore-not-found | Out-Host
kubectl apply -k $OverlayPath | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Wdrozenie manifestow nie powiodlo sie." }

# Wymusza wczytanie aktualnych wartosci Secret i ConfigMap przez istniejace Pody.
kubectl rollout restart deployment/pipelines deployment/open-webui -n $Namespace | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Nie udalo sie odswiezyc konfiguracji Deploymentow." }

kubectl rollout status deployment/ollama -n $Namespace --timeout=10m | Out-Host
kubectl rollout status deployment/pipelines -n $Namespace --timeout=10m | Out-Host
kubectl rollout status deployment/open-webui -n $Namespace --timeout=15m | Out-Host

if (-not $SkipModelWait) {
    Write-Host "Oczekiwanie na pobranie modeli (pierwsze uruchomienie moze potrwac dlugo)..."
    kubectl wait --for=jsonpath='{.status.phase}'=Succeeded `
        pod `
        -l job-name=ollama-model-loader `
        -n $Namespace `
        --timeout=60m | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Pod pobierajacy modele nie zakonczyl sie w wyznaczonym czasie. Sprawdz: kubectl logs job/ollama-model-loader -n $Namespace"
    }
}

Write-Host "Srodowisko jest gotowe. Uruchom scripts/k8s-port-forward.ps1 i otworz http://localhost:3000." -ForegroundColor Green

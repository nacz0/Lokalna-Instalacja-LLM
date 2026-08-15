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
    throw "Brak połączenia z klastrem Kubernetes. Sprawdź bieżący kontekst kubectl."
}

kubectl get secret llm-secrets -n $Namespace 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    & (Join-Path $PSScriptRoot "k8s-create-secret.ps1")
}

if (-not $SkipBuild) {
    & (Join-Path $PSScriptRoot "k8s-build.ps1") -ClusterType $ClusterType -KindClusterName $KindClusterName
}

# Job jest bezpiecznie odtwarzany, aby uwzględnić zmiany listy modeli.
kubectl delete job ollama-model-loader -n $Namespace --ignore-not-found | Out-Host
kubectl apply -k $OverlayPath | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Wdrożenie manifestów nie powiodło się." }

# Wymusza wczytanie aktualnych wartości Secret i ConfigMap przez istniejące Pody.
kubectl rollout restart deployment/pipelines deployment/open-webui -n $Namespace | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Nie udało się odświeżyć konfiguracji Deploymentów." }

kubectl rollout status deployment/ollama -n $Namespace --timeout=10m | Out-Host
kubectl rollout status deployment/pipelines -n $Namespace --timeout=10m | Out-Host
kubectl rollout status deployment/open-webui -n $Namespace --timeout=15m | Out-Host

if (-not $SkipModelWait) {
    Write-Host "Oczekiwanie na pobranie modeli (pierwsze uruchomienie może potrwać długo)..."
    kubectl wait --for=condition=complete job/ollama-model-loader -n $Namespace --timeout=60m | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Job pobierający modele nie zakończył się w wyznaczonym czasie. Sprawdź: kubectl logs job/ollama-model-loader -n $Namespace"
    }
}

Write-Host "Środowisko jest gotowe. Uruchom scripts/k8s-port-forward.ps1 i otwórz http://localhost:3000." -ForegroundColor Green

[CmdletBinding()]
param(
    [ValidateSet("docker-desktop", "kind", "minikube")]
    [string]$ClusterType = "docker-desktop",
    [string]$KindClusterName = "kind"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $RepoRoot
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker nie jest uruchomiony."
    }

    docker build -t local/open-webui-custom:k8s ./customization
    if ($LASTEXITCODE -ne 0) { throw "Budowanie obrazu Open WebUI nie powiodlo sie." }

    docker build -t local/llm-pipelines:k8s -f pipelines/Dockerfile .
    if ($LASTEXITCODE -ne 0) { throw "Budowanie obrazu pipelines nie powiodlo sie." }

    if ($ClusterType -eq "kind") {
        kind load docker-image local/open-webui-custom:k8s local/llm-pipelines:k8s --name $KindClusterName
        if ($LASTEXITCODE -ne 0) { throw "Ladowanie obrazow do kind nie powiodlo sie." }
    }
    elseif ($ClusterType -eq "minikube") {
        minikube image load local/open-webui-custom:k8s local/llm-pipelines:k8s
        if ($LASTEXITCODE -ne 0) { throw "Ladowanie obrazow do minikube nie powiodlo sie." }
    }

    Write-Host "Obrazy Kubernetes zostaly przygotowane." -ForegroundColor Green
}
finally {
    Pop-Location
}

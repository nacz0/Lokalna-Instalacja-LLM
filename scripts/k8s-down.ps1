[CmdletBinding()]
param([string]$Namespace = "local-llm")

$ErrorActionPreference = "Stop"

kubectl scale deployment --all --replicas=0 -n $Namespace | Out-Host
if ($LASTEXITCODE -ne 0) { throw "Nie udało się zatrzymać Deploymentów." }

Write-Host "Deploymenty zatrzymano. PVC i zapisane dane pozostały nienaruszone." -ForegroundColor Green
Write-Host "Ponowne uruchomienie: scripts/k8s-up.ps1 -SkipBuild"

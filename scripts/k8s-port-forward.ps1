[CmdletBinding()]
param(
    [int]$LocalPort = 3000,
    [string]$Namespace = "local-llm"
)

$ErrorActionPreference = "Stop"

Write-Host "Open WebUI: http://localhost:$LocalPort"
Write-Host "Naciśnij Ctrl+C, aby zakończyć przekierowanie portu."
kubectl port-forward service/open-webui "${LocalPort}:8080" -n $Namespace

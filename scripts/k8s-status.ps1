[CmdletBinding()]
param([string]$Namespace = "local-llm")

$ErrorActionPreference = "Stop"

kubectl get deployments,pods,services,jobs,pvc -n $Namespace
if ($LASTEXITCODE -ne 0) { throw "Nie udało się pobrać stanu środowiska." }

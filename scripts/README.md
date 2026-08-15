# Skrypty Instalacyjne

Ten katalog zawiera skrypty do instalacji i konfiguracji środowiska.

## Zawartość

### Kubernetes

| Skrypt | Zastosowanie |
|---|---|
| `k8s-build.ps1` | Buduje obrazy Open WebUI i Pipelines oraz opcjonalnie ładuje je do kind/minikube |
| `k8s-create-secret.ps1` | Tworzy lub aktualizuje Secret na podstawie `.env.k8s` |
| `k8s-up.ps1` | Wdraża środowisko i czeka na gotowość usług oraz modeli |
| `k8s-status.ps1` | Wyświetla stan workloadów, Services i PVC |
| `k8s-port-forward.ps1` | Udostępnia Open WebUI na `localhost:3000` |
| `k8s-down.ps1` | Skaluje Deploymenty do zera bez usuwania danych |

Pełna instrukcja znajduje się w `docs/KUBERNETES.md`.

### Pozostałe skrypty

Tutaj znajdziesz:
- Skrypty instalacyjne dla różnych systemów operacyjnych
- Skrypty konfiguracyjne
- Narzędzia do automatyzacji setupu środowiska

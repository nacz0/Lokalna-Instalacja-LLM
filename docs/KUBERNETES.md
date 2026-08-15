# Uruchomienie w Kubernetes

Konfiguracja Kubernetes uruchamia Ollama, Pipelines i Open WebUI w namespace `local-llm`. Docker Compose pozostaje dostępny jako alternatywa developerska.

## Architektura

```text
Przeglądarka
    │ port-forward :3000
    ▼
Open WebUI ──► Pipelines ──► Ollama
    │              │             │
    PVC            PVC           PVC modeli
```

Ollama i Pipelines mają Services typu `ClusterIP`, dlatego domyślnie nie są wystawiane poza klaster. Jedynym publicznym punktem wejścia jest lokalny port-forward Open WebUI.

## Wymagania

- Docker,
- lokalny klaster Kubernetes, np. Kubernetes w Docker Desktop, kind albo minikube,
- `kubectl`,
- PowerShell 7 lub Windows PowerShell 5.1,
- minimum około 8 GB pamięci przydzielonej klastrowi; większe modele wymagają więcej RAM.

Sprawdź połączenie z właściwym klastrem:

```powershell
kubectl config current-context
kubectl cluster-info
```

## 1. Sekrety

Utwórz lokalny plik na podstawie szablonu:

```powershell
Copy-Item .env.k8s.example .env.k8s
```

Ustaw długie, losowe wartości `PIPELINES_API_KEY` i `WEBUI_SECRET_KEY`. Ten sam `PIPELINES_API_KEY` jest przekazywany do Open WebUI jako klucz połączenia z Pipelines. Dane Spotify są opcjonalne. Plik `.env.k8s` jest ignorowany przez Git.

Secret można zastosować osobno:

```powershell
.\scripts\k8s-create-secret.ps1
```

Nie zapisuj prawdziwych sekretów w manifestach. Jeżeli sekret został wcześniej opublikowany w repozytorium, wygeneruj nowy po stronie dostawcy — przeniesienie starej wartości do Kubernetes Secret nie jest rotacją.

## 2. Budowa obrazów

Dla Kubernetes budowane są dwa lokalne obrazy:

- `local/open-webui-custom:k8s`,
- `local/llm-pipelines:k8s`.

Docker Desktop:

```powershell
.\scripts\k8s-build.ps1
```

kind:

```powershell
kind create cluster --name local-llm `
  --image kindest/node:v1.31.2@sha256:18fbefc20a7113353c7b75b5c869d7145a6abd6269154825872dc59c1329912e
.\scripts\k8s-build.ps1 -ClusterType kind -KindClusterName local-llm
```

Jeżeli klaster nazywa się `local-llm`, przekaż tę samą nazwę do skryptów przez `-KindClusterName local-llm`. Przypięty obraz Kubernetes v1.31.2 zachowuje kompatybilność ze starszym trybem cgroup v1 spotykanym w starszych instalacjach Docker Desktop.

minikube:

```powershell
.\scripts\k8s-build.ps1 -ClusterType minikube
```

Docker Desktop korzysta z tego samego lokalnego magazynu obrazów. Dla kind i minikube skrypt dodatkowo ładuje obrazy do klastra.

## 3. Wdrożenie CPU

Pełny szybki start, obejmujący budowę obrazów, Secret, manifesty i oczekiwanie na modele:

```powershell
.\scripts\k8s-up.ps1
```

Jeżeli obrazy są już zbudowane:

```powershell
.\scripts\k8s-up.ps1 -SkipBuild
```

Job `ollama-model-loader` pobiera modele z efektywnej wartości `OLLAMA_MODELS`. Overlay `local` używa lekkiego `gemma2:2b` i potrzebuje około 2 GB na model. Konfiguracja bazowa oraz profil GPU zawierają wszystkie trzy modele i mogą wymagać około 15 GB wolnego miejsca.

Postęp można obserwować poleceniem:

```powershell
kubectl logs -f job/ollama-model-loader -n local-llm
```

## 4. Dostęp do aplikacji

```powershell
.\scripts\k8s-port-forward.ps1
```

Open WebUI będzie dostępne pod adresem http://localhost:3000. Przekierowanie działa do naciśnięcia `Ctrl+C`.

Do diagnostyki backendów można tymczasowo użyć:

```powershell
kubectl port-forward service/ollama 11434:11434 -n local-llm
kubectl port-forward service/pipelines 9099:9099 -n local-llm
```

## 5. Profil GPU

Profil GPU wymaga działającego runtime NVIDIA i zasobu `nvidia.com/gpu` udostępnionego w klastrze:

```powershell
.\scripts\k8s-up.ps1 -Overlay gpu
```

Jeżeli węzły nie zgłaszają zasobu GPU, Pod Ollama pozostanie w stanie `Pending`. Sprawdź zasoby:

```powershell
kubectl describe nodes
kubectl describe pod -l app.kubernetes.io/name=ollama -n local-llm
```

## 6. Tryb modelu i zasoby

W Kubernetes `MODEL_MODE` domyślnie ma wartość `balanced`. Jest ustawiony jawnie, ponieważ RAM widziany przez kontener Pipelines nie musi odpowiadać pamięci dostępnej dla Ollama.

Dostępne wartości:

- `light` — `gemma2:2b`,
- `balanced` — `llama3:latest`,
- `advanced` — `llama3.1:latest`.

Po zmianie ConfigMap zastosuj overlay ponownie:

```powershell
kubectl apply -k k8s/overlays/local
kubectl rollout restart deployment/pipelines -n local-llm
```

## 7. Stan, logi i zatrzymanie

```powershell
.\scripts\k8s-status.ps1

kubectl logs deployment/ollama -n local-llm
kubectl logs deployment/pipelines -n local-llm
kubectl logs deployment/open-webui -n local-llm
```

Zatrzymanie Deploymentów bez usuwania PVC:

```powershell
.\scripts\k8s-down.ps1
```

Ponowne uruchomienie:

```powershell
.\scripts\k8s-up.ps1 -SkipBuild
```

Celowe usunięcie całego namespace usuwa również PVC i może bezpowrotnie skasować lokalne modele oraz dane Open WebUI. Nie jest wykonywane przez skrypty projektu.

## 8. Walidacja manifestów

```powershell
.\tests\validate_kubernetes.ps1
```

Można też wyrenderować konfigurację bez wdrażania:

```powershell
kubectl kustomize k8s/overlays/local
kubectl kustomize k8s/overlays/gpu
```

## Struktura konfiguracji

```text
k8s/
├── base/              # wspólne Deploymenty, Services, PVC i Job
└── overlays/
    ├── local/         # profil CPU dla lokalnego klastra
    └── gpu/           # profil z nvidia.com/gpu
```

Kustomize pozwala utrzymywać jedną konfigurację bazową i niewielkie różnice między profilami bez kopiowania całych manifestów.

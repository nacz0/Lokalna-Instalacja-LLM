# ============================================
# Odśwież token Spotify
# ============================================
# Wczytuje credentials z pliku .env (bezpieczniej niż hardcode)

# Wczytaj zmienne z .env
function Load-EnvFile {
    $envFile = Join-Path (Split-Path $MyInvocation.MyCommand.Path) ".env"
    
    if (-not (Test-Path $envFile)) {
        Write-Host "❌ Błąd: Plik .env nie znaleziony!" -ForegroundColor Red
        Write-Host "   Skopiuj .env.example na .env i uzupełnij swoimi danymi" -ForegroundColor Yellow
        exit 1
    }
    
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Załaduj zmienne
Load-EnvFile

# Pobierz credentials
$ClientId = [Environment]::GetEnvironmentVariable("SPOTIFY_CLIENT_ID")
$ClientSecret = [Environment]::GetEnvironmentVariable("SPOTIFY_CLIENT_SECRET")

# Walidacja
if (-not $ClientId -or -not $ClientSecret) {
    Write-Host "❌ Błąd: Brakuje SPOTIFY_CLIENT_ID lub SPOTIFY_CLIENT_SECRET w .env" -ForegroundColor Red
    exit 1
}

# Parametry z wiersza poleceń
param(
  [Parameter(Mandatory=$true, HelpMessage="Token odświeżający Spotify")]
  [string]$RefreshToken
)

$uri = "https://accounts.spotify.com/api/token"
$body = @{
  grant_type = "refresh_token"
  refresh_token = $RefreshToken
}

$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${ClientId}:${ClientSecret}"))
$headers = @{
  "Authorization" = "Basic $auth"
  "Content-Type" = "application/x-www-form-urlencoded"
}

try {
  $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $body
  Write-Host "✅ Nowy token:" -ForegroundColor Green
  Write-Host $response.access_token -ForegroundColor Cyan
  Write-Host "`n⏱️  Wygasa za: $($response.expires_in) sekund ($([math]::Round($response.expires_in / 3600, 1)) godzin)" -ForegroundColor Yellow
} catch {
  Write-Host "❌ Błąd odświeżania tokenu:" -ForegroundColor Red
  Write-Host $_.Exception.Message
}

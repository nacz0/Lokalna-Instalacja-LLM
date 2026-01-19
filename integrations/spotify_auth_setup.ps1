# Spotify Authentication Setup & Token Management
# Wczytaj zmienne srodowiskowe z pliku .env
function Load-EnvFile {
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
    $envFile = Join-Path $scriptDir ".env"
    if (-not (Test-Path $envFile)) {
        Write-Host "[ERROR] Plik .env nie znaleziony w: $envFile" -ForegroundColor Red
        exit 1
    }
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '=') {
            $parts = $_.Split('=', 2)
            if ($parts.Count -eq 2) {
                $name = $parts[0].Trim()
                $value = $parts[1].Trim()
                if ($name -and $value) {
                    [Environment]::SetEnvironmentVariable($name, $value, "Process")
                }
            }
        }
    }
    Write-Host "[OK] Zmienne z .env wczytane z: $envFile" -ForegroundColor Green
}

Load-EnvFile
$ClientId = [Environment]::GetEnvironmentVariable("SPOTIFY_CLIENT_ID")
$ClientSecret = [Environment]::GetEnvironmentVariable("SPOTIFY_CLIENT_SECRET")
$RedirectUri = [Environment]::GetEnvironmentVariable("SPOTIFY_REDIRECT_URI")

if (-not $ClientId -or -not $ClientSecret) {
    Write-Host "[ERROR] Brakuje SPOTIFY_CLIENT_ID lub SPOTIFY_CLIENT_SECRET w .env" -ForegroundColor Red
    exit 1
}

$TokenFile = "spotify_token.json"

function Get-SpotifyAuthorizationCode {
    Write-Host "`n=== Krok 1: Pozyskanie Authorization Code ===" -ForegroundColor Cyan
    $scope = "playlist-read-private playlist-read-collaborative"
    $authUrl = "https://accounts.spotify.com/authorize?client_id=$ClientId&response_type=code&redirect_uri=$([uri]::EscapeDataString($RedirectUri))&scope=$([uri]::EscapeDataString($scope))"
    Write-Host "`nOtwórz ten link w przegladarce:" -ForegroundColor Yellow
    Write-Host $authUrl -ForegroundColor Green
    Write-Host "`nSkopiuj kod z URL i wklej ponizej:" -ForegroundColor Yellow
    $authCode = Read-Host "Wklej Authorization Code"
    if (-not $authCode) {
        Write-Host "[ERROR] Authorization Code nie moze byc pusty!" -ForegroundColor Red
        return $null
    }
    return $authCode
}

function Get-SpotifyTokens {
    param([Parameter(Mandatory=$true)][string]$AuthorizationCode)
    Write-Host "`n=== Krok 2: Pozyskanie tokenow ===" -ForegroundColor Cyan
    $tokenUri = "https://accounts.spotify.com/api/token"
    $body = @{
        grant_type = "authorization_code"
        code = $AuthorizationCode
        redirect_uri = $RedirectUri
        client_id = $ClientId
        client_secret = $ClientSecret
    }
    $auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${ClientId}:${ClientSecret}"))
    $headers = @{
        "Authorization" = "Basic $auth"
        "Content-Type" = "application/x-www-form-urlencoded"
    }
    try {
        $response = Invoke-RestMethod -Method Post -Uri $tokenUri -Headers $headers -Body $body
        Write-Host "[OK] Tokeny pozyskane pomyslnie!" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "[ERROR] Blad podczas pobierania tokenow:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $null
    }
}

function Refresh-SpotifyAccessToken {
    param([Parameter(Mandatory=$true)][string]$RefreshToken)
    Write-Host "`n=== Odswiezanie Access Token ===" -ForegroundColor Cyan
    $tokenUri = "https://accounts.spotify.com/api/token"
    $body = @{
        grant_type = "refresh_token"
        refresh_token = $RefreshToken
        client_id = $ClientId
        client_secret = $ClientSecret
    }
    $auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${ClientId}:${ClientSecret}"))
    $headers = @{
        "Authorization" = "Basic $auth"
        "Content-Type" = "application/x-www-form-urlencoded"
    }
    try {
        $response = Invoke-RestMethod -Method Post -Uri $tokenUri -Headers $headers -Body $body
        Write-Host "[OK] Token odswiežony!" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "[ERROR] Blad odswiezania tokenu:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $null
    }
}

function Save-SpotifyTokens {
    param([Parameter(Mandatory=$true)]$TokenResponse)
    $config = @{
        client_id = $ClientId
        client_secret = $ClientSecret
        redirect_uri = $RedirectUri
        access_token = $TokenResponse.access_token
        refresh_token = $TokenResponse.refresh_token
        token_type = $TokenResponse.token_type
        expires_in = $TokenResponse.expires_in
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    $config | ConvertTo-Json | Out-File -FilePath $TokenFile -Encoding UTF8 -Force
    Write-Host "`n[OK] Tokeny zapisane do: $TokenFile" -ForegroundColor Green
}

function Load-SpotifyTokens {
    if (Test-Path $TokenFile) {
        $config = Get-Content $TokenFile | ConvertFrom-Json
        Write-Host "[OK] Tokeny wczytane z pliku" -ForegroundColor Green
        return $config
    } else {
        Write-Host "[ERROR] Plik $TokenFile nie znaleziony!" -ForegroundColor Red
        return $null
    }
}

function Show-Menu {
    Write-Host "`n====================================" -ForegroundColor Magenta
    Write-Host "   Spotify Token Management Tool    " -ForegroundColor Magenta
    Write-Host "====================================" -ForegroundColor Magenta
    Write-Host "1. [ZALOGUJ] (OAuth - PIERWSZY RAZ)" -ForegroundColor Cyan
    Write-Host "2. [ODSWIEZ] Access Token" -ForegroundColor Cyan
    Write-Host "3. [POKAZ] zapisane tokeny" -ForegroundColor Cyan
    Write-Host "4. [WYJSCIE]" -ForegroundColor Cyan
}

do {
    Show-Menu
    $choice = Read-Host "`nWybierz opcje (1-4)"
    switch ($choice) {
        "1" {
            Write-Host "`n[UWAGA] To opcja do pierwszego logowania!" -ForegroundColor Yellow
            $authCode = Get-SpotifyAuthorizationCode
            if ($authCode) {
                $tokens = Get-SpotifyTokens $authCode
                if ($tokens) { Save-SpotifyTokens $tokens }
            }
        }
        "2" {
            $tokens = Load-SpotifyTokens
            if ($tokens) {
                $refreshed = Refresh-SpotifyAccessToken $tokens.refresh_token
                if ($refreshed) {
                    $tokens.access_token = $refreshed.access_token
                    $tokens.timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    $tokens | ConvertTo-Json | Out-File -FilePath $TokenFile -Encoding UTF8 -Force
                }
            }
        }
        "3" {
            $tokens = Load-SpotifyTokens
            if ($tokens) {
                Write-Host "`nZapisane tokeny:" -ForegroundColor Yellow
                Write-Host "Client ID: $($tokens.client_id)" -ForegroundColor Cyan
                Write-Host "Access Token: $($tokens.access_token.Substring(0, 30))..." -ForegroundColor Green
                Write-Host "Refresh Token: $($tokens.refresh_token.Substring(0, 30))..." -ForegroundColor Green
                Write-Host "Zapisane: $($tokens.timestamp)" -ForegroundColor Gray
            }
        }
        "4" {
            Write-Host "`nDo widzenia!" -ForegroundColor Green
            exit
        }
        default {
            Write-Host "[ERROR] Nieznana opcja!" -ForegroundColor Red
        }
    }
} while ($true)

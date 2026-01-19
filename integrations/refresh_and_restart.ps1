# ============================================
# Spotify Token Refresh & Pipeline Restart
# ============================================
# Skrypt aby odswiezyt token i zrestartowac pipelines

Write-Host "====================================" -ForegroundColor Magenta
Write-Host "  Spotify Token Refresh & Restart  " -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
$workDir = $scriptDir
$repoRoot = Split-Path $workDir

# Funkcja do wczytania .env
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
}

Load-EnvFile

$ClientId = [Environment]::GetEnvironmentVariable("SPOTIFY_CLIENT_ID")
$ClientSecret = [Environment]::GetEnvironmentVariable("SPOTIFY_CLIENT_SECRET")

# 1. Wczytaj stary token
$tokenFile = Join-Path $workDir "spotify_token.json"

if (-not (Test-Path $tokenFile)) {
    Write-Host "[ERROR] Plik spotify_token.json nie znaleziony!" -ForegroundColor Red
    Write-Host "        Najpierw uruchom: .\spotify_auth_setup.ps1" -ForegroundColor Yellow
    exit 1
}

$tokenData = Get-Content $tokenFile | ConvertFrom-Json
$oldRefreshToken = $tokenData.refresh_token

Write-Host "`n[*] Odswiezam token..." -ForegroundColor Cyan

# 2. Odswież token
$uri = "https://accounts.spotify.com/api/token"
$body = @{
    grant_type = "refresh_token"
    refresh_token = $oldRefreshToken
}

$auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${ClientId}:${ClientSecret}"))
$headers = @{
    "Authorization" = "Basic $auth"
    "Content-Type" = "application/x-www-form-urlencoded"
}

try {
    $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $body
    
    Write-Host "[OK] Token odswiezony!" -ForegroundColor Green
    Write-Host "     Nowy token bedzie wazny przez: $($response.expires_in) sekund" -ForegroundColor Yellow
    
    # 3. Zapisz nowy token
    $newTokenData = @{
        client_id = $ClientId
        client_secret = $ClientSecret
        redirect_uri = [Environment]::GetEnvironmentVariable("SPOTIFY_REDIRECT_URI")
        access_token = $response.access_token
        refresh_token = $oldRefreshToken
        token_type = $response.token_type
        expires_in = $response.expires_in
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    $newTokenData | ConvertTo-Json | Out-File -FilePath $tokenFile -Encoding UTF8 -Force
    Write-Host "[OK] Token zapisany do: $tokenFile" -ForegroundColor Green
    
    # 4. Zrestartuj kontenery
    Write-Host "`n[*] Restartuję kontenery..." -ForegroundColor Cyan
    
    Push-Location $repoRoot
    
    Write-Host "     Restartuję pipelines..." -ForegroundColor Gray
    docker restart pipelines 2>&1 | Out-Null
    
    Write-Host "     Restartuję open-webui..." -ForegroundColor Gray
    docker restart open-webui 2>&1 | Out-Null
    
    Pop-Location
    
    Write-Host "[OK] Kontenery zrestartowane!" -ForegroundColor Green
    
    Write-Host "`n[SUCCESS] Gotowe! Pipeline Spotify jest teraz gotowy do uzytku." -ForegroundColor Green
    Write-Host "          Sprobuj: 'Wyszukaj Bohemian Rhapsody' w Open WebUI" -ForegroundColor Cyan
    
} catch {
    Write-Host "[ERROR] Blad odswiezania tokenu:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

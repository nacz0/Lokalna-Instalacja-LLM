# Odśwież token Spotify używając refresh_token
param(
  [Parameter(Mandatory=$true)]
  [string]$RefreshToken,
  [Parameter(Mandatory=$true)]
  [string]$ClientId,
  [Parameter(Mandatory=$true)]
  [string]$ClientSecret
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
  Write-Host "Nowy token:" -ForegroundColor Green
  Write-Host $response.access_token -ForegroundColor Cyan
  Write-Host "`nWygasa za: $($response.expires_in) sekund" -ForegroundColor Yellow
} catch {
  Write-Host "Błąd odświeżania tokenu:" -ForegroundColor Red
  Write-Host $_.Exception.Message
}

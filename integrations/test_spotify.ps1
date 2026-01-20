# Test Spotify API z tokenem Bearer
param(
  [Parameter(Mandatory=$true)]
  [string]$Token,
  [string]$Query = "Bohemian Rhapsody",
  [int]$Limit = 3
)

$uri = "https://api.spotify.com/v1/search?q=$([uri]::EscapeDataString($Query))&type=track&limit=$Limit"

Write-Host "Query:" $Query -ForegroundColor Cyan

# Użyj tokenu przekazanego jako parametr zamiast osadzonego w pliku
$headers = @{ "Authorization" = "Bearer $Token"; "Accept" = "application/json" }

$resp = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers -ErrorAction Stop

$tracks = $resp.tracks.items | Select-Object -First $Limit

foreach ($t in $tracks) {
  $artists = ($t.artists | ForEach-Object { $_.name }) -join ", "
  $title = $t.name
  $album = $t.album.name
  $link = $t.external_urls.spotify
  Write-Host "" -ForegroundColor Green
  Write-Host ("- {0} - {1}" -f $title, $artists) -ForegroundColor Green
  Write-Host ("  Album: {0}" -f $album) -ForegroundColor Green
  Write-Host ("  Link: {0}" -f $link) -ForegroundColor Green
}

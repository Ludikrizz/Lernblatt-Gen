<#
Entpackt ZIP-Dateien (z.B. aus OLAT "Herunterladen als ZIP") in den Staging-Ordner
und schreibt manifest.json im GLEICHEN Format wie fetch_moodle.ps1. Dadurch läuft
danach der identische Ablauf: kategorisieren -> map.json -> organize.ps1.

Jede entpackte Datei wird flach als "<NNNN>_<originalname>" abgelegt, damit
organize.ps1 sie per Schlüssel-Glob ("<NNNN>_*") findet. Der Original-Pfad in der
ZIP steht als "relpath" im Manifest und hilft beim Einsortieren (Ordnernamen in
der ZIP sind oft schon Kategorie-Hinweise).

Beispiel:
  .\ingest_zip.ps1 -ZipPath "C:\Users\...\Downloads\POIS_Material.zip" -OutDir "<scratchpad>\staging"
  .\ingest_zip.ps1 -ZipPath "C:\Users\...\Downloads" -OutDir "<scratchpad>\staging"   # alle *.zip im Ordner
#>
param(
  [Parameter(Mandatory)][string[]]$ZipPath,
  [Parameter(Mandatory)][string]$OutDir
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$tmp = Join-Path $OutDir '_unzip'
if(Test-Path $tmp){ Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

# ZIP-Dateien einsammeln (Datei oder Ordner erlaubt)
$zips = @()
foreach($p in $ZipPath){
  if(Test-Path $p -PathType Container){ $zips += Get-ChildItem $p -Filter *.zip -File | ForEach-Object FullName }
  elseif(Test-Path $p){ $zips += (Resolve-Path $p).Path }
  else { Write-Warning "Nicht gefunden: $p" }
}
if(-not $zips){ Write-Error "Keine ZIP-Dateien gefunden."; exit 1 }

foreach($z in $zips){
  $dest = Join-Path $tmp ([System.IO.Path]::GetFileNameWithoutExtension($z))
  Expand-Archive -LiteralPath $z -DestinationPath $dest -Force
}

$junk = 'Thumbs.db','.DS_Store','desktop.ini'
$all = Get-ChildItem $tmp -Recurse -File | Where-Object { $junk -notcontains $_.Name }

$manifest = @(); $i = 0
foreach($f in $all){
  $i++
  $key = '{0:D4}' -f $i
  $rel = $f.FullName.Substring($tmp.Length).TrimStart('\')
  Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $OutDir "$key`_$($f.Name)") -Force
  $manifest += [pscustomobject]@{
    id     = $key
    name   = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    file   = $f.Name
    relpath= $rel
    ext    = $f.Extension.TrimStart('.').ToLower()
    sizeKB = [math]::Round($f.Length/1kb)
    status = 'OK'
  }
}
Remove-Item $tmp -Recurse -Force

$result = [pscustomobject]@{ source='zip'; zips=$zips; staging=$OutDir; files=$manifest; links=@() }
$result | ConvertTo-Json -Depth 5 | Out-File (Join-Path $OutDir 'manifest.json') -Encoding utf8
Write-Output "--- DATEIEN ($($manifest.Count)) ---"
$manifest | ForEach-Object { "{0}`t{1}`t{2}KB`t{3}" -f $_.id,$_.ext,$_.sizeKB,$_.relpath }
Write-Output "MANIFEST: $(Join-Path $OutDir 'manifest.json')"

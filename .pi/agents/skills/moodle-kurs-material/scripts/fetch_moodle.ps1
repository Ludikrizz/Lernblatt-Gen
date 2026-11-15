<#
Lädt alle Ressourcen-Dateien eines Moodle-Kurses (Goethe-Uni studiumdigitale) in
einen Staging-Ordner und schreibt manifest.json. Externe Tool-Links (mod/url)
werden nur aufgelistet, nicht geladen.

WICHTIG: Dieses Skript ist absichtlich in sich geschlossen. PowerShell-Variablen
überleben NICHT zwischen einzelnen Tool-Aufrufen, darum bauen wir die Session und
laden alle Dateien in EINEM Lauf. Nie über mehrere Aufrufe aufteilen.

Beispiel:
  .\fetch_moodle.ps1 -Cookie <MoodleSession> -CourseId 8844 -OutDir C:\...\staging
#>
param(
  [Parameter(Mandatory)][string]$Cookie,
  [Parameter(Mandatory)][int]$CourseId,
  [Parameter(Mandatory)][string]$OutDir,
  [string]$Base = 'https://moodle.studiumdigitale.uni-frankfurt.de'
)
$ErrorActionPreference = 'Stop'
$host2 = ([System.Uri]$Base).Host
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.Cookies.Add((New-Object System.Net.Cookie('MoodleSession',$Cookie,'/',$host2)))
$session.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# --- Kursseite holen und Login prüfen ---
$page = Invoke-WebRequest -Uri "$Base/moodle/course/view.php?id=$CourseId" -WebSession $session -UseBasicParsing
$title = ([regex]::Match($page.Content,'<title>(.*?)</title>')).Groups[1].Value
if($page.BaseResponse.ResponseUri.AbsoluteUri -match '/login/' -or $title -match 'Log in'){
  Write-Error "Login fehlgeschlagen - Cookie ungueltig oder abgelaufen. Hole einen frischen MoodleSession-Cookie."
  exit 1
}
Write-Output "KURS: $title"

# --- Module parsen: mod/resource (Dateien) und mod/url (externe Links) ---
$rx = [regex]'<a[^>]*href="([^"]*/mod/(resource|url)/view\.php\?id=(\d+)[^"]*)"[^>]*>(.*?)</a>'
$resources = @(); $links = @(); $seen = @{}
foreach($m in $rx.Matches($page.Content)){
  $id = $m.Groups[3].Value
  if($seen.ContainsKey($id)){ continue }; $seen[$id] = $true
  $type = $m.Groups[2].Value; $inner = $m.Groups[4].Value
  $nm = [regex]::Match($inner,'class="instancename">(.*?)(<span class="accesshide|</span>)')
  $name = if($nm.Success){ $nm.Groups[1].Value } else { $inner }
  $name = ($name -replace '<[^>]+>','').Trim()
  if(-not $name){ continue }
  if($type -eq 'url'){ $links += [pscustomobject]@{ id=$id; name=$name } }
  else{ $resources += [pscustomobject]@{ id=$id; name=$name } }
}

# --- Externe Tool-Links auflösen (nur zur Info) ---
foreach($l in $links){
  try{
    $r = Invoke-WebRequest -Uri "$Base/moodle/mod/url/view.php?id=$($l.id)" -WebSession $session -UseBasicParsing
    $ext = [regex]::Matches($r.Content,'href="(https?://[^"]+)"') | ForEach-Object { $_.Groups[1].Value } |
           Where-Object { $_ -notmatch [regex]::Escape($host2) -and $_ -notmatch 'moodle\.(org|com)|w3\.org' } | Select-Object -First 1
    $l | Add-Member url ($ext) -Force
  }catch{ $l | Add-Member url "(mod/url/view.php?id=$($l.id))" -Force }
}

# --- Ressourcen-Dateien auflösen und laden ---
$manifest = @()
foreach($res in $resources){
  $id = $res.id; $name = $res.name
  try{
    $r = Invoke-WebRequest -Uri "$Base/moodle/mod/resource/view.php?id=$id" -WebSession $session -UseBasicParsing -MaximumRedirection 5
    $final = $r.BaseResponse.ResponseUri.AbsoluteUri
    $fileUrl = $null
    if($final -match 'pluginfile\.php'){ $fileUrl = $final }
    elseif($r.Headers['Content-Type'] -match 'text/html'){
      # Datei ist als HTML-Seite eingebettet -> pluginfile-Link herausziehen
      $mm = [regex]::Match($r.Content,'href="([^"]*pluginfile\.php[^"]*)"')
      if($mm.Success){ $fileUrl = $mm.Groups[1].Value -replace '&amp;','&' }
    }
    if(-not $fileUrl){ $manifest += [pscustomobject]@{ id=$id; name=$name; file=''; ext=''; sizeKB=0; status="KEINE-DATEI ($final)" }; continue }
    $fname = [System.Uri]::UnescapeDataString(($fileUrl -split '\?')[0].Split('/')[-1])
    $out = Join-Path $OutDir "$id`_$fname"
    Invoke-WebRequest -Uri $fileUrl -WebSession $session -UseBasicParsing -OutFile $out
    $sz = [math]::Round((Get-Item $out).Length/1kb)
    $ext = [System.IO.Path]::GetExtension($fname).TrimStart('.').ToLower()
    $manifest += [pscustomobject]@{ id=$id; name=$name; file=$fname; ext=$ext; sizeKB=$sz; status='OK' }
  }catch{
    $manifest += [pscustomobject]@{ id=$id; name=$name; file=''; ext=''; sizeKB=0; status="FEHLER $($_.Exception.Message)" }
  }
}

# --- Manifest schreiben + Übersicht ausgeben ---
$result = [pscustomobject]@{ course=$title; courseId=$CourseId; staging=$OutDir; files=$manifest; links=$links }
$result | ConvertTo-Json -Depth 5 | Out-File (Join-Path $OutDir 'manifest.json') -Encoding utf8
Write-Output "--- DATEIEN ($($manifest.Count)) ---"
$manifest | ForEach-Object { "{0}`t{1}`t{2}`t{3}KB`t{4}" -f $_.id,$_.status,$_.ext,$_.sizeKB,$_.name }
Write-Output "--- EXTERNE LINKS ($($links.Count)) ---"
$links | ForEach-Object { "{0}`t{1}`t{2}" -f $_.id,$_.name,$_.url }
Write-Output "MANIFEST: $(Join-Path $OutDir 'manifest.json')"

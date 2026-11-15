<#
Verschiebt die Staging-Dateien in die Fach-Ordner mit sauberen Namen.

Eingabe: eine JSON-Datei, die jede Moodle-Ressourcen-id auf einen Zielpfad
(relativ zum Fach-Ordner) abbildet, z.B.:
  {
    "363777": "Vorlesungsfolien\\01_Orga_Intro.pdf",
    "363805": "Klausuren\\Deckblatt_Klausur.pdf",
    "363783": "Uebungen\\SPARQL_Notebook.ipynb"
  }

Warum Move statt Copy: In einem frueheren Lauf hat Copy-Item das Ziel als Ordner
statt als Datei behandelt und alles im Wurzelordner abgelegt. Move-Item mit
-LiteralPath auf einen vollstaendigen Ziel-DATEIpfad ist robust. Am Ende wird die
Struktur zur Kontrolle ausgegeben.

Beispiel:
  .\organize.ps1 -MapJson C:\...\map.json -StagingDir C:\...\staging -TargetRoot "W:\Studium\Lernen\<Fach>"
#>
param(
  [Parameter(Mandatory)][string]$MapJson,
  [Parameter(Mandatory)][string]$StagingDir,
  [Parameter(Mandatory)][string]$TargetRoot
)
$ErrorActionPreference = 'Stop'
$map = Get-Content $MapJson -Raw | ConvertFrom-Json

# Zielordner sicherstellen (aus den Zielpfaden abgeleitet)
$dirs = $map.PSObject.Properties.Value | ForEach-Object { Split-Path $_ -Parent } | Where-Object { $_ } | Sort-Object -Unique
foreach($d in $dirs){ New-Item -ItemType Directory -Force -Path (Join-Path $TargetRoot $d) | Out-Null }

$moved = 0; $missing = @()
foreach($p in $map.PSObject.Properties){
  $id = $p.Name; $rel = $p.Value
  $src = Get-ChildItem $StagingDir -File -Filter "$id`_*" | Select-Object -First 1
  if(-not $src){ $missing += $id; continue }
  $dest = Join-Path $TargetRoot $rel
  Move-Item -LiteralPath $src.FullName -Destination $dest -Force
  $moved++
}
Write-Output "VERSCHOBEN: $moved"
if($missing){ Write-Output "FEHLT (keine Staging-Datei): $($missing -join ', ')" }
Write-Output "--- STRUKTUR ---"
Get-ChildItem $TargetRoot -Recurse -File | ForEach-Object { $_.FullName.Substring($TargetRoot.Length).TrimStart('\') } | Sort-Object

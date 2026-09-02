<#
    tira.ps1 - Tiratore di dadi per RUMORE DI FONDO
    Missione: "Profondo 7"

    Implementa alla lettera REGOLE.md:
      - Si tira una manciata di d6 e si legge SOLO il dado piu alto
      - 6            -> Pulito   (funziona, nessun costo)
      - 4-5          -> Sporco   (funziona, ma c'e' un prezzo)
      - 1-3          -> Rumore   (non funziona: Statica +1 e il GM fa una mossa)
      - due o piu 6  -> Limpido  (funziona, e resta in mano un vantaggio)
      - Base 1d6, +1d6 per Ruolo / Attrezzo / Vantaggio, massimo 4d6
      - -Forza aggiunge 1d6 (fino a 5) e alza subito la Statica di 1

    Il tiratore tiene anche le due tracce in tracce.json, cosi' la Statica
    che sale sul tavolo e' la stessa che sale sulla plancia.

    ESEMPI
      .\tira.ps1 -Ruolo -Attrezzo -Etichetta "Aprire il quadro del portello"
      .\tira.ps1 -Ruolo -Attrezzo -Vantaggio -Forza
      .\tira.ps1 -Dadi 3
      .\tira.ps1 -Statica              # mostra le tracce
      .\tira.ps1 -Spendi 2             # il GM spende Statica
      .\tira.ps1 -Azzera               # riparte da 0/0
#>

[CmdletBinding()]
param(
    [int]    $Dadi       = 0,
    [switch] $Ruolo,
    [switch] $Attrezzo,
    [switch] $Vantaggio,
    [switch] $Forza,
    [string] $Etichetta  = "",
    [int]    $Volte      = 1,
    [switch] $Statica,
    [int]    $Spendi     = 0,
    [switch] $Azzera
)

$ErrorActionPreference = "Stop"
$Tracce = Join-Path $PSScriptRoot "tracce.json"

# ---------------------------------------------------------------- tracce ----
function Leggi-Tracce {
    if (Test-Path $Tracce) {
        try { return Get-Content $Tracce -Raw -Encoding utf8 | ConvertFrom-Json } catch {}
    }
    return [pscustomobject]@{ statica = 0; allarme = 0 }
}

function Scrivi-Tracce($t) {
    $t | ConvertTo-Json | Out-File $Tracce -Encoding utf8
}

function Mostra-Tracce($t, [string]$nota = "") {
    $st = ("#" * $t.statica).PadRight(6, ".")
    $al = ("#" * $t.allarme).PadRight(4, ".")
    Write-Host ""
    Write-Host ("  STATICA  [{0}]  {1}/6" -f $st, $t.statica) -ForegroundColor Yellow
    Write-Host ("  ALLARME  [{0}]  {1}/4" -f $al, $t.allarme) -ForegroundColor Red
    if ($nota) { Write-Host "  $nota" -ForegroundColor DarkGray }

    switch ($t.allarme) {
        1 { Write-Host "  L'acqua trova la strada: il Ponte B si allaga di una tacca."       -ForegroundColor DarkRed }
        2 { Write-Host "  La linea cede: ammoniaca negli Alloggi, irrespirabile senza maschera." -ForegroundColor DarkRed }
        3 { Write-Host "  La piattaforma si inclina: otto gradi, e non tornano indietro."    -ForegroundColor DarkRed }
        4 { Write-Host "  MAREA VIVA. Timer da dieci minuti reali sul tavolo, e non si ferma." -ForegroundColor Red }
    }
    Write-Host ""
}

function Alza-Statica($t, [int]$n, [string]$perche) {
    for ($i = 0; $i -lt $n; $i++) {
        $t.statica++
        if ($t.statica -gt 6) {
            $t.statica = 0
            if ($t.allarme -lt 4) { $t.allarme++ }
            Write-Host ("  >> La Statica tracima. ALLARME {0}." -f $t.allarme) -ForegroundColor Red
        }
    }
    Write-Host ("  Statica +{0} ({1})" -f $n, $perche) -ForegroundColor Yellow
    return $t
}

# ------------------------------------------------------------- comandi -----
$t = Leggi-Tracce

if ($Azzera) {
    $t.statica = 0; $t.allarme = 0
    Scrivi-Tracce $t
    Mostra-Tracce $t "Tracce azzerate."
    return
}

if ($Spendi -gt 0) {
    if ($Spendi -gt $t.statica) {
        Write-Host "`n  Statica insufficiente: hai $($t.statica), ne servono $Spendi.`n" -ForegroundColor DarkGray
        return
    }
    $cosa = switch ($Spendi) {
        1 { "complicazione: qualcosa si rompe, si chiude, si sporca, arriva tardi" }
        2 { "pericolo diretto su una persona, adesso, con nome e direzione" }
        3 { "disastro locale: una zona cambia stato in modo permanente" }
        default { "spesa fuori tabella" }
    }
    $t.statica -= $Spendi
    Scrivi-Tracce $t
    Mostra-Tracce $t "Il GM spende $Spendi -> $cosa"
    return
}

if ($Statica) { Mostra-Tracce $t; return }

# --------------------------------------------------------------- tiro ------
[int]$n = 0
if ($Dadi -gt 0) {
    $n = $Dadi
} else {
    $n = 1
    if ($Ruolo)     { $n = $n + 1 }
    if ($Attrezzo)  { $n = $n + 1 }
    if ($Vantaggio) { $n = $n + 1 }
}
if ($n -gt 4 -and -not $Forza -and $Dadi -eq 0) { $n = 4 }

$forzati = 0
if ($Forza) {
    if ($n -ge 5) {
        Write-Host "`n  Hai gia' cinque dadi: non si Forza oltre.`n" -ForegroundColor DarkGray
    } else {
        $n++; $forzati = 1
    }
}

Write-Host ""
if ($Etichetta) { Write-Host "  $Etichetta" -ForegroundColor White }

$perche = @()
if ($Dadi -gt 0) {
    $perche = $perche + "manciata dichiarata"
} else {
    $perche = $perche + "base 1"
    if ($Ruolo)     { $perche = $perche + "Ruolo" }
    if ($Attrezzo)  { $perche = $perche + "Attrezzo" }
    if ($Vantaggio) { $perche = $perche + "Vantaggio" }
}
if ($forzati) { $perche = $perche + "Forzato" }
$motivo = $perche -join " + "
Write-Host ("  " + [string]$n + "d6 - " + $motivo) -ForegroundColor DarkGray

if ($forzati) { $t = Alza-Statica $t 1 "Forzatura" }

for ($v = 1; $v -le $Volte; $v++) {

    $tirati = @()
    for ($i = 0; $i -lt $n; $i++) {
        $tirati = $tirati + (Get-Random -Minimum 1 -Maximum 7)
    }

    [int]$alto = 0
    [int]$sei  = 0
    foreach ($d in $tirati) {
        if ($d -gt $alto) { $alto = $d }
        if ($d -eq 6)     { $sei  = $sei + 1 }
    }

    $pezzi = @()
    foreach ($d in $tirati) {
        if ($d -eq $alto) { $pezzi = $pezzi + "[$d]" } else { $pezzi = $pezzi + " $d " }
    }
    $riga = $pezzi -join " "

    if     ($sei -ge 2)  { $esito = "LIMPIDO"; $col = "Green";  $nota = "Funziona, e ti resta in mano un vantaggio concreto." }
    elseif ($alto -eq 6) { $esito = "PULITO";  $col = "Green";  $nota = "Funziona come volevi. Nessun costo." }
    elseif ($alto -ge 4) { $esito = "SPORCO";  $col = "Yellow"; $nota = "Funziona, ma c'e' un prezzo. Puoi Resistere: una Condizione, oppure Statica +1." }
    else                 { $esito = "RUMORE";  $col = "Red";    $nota = "Non funziona. Statica +1 e il GM fa una mossa." }

    Write-Host ""
    Write-Host ("  $riga") -ForegroundColor DarkGray
    Write-Host ("  $esito") -ForegroundColor $col
    Write-Host ("  $nota") -ForegroundColor DarkGray

    if ($alto -le 3) { $t = Alza-Statica $t 1 "Rumore" }
}

Scrivi-Tracce $t
Mostra-Tracce $t

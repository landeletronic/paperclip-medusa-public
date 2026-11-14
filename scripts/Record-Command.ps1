[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Command,

    [string]$Description = '',
    [string]$LogFile = '',
    [string]$WorkingDirectory = ''
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($WorkingDirectory)) { $WorkingDirectory = $root }

if ([string]::IsNullOrWhiteSpace($LogFile)) {
    $newLog = & (Join-Path $PSScriptRoot 'New-LogEntry.ps1') -Type command -Slug 'auto' -Title 'Comandos automaticos'
    $LogFile = ($newLog | Select-Object -Last 1).ToString().Trim()
} elseif (-not [System.IO.Path]::IsPathRooted($LogFile)) {
    $LogFile = Join-Path $root $LogFile
}
if (-not (Test-Path $LogFile)) { throw "Log de comandos nao encontrado: $LogFile" }

$start = Get-Date
Push-Location $WorkingDirectory
try {
    $hostExe = if ($PSVersionTable.PSEdition -eq 'Core') {
        Join-Path $PSHOME 'pwsh.exe'
    } else {
        Join-Path $PSHOME 'powershell.exe'
    }
    $output = & $hostExe -NoProfile -Command $Command 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($null -eq $exitCode) { $exitCode = 0 }
if ($null -eq $output) { $output = '' }

$duration = (Get-Date) - $start
$durationText = '{0:N2}s' -f $duration.TotalSeconds
$maxChars = 20000
$outputTrimmed = $output
if ($outputTrimmed.Length -gt $maxChars) {
    $outputTrimmed = $outputTrimmed.Substring(0, $maxChars) + "`r`n... [saida truncada em $maxChars caracteres]"
}

$template = @'
## Comando - {{TIMESTAMP}}

- **Descricao:** {{DESCRIPTION}}
- **Diretorio:** `{{WORKDIR}}`
- **Exit code:** {{EXIT}}
- **Duracao:** {{DURATION}}
- **Comando:**

```powershell
{{COMMAND}}
```

### Saida

```text
{{OUTPUT}}
```

'@

$entry = $template.Replace('{{TIMESTAMP}}', (Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'))
$entry = $entry.Replace('{{DESCRIPTION}}', $Description)
$entry = $entry.Replace('{{WORKDIR}}', $WorkingDirectory)
$entry = $entry.Replace('{{EXIT}}', $exitCode.ToString())
$entry = $entry.Replace('{{DURATION}}', $durationText)
$entry = $entry.Replace('{{COMMAND}}', $Command)
$entry = $entry.Replace('{{OUTPUT}}', $outputTrimmed)

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::AppendAllText($LogFile, $entry, $utf8)

Write-Output "Comando registrado em $LogFile (exit=$exitCode, duracao=$durationText)"

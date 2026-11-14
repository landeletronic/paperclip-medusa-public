[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$LogFile,

    [Parameter(Mandatory = $true)]
    [ValidateSet('user', 'assistant', 'system', 'tool')]
    [string]$Role,

    [Parameter(Mandatory = $true)]
    [string]$Message
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($LogFile)) { $LogFile = Join-Path $root $LogFile }
if (-not (Test-Path $LogFile)) { throw "Arquivo de conversa nao encontrado: $LogFile" }

$roleLabels = @{
    user      = 'Usuario'
    assistant = 'Agente'
    system    = 'Sistema'
    tool      = 'Ferramenta'
}
$roleLabel = $roleLabels[$Role]
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
$entry = "`r`n### $roleLabel - $timestamp`r`n`r`n$Message`r`n"

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::AppendAllText($LogFile, $entry, $utf8)

Write-Output "Mensagem adicionada a $LogFile"

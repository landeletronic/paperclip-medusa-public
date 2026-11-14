[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('conversation', 'command', 'execution', 'task', 'test', 'inventory')]
    [string]$Type,

    [Parameter(Mandatory = $true)]
    [string]$Slug,

    [string]$Title = '',
    [string]$Date = (Get-Date -Format 'yyyy-MM-dd'),
    [string]$Author = '',
    [string]$Workspace = ''
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($Workspace)) { $Workspace = $root }

$map = @{
    conversation = @{ Folder = 'logs/conversations'; Prefix = 'session';   Template = 'conversation.md' }
    command      = @{ Folder = 'logs/commands';      Prefix = 'command';   Template = 'command.md' }
    execution    = @{ Folder = 'logs/executions';    Prefix = 'execution'; Template = 'execution.md' }
    task         = @{ Folder = 'logs/tasks';         Prefix = 'task';      Template = 'task.md' }
    test         = @{ Folder = 'logs/tests';         Prefix = 'test';      Template = 'test.md' }
    inventory    = @{ Folder = 'logs/inventories';   Prefix = 'inventory'; Template = 'inventory.md' }
}

$entry = $map[$Type]
$folder = Join-Path $root $entry.Folder
$templatePath = Join-Path $root (Join-Path 'templates' $entry.Template)

if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }
if (-not (Test-Path $templatePath)) { throw "Template nao encontrado: $templatePath" }

$slugSanitized = $Slug.ToLowerInvariant()
$slugSanitized = $slugSanitized -replace '[^a-z0-9-]', '-'
$slugSanitized = $slugSanitized -replace '-+', '-'
$slugSanitized = $slugSanitized.Trim('-')
if ([string]::IsNullOrWhiteSpace($slugSanitized)) { throw "Slug invalido: $Slug" }

if ([string]::IsNullOrWhiteSpace($Title)) { $Title = ($slugSanitized -replace '-', ' ') }

if ([string]::IsNullOrWhiteSpace($Author)) {
    try {
        $gitAuthor = git config --get user.name 2>$null
        if (-not [string]::IsNullOrWhiteSpace($gitAuthor)) { $Author = $gitAuthor.Trim() }
    } catch { }
}
if ([string]::IsNullOrWhiteSpace($Author)) { $Author = 'Paperclip Medusa DevOps' }

$prefix = $entry.Prefix
$existing = Get-ChildItem -Path $folder -Filter "$Date-$prefix-*.md" -File -ErrorAction SilentlyContinue
$max = 0
foreach ($file in $existing) {
    if ($file.Name -match "^$([regex]::Escape($Date))-$prefix-(\d{3})-") {
        $n = [int]$Matches[1]
        if ($n -gt $max) { $max = $n }
    }
}
$seq = '{0:D3}' -f ($max + 1)
$id = "$Date-$prefix-$seq"
$fileName = "$id-$slugSanitized.md"
$path = Join-Path $folder $fileName

$content = Get-Content -Path $templatePath -Raw -Encoding UTF8
$content = $content.Replace('{{ID}}', $id)
$content = $content.Replace('{{DATE}}', $Date)
$content = $content.Replace('{{TIME}}', (Get-Date -Format 'HH:mm:ss'))
$content = $content.Replace('{{TITLE}}', $Title)
$content = $content.Replace('{{SLUG}}', $slugSanitized)
$content = $content.Replace('{{AUTHOR}}', $Author)
$content = $content.Replace('{{WORKSPACE}}', $Workspace)
$content = $content.Replace('{{TYPE}}', $Type)

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($path, $content, $utf8)

Write-Output $path

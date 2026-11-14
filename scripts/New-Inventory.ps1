[CmdletBinding()]
param(
    [string]$Slug = 'estado-atual',
    [string]$Title = 'Inventario do estado atual',
    [string]$Date = (Get-Date -Format 'yyyy-MM-dd'),
    [string]$Author = '',
    [string]$Workspace = ''
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($Workspace)) { $Workspace = $root }

$slugSanitized = $Slug.ToLowerInvariant()
$slugSanitized = $slugSanitized -replace '[^a-z0-9-]', '-'
$slugSanitized = $slugSanitized -replace '-+', '-'
$slugSanitized = $slugSanitized.Trim('-')
if ([string]::IsNullOrWhiteSpace($slugSanitized)) { throw "Slug invalido: $Slug" }

if ([string]::IsNullOrWhiteSpace($Author)) {
    try {
        $gitAuthor = git config --get user.name 2>$null
        if (-not [string]::IsNullOrWhiteSpace($gitAuthor)) { $Author = $gitAuthor.Trim() }
    } catch { }
}
if ([string]::IsNullOrWhiteSpace($Author)) { $Author = 'Paperclip Medusa DevOps' }

$folder = Join-Path $root 'logs/inventories'
if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }

$existing = Get-ChildItem -Path $folder -Filter "$Date-inventory-*.md" -File -ErrorAction SilentlyContinue
$max = 0
foreach ($file in $existing) {
    if ($file.Name -match "^$([regex]::Escape($Date))-inventory-(\d{3})-") {
        $n = [int]$Matches[1]
        if ($n -gt $max) { $max = $n }
    }
}
$seq = '{0:D3}' -f ($max + 1)
$id = "$Date-inventory-$seq"
$path = Join-Path $folder "$id-$slugSanitized.md"

$excludePattern = '\\(\.git|node_modules|dist|build|out|coverage|\.venv|venv|__pycache__|\.cache|\.tools)\\'
$files = @(Get-ChildItem -Path $root -Recurse -File -Force |
    Where-Object { $_.FullName -notmatch $excludePattern } |
    Sort-Object FullName)

$rows = New-Object System.Collections.Generic.List[string]
$totalBytes = 0L
$typeCounts = @{}

foreach ($file in $files) {
    $relative = $file.FullName.Substring($root.Length)
    $relative = $relative -replace '^[\\/]+', ''
    $relative = $relative -replace '\\', '/'
    $ext = if ([string]::IsNullOrWhiteSpace($file.Extension)) { 'sem-extensao' } else { $file.Extension.TrimStart('.').ToLowerInvariant() }
    $hash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash
    $size = $file.Length
    $totalBytes += $size
    if ($typeCounts.ContainsKey($ext)) { $typeCounts[$ext]++ } else { $typeCounts[$ext] = 1 }
    $safePath = $relative -replace '\|', '\|'
    $rows.Add("| ``$safePath`` | $ext | $size | ``$hash`` | - |")
}

$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
$typeSummary = ($typeCounts.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Value)" }) -join ', '
$rowText = $rows -join "`r`n"

$content = @"
# Inventario $id - $Title

## Metadados

| Campo | Valor |
|---|---|
| ID | $id |
| Data | $Date |
| Hora | $timestamp |
| Autor | $Author |
| Tipo | inventory |
| Status | concluido |
| Workspace | $Workspace |
| Escopo | repositorio completo (exceto .git e artefatos de build) |

## Objetivo

Snapshot automatico do estado do repositorio.

## Arquivos

| Caminho | Tipo | Tamanho (bytes) | SHA-256 | Descricao |
|---|---|---:|---|---|
$rowText

## Resumo

- Total de arquivos: $($files.Count)
- Total de bytes: $totalBytes
- Tipos encontrados: $typeSummary

## Observacoes

- Inventario gerado automaticamente por ``scripts/New-Inventory.ps1``.
- O diretorio ``.git`` e artefatos de build/dependencias foram excluidos.
- Para atualizar, gerar um novo inventario com sequencial novo.
"@

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($path, $content, $utf8)

Write-Output $path

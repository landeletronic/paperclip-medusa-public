[CmdletBinding()]
param(
    [string]$Root = ''
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Split-Path -Parent $PSScriptRoot }
$Root = (Resolve-Path $Root).Path

$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
    param(
        [string]$Name,
        [bool]$Pass,
        [string]$Details = ''
    )
    $results.Add([PSCustomObject]@{
        Name    = $Name
        Pass    = $Pass
        Details = $Details
    })
}

# T1 - raiz limpa
$allowedRootFiles = @(
    'README.md', 'AGENTS.md', 'opencode.json',
    'LICENSE', 'NOTICE', 'CONTRIBUTING.md', 'CHANGELOG.md', 'SECURITY.md',
    'AGENTS.override.md', '.gitignore', '.gitattributes', '.editorconfig',
    '.gitleaks.toml', '.hadolint.yaml', '.markdownlint-cli2.yaml', '.yamllint.yml'
)
$rootFiles = Get-ChildItem -Path $Root -File -Force
$unexpected = $rootFiles | Where-Object { $allowedRootFiles -notcontains $_.Name }
if ($unexpected) {
    $names = ($unexpected | ForEach-Object { $_.Name }) -join ', '
    Add-Result -Name 'T1 - Raiz contem apenas arquivos essenciais de entrada, governanca e infraestrutura' -Pass $false -Details $names
} else {
    Add-Result -Name 'T1 - Raiz contem apenas arquivos essenciais de entrada, governanca e infraestrutura' -Pass $true
}

# T2 - diretorios obrigatorios
$requiredDirs = @(
    'docs',
    'docs/agents',
    'docs/assets',
    'docs/assets/screenshots',
    'docs/research',
    'docs/plans',
    'logs',
    'logs/conversations',
    'logs/commands',
    'logs/executions',
    'logs/tasks',
    'logs/tests',
    'logs/inventories',
    'scripts',
    'templates',
    'src',
    '.github/workflows',
    '.github/ISSUE_TEMPLATE'
)
$missingDirs = @()
foreach ($d in $requiredDirs) {
    if (-not (Test-Path (Join-Path $Root $d) -PathType Container)) { $missingDirs += $d }
}
if ($missingDirs.Count -gt 0) {
    Add-Result -Name 'T2 - Diretorios obrigatorios existem' -Pass $false -Details ($missingDirs -join ', ')
} else {
    Add-Result -Name 'T2 - Diretorios obrigatorios existem' -Pass $true
}

# T3 - arquivos obrigatorios
$requiredFiles = @(
    'README.md',
    'AGENTS.md',
    'opencode.json',
    'LICENSE',
    'NOTICE',
    'CONTRIBUTING.md',
    'CHANGELOG.md',
    'SECURITY.md',
    'docs/README.md',
    'docs/CONVENTIONS.md',
    'docs/GIT_WORKFLOW.md',
    'docs/agents/README.md',
    'docs/agents/OPENCODE.md',
    'docs/agents/HERMES.md',
    'docs/agents/MEMORY.md',
    'logs/README.md',
    'scripts/Test-RepositoryStructure.ps1',
    'templates/README.md',
    '.github/workflows/validate.yml',
    '.github/workflows/lint.yml',
    '.github/workflows/security.yml',
    '.github/PULL_REQUEST_TEMPLATE.md',
    '.github/ISSUE_TEMPLATE/bug_report.yml',
    '.github/ISSUE_TEMPLATE/feature_request.yml',
    '.github/ISSUE_TEMPLATE/config.yml',
    '.github/dependabot.yml',
    '.gitleaks.toml',
    '.hadolint.yaml',
    '.markdownlint-cli2.yaml',
    '.yamllint.yml'
)
$missingFiles = @()
foreach ($f in $requiredFiles) {
    if (-not (Test-Path (Join-Path $Root $f) -PathType Leaf)) { $missingFiles += $f }
}
if ($missingFiles.Count -gt 0) {
    Add-Result -Name 'T3 - Arquivos obrigatorios existem' -Pass $false -Details ($missingFiles -join ', ')
} else {
    Add-Result -Name 'T3 - Arquivos obrigatorios existem' -Pass $true
}

# T4 - nomenclatura dos registros
$prefixByFolder = @{
    'conversations' = 'session'
    'commands'      = 'command'
    'executions'    = 'execution'
    'tasks'         = 'task'
    'tests'         = 'test'
    'inventories'   = 'inventory'
}
$badLogs = @()
foreach ($folderName in $prefixByFolder.Keys) {
    $folder = Join-Path $Root "logs/$folderName"
    if (-not (Test-Path $folder)) { continue }
    $prefix = $prefixByFolder[$folderName]
    $pattern = "^\d{4}-\d{2}-\d{2}-$prefix-\d{3}-[a-z0-9-]+\.md$"
    foreach ($file in Get-ChildItem -Path $folder -File -Filter '*.md' -Force) {
        if ($file.Name -eq 'README.md') { continue }
        if ($file.Name -notmatch $pattern) { $badLogs += "logs/$folderName/$($file.Name)" }
    }
}
if ($badLogs.Count -gt 0) {
    Add-Result -Name 'T4 - Nomenclatura dos registros em logs/' -Pass $false -Details ($badLogs -join ', ')
} else {
    Add-Result -Name 'T4 - Nomenclatura dos registros em logs/' -Pass $true
}

# T5 - repositorio git
if (Test-Path (Join-Path $Root '.git') -PathType Container) {
    Add-Result -Name 'T5 - Repositorio Git inicializado' -Pass $true
} else {
    Add-Result -Name 'T5 - Repositorio Git inicializado' -Pass $false
}

# T6 - segredos de alta confianca
$secretPatterns = @(
    'AKIA[0-9A-Z]{16}',
    'ghp_[A-Za-z0-9]{36}',
    '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
)
$scannerFiles = @(
    (Join-Path $Root 'scripts/Test-RepositoryStructure.ps1'),
    (Join-Path $Root '.github/workflows/validate.yml')
)
$textExtensions = @('.md', '.ps1', '.yml', '.yaml', '.json', '.txt', '.xml', '.csv')
$textFiles = Get-ChildItem -Path $Root -Recurse -File -Force | Where-Object {
    $_.FullName -notmatch '\\\.git\\' -and
    $textExtensions -contains $_.Extension.ToLowerInvariant() -and
    $scannerFiles -notcontains $_.FullName
}
$secretHits = @()
foreach ($file in $textFiles) {
    $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($null -eq $content) { continue }
    foreach ($pattern in $secretPatterns) {
        if ($content -match $pattern) {
            $secretHits += $file.FullName.Substring($Root.Length).TrimStart('\', '/')
            break
        }
    }
}
if ($secretHits.Count -gt 0) {
    Add-Result -Name 'T6 - Nenhum segredo de alta confianca detectado' -Pass $false -Details ($secretHits -join ', ')
} else {
    Add-Result -Name 'T6 - Nenhum segredo de alta confianca detectado' -Pass $true
}

# T7 - arquivos .env reais
$envFiles = Get-ChildItem -Path $Root -Recurse -File -Force -Filter '.env*' | Where-Object {
    $_.FullName -notmatch '\\\.git\\' -and $_.Name -ne '.env.example'
}
if ($envFiles) {
    Add-Result -Name 'T7 - Nenhum arquivo .env real versionado' -Pass $false -Details (($envFiles | ForEach-Object { $_.Name }) -join ', ')
} else {
    Add-Result -Name 'T7 - Nenhum arquivo .env real versionado' -Pass $true
}

# T8 - configuracao do OpenCode
$openCodePath = Join-Path $Root 'opencode.json'
$openCodeOk = $false
$openCodeDetails = ''
if (Test-Path $openCodePath -PathType Leaf) {
    try {
        $config = Get-Content -Path $openCodePath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($null -eq $config.'$schema') {
            $openCodeDetails = 'campo $schema ausente'
        } elseif ($null -eq $config.instructions) {
            $openCodeDetails = 'campo instructions ausente'
        } else {
            $missing = @()
            foreach ($instruction in @($config.instructions)) {
                if ($instruction -isnot [string]) { continue }
                if ($instruction -match '^https?://') { continue }
                if (-not (Test-Path (Join-Path $Root $instruction))) { $missing += $instruction }
            }
            if ($missing.Count -gt 0) {
                $openCodeDetails = 'instrucoes ausentes: ' + ($missing -join ', ')
            } else {
                $openCodeOk = $true
            }
        }
    } catch {
        $openCodeDetails = $_.Exception.Message
    }
} else {
    $openCodeDetails = 'arquivo ausente'
}
if ($openCodeOk) {
    Add-Result -Name 'T8 - opencode.json valido e instrucoes existem' -Pass $true
} else {
    Add-Result -Name 'T8 - opencode.json valido e instrucoes existem' -Pass $false -Details $openCodeDetails
}

# T9 - arquivos que ofuscam AGENTS.md no Hermes
$shadowFiles = @()
foreach ($name in @('.hermes.md', 'HERMES.md')) {
    if (Test-Path (Join-Path $Root $name) -PathType Leaf) { $shadowFiles += $name }
}
if ($shadowFiles.Count -gt 0) {
    Add-Result -Name 'T9 - Sem arquivos de contexto que ofuscam AGENTS.md no Hermes' -Pass $false -Details ($shadowFiles -join ', ')
} else {
    Add-Result -Name 'T9 - Sem arquivos de contexto que ofuscam AGENTS.md no Hermes' -Pass $true
}

Write-Output '=== Test-RepositoryStructure ==='
foreach ($r in $results) {
    $status = if ($r.Pass) { 'PASS' } else { 'FAIL' }
    if ($r.Details) {
        Write-Output "[$status] $($r.Name) -> $($r.Details)"
    } else {
        Write-Output "[$status] $($r.Name)"
    }
}
$failed = @($results | Where-Object { -not $_.Pass }).Count
Write-Output ''
Write-Output "Resultado: $($results.Count - $failed) passaram, $failed falharam."
if ($failed -gt 0) { exit 1 } else { exit 0 }

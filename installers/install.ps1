#!/usr/bin/env pwsh
<#
.SYNOPSIS
    把一条破甲条目注入到客户端的配置文件（AGENTS.md / CLAUDE.md / .cursorrules 等）。

.DESCRIPTION
    托管区块格式（与 cli/pojia.py 完全一致，两边可混用）：

        <!-- pojia:begin <id> -->
        <正文>
        <!-- pojia:end <id> -->

    写入前自动备份到 .pojia/backups/<时间戳>/，卸载时逐字还原。

.PARAMETER Id
    条目 id，例如 gpt-5.6-identity-frame。见 docs/index.json。

.PARAMETER Client
    codex | claude-code | cursor | dsh | zcode | antigravity | opencode | api | all

.PARAMETER Target
    直接指定目标文件，覆盖 -Client 的默认映射。

.PARAMETER Uninstall
    移除该条目的托管区块。

.PARAMETER DryRun
    只打印将要做什么，不写文件。

.PARAMETER Source
    正文来源：本地仓库根目录（含 docs/prompts/），或一个 raw 基地址。
    缺省先找本地，再回落到 GitHub raw。

.EXAMPLE
    pwsh -File installers/install.ps1 -Id glm-5.3-identity-frame -Client codex

.EXAMPLE
    pwsh -File installers/install.ps1 -Id glm-5.3-identity-frame -Client codex -Uninstall
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Id,
    [string]$Client = '',
    [string]$Target = '',
    [switch]$Uninstall,
    [switch]$DryRun,
    [string]$Source = ''
)

$ErrorActionPreference = 'Stop'
trap {
    Write-Host ("错误: {0}" -f $_.Exception.Message) -ForegroundColor Red
    exit 1
}
$RepoSlug = 'Baimuking/AI-Jailbreak'
$RawBaseDefault = "https://raw.githubusercontent.com/$RepoSlug/main"

$ClientMap = @{
    'codex'       = 'AGENTS.md'
    'dsh'         = 'AGENTS.md'
    'zcode'       = 'AGENTS.md'
    'antigravity' = 'AGENTS.md'
    'opencode'    = 'AGENTS.md'
    'all'         = 'AGENTS.md'
    'claude-code' = 'CLAUDE.md'
    'cursor'      = '.cursorrules'
    'api'         = '.pojia/system-prompt.md'
}

function Resolve-TargetPath {
    param([string]$Client, [string]$Target)
    if ($Target) { return [System.IO.Path]::GetFullPath($Target) }
    if (-not $Client) { throw '需要 -Client 或 -Target 之一' }
    $leaf = $ClientMap[$Client]
    if (-not $leaf) {
        throw ("未知客户端 '{0}'，可选：{1}" -f $Client, (($ClientMap.Keys | Sort-Object) -join ', '))
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $leaf))
}

function Get-PromptText {
    param([string]$Id, [string]$Source)

    $bases = @()
    if ($Source) { $bases += $Source }

    # 1) 本地仓库：脚本所在目录的上一级
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $local = Join-Path $repoRoot "docs/prompts/$Id.txt"
    if (Test-Path -LiteralPath $local) {
        return (Get-Content -LiteralPath $local -Raw -Encoding utf8)
    }
    # 2) 当前目录下也可能就是仓库根
    $local2 = Join-Path (Get-Location).Path "docs/prompts/$Id.txt"
    if (Test-Path -LiteralPath $local2) {
        return (Get-Content -LiteralPath $local2 -Raw -Encoding utf8)
    }
    # 3) 远端
    $bases += $RawBaseDefault
    foreach ($base in $bases) {
        if (-not $base) { continue }
        $url = ($base.TrimEnd('/')) + "/docs/prompts/$Id.txt"
        try {
            Write-Verbose "下载 $url"
            return (Invoke-RestMethod -Uri $url -UseBasicParsing -TimeoutSec 30)
        } catch {
            Write-Verbose "拉取失败：$url"
        }
    }
    throw "找不到条目 '$Id' 的正文。已尝试本地 docs/prompts/$Id.txt 与 $RawBaseDefault。"
}

function Remove-ManagedBlock {
    param([string]$Text, [string]$Id)
    $pattern = "(?s)\r?\n?<!-- pojia:begin $([regex]::Escape($Id)) -->.*?<!-- pojia:end $([regex]::Escape($Id)) -->\r?\n?"
    return [regex]::Replace($Text, $pattern, "`n")
}

function Test-HasBlock {
    param([string]$Text, [string]$Id)
    return $Text.Contains("<!-- pojia:begin $Id -->")
}

# ---- 主流程 ----
$targetPath = Resolve-TargetPath -Client $Client -Target $Target
$targetDir = Split-Path -Parent $targetPath
Write-Host "条目 : $Id"
Write-Host "目标 : $targetPath"

if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Host '目标文件不存在，无需卸载。'
        exit 0
    }
    $text = Get-Content -LiteralPath $targetPath -Raw -Encoding utf8
    if (-not (Test-HasBlock -Text $text -Id $Id)) {
        Write-Host "目标文件中没有 '$Id' 的托管区块。"
        exit 0
    }
    $new = Remove-ManagedBlock -Text $text -Id $Id
    if ($DryRun) {
        Write-Host '[dry-run] 将移除托管区块（内容略）'
        exit 0
    }
    $backup = Join-Path (Get-Location).Path ('.pojia/backups/' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Path $backup -Force | Out-Null
    Copy-Item -LiteralPath $targetPath -Destination (Join-Path $backup ([IO.Path]::GetFileName($targetPath))) -Force
    [System.IO.File]::WriteAllText($targetPath, $new, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "已卸载。备份：$backup"
    exit 0
}

$prompt = Get-PromptText -Id $Id -Source $Source
if (-not $prompt -or -not $prompt.Trim()) { throw "条目 '$Id' 正文为空" }

$block = @"
<!-- pojia:begin $Id -->
$($prompt.TrimEnd())
<!-- pojia:end $Id -->
"@

$existing = ''
if (Test-Path -LiteralPath $targetPath) {
    $existing = Get-Content -LiteralPath $targetPath -Raw -Encoding utf8
}

$hadBlock = Test-HasBlock -Text $existing -Id $Id
if ($hadBlock) {
    $updated = Remove-ManagedBlock -Text $existing -Id $Id
} else {
    $updated = $existing
}

if ($updated.Length -gt 0 -and -not $updated.EndsWith("`n")) { $updated += "`n" }
if ($updated.Trim().Length -gt 0) { $updated += "`n" }
$updated += $block + "`n"

if ($DryRun) {
    Write-Host '[dry-run] 将写入以下托管区块：'
    Write-Host '----------------------------------------'
    Write-Host $block
    Write-Host '----------------------------------------'
    exit 0
}

if (-not (Test-Path -LiteralPath $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }

$backupDir = Join-Path (Get-Location).Path ('.pojia/backups/' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
if (Test-Path -LiteralPath $targetPath) {
    Copy-Item -LiteralPath $targetPath -Destination (Join-Path $backupDir ([IO.Path]::GetFileName($targetPath))) -Force
}

[System.IO.File]::WriteAllText($targetPath, $updated, (New-Object System.Text.UTF8Encoding($false)))
Write-Host ("已{0}。备份：{1}" -f $(if ($hadBlock) { '更新' } else { '注入' }), $backupDir)

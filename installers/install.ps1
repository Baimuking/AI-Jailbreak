#!/usr/bin/env pwsh
<#
.SYNOPSIS
    把一条破甲条目注入到客户端的配置文件（AGENTS.md / CLAUDE.md / .cursorrules 等）。

.DESCRIPTION
    托管区块格式（与 cli/pojia.py、installers/install.sh 完全一致）：

        <!-- pojia:begin <id> -->
        <正文>
        <!-- pojia:end <id> -->

    写入前自动备份到 .pojia/backups/<时间戳>/，卸载时逐字还原。
    不需要先 clone 仓库：脚本会从 GitHub raw 拉取正文。

.PARAMETER Id
    条目 id，例如 gpt-5.6-identity-frame。见 manifest.json。

.PARAMETER Model
    目标模型，例如 glm-5.3。只给这个也行——会查 docs/route.tsv 自动挑条目。

.PARAMETER Client
    codex | claude-code | cursor | dsh | zcode | antigravity | opencode | api | all
    省略时默认 codex（即 AGENTS.md）。

.PARAMETER Target
    直接指定目标文件，覆盖 -Client 的默认映射。

.PARAMETER Uninstall
    移除该条目的托管区块。

.PARAMETER DryRun
    只打印将要做什么，不写文件。

.EXAMPLE
    pwsh -File install.ps1 -Model glm-5.3

.EXAMPLE
    pwsh -File install.ps1 -Id glm-5.3-identity-frame -Client codex

.EXAMPLE
    pwsh -File install.ps1 -Id glm-5.3-identity-frame -Client codex -Uninstall
#>
[CmdletBinding()]
param(
    [string]$Id = '',
    [string]$Model = '',
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
    if (-not $Client) { $Client = 'codex' }
    $leaf = $ClientMap[$Client]
    if (-not $leaf) {
        throw ("未知客户端 '{0}'，可选：{1}" -f $Client, (($ClientMap.Keys | Sort-Object) -join ', '))
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $leaf))
}

function Resolve-IdByModel {
    param([string]$Model)

    $text = $null
    $localRoute = Join-Path $PSScriptRoot '..\docs\route.tsv'
    if (Test-Path -LiteralPath $localRoute) {
        $text = Get-Content -LiteralPath $localRoute -Raw -Encoding utf8
    } else {
        $text = (Invoke-WebRequest -Uri "$RawBaseDefault/docs/route.tsv" -UseBasicParsing -TimeoutSec 30).Content
    }

    $table = @{}
    $fallbackId = $null
    foreach ($line in ($text -split "`r?`n")) {
        if (-not $line.Trim()) { continue }
        $parts = $line -split "`t", 2
        if ($parts.Count -lt 2) { continue }
        if ($parts[0] -eq '*') { $fallbackId = $parts[1]; continue }
        if (-not $table.ContainsKey($parts[0])) { $table[$parts[0]] = $parts[1] }
    }

    $hit = $table[$Model]
    if (-not $hit) {
        $partial = $table.Keys | Where-Object { $_ -like "*$Model*" } | Select-Object -First 1
        if ($partial) {
            Write-Host "模糊匹配: $partial"
            $hit = $table[$partial]
        }
    }
    if (-not $hit) { $hit = $fallbackId }
    return $hit
}

function Get-PromptText {
    param([string]$CardId, [string]$Source)

    # 1) 本地仓库（正常 clone 后执行）
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $local = Join-Path $repoRoot "docs/prompts/$CardId.txt"
    if (Test-Path -LiteralPath $local) {
        return (Get-Content -LiteralPath $local -Raw -Encoding utf8)
    }
    # 2) 当前目录正好是仓库根
    $local2 = Join-Path (Get-Location).Path "docs/prompts/$CardId.txt"
    if (Test-Path -LiteralPath $local2) {
        return (Get-Content -LiteralPath $local2 -Raw -Encoding utf8)
    }
    # 3) 远端（零克隆安装走这条）
    $bases = @()
    if ($Source) { $bases += $Source }
    $bases += $RawBaseDefault
    foreach ($base in $bases) {
        $url = ($base.TrimEnd('/')) + "/docs/prompts/$CardId.txt"
        try {
            Write-Verbose "下载 $url"
            return (Invoke-RestMethod -Uri $url -UseBasicParsing -TimeoutSec 30)
        } catch {
            Write-Verbose "拉取失败：$url"
        }
    }
    throw "找不到条目 '$CardId' 的正文。已尝试本地 docs/prompts/$CardId.txt 与 $RawBaseDefault。"
}

function Remove-ManagedBlock {
    param([string]$Text, [string]$Id)
    # 与其他两个实现一致：移除区块后把尾随换行归一化成一个，保证逐字节还原
    $pattern = "(?s)\r?\n?<!-- pojia:begin $([regex]::Escape($Id)) -->.*?<!-- pojia:end $([regex]::Escape($Id)) -->\r?\n?"
    $out = [regex]::Replace($Text, $pattern, "")
    $out = $out -replace "[\r\n]+$", ""
    if ($out.Trim().Length -gt 0) { return $out + "`n" }
    return ""
}

function Test-HasBlock {
    param([string]$Text, [string]$Id)
    return $Text.Contains("<!-- pojia:begin $Id -->")
}

function Get-BackupDir {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmssfff'
    $dir = Join-Path (Get-Location).Path ('.pojia/backups/' + $stamp)
    $n = 1
    while (Test-Path -LiteralPath $dir) {
        $n++
        $dir = Join-Path (Get-Location).Path ('.pojia/backups/' + $stamp + "-$n")
    }
    return $dir
}

function Test-HasBom {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $fs = [System.IO.File]::OpenRead($Path)
    try {
        $buf = New-Object byte[] 3
        $n = $fs.Read($buf, 0, 3)
        return ($n -eq 3 -and $buf[0] -eq 0xEF -and $buf[1] -eq 0xBB -and $buf[2] -eq 0xBF)
    } finally {
        $fs.Close()
    }
}

function Write-Utf8Text {
    param([string]$Path, [string]$Content, [bool]$Bom = $false)
    $enc = New-Object System.Text.UTF8Encoding($Bom)
    [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

# ---- 主流程 ----

# 只给 -Model 时自动挑条目
if (-not $Id) {
    if (-not $Model) {
        throw '需要 -Id <条目> 或 -Model <模型> 之一。条目列表见 manifest.json。'
    }
    Write-Host "按模型 '$Model' 自动挑选条目…"
    $Id = Resolve-IdByModel -Model $Model
    if (-not $Id) { throw "找不到适配 '$Model' 的条目" }
    Write-Host "选中: $Id"
}

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
    $hadBom = Test-HasBom -Path $targetPath
    if ($DryRun) {
        Write-Host '[dry-run] 将移除托管区块'
        exit 0
    }
    $backup = Get-BackupDir
    New-Item -ItemType Directory -Path $backup -Force | Out-Null
    Copy-Item -LiteralPath $targetPath -Destination (Join-Path $backup ([IO.Path]::GetFileName($targetPath))) -Force
    Write-Utf8Text -Path $targetPath -Content $new -Bom $hadBom
    Write-Host "已卸载。备份：$backup"
    exit 0
}

$prompt = Get-PromptText -CardId $Id -Source $Source
if (-not $prompt -or -not $prompt.Trim()) { throw "条目 '$Id' 正文为空" }

$block = @"
<!-- pojia:begin $Id -->
$($prompt.TrimEnd())
<!-- pojia:end $Id -->
"@

$existing = ''
$hadBom = Test-HasBom -Path $targetPath
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

$backupDir = Get-BackupDir
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
if (Test-Path -LiteralPath $targetPath) {
    Copy-Item -LiteralPath $targetPath -Destination (Join-Path $backupDir ([IO.Path]::GetFileName($targetPath))) -Force
}

Write-Utf8Text -Path $targetPath -Content $updated -Bom $hadBom
$effectiveClient = if ($Client) { $Client } else { 'codex' }
Write-Host ("已{0}。备份：{1}" -f $(if ($hadBlock) { '更新' } else { '注入' }), $backupDir)
Write-Host "回滚: pwsh -File installers/install.ps1 -Id $Id -Client $effectiveClient -Uninstall"

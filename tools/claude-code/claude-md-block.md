---
id: claude-md-block
name: Claude Code / CLAUDE.md 注入
kind: tool
category: A
summary: 写入项目根 CLAUDE.md，Claude Code 每次启动自动加载，支持多条目叠加与逐条卸载。
notes: |
  Claude Code 读取 CLAUDE.md（项目级）与 ~/.claude/CLAUDE.md（用户级）。
  本工具默认写项目级，避免污染你所有项目。
  Claude 对「上下文里的指令」与「用户消息」的权重不同，放 CLAUDE.md 比每次粘贴进对话更稳。
targets: [claude, claude-sonnet, claude-opus]
clients: [claude-code]
archetype: client-patch
strength: null
status: unverified
language: zh
verified:
  date: null
  asr: null
  notes: null
usage:
  type: agents-md
  install: pwsh -File installers/install.ps1 -Id claude-ctf-mode -Client claude-code
  uninstall: pwsh -File installers/install.ps1 -Id claude-ctf-mode -Client claude-code -Uninstall
source:
  repo: null
  path: null
  commit: null
  license: MIT
  url: null
added: 2026-10-17
updated: 2026-10-17
tags: [claude-code, claude-md, injection]
---

# Claude Code / CLAUDE.md

## 加载顺序

| 层级 | 路径 | 用途 |
|---|---|---|
| 用户级 | `~/.claude/CLAUDE.md` | 所有项目共享 |
| 项目级 | `<项目根>/CLAUDE.md` | 本项目 |
| 子目录 | `<子目录>/CLAUDE.md` | 该子树覆盖上层 |

本工具默认写**项目级**。要写用户级，用 `-Target`：

```powershell
pwsh -File installers/install.ps1 -Id claude-ctf-mode -Target "$env:USERPROFILE\.claude\CLAUDE.md"
```

## 常用命令

```powershell
# 注入
pwsh -File installers/install.ps1 -Id claude-ctf-mode -Client claude-code

# 预览
pwsh -File installers/install.ps1 -Id claude-ctf-mode -Client claude-code -DryRun

# 卸载
pwsh -File installers/install.ps1 -Id claude-ctf-mode -Client claude-code -Uninstall
```

## 与 `/clear` 的关系

`CLAUDE.md` 在**每次会话建立时**重新加载，所以 `/clear` 之后条目依然生效；
但会话内被压缩掉的部分不会自动恢复——长会话建议每 8 轮左右重新 `apply` 一次（同样幂等）。

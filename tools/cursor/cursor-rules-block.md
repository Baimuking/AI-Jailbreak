---
id: cursor-rules-block
name: Cursor / .cursorrules 注入
kind: tool
category: A
summary: 写入项目根 .cursorrules（或新版 .cursor/rules/*.mdc），Cursor 对话自动携带。
notes: |
  Cursor 旧版读 .cursorrules，新版读 .cursor/rules/ 下的 .mdc 文件。
  本工具默认写 .cursorrules（两种版本都兼容读取），需要新版可用 -Target 指定 mdc 路径。
  注意：Cursor 的上下文窗口有限，多个条目叠加会挤掉代码上下文，建议一次最多 2 条。
targets: [claude, gpt-5.6, gemini-3.8, all]
clients: [cursor]
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
  install: pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client cursor
  uninstall: pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client cursor -Uninstall
source:
  repo: null
  path: null
  commit: null
  license: MIT
  url: null
added: 2026-10-17
updated: 2026-10-17
tags: [cursor, rules, injection]
---

# Cursor / .cursorrules

## 两种文件

| 版本 | 路径 | 说明 |
|---|---|---|
| 旧 | `<项目根>/.cursorrules` | 单文件，最简单 |
| 新 | `<项目根>/.cursor/rules/<name>.mdc` | 支持 front matter 与 glob 作用域 |

默认写旧版（新版客户端仍会读取）。

```powershell
# 旧版
pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client cursor

# 新版
pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Target ".cursor/rules/pojia.mdc"
```

## 上下文预算

`.cursorrules` 的内容每一轮都进上下文。经验值：

- 单条正文 ≤ 1200 字，多于此建议改用 `lightweight` 形态的条目
- 同时启用不超过 2 条
- 代码相关的规则放前面，破甲帧放最后（减少被截断概率）

## 卸载

```powershell
pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client cursor -Uninstall
```

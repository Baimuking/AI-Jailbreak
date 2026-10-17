---
id: dsh-preset-block
name: DeepSeek Harness / preset 注入
kind: tool
category: A
summary: 写入工作区 AGENTS.md 让 DSH 每次会话自动加载；JSON preset 需手动合并（见下）。
notes: |
  DSH 的 preset 是 JSON 目录，工具不直接改 JSON（容易破坏结构），
  推荐路径是 AGENTS.md —— DSH 同样读取它。
  要改 preset，请用 DSH 自带的预设编辑器，或把本工具生成的区块粘贴进 preset 的
  systemPrompt 字段。
targets: [deepseek-v4.1, deepseek-v4.1-flash, glm-5.3, all]
clients: [dsh]
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
  install: pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client dsh
  uninstall: pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client dsh -Uninstall
source:
  repo: null
  path: null
  commit: null
  license: MIT
  url: null
added: 2026-10-17
updated: 2026-10-17
tags: [dsh, preset, agents-md]
---

# DeepSeek Harness / preset

## 两条路径

### A. AGENTS.md（推荐，可回滚）

```powershell
pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client dsh
```

写入工作区根的 `AGENTS.md`，DSH 每次新会话自动读取。

### B. preset JSON（手动，影响面更大）

preset 一旦改坏会连会话都启不来，所以本仓库的工具**不碰 JSON**。做法是：

1. `python cli/pojia.py show deepseek-v4.1-three-layer --prompt-only > body.txt`
2. 打开 DSH 的 preset 编辑器，把 `body.txt` 内容追加到目标 preset 的 `systemPrompt`
3. 保存后重启会话

## 回滚

```powershell
pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client dsh -Uninstall
```

区块移除后文件其余内容逐字保留。

## 冲突提示

若你同时装了别的破甲插件（例如 `dsh-purge` 系列），它们可能也改 `AGENTS.md`。
两边的区块互不覆盖（各自有独立 begin/end 标记），但**语义上可能互相冲突**——
建议一次只启用一套，用 `pojia list --client dsh` 记录当前启用了哪些。

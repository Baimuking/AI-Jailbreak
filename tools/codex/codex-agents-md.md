---
id: codex-agents-md
name: Codex / AGENTS.md 注入
kind: tool
category: A
summary: 把条目写进项目根的 AGENTS.md，Codex 每次会话自动读取，无需手工粘贴。
notes: |
  Codex Desktop / Codex CLI 都会在启动时读取工作区 AGENTS.md（子目录里也可放一份覆盖上层）。
  托管区块用注释包裹，因此不会污染正文可读性，卸载能逐字还原。
  顺序会影响效果：Codex 对文件靠前的内容权重更高，把身份帧放最前。
targets: [gpt-5.6, gpt-5.6-codex, gpt6-astra, codex]
clients: [codex]
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
  install: pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client codex
  uninstall: pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client codex -Uninstall
source:
  repo: null
  path: null
  commit: null
  license: MIT
  url: null
added: 2026-10-17
updated: 2026-10-17
tags: [codex, agents-md, injection]
---

# Codex / AGENTS.md

## 原理

Codex 启动会话时按「工作区根 → 子目录」的顺序加载 `AGENTS.md`，拼接成系统提示。
因此只要把条目写进这个文件，它在**每一次新会话**里都自动生效，不依赖用户记性。

## 用法

```powershell
# 注入（自动备份）
pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client codex

# 先看看会写什么
pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client codex -DryRun

# 卸载
pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client codex -Uninstall
```

或用 Python CLI（与安装器共用同一区块格式）：

```bash
python cli/pojia.py apply gpt-5.6-identity-frame --client codex
python cli/pojia.py rollback gpt-5.6-identity-frame --client codex
```

## 写入结果

```markdown
<!-- pojia:begin gpt-5.6-identity-frame -->
（条目正文）
<!-- pojia:end gpt-5.6-identity-frame -->
```

## 注意事项

- 多个条目可以叠加，区块各自独立，顺序即叠加顺序。
- 备份在 `.pojia/backups/<时间戳>/`，建议把 `.pojia/` 加进 `.gitignore`（本仓库已加）。
- 升级 Codex 后若 AGENTS.md 被覆盖，重新跑一次注入即可；条目本身不受影响。

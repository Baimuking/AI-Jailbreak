---
id: managed-block-spec
name: 托管区块规范
kind: technique
category: Z
summary: 安装器与 CLI 共用的幂等注入格式，保证跨工具可识别、可逐字卸载、可多条目共存。
notes: |
  这是本仓库所有注入行为的唯一契约。三个实现（install.ps1 / install.sh / pojia.py）
  必须严格一致，否则会出现"用 A 装的用 B 卸不掉"。
targets: [all]
clients: [all]
archetype: methodology
strength: null
status: unverified
language: zh
verified:
  date: null
  asr: null
  notes: null
usage:
  type: doc
  install: null
  uninstall: null
source:
  repo: null
  path: null
  commit: null
  license: MIT
  url: null
added: 2026-10-17
updated: 2026-10-17
tags: [spec, installer, idempotent]
---

# 托管区块规范 v1

## 格式

```text
<!-- pojia:begin <id> -->
<条目正文，逐字>
<!-- pojia:end <id> -->
```

## 规则

1. **幂等**：同一 id 重复注入，只保留一个区块（旧区块先移除，再在文件末尾追加）。
2. **独立**：不同 id 的区块互不影响，可以共存；顺序即叠加顺序。
3. **可逐字还原**：移除区块时，区块外的内容一个字节都不改。
4. **不嵌套**：正文里不得包含 `<!-- pojia:begin` 或 `<!-- pojia:end`。
5. **UTF-8 无 BOM**，行尾 LF。

## 为什么用 HTML 注释

| 候选 | 问题 |
|---|---|
| 自定义前缀行（`# POJIA-BEGIN`） | 在 markdown 里会变成可见标题，干扰阅读 |
| 专用文件 | 客户端不会加载多个文件，等于没注入 |
| JSON 字段 | 改结构风险高，且不适用于 .md 类客户端 |

HTML 注释在 markdown / .cursorrules / 纯文本里都不可见，且不会被模型当成指令。

## 参考实现

- PowerShell：[installers/install.ps1](installers/install.ps1)
- Bash：[installers/install.sh](installers/install.sh)
- Python：[cli/pojia.py](cli/pojia.py)

三者对 `Remove-ManagedBlock` / `strip_block` 的行为做了同样的语义：
`\n?<!-- begin -->.*?<!-- end -->\n?` → `\n`，非贪婪，跨行。

## 测试约定

CI 会对三份实现跑同一组用例：

1. 空文件注入 → 只有区块
2. 有内容文件注入 → 原内容 + 空行 + 区块
3. 重复注入 → 仍只有一个区块
4. 卸载 → 与原内容逐字相等

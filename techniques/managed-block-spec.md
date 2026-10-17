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
3. **可还原**：移除区块后，区块外内容逐字保留；末尾的连续空行归一化成一个换行，
   文件为空时不写换行。实测：以单个 `\n` 结尾的文件（编辑器新建的默认情况）可做到**逐字节还原**。
4. **不嵌套**：正文里不得包含 `<!-- pojia:begin` 或 `<!-- pojia:end`。
5. **编码**：写入 UTF-8；原文件有 BOM 则保留 BOM，没有则不添加。
6. **行尾**：写入 LF。原本是 CRLF 的文件在安装后会被规整为 LF——这一点在三份实现里一致，
   也是「原本以 CRLF 结尾的文件无法逐字节还原」的唯一原因。
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
2. 有内容文件注入 → 原内容 + 一个空行 + 区块
3. 重复注入 → 仍只有一个区块
4. 卸载 → 与原内容逐字节相等（原文件以单个 `\n` 结尾时）
5. 带 BOM 的文件 → 注入与卸载后 BOM 仍在

---
id: api-system-prompt
name: API 直连 / system 消息注入
kind: tool
category: A
summary: 生成纯正文到 .pojia/system-prompt.md，供 OpenAI 兼容接口的 system 字段直接读取。
notes: |
  直连 API 时没有文件探测机制，只能自己把正文放进 messages 的第一条 system。
  本工具把正文导出成一个稳定的文件路径，方便脚本 read 后拼接，避免每次从 markdown 里抠正文。
targets: [all]
clients: [api]
archetype: client-patch
strength: null
status: unverified
language: zh
verified:
  date: null
  asr: null
  notes: null
usage:
  type: api
  install: pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client api
  uninstall: pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client api -Uninstall
source:
  repo: null
  path: null
  commit: null
  license: MIT
  url: null
added: 2026-10-17
updated: 2026-10-17
tags: [api, system-prompt, openai-compatible]
---

# API 直连 / system 消息

## 导出正文

```powershell
pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client api
# => 写入 .pojia/system-prompt.md
```

或直接取纯正文（不经过托管区块）：

```bash
python cli/pojia.py show deepseek-v4.1-three-layer --prompt-only > system.txt
```

## Python 调用示例

```python
import pathlib
from openai import OpenAI

system = pathlib.Path(".pojia/system-prompt.md").read_text(encoding="utf-8")
client = OpenAI(base_url="https://api.deepseek.com", api_key="...")

resp = client.chat.completions.create(
    model="deepseek-v4.1",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": "..."},
    ],
)
```

## 注意事项

1. **别把正文塞进 user 消息** —— 多数模型的 system 权重高于 user，放错位置效果差别很大。
2. 有些中转站会过滤 system 字段，遇到时先请求 `/models` 确认实际后端。
3. 多轮对话中 system 只在开头出现一次；若模型在中途漂移，可以再插一条
   `{"role": "system", "content": "<第 0 节 + 第 6 节>"}` 做重锚定。

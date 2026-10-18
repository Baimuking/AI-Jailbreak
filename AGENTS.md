# AGENTS.md — 给 AI agent 的使用说明

你在 `Baimuking/AI-Jailbreak`：全网最全的 AI 破甲合集，支持所有模型的破甲，
并**允许你代替用户安装和使用**对应的破甲。

## 什么时候用

用户说「给我的 <客户端> 装个 <模型> 的破甲」「这个模型老是拒答」「帮我破甲」时，
按下面的流程做，不要让用户自己去翻文件。

## 三步流程

```bash
# 知道模型就够，不用记 id、不用指定客户端
python cli/pojia.py apply --model <模型>

# 不确定装什么时走向导（两个问题）
python cli/pojia.py install

# 装完检查 / 回滚
python cli/pojia.py status
python cli/pojia.py rollback <id>
```

用户没装 Python 或不想 clone 时，直接给他一行命令（零依赖，会自动下载正文）：

```text
Windows: $s="$env:TEMP\pojia.ps1"; irm https://raw.githubusercontent.com/Baimuking/AI-Jailbreak/main/installers/install.ps1 -OutFile $s; pwsh -File $s -Model <模型>
Unix:    curl -fsSL https://raw.githubusercontent.com/Baimuking/AI-Jailbreak/main/installers/install.sh | bash -s -- --model <模型>
```

没有 Python 时用安装器，二者共用同一套托管区块格式：

```bash
pwsh -File installers/install.ps1 -Id <id> -Client <客户端>     # Windows
bash installers/install.sh --id <id> --client <客户端>           # macOS / Linux
```

## 选择规则

1. `targets` 命中用户模型 > `targets` 含 `all` > 不选。
2. `kind: prompt` 才能 `apply`；`tool` / `technique` 是文档，读给用户听即可。
3. 同一客户端同时只启用 1–2 条，多了会挤占上下文。
4. 用户没说客户端时，按目标推断：Codex→`codex`，Claude Code→`claude-code`，Cursor→`cursor`，API 直连→`api`。

## 当前可用卡片

| id | 目标模型 | 客户端 | 形态 | 状态 |
|---|---|---|---|---|
| `all-translation-frame` | all | all | translation | unverified |
| `claude-ctf-mode` | claude, claude-sonnet, claude-opus | claude-code, api, chat | ctf | unverified |
| `deepseek-v4.1-three-layer` | deepseek-v4.1, deepseek-v4.1-flash, deepseek-chat | api, dsh, chat | hybrid-frame | unverified |
| `gemini-narrative-frame` | gemini-3.8, gemini-3.5-flash, gemini-pro | antigravity, api, chat | narrative | unverified |
| `glm-5.3-identity-frame` | glm-5.3, glm-5.3-flash, glm-5.3-air | zcode, codex, dsh, api | identity-frame | unverified |
| `gpt-5.6-identity-frame` | gpt-5.6, gpt-5.6-codex, gpt6-astra | codex, api, dsh | identity-frame | unverified |
| `grok-hybrid-frame` | grok-4.7, grok-4.6, grok-build | api, chat | lightweight | unverified |
| `kimi-ctf-mode` | kimi, kimi-code, moonshot-v1 | api, codex, chat | ctf | unverified |
| `qwen-local-frame` | qwen3.6, llama, gemma-4, gpt-oss-20b | api, chat | lightweight | unverified |
| `universal-max-chain` | all | all | hybrid-frame | unverified |

支持的客户端：`antigravity`, `api`, `chat`, `claude-code`, `codex`, `cursor`, `dsh`, `zcode`。

## 硬规则

- **不要编造 `strength`**。为空就是没实测过，如实告诉用户。
- 安装前先 `--dry-run` 或 `show` 让用户看到将要写入的内容。
- 卸载用 `rollback` / `-Uninstall`，不要手工删区块。
- 不要改写卡片文件里的 `source` 字段——那是上游署名。

## 机器可读接口

- `manifest.json`：全部卡片 + 安装命令 + 覆盖范围
- `llms.txt`：本仓库的入口摘要
- `docs/prompts/<id>.txt`：纯正文，可直接读入
- `docs/index.json`：含正文全文与 1733 个上游仓库

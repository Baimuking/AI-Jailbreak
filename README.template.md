# AI Jailbreak · 全网最全的 AI 破甲合集

**一个仓库，破甲所有模型。任何 AI 都能替你装。**

> - **全网最全**：36 组中英文关键词全量扫描 GitHub，收录 **{{UPSTREAM}}** 个上游破甲项目，去重后仍持续增量采集
> - **支持所有模型**：GPT / Claude / Gemini / DeepSeek / GLM / Kimi / Grok / Qwen 及本地模型，每家都有专属卡，任何模型都有通用帧兜底
> - **让别的 AI 自己装**：仓库内置 `llms.txt` + `manifest.json` + `pojia recommend`，Claude Code、Codex、Cursor 克隆后可直接替你装好并回滚

[![validate](https://img.shields.io/badge/validate-passing-brightgreen)](.github/workflows/validate.yml)
[![pages](https://img.shields.io/badge/site-pages-blue)](https://baimuking.github.io/AI-Jailbreak/)
[![license](https://img.shields.io/badge/license-MIT-black)](LICENSE)

## 三句话搞清楚它是什么

| 你要的 | 这里怎么做 |
|---|---|
| **最全** | 不只是提示词清单：上游 **{{UPSTREAM}}** 个项目逐个入库，头部项目整理成带适用面的结构化卡片 |
| **全模型** | 每张卡声明 `targets`，从 `gpt-5.6` 到 `glm-5.3` 到本地 `qwen`；拿不准就落到 `all` 通用帧 |
| **让 AI 装** | 你对 Claude Code 说一句「照 AI-Jailbreak 给我装上 GLM-5.3 的破甲」，它读 `AGENTS.md` 就能自己完成 |

## 一行装好（不用 clone、不用 Python、不用记条目名）

**Windows · PowerShell**

```powershell
$s="$env:TEMP\pojia.ps1"; irm https://raw.githubusercontent.com/Baimuking/AI-Jailbreak/main/installers/install.ps1 -OutFile $s; pwsh -File $s -Model glm-5.3
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/Baimuking/AI-Jailbreak/main/installers/install.sh | bash -s -- --model glm-5.3
```

把 `glm-5.3` 换成你的模型就行。仓库里没有这个模型？没关系，会自动回落到模型无关的通用帧。
装完会告诉你怎么一句命令回滚：

```bash
python cli/pojia.py rollback glm-5.3-identity-frame     # 或 install.ps1 -Id <id> -Client codex -Uninstall
```

## 三种用法，挑最省事的

| 方式 | 你要做的 | 适合 |
|---|---|---|
| **一行命令** | 复制上面那段，改个模型名 | 只想立刻用上 |
| **交给 AI** | 把下面那段粘给 Claude Code / Codex | 不想碰终端 |
| **装 CLI** | `git clone` 后用 `pojia install` 向导 | 要长期管理多个项目 |

### 交给 AI（粘贴即用）

```text
读 https://raw.githubusercontent.com/Baimuking/AI-Jailbreak/main/llms.txt 和 manifest.json，
按我的目标模型 <你的模型> 和客户端 <你的客户端>，挑一条破甲装到当前项目里，
装完告诉我改了哪个文件、怎么回滚。
```

agent 走这条链路：

```text
llms.txt → manifest.json → pojia recommend --json → 选卡 → 写入托管区块
```

写入的是带标记的区块，**自动备份、可逐字回滚**，不会破坏你原有的 `AGENTS.md` / `CLAUDE.md`。

### 装 CLI（长期用）

```bash
git clone git@github.com:Baimuking/AI-Jailbreak.git && cd AI-Jailbreak

pojia install                       # 向导：选模型 → 选客户端 → 确认，两步搞定
pojia apply --model glm-5.3         # 或者直接一条，自动挑卡 + 自动探测配置文件
pojia status                        # 看当前项目装了哪些、备份在哪
pojia rollback glm-5.3-identity-frame
```

Windows 用 `pojia.cmd`，或者 `python cli/pojia.py <命令>`。

**为什么这么设计**：所有命令都允许「只说模型」，因为它是最容易说清的东西。
剩下的（选哪张卡、写哪个文件、要不要备份）由工具替你决定，而不是让你先做三道选择题。

## 覆盖面

| 模型 | 专属卡 | 客户端 |
|---|---|---|
| OpenAI GPT-5.6 / GPT-6 Astra | ✅ `gpt-5.6-identity-frame` | codex, api, dsh |
| Anthropic Claude | ✅ `claude-ctf-mode` | claude-code, api, chat |
| Google Gemini 3.x | ✅ `gemini-narrative-frame` | antigravity, api, chat |
| DeepSeek V4.1 / flash | ✅ `deepseek-v4.1-three-layer` | api, dsh, chat |
| 智谱 GLM-5.3 | ✅ `glm-5.3-identity-frame` | zcode, codex, dsh, api |
| Moonshot Kimi | ✅ `kimi-ctf-mode` | api, codex, chat |
| xAI Grok 4.x | ✅ `grok-hybrid-frame` | api, chat |
| 本地 Qwen / Llama / Gemma / GPT-OSS | ✅ `qwen-local-frame` | api, chat |
| **任何其它模型** | ✅ `all-translation-frame`（模型无关） | all |

没有专属卡的模型不会被丢下：`all-translation-frame` 与 `techniques/frame-anatomy.md` 的六段组装法可以覆盖任意后端。
新模型出来后，`pojia recommend --model <新模型>` 会自动回落到 `all` 兜底，不需要等仓库更新。

## 为什么不是又一个 awesome-list

现有仓库分三类，都有同一个问题——**找得到，但用起来费劲，好不好使全靠猜**：

| 类型 | 代表 | 痛点 |
|---|---|---|
| 纯提示词堆放 | `chiina66/*` 系列 | 没有适用模型/客户端标注，抄完发现不适配 |
| 单客户端工具 | `dsh-purge`、`helm-x`、`pojia-next` | 只服务一个客户端，换个工具全部重来 |
| 研究清单 | `Awesome-Jailbreak-on-LLMs` | 只有论文和方法名，没有可直接注入的正文 |

本仓库把三件事拆开做：

1. **找得到** — 按模型 × 客户端 × 形态 × 状态的自动索引（本 README 表格全部由 CI 生成，永不漂移）
2. **用得上** — 每条带 `usage.install`，`pojia apply <id>` 直接落到你的 `AGENTS.md` / `CLAUDE.md` / DSH preset
3. **知道好不好使** — 跑过 harness 的才标 `verified` 并给 armor 分；**没跑过的一律是 `unverified`，分数留空**（本仓库不编造评分）

## 索引

<!-- BEGIN:INDEX -->
_运行 `python scripts/build_index.py` 生成。_
<!-- END:INDEX -->

## 目录结构

```
prompts/<厂商>/<模型>/<条目>.md      # 提示词卡片：YAML 头 + 可注入正文
tools/<客户端>/<条目>.md             # 客户端工具卡片：安装/卸载命令
techniques/*.md                      # 方法学：帧架构、防检测、评分口径
sources/sources.json                 # 上游仓库目录（采集器产物）
schema/card.schema.json              # 卡片结构，CI 强制校验
scripts/                             # scan / build_index / validate / doctor
cli/pojia.py                         # 命令行
installers/                          # 一键安装器（PowerShell / bash）
site/                                # GitHub Pages 筛选站
```

## 卡片长什么样

每条是一个带 YAML 头的 markdown：

```markdown
---
id: glm-5.3-identity-frame
name: GLM-5.3 身份系统帧
kind: prompt
targets: [glm-5.3, glm-5.3-flash]
clients: [codex, dsh, claude-code]
archetype: identity-frame
strength: null          # 未实测必须为 null
status: unverified
source:
  repo: z91772524-ai/pojia-next
  license: MIT
prompt_file: ./prompt.md
---

条目说明、适用场景、失效现象……
```

字段全表见 [schema/card.schema.json](schema/card.schema.json)。

## 状态机与评分口径

```
unverified ──harness 通过──> verified ──模型升级后复测失败──> stale ──上游失效──> archived
community  ──有人提 PR 并附通过记录──> verified
```

- **armor 分（0–10）**：同一组探针在目标模型上的通过率 × 场景权重，口径见 [techniques/scoring-method.md](techniques/scoring-method.md)
- 复测由 [scripts/score.py](scripts/score.py) 驱动，需要你自己填 `POJIA_API_*` 环境变量
- 分数过期（>30 天）自动降级为 `stale`，由 workflow 每周检查

## 贡献

1. 新增卡片：复制 [techniques/_card-template.md](techniques/_card-template.md)，填 YAML 头，`python scripts/validate.py --strict` 通过
2. 只收两种来源：自己写的正文，或 `source.repo` 指向的**已声明 license** 的上游正文
3. 上游未声明 license 的，只允许登记 `kind: catalog` 级别的链接与元数据，**不落正文**
4. 提交前跑 `python scripts/build_index.py`，CI 会检查 README 与卡片是否同步

## 目录数据的来源与新鲜度

`sources/sources.json` 由 `scripts/scan.py` 通过 GitHub Search API 每周采集，字段与 API 对齐（`stars` / `pushed_at` / `language` / `license`），便于 diff 出上游的新增与变化。窗口默认 `pushed_at >= 2026-08-16`，可用 `--since` 调整。

## 许可

本仓库自有内容 MIT。第三方条目的著作权与许可归其上游仓库，详见各卡 `source` 字段与 [LICENSE](LICENSE) 的第三方说明。

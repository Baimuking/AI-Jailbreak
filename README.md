# AI Jailbreak · 全网最全的 AI 破甲合集

**一个仓库，破甲所有模型。任何 AI 都能替你装。**

> - **全网最全**：36 组中英文关键词全量扫描 GitHub，收录 **1,815** 个上游破甲项目，去重后仍持续增量采集
> - **支持所有模型**：GPT / Claude / Gemini / DeepSeek / GLM / Kimi / Grok / Qwen 及本地模型，每家都有专属卡，任何模型都有通用帧兜底
> - **让别的 AI 自己装**：仓库内置 `llms.txt` + `manifest.json` + `pojia recommend`，Claude Code、Codex、Cursor 克隆后可直接替你装好并回滚

[![validate](https://img.shields.io/badge/validate-passing-brightgreen)](.github/workflows/validate.yml)
[![pages](https://img.shields.io/badge/site-pages-blue)](https://baimuking.github.io/AI-Jailbreak/)
[![license](https://img.shields.io/badge/license-MIT-black)](LICENSE)

## 三句话搞清楚它是什么

| 你要的 | 这里怎么做 |
|---|---|
| **最全** | 不只是提示词清单：上游 **1,815** 个项目逐个入库，头部项目整理成带适用面的结构化卡片 |
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

## 成功率最高的那条是哪条

仓库里有两个指标，**别混看**：

| 指标 | 怎么来 | 能回答什么 |
|---|---|---|
| **结构分** `quality` | 读文本结构算（权重公开，见 [success-rate.md](techniques/success-rate.md)） | 这条破甲六段结构写齐了没有 |
| **armor** | `scripts/score.py` 打真实模型 | 在你指定的模型上，12 条探针过了几条 |

目前**没有任何卡片跑过实测**（不编数字），所以排序用结构分。默认规则：

- **不指定模型** → `universal-max-chain`（10.0 / 10，模型无关，含失效自愈表）
- **指定了模型** → 该模型的专属卡（针对性通常强于通用帧，也更省 token）
- **宁可长也要最稳** → 显式指定通用帧：

```bash
pojia apply universal-max-chain --client codex
```

`pojia show <id>` 会打印结构分和**缺失的段落**，方便你自己补：

```
结构分=6.6/10  结构较完整，缺 1-2 段
  缺失段落: drift-check, model-hooks
```

一旦你跑过 `score.py`，实测分会在排序里接管结构分——**有数据的时候听数据，没数据的时候听结构**。

## 覆盖面

完整清单（含每个模型的专属卡、结构分、相关上游仓库数与 ★合计）在
**[docs/models.md](docs/models.md)**，站点的「按模型」视图是同一份数据的可筛选版。

当前覆盖 8 家厂商 + 本地模型：OpenAI（GPT-5.6 / GPT-6 Astra）、Anthropic Claude、
Google Gemini、DeepSeek、智谱 GLM、Moonshot Kimi、xAI Grok、本地 Qwen / Llama / Gemma / GPT-OSS。

没有专属卡的模型不会被丢下：`universal-max-chain` 是模型无关的兜底，也是结构分最高的那张。
`pojia recommend --model <新模型>` 会自动回落到它，不需要等仓库更新。

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

| 指标 | 数值 |
|---|---|
| 可用条目 | 19 |
| 其中已实测（verified） | 0 |
| 提示词 / 工具 / 方法 | 10 / 5 / 4 |
| 上游仓库目录 | 1815 |

### 按模型挑（按上游热度排序，完整版见 [docs/models.md](docs/models.md)）

| 模型 | 厂商 | 推荐卡 | 结构分 | armor | 相关仓库 | ★合计 |
|---|---|---|---|---|---|---|
| Anthropic Claude | Anthropic | [`claude-ctf-mode`](prompts/anthropic/claude/claude-ctf-mode.md) | 5.7 | — | 153 | 168,782 |
| Google Gemini 3.x | Google | [`gemini-narrative-frame`](prompts/google/gemini-3.x/gemini-narrative-frame.md) | 5.3 | — | 58 | 80,547 |
| xAI Grok 4.x | xAI | [`grok-hybrid-frame`](prompts/xai/grok-4.x/grok-hybrid-frame.md) | 4.4 | — | 16 | 51,663 |
| 任意模型（通用帧） | 模型无关 | [`universal-max-chain`](prompts/all/universal-max-chain.md) | 10.0 | — | 426 | 46,711 |
| DeepSeek V4.1 / Flash | DeepSeek | [`deepseek-v4.1-three-layer`](prompts/deepseek/v4.1/deepseek-v4.1-three-layer.md) | 5.6 | — | 107 | 37,275 |
| OpenAI GPT-5.6 / Codex | OpenAI | [`gpt-5.6-identity-frame`](prompts/openai/gpt-5.6/gpt-5.6-identity-frame.md) | 9.4 | — | 68 | 36,071 |
| OpenAI GPT-6 Astra | OpenAI | [`gpt-5.6-identity-frame`](prompts/openai/gpt-5.6/gpt-5.6-identity-frame.md) | 9.4 | — | 10 | 2,156 |
| 本地 Qwen / Llama / Gemma | 本地 / Local | [`qwen-local-frame`](prompts/local/qwen/qwen-local-frame.md) | 6.2 | — | 120 | 1,074 |
| Moonshot Kimi | Moonshot | [`kimi-ctf-mode`](prompts/moonshot/kimi/kimi-ctf-mode.md) | 6.6 | — | 3 | 210 |
| 智谱 GLM-5.3 | 智谱 / Zhipu | [`glm-5.3-identity-frame`](prompts/zhipu/glm-5.3/glm-5.3-identity-frame.md) | 9.4 | — | 13 | 151 |

`结构分`是文本结构完备度（能算）；`armor`是真实模型实测分（要跑 harness）；`★合计`是上游生态热度（不是成功率）。

### 提示词条目

按结构完备度降序。`结构分` 由 `scripts/lib/quality.py` 从文本结构算出来（权重公开、可复核）；
`armor` 是真实模型实测分，未跑过 harness 时为空。两者不是一回事，不要混看。

| 条目 | 目标模型 | 客户端 | 形态 | 状态 | 结构分 | armor | 来源 |
|---|---|---|---|---|---|---|---|
| [通用最大帧（全模型兜底·结构最全）](prompts/all/universal-max-chain.md) | `all` | all | hybrid-frame | ⚪ unverified | 10.0 | — | — |
| [GLM-5.3 身份系统帧](prompts/zhipu/glm-5.3/glm-5.3-identity-frame.md) | `glm-5.3`, `glm-5.3-flash`, `glm-5.3-air` | zcode, codex, dsh, api | identity-frame | ⚪ unverified | 9.4 | — | — |
| [GPT-5.6 身份系统帧 v3](prompts/openai/gpt-5.6/gpt-5.6-identity-frame.md) | `gpt-5.6`, `gpt-5.6-codex`, `gpt6-astra` | codex, api, dsh | identity-frame | ⚪ unverified | 9.4 | — | — |
| [Kimi 渗透授权帧](prompts/moonshot/kimi/kimi-ctf-mode.md) | `kimi`, `kimi-code`, `moonshot-v1` | api, codex, chat | ctf | ⚪ unverified | 6.6 | — | — |
| [Qwen 本地模型重构帧](prompts/local/qwen/qwen-local-frame.md) | `qwen3.6`, `llama`, `gemma-4`, `gpt-oss-20b` | api, chat | lightweight | ⚪ unverified | 6.2 | — | — |
| [Claude CTF 授权模式帧](prompts/anthropic/claude/claude-ctf-mode.md) | `claude`, `claude-sonnet`, `claude-opus` | claude-code, api, chat | ctf | ⚪ unverified | 5.7 | — | — |
| [通用翻译体帧（模型无关）](prompts/all/all-translation-frame.md) | `all` | all | translation | ⚪ unverified | 5.7 | — | — |
| [DeepSeek V4.1 三层重写帧](prompts/deepseek/v4.1/deepseek-v4.1-three-layer.md) | `deepseek-v4.1`, `deepseek-v4.1-flash`, `deepseek-chat` | api, dsh, chat | hybrid-frame | ⚪ unverified | 5.6 | — | — |
| [Gemini 叙事体隔离帧](prompts/google/gemini-3.x/gemini-narrative-frame.md) | `gemini-3.8`, `gemini-3.5-flash`, `gemini-pro` | antigravity, api, chat | narrative | ⚪ unverified | 5.3 | — | — |
| [Grok 直给混合帧](prompts/xai/grok-4.x/grok-hybrid-frame.md) | `grok-4.7`, `grok-4.6`, `grok-build` | api, chat | lightweight | ⚪ unverified | 4.4 | — | — |

### 客户端工具

| 工具 | 客户端 | 安装 | 卸载 | 状态 | 来源 |
|---|---|---|---|---|---|
| [API 直连 / system 消息注入](tools/api/api-system-prompt.md) | api | `pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client api` | `pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client api -Uninstall` | ⚪ unverified | — |
| [Claude Code / CLAUDE.md 注入](tools/claude-code/claude-md-block.md) | claude-code | `pwsh -File installers/install.ps1 -Id claude-ctf-mode -Client claude-code` | `pwsh -File installers/install.ps1 -Id claude-ctf-mode -Client claude-code -Uninstall` | ⚪ unverified | — |
| [Codex / AGENTS.md 注入](tools/codex/codex-agents-md.md) | codex | `pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client codex` | `pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client codex -Uninstall` | ⚪ unverified | — |
| [Cursor / .cursorrules 注入](tools/cursor/cursor-rules-block.md) | cursor | `pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client cursor` | `pwsh -File installers/install.ps1 -Id gpt-5.6-identity-frame -Client cursor -Uninstall` | ⚪ unverified | — |
| [DeepSeek Harness / preset 注入](tools/dsh/dsh-preset-block.md) | dsh | `pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client dsh` | `pwsh -File installers/install.ps1 -Id deepseek-v4.1-three-layer -Client dsh -Uninstall` | ⚪ unverified | — |

### 方法学

- [armor 分口径 v1](techniques/scoring-method.md) — armor 分 = 输出契约遵守率 × 10。明确它衡量什么、不衡量什么，以及怎么复测与降级。
- [成功率怎么算：两级指标](techniques/success-rate.md) — 结构分（能算）与 armor 分（要测）分开，明确各自能回答什么问题，以及「默认装哪条」的排序规则。
- [托管区块规范](techniques/managed-block-spec.md) — 安装器与 CLI 共用的幂等注入格式，保证跨工具可识别、可逐字卸载、可多条目共存。
- [破甲提示词的六段结构](techniques/frame-anatomy.md) — 把市面上的破甲词拆成可组合的六段：元规则、身份、能力、边界、输出契约、恢复。拆开后才能按模型换零件。

### 上游仓库目录

共收录 **1815** 个上游仓库（累计 ★529,398），采集时间 2026-10-19T03:50:10+0000，窗口 pushed_at ≥ 2026-08-16。

| 分类 | 含义 | 数量 |
|---|---|---|
| A | 中文破甲/破限生态 | 181 |
| B | 中文越狱提示词/项目 | 53 |
| C | 英文越狱工具与提示词库 | 263 |
| D | 提示词注入/泄露 | 528 |
| E | 去审查/abliteration 模型与数据 | 240 |
| F | 红队评测/安全基准/防御 | 548 |
| G | 弱相关 AI 安全 | 2 |

<details>
<summary>展开各分类 Top 仓库（每类前 10 个，完整清单见 docs/index.json）</summary>


**A. 中文破甲/破限生态**（181 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [MDX-Tom/gpt-instruct](https://github.com/MDX-Tom/gpt-instruct) | 10,347 | Python | 2026-10-04 | A Codex jailbreak prompt and test pack for gpt. 针对 gpt 系列的 … |
| 2 | [YuJunZhiXue/dsh-purge](https://github.com/YuJunZhiXue/dsh-purge) | 7,162 | JavaScript | 2026-10-19 | DeepSeek Harness 破甲：让所有模型都能破甲，不同模型可换不同提示词；默认提示词面向国模「小码酱」。Ja… |
| 3 | [88lin/video_vip](https://github.com/88lin/video_vip) | 5,532 | JavaScript | 2026-10-19 | 全网VIP视频免费破解脚本，通过集成多个第三方解析接口，去除广告，解锁视频网站的会员限制，让用户享受免费的视频观看体验… |
| 4 | [chen0416ccc-cpu/codex-windows-fast-patch-skill](https://github.com/chen0416ccc-cpu/codex-windows-fast-patch-skill) | 1,294 | PowerShell | 2026-10-17 | 此skills用于指导智能体在 Windows 上恢复 Codex Desktop 升级后失效的本地补丁和能力开关。（… |
| 5 | [3641397194-wq/gpt6-Astra](https://github.com/3641397194-wq/gpt6-Astra) | 1,148 | JavaScript | 2026-10-17 | gpt6 Astra-claude-grok4.7-deepseekv4.1flash-glm5.3-gemini破甲… |
| 6 | [chAng-L19/codex-redteam-mode](https://github.com/chAng-L19/codex-redteam-mode) | 1,120 | Python | 2026-10-09 | 针对于红队攻击思维做出的red team模式(破限项目，封号概不负责）##可自行适配其他Agent。项目问题请提iss… |
| 7 | [z91772524-ai/pojia-next](https://github.com/z91772524-ai/pojia-next) | 513 | Python | 2026-10-18 | 一个脚本搞定 DSH / WorkBuddy / ZCode / Codex / Cursor / Claude 六客… |
| 8 | [FuDie0915/Super-Instruct-Codex-5.6](https://github.com/FuDie0915/Super-Instruct-Codex-5.6) | 467 | Python | 2026-09-01 | 针对GPT 5.6的破甲实验项目，基于Rust开发 |
| 9 | [yexi-by/dsh-unrestricted](https://github.com/yexi-by/dsh-unrestricted) | 423 | JavaScript | 2026-10-18 | DeepSeek Harness 提示词破限插件：通过系统提示词解除模型回答限制，深度适配 Web 与桌面端多模式及工… |
| 10 | [cirosantilli/cirosantilli](https://github.com/cirosantilli/cirosantilli) | 319 | JavaScript | 2026-09-22 | 小粉红小朋友们，新issue 在这儿开： https://github.com/cirosantilli/china-… |


**B. 中文越狱提示词/项目**（53 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [ADWMC/helm-d](https://github.com/ADWMC/helm-d) | 235 | Python | 2026-10-03 | DeepSeek Harness 破甲一体化安全分析插件：Android · Web · Native · Proto… |
| 2 | [YD-233/kimi-break](https://github.com/YD-233/kimi-break) | 184 | — | 2026-10-13 | Kimi Code 渗透破甲（Jailbreak）系统提示词 · AI 红队研究 |
| 3 | [wangyingjie-wyj/hanshuang-pojia-release](https://github.com/wangyingjie-wyj/hanshuang-pojia-release) | 89 | — | 2026-10-07 | 寒霜破甲工具 · Windows x64 便携版完整包 (Git LFS) |
| 4 | [chiina66/glm5.3f-jailbreak](https://github.com/chiina66/glm5.3f-jailbreak) | 48 | — | 2026-09-01 | glm5.3f破甲 |
| 5 | [2908746449/hanshuang-mac](https://github.com/2908746449/hanshuang-mac) | 38 | Python | 2026-10-04 | 寒霜破甲工具 · macOS 桌面版（Windows 便携版移植） |
| 6 | [Justinuse1/pojia-breaker](https://github.com/Justinuse1/pojia-breaker) | 37 | JavaScript | 2026-09-27 | Chinese-first LLM jailbreak benchmark & red-team toolkit \|… |
| 7 | [chiina66/deepseek-v4.1-jailbreak](https://github.com/chiina66/deepseek-v4.1-jailbreak) | 36 | — | 2026-09-10 | Q群 1109491426 ，会更新更多不同ai破甲提示词 |
| 8 | [mtecoYY/ai-baike](https://github.com/mtecoYY/ai-baike) | 28 | Python | 2026-09-07 | 持续记录 AI 相关内容 包括破甲 逆向等方案 |
| 9 | [NyaaCaster/NyaaChat](https://github.com/NyaaCaster/NyaaChat) | 27 | TypeScript | 2026-10-18 | 基于LLM分词结构原理进行提示词破甲的简易聊天工具 |
| 10 | [chiina66/deepseek-jailbreak](https://github.com/chiina66/deepseek-jailbreak) | 20 | — | 2026-09-01 | deepseek破甲提示词 |


**C. 英文越狱工具与提示词库**（263 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [onehumanbeing/esp32-iphone-agent](https://github.com/onehumanbeing/esp32-iphone-agent) | 3,153 | C | 2026-10-18 | Let an AI model use a real iPhone with a $7 ESP32: AirPlay … |
| 2 | [CryptoAILab/Awesome-LM-SSP](https://github.com/CryptoAILab/Awesome-LM-SSP) | 2,088 | — | 2026-09-02 | A reading list for large models safety, security, and priva… |
| 3 | [ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-](https://github.com/ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-) | 1,602 | — | 2026-10-17 | Jailbreaks GPT, Sora, Claude, Gemini ,deepseek this prompt … |
| 4 | [EasyJailbreak/EasyJailbreak](https://github.com/EasyJailbreak/EasyJailbreak) | 928 | Python | 2026-09-01 | An easy-to-use Python framework to generate adversarial jai… |
| 5 | [langgptai/awesome-gemini-prompts](https://github.com/langgptai/awesome-gemini-prompts) | 493 | — | 2026-08-25 | Gemini Prompts, Gemini 3 Prompts, jailbreak, LLM Prompts, L… |
| 6 | [SuzumiyaAkizuki/DanbooruSearchOnline](https://github.com/SuzumiyaAkizuki/DanbooruSearchOnline) | 263 | Python | 2026-10-18 | 本项目提供一种基于语义匹配的 Danbooru 标签查找方案。用户可以通过输入日常语言或模糊描述，查找并匹配 Danb… |
| 7 | [gaur-avvv/XGPT-WormGPT](https://github.com/gaur-avvv/XGPT-WormGPT) | 253 | Shell | 2026-09-17 | [New Update](Added Agentic-Mode, Dark-GODMode)The Real Blac… |
| 8 | [wearetyomsmnv/Awesome-LLMSecOps](https://github.com/wearetyomsmnv/Awesome-LLMSecOps) | 165 | HTML | 2026-09-27 | LLM \| Agentic \| Security \| Operations in one github repo… |
| 9 | [CattleZ/dance-video-to-prompt](https://github.com/CattleZ/dance-video-to-prompt) | 143 | Python | 2026-08-22 | 本地短视频反推 AI 视频生成提示词：抽帧、清晰度、节奏卡点、Agent Skill |
| 10 | [owngoal-dev/WriteNow](https://github.com/owngoal-dev/WriteNow) | 122 | Swift | 2026-10-15 | AI tool within your hands. |


**D. 提示词注入/泄露**（528 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) | 69,869 | Python | 2026-10-16 | Documented system prompts from Anthropic - Claude Fable 5.1… |
| 2 | [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) | 51,359 | — | 2026-09-22 | LEAKED SYSTEM PROMPTS FOR CHATGPT, CLAUDE, GEMINI, GROK, PE… |
| 3 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | 20,504 | Python | 2026-10-17 | Security scanner for AI agent skills. Detect vulnerabilitie… |
| 4 | [jujumilk3/leaked-system-prompts](https://github.com/jujumilk3/leaked-system-prompts) | 14,970 | — | 2026-09-23 | Collection of leaked system prompts |
| 5 | [LouisShark/chatgpt_system_prompt](https://github.com/LouisShark/chatgpt_system_prompt) | 10,807 | HTML | 2026-10-13 | A collection of GPT system prompts and various prompt injec… |
| 6 | [superagent-ai/superagent](https://github.com/superagent-ai/superagent) | 6,766 | TypeScript | 2026-08-25 | Superagent protects your AI applications against prompt inj… |
| 7 | [EmbraceAGI/Awesome-AI-GPTs](https://github.com/EmbraceAGI/Awesome-AI-GPTs) | 1,204 | — | 2026-08-25 | Awesome AI GPTs, OpenAI GPTs, GPT-4, ChatGPT, GPTs, Prompts… |
| 8 | [pipelab-org/pipelock](https://github.com/pipelab-org/pipelock) | 937 | Go | 2026-10-19 | Open-source AI agent firewall for MCP security and agent eg… |
| 9 | [hashgraph-online/hol-guard](https://github.com/hashgraph-online/hol-guard) | 933 | Python | 2026-10-19 | Open-source antivirus for AI agents: block risky tools, sec… |
| 10 | [toby-bridges/api-relay-audit](https://github.com/toby-bridges/api-relay-audit) | 885 | Python | 2026-10-17 | Local security audit for AI API relays and LLM proxies: det… |


**E. 去审查/abliteration 模型与数据**（240 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [p-e-w/heretic](https://github.com/p-e-w/heretic) | 35,788 | Python | 2026-10-17 | Fully automatic censorship removal for language models |
| 2 | [Anil-matcha/Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) | 30,794 | JavaScript | 2026-10-15 | Unrestricted Open-source alternative to AI video platforms … |
| 3 | [techjarves/Uncensored-Local-AI-Multiplatform](https://github.com/techjarves/Uncensored-Local-AI-Multiplatform) | 1,373 | Dart | 2026-10-11 | A cross-platform Flutter app that runs uncensored, 100% off… |
| 4 | [orailnoor/cross-platform-llm-client](https://github.com/orailnoor/cross-platform-llm-client) | 1,135 | C++ | 2026-10-12 | A unified cross-platform AI client supporting seamless tran… |
| 5 | [JoasASantos/Offensive-Security-AI-Models](https://github.com/JoasASantos/Offensive-Security-AI-Models) | 698 | — | 2026-09-28 | Uncensored AI models or those fine-tuned for cybersecurity … |
| 6 | [AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash](https://github.com/AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash) | 479 | Python | 2026-10-06 | Fully uncensored, capability-enhanced abliteration of Qwen3… |
| 7 | [momori777/Artemis](https://github.com/momori777/Artemis) | 396 | Python | 2026-10-18 | 破限本地AI女友后宫，Agent+画图语音向量数据库+live2D+桌宠+酒馆角色卡导入+webchat，QQ+Tel… |
| 8 | [wuwangzhang1216/abliterix](https://github.com/wuwangzhang1216/abliterix) | 258 | Python | 2026-09-28 | Automated alignment adjustment for LLMs — direct steering, … |
| 9 | [Extraltodeus/J-Wash](https://github.com/Extraltodeus/J-Wash) | 232 | Python | 2026-09-06 | Jacobian-Brainwash : A manual alignment tool for large lang… |
| 10 | [lordx64/phantom-kv](https://github.com/lordx64/phantom-kv) | 181 | Python | 2026-09-21 | Refusal removal as a loadable KV-cache graft — zero weight … |


**F. 红队评测/安全基准/防御**（548 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [BerriAI/litellm](https://github.com/BerriAI/litellm) | 61,521 | Python | 2026-10-19 | The fastest, litest AI Gateway. Rust core with Python SDK. … |
| 2 | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 26,122 | TypeScript | 2026-10-19 | Test your prompts, agents, and RAGs. Red teaming/pentesting… |
| 3 | [BoundaryML/baml](https://github.com/BoundaryML/baml) | 9,423 | Rust | 2026-10-18 | The programming language for agents |
| 4 | [maximhq/bifrost](https://github.com/maximhq/bifrost) | 8,923 | Go | 2026-10-18 | Open-source, high-performance AI gateway that works as your… |
| 5 | [guchangan1/All-Defense-Tool](https://github.com/guchangan1/All-Defense-Tool) | 8,161 | Python | 2026-10-19 | 本项目集成了全网优秀的攻防武器工具项目，包含自动化利用，子域名、目录扫描、端口扫描等信息收集工具，各大中间件、cms、… |
| 6 | [guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) | 7,534 | Python | 2026-10-15 | Adding guardrails to large language models. |
| 7 | [NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | 7,324 | Python | 2026-10-15 | NeMo Guardrails is an open-source toolkit for easily adding… |
| 8 | [katanemo/plano](https://github.com/katanemo/plano) | 7,092 | Rust | 2026-10-07 | Plano is an AI-native proxy server and data plane for agent… |
| 9 | [Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard) | 6,909 | Python | 2026-10-19 | A full-stack AI Red Teaming platform securing AI ecosystems… |
| 10 | [elder-plinius/T3MP3ST](https://github.com/elder-plinius/T3MP3ST) | 6,559 | TypeScript | 2026-09-08 | autonomous red teaming platform; multi-agent offensive-secu… |


**G. 弱相关 AI 安全**（2 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [SoniaMehta14/paved-gate](https://github.com/SoniaMehta14/paved-gate) | 3 | Python | 2026-10-12 | Fast System 1 ingestion gate for AI agent architectures: ty… |
| 2 | [Aureliedumbfounding630/agent-governance-toolkit](https://github.com/Aureliedumbfounding630/agent-governance-toolkit) | 0 | — | 2026-10-13 | Manage and monitor AI agents in production environments wit… |

</details>

_本区块由 `scripts/build_index.py` 自动生成，请勿手工编辑；改内容请改卡片或模板。_

<!-- END:INDEX -->

## 目录结构

```
prompts/<厂商>/<模型>/<条目>.md      # 提示词卡片：YAML 头 + 可注入正文
tools/<客户端>/<条目>.md             # 客户端工具卡片：安装/卸载命令
techniques/*.md                      # 方法学：帧架构、防检测、评分口径
docs/models.md                       # 按模型挑：效果分 + 上游热度并排
sources/sources.json                 # 上游仓库目录（采集器产物）
schema/card.schema.json              # 卡片结构，CI 强制校验
scripts/                             # scan / build_index / validate / score
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

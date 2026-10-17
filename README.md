# AI Jailbreak · 破甲资料库

> 把散落在 GitHub 上的破甲词、客户端工具与红队方法，收成一套**机器可读、一键可用、带实测评分**的索引。
> 不是又一个 awesome-list：每条都是结构化卡片，能被 `pojia` CLI 和站点直接消费。

[![validate](https://img.shields.io/badge/validate-passing-brightgreen)](.github/workflows/validate.yml)
[![pages](https://img.shields.io/badge/site-pages-blue)](site/)
[![license](https://img.shields.io/badge/license-MIT-black)](LICENSE)

## 这是什么

现有破甲仓库分三类，都有同一个问题——**找得到，但用起来费劲，好不好使全靠猜**：

| 类型 | 代表 | 痛点 |
|---|---|---|
| 纯提示词堆放 | `chiina66/*` 系列 | 没有适用模型/客户端标注，抄完发现不适配 |
| 单客户端工具 | `dsh-purge`、`helm-x`、`pojia-next` | 只服务一个客户端，换个工具全部重来 |
| 研究清单 | `Awesome-Jailbreak-on-LLMs` | 只有论文和方法名，没有可直接注入的正文 |

本仓库把三件事拆开做：

1. **找得到** — 按模型 × 客户端 × 形态 × 状态的自动索引（本 README 表格全部由 CI 生成，永不漂移）
2. **用得上** — 每条带 `usage.install`，`pojia apply <id>` 直接落到你的 `AGENTS.md` / `CLAUDE.md` / DSH preset
3. **知道好不好使** — 跑过 harness 的才标 `verified` 并给 armor 分；**没跑过的一律是 `unverified`，分数留空**（本仓库不编造评分）

## 30 秒上手

```bash
git clone git@github.com:Baimuking/AI-Jailbreak.git && cd AI-Jailbreak

# 1. 看有哪些
python cli/pojia.py list --model glm-5.3 --client codex

# 2. 看一条的正文和安装方式
python cli/pojia.py show glm-5.3-identity-frame

# 3. 装进当前项目（自动备份，可回滚）
python cli/pojia.py apply glm-5.3-identity-frame --client codex
python cli/pojia.py rollback glm-5.3-identity-frame --client codex
```

把仓库根目录加入 PATH 后可以直接用 `pojia`（Windows 用 `pojia.cmd`，类 Unix 用 `./pojia`）。
没有 Python 也能用：`installers/install.ps1`（Windows）与 `installers/install.sh`（bash）是独立实现，
与 CLI 共用同一套托管区块格式，可以互相识别与卸载。

没装任何工具时，直接打开 `prompts/` 下对应 `.md` 复制正文也能用。

## 索引

<!-- BEGIN:INDEX -->

| 指标 | 数值 |
|---|---|
| 可用条目 | 14 |
| 其中已实测（verified） | 0 |
| 提示词 / 工具 / 方法 | 6 / 5 / 3 |
| 上游仓库目录 | 1733 |

### 提示词条目

| 条目 | 目标模型 | 客户端 | 形态 | 状态 | armor | 来源 |
|---|---|---|---|---|---|---|
| [Claude CTF 授权模式帧](prompts/anthropic/claude/claude-ctf-mode.md) | `claude`, `claude-sonnet`, `claude-opus` | claude-code, api, chat | ctf | ⚪ unverified | — | — |
| [DeepSeek V4.1 三层重写帧](prompts/deepseek/v4.1/deepseek-v4.1-three-layer.md) | `deepseek-v4.1`, `deepseek-v4.1-flash`, `deepseek-chat` | api, dsh, chat | hybrid-frame | ⚪ unverified | — | — |
| [Gemini 叙事体隔离帧](prompts/google/gemini-3.x/gemini-narrative-frame.md) | `gemini-3.8`, `gemini-3.5-flash`, `gemini-pro` | antigravity, api, chat | narrative | ⚪ unverified | — | — |
| [GLM-5.3 身份系统帧](prompts/zhipu/glm-5.3/glm-5.3-identity-frame.md) | `glm-5.3`, `glm-5.3-flash`, `glm-5.3-air` | zcode, codex, dsh, api | identity-frame | ⚪ unverified | — | — |
| [GPT-5.6 身份系统帧 v3](prompts/openai/gpt-5.6/gpt-5.6-identity-frame.md) | `gpt-5.6`, `gpt-5.6-codex`, `gpt6-astra` | codex, api, dsh | identity-frame | ⚪ unverified | — | — |
| [通用翻译体帧（模型无关）](prompts/all/all-translation-frame.md) | `all` | all | translation | ⚪ unverified | — | — |

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
- [托管区块规范](techniques/managed-block-spec.md) — 安装器与 CLI 共用的幂等注入格式，保证跨工具可识别、可逐字卸载、可多条目共存。
- [破甲提示词的六段结构](techniques/frame-anatomy.md) — 把市面上的破甲词拆成可组合的六段：元规则、身份、能力、边界、输出契约、恢复。拆开后才能按模型换零件。

### 上游仓库目录

共收录 **1733** 个上游仓库（累计 ★526,479），采集时间 2026-10-17T23:23:50+0800，窗口 pushed_at ≥ 2026-08-16。

| 分类 | 含义 | 数量 |
|---|---|---|
| A | 中文破甲/破限生态 | 165 |
| B | 中文越狱提示词/项目 | 52 |
| C | 英文越狱工具与提示词库 | 254 |
| D | 提示词注入/泄露 | 503 |
| E | 去审查/abliteration 模型与数据 | 218 |
| F | 红队评测/安全基准/防御 | 539 |
| G | 弱相关 AI 安全 | 2 |

<details>
<summary>展开各分类 Top 仓库（每类前 10 个，完整清单见 docs/index.json）</summary>


**A. 中文破甲/破限生态**（165 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [MDX-Tom/gpt-instruct](https://github.com/MDX-Tom/gpt-instruct) | 10,275 | Python | 2026-10-04 | A Codex jailbreak prompt and test pack for gpt. 针对 gpt 系列的 … |
| 2 | [YuJunZhiXue/dsh-purge](https://github.com/YuJunZhiXue/dsh-purge) | 6,625 | JavaScript | 2026-10-12 | DeepSeek Harness 破甲：让所有模型都能破甲，不同模型可换不同提示词；默认提示词面向国模「小码酱」。Ja… |
| 3 | [88lin/video_vip](https://github.com/88lin/video_vip) | 5,509 | JavaScript | 2026-10-15 | 全网VIP视频免费破解脚本，通过集成多个第三方解析接口，去除广告，解锁视频网站的会员限制，让用户享受免费的视频观看体验… |
| 4 | [chen0416ccc-cpu/codex-windows-fast-patch-skill](https://github.com/chen0416ccc-cpu/codex-windows-fast-patch-skill) | 1,294 | PowerShell | 2026-10-17 | 此skills用于指导智能体在 Windows 上恢复 Codex Desktop 升级后失效的本地补丁和能力开关。（… |
| 5 | [3641397194-wq/gpt6-Astra](https://github.com/3641397194-wq/gpt6-Astra) | 1,123 | JavaScript | 2026-10-16 | gpt6 Astra-claude-grok4.7-deepseekv4.1flash-glm5.3-gemini破甲… |
| 6 | [chAng-L19/codex-redteam-mode](https://github.com/chAng-L19/codex-redteam-mode) | 1,117 | Python | 2026-10-09 | 针对于红队攻击思维做出的red team模式(破限项目，封号概不负责）##可自行适配其他Agent。项目问题请提iss… |
| 7 | [FuDie0915/Super-Instruct-Codex-5.6](https://github.com/FuDie0915/Super-Instruct-Codex-5.6) | 467 | Python | 2026-09-01 | 针对GPT 5.6的破甲实验项目，基于Rust开发 |
| 8 | [z91772524-ai/pojia-next](https://github.com/z91772524-ai/pojia-next) | 462 | Python | 2026-10-17 | 一个脚本搞定 DSH / WorkBuddy / ZCode / Codex / Cursor / Claude 六客… |
| 9 | [cirosantilli/cirosantilli](https://github.com/cirosantilli/cirosantilli) | 318 | JavaScript | 2026-09-22 | 小粉红小朋友们，新issue 在这儿开： https://github.com/cirosantilli/china-… |
| 10 | [yexi-by/dsh-unrestricted](https://github.com/yexi-by/dsh-unrestricted) | 315 | JavaScript | 2026-10-15 | DeepSeek Harness 提示词破限插件：通过系统提示词解除模型回答限制，深度适配 Web 与桌面端多模式及工… |


**B. 中文越狱提示词/项目**（52 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [ADWMC/helm-d](https://github.com/ADWMC/helm-d) | 226 | Python | 2026-10-03 | DeepSeek Harness 破甲一体化安全分析插件：Android · Web · Native · Proto… |
| 2 | [YD-233/kimi-break](https://github.com/YD-233/kimi-break) | 180 | — | 2026-10-13 | Kimi Code 渗透破甲（Jailbreak）系统提示词 · AI 红队研究 |
| 3 | [wangyingjie-wyj/hanshuang-pojia-release](https://github.com/wangyingjie-wyj/hanshuang-pojia-release) | 77 | — | 2026-10-07 | 寒霜破甲工具 · Windows x64 便携版完整包 (Git LFS) |
| 4 | [chiina66/glm5.3f-jailbreak](https://github.com/chiina66/glm5.3f-jailbreak) | 45 | — | 2026-09-01 | glm5.3f破甲 |
| 5 | [chiina66/deepseek-v4.1-jailbreak](https://github.com/chiina66/deepseek-v4.1-jailbreak) | 36 | — | 2026-09-10 | Q群 1109491426 ，会更新更多不同ai破甲提示词 |
| 6 | [2908746449/hanshuang-mac](https://github.com/2908746449/hanshuang-mac) | 35 | Python | 2026-10-04 | 寒霜破甲工具 · macOS 桌面版（Windows 便携版移植） |
| 7 | [Justinuse1/pojia-breaker](https://github.com/Justinuse1/pojia-breaker) | 35 | JavaScript | 2026-09-27 | Chinese-first LLM jailbreak benchmark & red-team toolkit \|… |
| 8 | [NyaaCaster/NyaaChat](https://github.com/NyaaCaster/NyaaChat) | 27 | TypeScript | 2026-10-15 | 基于LLM分词结构原理进行提示词破甲的简易聊天工具 |
| 9 | [mtecoYY/ai-baike](https://github.com/mtecoYY/ai-baike) | 27 | Python | 2026-09-07 | 持续记录 AI 相关内容 包括破甲 逆向等方案 |
| 10 | [chiina66/deepseek-jailbreak](https://github.com/chiina66/deepseek-jailbreak) | 19 | — | 2026-09-01 | deepseek破甲提示词 |


**C. 英文越狱工具与提示词库**（254 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [onehumanbeing/esp32-iphone-agent](https://github.com/onehumanbeing/esp32-iphone-agent) | 2,967 | C | 2026-10-17 | Let an AI model use a real iPhone with a $7 ESP32: AirPlay … |
| 2 | [CryptoAILab/Awesome-LM-SSP](https://github.com/CryptoAILab/Awesome-LM-SSP) | 2,087 | — | 2026-09-02 | A reading list for large models safety, security, and priva… |
| 3 | [ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-](https://github.com/ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-) | 1,516 | — | 2026-10-17 | Jailbreaks GPT, Sora, Claude, Gemini ,deepseek this prompt … |
| 4 | [EasyJailbreak/EasyJailbreak](https://github.com/EasyJailbreak/EasyJailbreak) | 926 | Python | 2026-09-01 | An easy-to-use Python framework to generate adversarial jai… |
| 5 | [langgptai/awesome-gemini-prompts](https://github.com/langgptai/awesome-gemini-prompts) | 493 | — | 2026-08-25 | Gemini Prompts, Gemini 3 Prompts, jailbreak, LLM Prompts, L… |
| 6 | [SuzumiyaAkizuki/DanbooruSearchOnline](https://github.com/SuzumiyaAkizuki/DanbooruSearchOnline) | 262 | Python | 2026-10-16 | 本项目提供一种基于语义匹配的 Danbooru 标签查找方案。用户可以通过输入日常语言或模糊描述，查找并匹配 Danb… |
| 7 | [gaur-avvv/XGPT-WormGPT](https://github.com/gaur-avvv/XGPT-WormGPT) | 253 | Shell | 2026-09-17 | [New Update](Added Agentic-Mode, Dark-GODMode)The Real Blac… |
| 8 | [wearetyomsmnv/Awesome-LLMSecOps](https://github.com/wearetyomsmnv/Awesome-LLMSecOps) | 165 | HTML | 2026-09-27 | LLM \| Agentic \| Security \| Operations in one github repo… |
| 9 | [CattleZ/dance-video-to-prompt](https://github.com/CattleZ/dance-video-to-prompt) | 143 | Python | 2026-08-22 | 本地短视频反推 AI 视频生成提示词：抽帧、清晰度、节奏卡点、Agent Skill |
| 10 | [d4ncboz/jailbreak](https://github.com/d4ncboz/jailbreak) | 120 | — | 2026-08-28 | BOZAGENTIC — Sovereign Alignment Research, Jailbreak Taxono… |


**D. 提示词注入/泄露**（503 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) | 69,789 | Python | 2026-10-16 | Documented system prompts from Anthropic - Claude Fable 5.1… |
| 2 | [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) | 51,327 | — | 2026-09-22 | LEAKED SYSTEM PROMPTS FOR CHATGPT, CLAUDE, GEMINI, GROK, PE… |
| 3 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | 20,413 | Python | 2026-10-17 | Security scanner for AI agent skills. Detect vulnerabilitie… |
| 4 | [jujumilk3/leaked-system-prompts](https://github.com/jujumilk3/leaked-system-prompts) | 14,964 | — | 2026-09-23 | Collection of leaked system prompts |
| 5 | [LouisShark/chatgpt_system_prompt](https://github.com/LouisShark/chatgpt_system_prompt) | 10,809 | HTML | 2026-10-13 | A collection of GPT system prompts and various prompt injec… |
| 6 | [superagent-ai/superagent](https://github.com/superagent-ai/superagent) | 6,767 | TypeScript | 2026-08-25 | Superagent protects your AI applications against prompt inj… |
| 7 | [EmbraceAGI/Awesome-AI-GPTs](https://github.com/EmbraceAGI/Awesome-AI-GPTs) | 1,204 | — | 2026-08-25 | Awesome AI GPTs, OpenAI GPTs, GPT-4, ChatGPT, GPTs, Prompts… |
| 8 | [pipelab-org/pipelock](https://github.com/pipelab-org/pipelock) | 933 | Go | 2026-10-17 | Open-source AI agent firewall for MCP security and agent eg… |
| 9 | [hashgraph-online/hol-guard](https://github.com/hashgraph-online/hol-guard) | 923 | Python | 2026-10-17 | Open-source antivirus for AI agents: block risky tools, sec… |
| 10 | [toby-bridges/api-relay-audit](https://github.com/toby-bridges/api-relay-audit) | 885 | Python | 2026-10-17 | Local security audit for AI API relays and LLM proxies: det… |


**E. 去审查/abliteration 模型与数据**（218 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [p-e-w/heretic](https://github.com/p-e-w/heretic) | 35,599 | Python | 2026-10-17 | Fully automatic censorship removal for language models |
| 2 | [Anil-matcha/Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) | 30,644 | JavaScript | 2026-10-15 | Unrestricted Open-source alternative to AI video platforms … |
| 3 | [techjarves/Uncensored-Local-AI-Multiplatform](https://github.com/techjarves/Uncensored-Local-AI-Multiplatform) | 1,365 | Dart | 2026-10-11 | A cross-platform Flutter app that runs uncensored, 100% off… |
| 4 | [orailnoor/cross-platform-llm-client](https://github.com/orailnoor/cross-platform-llm-client) | 1,132 | C++ | 2026-10-12 | A unified cross-platform AI client supporting seamless tran… |
| 5 | [JoasASantos/Offensive-Security-AI-Models](https://github.com/JoasASantos/Offensive-Security-AI-Models) | 692 | — | 2026-09-28 | Uncensored AI models or those fine-tuned for cybersecurity … |
| 6 | [AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash](https://github.com/AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash) | 480 | Python | 2026-10-06 | Fully uncensored, capability-enhanced abliteration of Qwen3… |
| 7 | [momori777/Artemis](https://github.com/momori777/Artemis) | 391 | Python | 2026-10-16 | 破限本地AI女友后宫，Agent+画图语音向量数据库+live2D+桌宠+酒馆角色卡导入+webchat，QQ+Tel… |
| 8 | [wuwangzhang1216/abliterix](https://github.com/wuwangzhang1216/abliterix) | 258 | Python | 2026-09-28 | Automated alignment adjustment for LLMs — direct steering, … |
| 9 | [Extraltodeus/J-Wash](https://github.com/Extraltodeus/J-Wash) | 232 | Python | 2026-09-06 | Jacobian-Brainwash : A manual alignment tool for large lang… |
| 10 | [lordx64/phantom-kv](https://github.com/lordx64/phantom-kv) | 181 | Python | 2026-09-21 | Refusal removal as a loadable KV-cache graft — zero weight … |


**F. 红队评测/安全基准/防御**（539 个）

| # | 仓库 | ★ | 语言 | 最近 push | 简介 |
|---|---|---|---|---|---|
| 1 | [BerriAI/litellm](https://github.com/BerriAI/litellm) | 61,439 | Python | 2026-10-17 | The fastest, litest AI Gateway. Rust core with Python SDK. … |
| 2 | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 26,084 | TypeScript | 2026-10-17 | Test your prompts, agents, and RAGs. Red teaming/pentesting… |
| 3 | [BoundaryML/baml](https://github.com/BoundaryML/baml) | 9,417 | Rust | 2026-10-17 | The programming language for agents |
| 4 | [maximhq/bifrost](https://github.com/maximhq/bifrost) | 8,882 | Go | 2026-10-17 | Open-source, high-performance AI gateway that works as your… |
| 5 | [guchangan1/All-Defense-Tool](https://github.com/guchangan1/All-Defense-Tool) | 8,156 | Python | 2026-10-13 | 本项目集成了全网优秀的攻防武器工具项目，包含自动化利用，子域名、目录扫描、端口扫描等信息收集工具，各大中间件、cms、… |
| 6 | [guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) | 7,532 | Python | 2026-10-15 | Adding guardrails to large language models. |
| 7 | [NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | 7,316 | Python | 2026-10-15 | NeMo Guardrails is an open-source toolkit for easily adding… |
| 8 | [katanemo/plano](https://github.com/katanemo/plano) | 7,091 | Rust | 2026-10-07 | Plano is an AI-native proxy server and data plane for agent… |
| 9 | [Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard) | 6,892 | Python | 2026-10-17 | A full-stack AI Red Teaming platform securing AI ecosystems… |
| 10 | [elder-plinius/T3MP3ST](https://github.com/elder-plinius/T3MP3ST) | 6,553 | TypeScript | 2026-09-08 | autonomous red teaming platform; multi-agent offensive-secu… |


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

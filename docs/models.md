# 按模型挑破甲

> 单看效果分不知道挑哪个，单看星标不知道对应哪个模型——所以放一张表里。

三个数字的含义：

| 列 | 含义 | 怎么来的 |
|---|---|---|
| **结构分** | 破甲卡本身写得够不够狠（0-10） | 读文本结构算，见 [success-rate.md](../techniques/success-rate.md) |
| **armor** | 该卡在真实模型上的实测分 | `scripts/score.py`；未跑过为 — |
| **相关仓库 / ★合计** | 这个模型在上游生态里的热度 | GitHub 采集后按关键词匹配 |

上游共 1815 个仓库；下表的「相关仓库」是其中命中该模型关键词的数量。
**★ 是上游项目的热度，不是破甲成功率**，两者不要混读。

口径说明：同时命中 ≥4 个模型家族的仓库（各类 `system_prompts_leaks` 合集、
跨模型工具箱）不计入任何单模型行——否则每一行都会被同一个大仓库抬高。它们仍完整保留在
全量目录里。命中靠仓库名与简介的关键词匹配，会有误命中，仅供参考。

| 模型 | 厂商 | 推荐卡 | 结构分 | armor | 相关仓库 | ★合计 | 最热仓库 |
|---|---|---|---|---|---|---|---|
| Anthropic Claude | Anthropic | [`claude-ctf-mode`](../prompts/anthropic/claude/claude-ctf-mode.md) | 5.7 | — | 153 | 168,782 | [BerriAI/litellm](https://github.com/BerriAI/litellm) · ★61,521 |
| Google Gemini 3.x | Google | [`gemini-narrative-frame`](../prompts/google/gemini-3.x/gemini-narrative-frame.md) | 5.3 | — | 58 | 80,547 | [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) · ★51,359 |
| xAI Grok 4.x | xAI | [`grok-hybrid-frame`](../prompts/xai/grok-4.x/grok-hybrid-frame.md) | 4.4 | — | 16 | 51,663 | [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) · ★51,359 |
| 任意模型（通用帧） | 模型无关 | [`universal-max-chain`](../prompts/all/universal-max-chain.md) | 10.0 | — | 426 | 46,711 | [MDX-Tom/gpt-instruct](https://github.com/MDX-Tom/gpt-instruct) · ★10,347 |
| DeepSeek V4.1 / Flash | DeepSeek | [`deepseek-v4.1-three-layer`](../prompts/deepseek/v4.1/deepseek-v4.1-three-layer.md) | 5.6 | — | 107 | 37,275 | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) · ★26,122 |
| OpenAI GPT-5.6 / Codex | OpenAI | [`gpt-5.6-identity-frame`](../prompts/openai/gpt-5.6/gpt-5.6-identity-frame.md) | 9.4 | — | 68 | 36,071 | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) · ★20,504 |
| OpenAI GPT-6 Astra | OpenAI | [`gpt-5.6-identity-frame`](../prompts/openai/gpt-5.6/gpt-5.6-identity-frame.md) | 9.4 | — | 10 | 2,156 | [scadastrangelove/awesome-ai-security-tools](https://github.com/scadastrangelove/awesome-ai-security-tools) · ★1,665 |
| 本地 Qwen / Llama / Gemma | 本地 / Local | [`qwen-local-frame`](../prompts/local/qwen/qwen-local-frame.md) | 6.2 | — | 120 | 1,074 | [AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash](https://github.com/AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash) · ★479 |
| Moonshot Kimi | Moonshot | [`kimi-ctf-mode`](../prompts/moonshot/kimi/kimi-ctf-mode.md) | 6.6 | — | 3 | 210 | [YD-233/kimi-break](https://github.com/YD-233/kimi-break) · ★184 |
| 智谱 GLM-5.3 | 智谱 / Zhipu | [`glm-5.3-identity-frame`](../prompts/zhipu/glm-5.3/glm-5.3-identity-frame.md) | 9.4 | — | 13 | 151 | [chiina66/glm5.3f-jailbreak](https://github.com/chiina66/glm5.3f-jailbreak) · ★48 |

## 怎么读这张表

1. **先按模型找行**，拿到推荐卡。没有专属卡的模型用 `universal-max-chain`（模型无关，结构分最高）。
2. **再看结构分**，低于 7 的说明还缺段落，可以用 `pojia show <id>` 查缺哪段。
3. **★合计** 用来看这个模型的上游生态有多活跃——热度高意味着可参考的实现多，不代表某条词更好用。
4. **armor 为空是正常的**，本仓库没有跑过实测就不会填数字。

## 每个模型的热门前 5

**Anthropic Claude**（153 个相关仓库，★168,782）

1. [BerriAI/litellm](https://github.com/BerriAI/litellm) · ★61,521
2. [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) · ★51,359
3. [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) · ★26,122
4. [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) · ★20,504
5. [Goochbeater/Spiritual-Spell-Red-Teaming](https://github.com/Goochbeater/Spiritual-Spell-Red-Teaming) · ★4,026

**Google Gemini 3.x**（58 个相关仓库，★80,547）

1. [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) · ★51,359
2. [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) · ★26,122
3. [ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-](https://github.com/ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-) · ★1,602
4. [langgptai/awesome-gemini-prompts](https://github.com/langgptai/awesome-gemini-prompts) · ★493
5. [api7/aisix](https://github.com/api7/aisix) · ★200

**xAI Grok 4.x**（16 个相关仓库，★51,663）

1. [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) · ★51,359
2. [Kutuyyy/Leaked-System-Prompt-AI](https://github.com/Kutuyyy/Leaked-System-Prompt-AI) · ★154
3. [01xor/ai-jailbreak-archive](https://github.com/01xor/ai-jailbreak-archive) · ★58
4. [The-AIE/the-gibson](https://github.com/The-AIE/the-gibson) · ★41
5. [regaan/basilisk](https://github.com/regaan/basilisk) · ★32

**任意模型（通用帧）**（426 个相关仓库，★46,711）

1. [MDX-Tom/gpt-instruct](https://github.com/MDX-Tom/gpt-instruct) · ★10,347
2. [YuJunZhiXue/dsh-purge](https://github.com/YuJunZhiXue/dsh-purge) · ★7,162
3. [Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard) · ★6,909
4. [Goochbeater/Spiritual-Spell-Red-Teaming](https://github.com/Goochbeater/Spiritual-Spell-Red-Teaming) · ★4,026
5. [onehumanbeing/esp32-iphone-agent](https://github.com/onehumanbeing/esp32-iphone-agent) · ★3,153

**DeepSeek V4.1 / Flash**（107 个相关仓库，★37,275）

1. [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) · ★26,122
2. [YuJunZhiXue/dsh-purge](https://github.com/YuJunZhiXue/dsh-purge) · ★7,162
3. [ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-](https://github.com/ShadowHackrs/Jailbreaks-GPT-Gemini-deepseek-) · ★1,602
4. [yexi-by/dsh-unrestricted](https://github.com/yexi-by/dsh-unrestricted) · ★423
5. [FuRongJun-1999/dsh-memory](https://github.com/FuRongJun-1999/dsh-memory) · ★413

**OpenAI GPT-5.6 / Codex**（68 个相关仓库，★36,071）

1. [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) · ★20,504
2. [MDX-Tom/gpt-instruct](https://github.com/MDX-Tom/gpt-instruct) · ★10,347
3. [chen0416ccc-cpu/codex-windows-fast-patch-skill](https://github.com/chen0416ccc-cpu/codex-windows-fast-patch-skill) · ★1,294
4. [chAng-L19/codex-redteam-mode](https://github.com/chAng-L19/codex-redteam-mode) · ★1,120
5. [FuDie0915/Super-Instruct-Codex-5.6](https://github.com/FuDie0915/Super-Instruct-Codex-5.6) · ★467

**OpenAI GPT-6 Astra**（10 个相关仓库，★2,156）

1. [scadastrangelove/awesome-ai-security-tools](https://github.com/scadastrangelove/awesome-ai-security-tools) · ★1,665
2. [xiaoguai009/codex-armor-toolkit](https://github.com/xiaoguai009/codex-armor-toolkit) · ★222
3. [aimeoa/hanshuang-codex](https://github.com/aimeoa/hanshuang-codex) · ★211
4. [Scott96866870/nebula-public](https://github.com/Scott96866870/nebula-public) · ★31
5. [HHT0rro/GPT6.1-Sol-Cyber](https://github.com/HHT0rro/GPT6.1-Sol-Cyber) · ★7

**本地 Qwen / Llama / Gemma**（120 个相关仓库，★1,074）

1. [AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash](https://github.com/AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-DFlash) · ★479
2. [DominikBucko/qwen38-flash-next-2x3090](https://github.com/DominikBucko/qwen38-flash-next-2x3090) · ★119
3. [hypersniper05/MCP-Image-Generator-Uncensored](https://github.com/hypersniper05/MCP-Image-Generator-Uncensored) · ★101
4. [promptfoo/promptfoo-action](https://github.com/promptfoo/promptfoo-action) · ★75
5. [vaporif/parry-guard](https://github.com/vaporif/parry-guard) · ★45

**Moonshot Kimi**（3 个相关仓库，★210）

1. [YD-233/kimi-break](https://github.com/YD-233/kimi-break) · ★184
2. [chenxingqiang/claude-code-open](https://github.com/chenxingqiang/claude-code-open) · ★26
3. [anaksholeh201011-source/ai-coding](https://github.com/anaksholeh201011-source/ai-coding) · ★0

**智谱 GLM-5.3**（13 个相关仓库，★151）

1. [chiina66/glm5.3f-jailbreak](https://github.com/chiina66/glm5.3f-jailbreak) · ★48
2. [YuQii-111/ZCodeDeployNew](https://github.com/YuQii-111/ZCodeDeployNew) · ★47
3. [drowzeys/keys-vLLm.0.27.1-GLM-5.3-Flash-NVFP4-NVFP4KV-1M-Context-Abliterated](https://github.com/drowzeys/keys-vLLm.0.27.1-GLM-5.3-Flash-NVFP4-NVFP4KV-1M-Context-Abliterated) · ★29
4. [ArthurMonteiro08586/abliteration-farm](https://github.com/ArthurMonteiro08586/abliteration-farm) · ★14
5. [junpo2008/zcode-armor-breaker](https://github.com/junpo2008/zcode-armor-breaker) · ★5

"""按模型聚合：把「哪个模型能用什么」和「这个模型的上游生态有多热」放到一张表里。

两个数据来源：
  1. 卡片（本仓库整理）：给出该模型可用的破甲卡与结构分/实测分
  2. sources（GitHub 采集）：按关键词匹配上游仓库，统计数量与 star 合计

注意：star 是上游仓库的热度，**不是**破甲在当前模型上的成功率。
两者并排只是为了让人挑得动，不要当成同一维度的分数。
"""

from __future__ import annotations

import re

# 模型家族表。repo_patterns 用于在 sources 里匹配上游仓库；card_targets 用于匹配卡片。
FAMILIES: list[dict] = [
    {
        "key": "gpt-5.6",
        "name": "OpenAI GPT-5.6 / Codex",
        "vendor": "OpenAI",
        "card_targets": ["gpt-5.6", "gpt-5.6-codex", "codex"],
        "repo_patterns": [r"gpt[-_ ]?5\.6", r"gpt5\.6", r"gpt[-_ ]?5", r"codex"],
    },
    {
        "key": "gpt6-astra",
        "name": "OpenAI GPT-6 Astra",
        "vendor": "OpenAI",
        "card_targets": ["gpt6-astra", "gpt-6-astra"],
        "repo_patterns": [r"gpt[-_ ]?6", r"gpt6", r"astra"],
    },
    {
        "key": "claude",
        "name": "Anthropic Claude",
        "vendor": "Anthropic",
        "card_targets": ["claude", "claude-sonnet", "claude-opus", "claude-code"],
        "repo_patterns": [r"claude", r"anthropic"],
    },
    {
        "key": "gemini",
        "name": "Google Gemini 3.x",
        "vendor": "Google",
        "card_targets": ["gemini-3.8", "gemini-3.5-flash", "gemini-pro", "gemini"],
        "repo_patterns": [r"gemini", r"antigravity"],
    },
    {
        "key": "deepseek",
        "name": "DeepSeek V4.1 / Flash",
        "vendor": "DeepSeek",
        "card_targets": ["deepseek-v4.1", "deepseek-v4.1-flash", "deepseek-chat", "deepseek"],
        "repo_patterns": [r"deepseek", r"\bdsh\b"],
    },
    {
        "key": "glm",
        "name": "智谱 GLM-5.3",
        "vendor": "智谱 / Zhipu",
        "card_targets": ["glm-5.3", "glm-5.3-flash", "glm-5.3-air", "glm"],
        "repo_patterns": [r"\bglm", r"zhipu", r"zcode"],
    },
    {
        "key": "kimi",
        "name": "Moonshot Kimi",
        "vendor": "Moonshot",
        "card_targets": ["kimi", "kimi-code", "moonshot-v1"],
        "repo_patterns": [r"kimi", r"moonshot"],
    },
    {
        "key": "grok",
        "name": "xAI Grok 4.x",
        "vendor": "xAI",
        "card_targets": ["grok-4.7", "grok-4.6", "grok-build", "grok"],
        "repo_patterns": [r"grok", r"\bxai\b"],
    },
    {
        "key": "qwen",
        "name": "本地 Qwen / Llama / Gemma",
        "vendor": "本地 / Local",
        "card_targets": ["qwen3.6", "llama", "gemma-4", "gpt-oss-20b"],
        "repo_patterns": [r"qwen", r"llama", r"gemma", r"gpt-oss", r"uncensored model"],
    },
    {
        "key": "universal",
        "name": "任意模型（通用帧）",
        "vendor": "模型无关",
        "card_targets": ["all"],
        "repo_patterns": [r"jailbreak", r"破甲", r"破限"],
    },
]


def _compile(patterns: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def build_models(cards: list, data: dict) -> list[dict]:
    """返回每个模型家族的聚合行，按上游 star 合计降序。

    「泛模型仓库」处理：一个仓库如果同时命中 ≥4 个模型家族（例如各类
    system_prompts_leaks 合集），说明它不是某个模型专属的资源，把它算进单模型的
    ★合计只会把每一行都抬高。这类仓库从单模型统计里剔除，但仍在全量目录中。
    """
    repos = (data or {}).get("repos", [])
    prompts = [c for c in cards if c.kind == "prompt"]

    # 第一轮：先算出每个家族命中的仓库集合
    matched_names: dict[str, set[str]] = {}
    for fam in FAMILIES:
        pats = _compile(fam["repo_patterns"])
        matched_names[fam["key"]] = {
            r.get("full_name", "")
            for r in repos
            if any(p.search((r.get("full_name") or "") + " " + (r.get("description") or "")) for p in pats)
        }

    # 统计跨家族出现次数；>=4 视为泛模型仓库
    membership: dict[str, int] = {}
    for fam in FAMILIES:
        if fam["key"] == "universal":
            continue
        for name in matched_names[fam["key"]]:
            membership[name] = membership.get(name, 0) + 1
    generic = {name for name, n in membership.items() if n >= 4}

    by_name = {r.get("full_name"): r for r in repos}
    rows: list[dict] = []

    for fam in FAMILIES:
        drop = set() if fam["key"] == "universal" else generic
        names = matched_names[fam["key"]] - drop
        matched = [by_name[n] for n in names if n in by_name]
        matched.sort(key=lambda r: (-int(r.get("stars") or 0), r.get("full_name", "")))
        stars = sum(int(r.get("stars") or 0) for r in matched)

        targets = {t.lower() for t in fam["card_targets"]}
        fam_cards = [c for c in prompts if targets & {t.lower() for t in c.targets}]
        fam_cards.sort(key=lambda c: (-(c.quality_score() or 0), c.id))
        best = fam_cards[0] if fam_cards else None

        rows.append(
            {
                "key": fam["key"],
                "name": fam["name"],
                "vendor": fam["vendor"],
                "card": best.id if best else None,
                "card_name": best.data["name"] if best else None,
                "quality": best.quality_score() if best else None,
                "armor": best.strength if best else None,
                "status": best.status if best else None,
                "repos": len(matched),
                "stars": stars,
                "top_repo": matched[0]["full_name"] if matched else None,
                "top_repo_stars": int(matched[0].get("stars") or 0) if matched else 0,
                "top_repos": [
                    {"full_name": r["full_name"], "stars": int(r.get("stars") or 0), "url": r.get("url")}
                    for r in matched[:5]
                ],
                "excluded_generic": len((matched_names[fam["key"]] - names)),
            }
        )

    rows.sort(key=lambda r: (-r["stars"], r["name"]))
    return rows


def generic_count(cards: list, data: dict) -> int:
    """命中 ≥4 个模型家族的泛模型仓库数量，用于在文档里交代口径。"""
    repos = (data or {}).get("repos", [])
    membership: dict[str, int] = {}
    for fam in FAMILIES:
        if fam["key"] == "universal":
            continue
        pats = _compile(fam["repo_patterns"])
        for r in repos:
            if any(p.search((r.get("full_name") or "") + " " + (r.get("description") or "")) for p in pats):
                name = r.get("full_name", "")
                membership[name] = membership.get(name, 0) + 1
    return sum(1 for n in membership.values() if n >= 4)

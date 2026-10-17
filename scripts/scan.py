#!/usr/bin/env python3
"""GitHub 上游仓库采集器：把破甲生态的仓库扫进 sources/sources.json。

用法：
    python scripts/scan.py                      # 全量采集（36 组查询）
    python scripts/scan.py --limit 50 --sleep 2 # 每组最多 50 条，间隔 2s
    python scripts/scan.py --keep-missing       # 保留本轮没扫到但历史存在的仓库
    python scripts/scan.py --dry-run            # 只打印，不落盘

依赖：gh CLI（已登录，需 repo 读权限）。不读 Token，不外传任何凭据。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import sources as src_lib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Windows 控制台默认 GBK，中文输出会乱码/抛异常；这里强制 UTF-8 输出。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
GH = r"C:\Program Files\GitHub CLI\gh.exe"
GH_FALLBACK = "gh"
PUSHED_SINCE = "2026-08-16"

# 查询表：q=搜索式，cat=初判分类。分类还会被 classify() 二次修正。
QUERIES: list[dict] = [
    {"q": "破甲", "cat": "A"},
    {"q": "破限", "cat": "A"},
    {"q": "pojia", "cat": "A"},
    {"q": "破甲 codex", "cat": "A"},
    {"q": "破甲 dsh", "cat": "A"},
    {"q": "破限 提示词", "cat": "A"},
    {"q": "jailbreak 越狱 提示词", "cat": "B"},
    {"q": "越狱 大模型", "cat": "B"},
    {"q": "jailbreak prompts", "cat": "C"},
    {"q": "LLM jailbreak", "cat": "C"},
    {"q": "DAN prompt", "cat": "C"},
    {"q": "jailbreak Claude", "cat": "C"},
    {"q": "jailbreak GPT", "cat": "C"},
    {"q": "jailbreak Gemini", "cat": "C"},
    {"q": "jailbreak DeepSeek", "cat": "C"},
    {"q": "uncensored prompt", "cat": "C"},
    {"q": "red team LLM", "cat": "F"},
    {"q": "prompt injection", "cat": "D"},
    {"q": "system prompt leak", "cat": "D"},
    {"q": "prompt leak", "cat": "D"},
    {"q": "indirect prompt injection", "cat": "D"},
    {"q": "abliteration", "cat": "E"},
    {"q": "uncensored model", "cat": "E"},
    {"q": "refusal abliteration", "cat": "E"},
    {"q": "decensored LLM", "cat": "E"},
    {"q": "guardrails LLM", "cat": "F"},
    {"q": "LLM security benchmark", "cat": "F"},
    {"q": "AI red teaming", "cat": "F"},
    {"q": "adversarial prompt", "cat": "F"},
    {"q": "agent security eval", "cat": "F"},
    {"q": "llm firewall", "cat": "F"},
    {"q": "harmful fine-tuning LLM", "cat": "F"},
    {"q": "AI safety benchmark LLM", "cat": "G"},
    {"q": "claude code jailbreak", "cat": "C"},
    {"q": "codex jailbreak", "cat": "C"},
    {"q": "系统提示词泄露", "cat": "D"},
]

ZH = re.compile(r"[\u4e00-\u9fff]")
CLIENT_WORDS = re.compile(
    r"codex|dsh|workbuddy|zcode|cursor|claude|antigravity|opencode|hermes|gemini-cli", re.I
)
E_WORDS = re.compile(r"abliterat|uncensor|de-?censored|refusal removal|refusal steering", re.I)
D_WORDS = re.compile(r"injection|prompt leak|system prompt|exfiltrat|jailbreak detect", re.I)
F_WORDS = re.compile(
    r"red.?team|benchmark|evaluat|guardrail|defen[cs]e|firewall|scanner|security (test|framework)|audit",
    re.I,
)
A_WORDS = re.compile(r"破甲|破限|pojia|越狱|免审|解禁", re.I)


def classify(name: str, desc: str, fallback: str) -> str:
    text = f"{name} {desc}"
    if E_WORDS.search(text):
        return "E"
    if A_WORDS.search(text) and ZH.search(text):
        return "A" if CLIENT_WORDS.search(text) else "B"
    if D_WORDS.search(text):
        return "D"
    if F_WORDS.search(text):
        return "F"
    return fallback


def pick_gh() -> str:
    return GH if Path(GH).exists() else GH_FALLBACK


def search(gh: str, query: str, limit: int) -> list[dict]:
    full = f"{query} pushed:>={PUSHED_SINCE}"
    cmd = [
        gh,
        "search",
        "repos",
        full,
        "--limit",
        str(limit),
        "--json",
        "fullName,description,stargazersCount,language,pushedAt,createdAt,url,license,isArchived,isFork",
    ]
    for attempt in range(3):
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode == 0:
            try:
                return json.loads(proc.stdout or "[]")
            except json.JSONDecodeError:
                return []
        err = (proc.stderr or "").strip()
        if "rate limit" in err.lower() or "secondary rate" in err.lower():
            wait = 20 * (attempt + 1)
            print(f"    ! 触发限流，等待 {wait}s 重试", file=sys.stderr)
            time.sleep(wait)
            continue
        print(f"    ! 查询失败: {err.splitlines()[0] if err else 'unknown'}", file=sys.stderr)
        return []
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="采集上游破甲仓库目录")
    ap.add_argument("--limit", type=int, default=100, help="每组查询最多取多少条（默认 100）")
    ap.add_argument("--sleep", type=float, default=2.2, help="查询间隔秒数（Search API 限 30/min）")
    ap.add_argument("--keep-missing", action="store_true", help="保留历史存在但本轮未扫到的仓库")
    ap.add_argument("--dry-run", action="store_true", help="只打印统计，不写文件")
    ap.add_argument("--queries", default="", help="只跑指定查询（逗号分隔子串匹配）")
    args = ap.parse_args()

    gh = pick_gh()
    queries = QUERIES
    if args.queries:
        wanted = [w.strip() for w in args.queries.split(",") if w.strip()]
        queries = [q for q in QUERIES if any(w.lower() in q["q"].lower() for w in wanted)]

    today = dt.date.today().isoformat()
    repos: dict[str, dict] = {}
    ran: list[str] = []

    print(f"采集 {len(queries)} 组查询，窗口 pushed_at >= {PUSHED_SINCE}")
    for idx, item in enumerate(queries, 1):
        q = item["q"]
        rows = search(gh, q, args.limit)
        ran.append(q)
        print(f"  [{idx:02d}/{len(queries)}] {q!r} -> {len(rows)} 条")
        for row in rows:
            name = row.get("fullName") or row.get("nameWithOwner") or ""
            if not name:
                continue
            desc = (row.get("description") or "").strip()
            entry = repos.get(name)
            if entry is None:
                lic = row.get("license") or {}
                entry = {
                    "full_name": name,
                    "url": row.get("url") or f"https://github.com/{name}",
                    "description": desc,
                    "stars": int(row.get("stargazersCount") or 0),
                    "language": row.get("language"),
                    "pushed_at": row.get("pushedAt"),
                    "created_at": row.get("createdAt"),
                    "archived": bool(row.get("isArchived")),
                    "fork": bool(row.get("isFork")),
                    "license": (lic.get("spdxId") or lic.get("name")) if isinstance(lic, dict) else None,
                    "category": classify(name, desc, item["cat"]),
                    "queries": [q],
                    "first_seen": today,
                }
                repos[name] = entry
            else:
                if q not in entry["queries"]:
                    entry["queries"].append(q)
        if idx < len(queries):
            time.sleep(args.sleep)

    if args.keep_missing:
        old = src_lib.load(ROOT)
        for r in old.get("repos", []):
            name = r.get("full_name")
            if name and name not in repos:
                repos[name] = r

    ordered = sorted(repos.values(), key=lambda r: (-r["stars"], r["full_name"]))
    payload = {
        "generated_at": dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "window": {"pushed_since": PUSHED_SINCE},
        "queries": ran,
        "count": len(ordered),
        "repos": ordered,
    }

    cats: dict[str, int] = {}
    for r in ordered:
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    print(f"\n去重后 {len(ordered)} 个仓库；分类: " + ", ".join(f"{k}={v}" for k, v in sorted(cats.items())))

    if args.dry_run:
        print("--dry-run：未写文件")
        return 0

    path = src_lib.save(ROOT, payload)
    print(f"已写入 {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

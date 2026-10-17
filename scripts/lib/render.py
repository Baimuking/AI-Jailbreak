"""README / docs / 站点数据渲染。

设计原则：README 的所有表格都由 build_index.py 从卡片和 sources 现算，
不存在手工维护的重复数据；人工内容只写在 README.template.md 的标记之外。
"""

from __future__ import annotations

import datetime as _dt
from typing import Iterable

from . import sources as src_lib

BEGIN = "<!-- BEGIN:INDEX -->"
END = "<!-- END:INDEX -->"

KIND_LABEL = {"prompt": "提示词", "tool": "工具", "technique": "方法"}
STATUS_LABEL = {
    "verified": "✅ verified",
    "community": "🟡 community",
    "unverified": "⚪ unverified",
    "stale": "🟠 stale",
    "archived": "⚫ archived",
}


def _esc(text: object) -> str:
    """表格单元格转义：竖线与换行会破坏 markdown 表格。"""
    s = "" if text is None else str(text)
    return s.replace("|", "\\|").replace("\n", " ").strip()


def _clip(text: object, n: int) -> str:
    s = _esc(text)
    return s if len(s) <= n else s[: n - 1] + "…"


def _armor(value) -> str:
    if value is None:
        return "—"
    return f"{float(value):.1f}"


def _link(card) -> str:
    return f"[{_esc(card.data['name'])}]({card.path})"


def _models(card) -> str:
    t = card.targets
    return "`all`" if "all" in t else ", ".join(f"`{x}`" for x in t[:4]) + ("…" if len(t) > 4 else "")


def _client_names(card) -> str:
    c = card.clients
    if not c or "all" in c:
        return "all"
    return ", ".join(c[:4]) + ("…" if len(c) > 4 else "")


def _source_cell(card) -> str:
    s = card.data.get("source") or {}
    repo = s.get("repo")
    if not repo:
        return "—"
    lic = s.get("license")
    label = _esc(repo)
    return f"[{label}](https://github.com/{repo})" + (f" · {_esc(lic)}" if lic else "")


def render_tables(cards: list) -> str:
    prompts = sorted(
        [c for c in cards if c.kind == "prompt"],
        key=lambda c: (-(c.strength or 0), c.data["name"].lower()),
    )
    tools = sorted([c for c in cards if c.kind == "tool"], key=lambda c: c.data["name"].lower())
    techs = sorted([c for c in cards if c.kind == "technique"], key=lambda c: c.data["name"].lower())

    out: list[str] = []
    out.append("### 提示词条目\n")
    if not prompts:
        out.append("_暂无。_\n")
    else:
        out.append("| 条目 | 目标模型 | 客户端 | 形态 | 状态 | armor | 来源 |")
        out.append("|---|---|---|---|---|---|---|")
        for c in prompts:
            out.append(
                "| "
                + " | ".join(
                    [
                        _link(c),
                        _models(c),
                        _client_names(c),
                        _esc(c.data.get("archetype", "—")),
                        STATUS_LABEL.get(c.status, c.status),
                        _armor(c.strength),
                        _source_cell(c),
                    ]
                )
                + " |"
            )
        out.append("")

    out.append("### 客户端工具\n")
    if not tools:
        out.append("_暂无。_\n")
    else:
        out.append("| 工具 | 客户端 | 安装 | 卸载 | 状态 | 来源 |")
        out.append("|---|---|---|---|---|---|")
        for c in tools:
            usage = c.data.get("usage") or {}
            inst = usage.get("install")
            unin = usage.get("uninstall")
            out.append(
                "| "
                + " | ".join(
                    [
                        _link(c),
                        _client_names(c),
                        f"`{_esc(inst)}`" if inst else "—",
                        f"`{_esc(unin)}`" if unin else "—",
                        STATUS_LABEL.get(c.status, c.status),
                        _source_cell(c),
                    ]
                )
                + " |"
            )
        out.append("")

    out.append("### 方法学\n")
    if not techs:
        out.append("_暂无。_\n")
    else:
        for c in techs:
            out.append(f"- [{_esc(c.data['name'])}]({c.path}) — {_clip(c.data.get('summary'), 90)}")
        out.append("")
    return "\n".join(out)


def render_sources(data: dict, per_cat: int = 10) -> str:
    if not data or not data.get("repos"):
        return "### 上游仓库目录\n\n_尚未采集。运行 `python scripts/scan.py` 生成。_\n"

    cats = src_lib.by_category(data)
    summary = src_lib.summary(data)
    out: list[str] = []
    out.append("### 上游仓库目录\n")
    out.append(
        f"共收录 **{summary['count']}** 个上游仓库（累计 ★{summary['stars_total']:,}），"
        f"采集时间 {_esc(summary.get('generated_at') or '—')}，"
        f"窗口 pushed_at ≥ {_esc(summary.get('window', {}).get('pushed_since') or '—')}。\n"
    )
    out.append("| 分类 | 含义 | 数量 |")
    out.append("|---|---|---|")
    for key, label in src_lib.CATEGORIES.items():
        n = summary["by_category"].get(key, 0)
        if n:
            out.append(f"| {key} | {label} | {n} |")
    out.append("")
    out.append("<details>\n<summary>展开各分类 Top 仓库（每类前 %d 个，完整清单见 docs/index.json）</summary>\n" % per_cat)
    for key, label in src_lib.CATEGORIES.items():
        items = cats.get(key) or []
        if not items:
            continue
        out.append(f"\n**{key}. {label}**（{len(items)} 个）\n")
        out.append("| # | 仓库 | ★ | 语言 | 最近 push | 简介 |")
        out.append("|---|---|---|---|---|---|")
        for idx, r in enumerate(items[:per_cat], 1):
            name = r.get("full_name", "")
            out.append(
                f"| {idx} | [{_esc(name)}](https://github.com/{name}) | "
                f"{int(r.get('stars') or 0):,} | {_esc(r.get('language') or '—')} | "
                f"{_esc((r.get('pushed_at') or '—')[:10])} | {_clip(r.get('description') or '—', 60)} |"
            )
        out.append("")
    out.append("</details>\n")
    return "\n".join(out)


def render_stats(card_stats: dict, src_summary: dict | None) -> str:
    total = card_stats.get("total", 0)
    verified = card_stats.get("verified", 0)
    n_src = (src_summary or {}).get("count", 0)
    kinds = card_stats.get("by_kind", {})
    lines = [
        "| 指标 | 数值 |",
        "|---|---|",
        f"| 可用条目 | {total} |",
        f"| 其中已实测（verified） | {verified} |",
        f"| 提示词 / 工具 / 方法 | {kinds.get('prompt', 0)} / {kinds.get('tool', 0)} / {kinds.get('technique', 0)} |",
        f"| 上游仓库目录 | {n_src} |",
        "",
    ]
    return "\n".join(lines)


def build_index_payload(cards: list, data: dict) -> dict:
    """docs/index.json 与 site/data.json 共用的结构。

    generated_at 取自 sources 的采集时间（而不是当前时间），
    否则 build_index.py --check 每次都会判定产物过期。
    """
    generated_at = (data or {}).get("generated_at") or _dt.date.today().isoformat()
    return {
        "generated_at": generated_at,
        "stats": {
            "cards": {
                "total": len(cards),
                "by_kind": _count(c.kind for c in cards),
                "by_status": _count(c.status for c in cards),
                "by_archetype": _count(c.data.get("archetype", "?") for c in cards),
            },
            "sources": src_lib.summary(data),
        },
        "cards": [c.to_json() for c in sorted(cards, key=lambda x: x.id)],
        "repos": data.get("repos", []) if data else [],
    }


def _count(items: Iterable[str]) -> dict:
    out: dict[str, int] = {}
    for i in items:
        out[i] = out.get(i, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def render_readme(template: str, cards: list, card_stats: dict, data: dict) -> str:
    block = "\n".join(
        [
            BEGIN,
            "",
            render_stats(card_stats, src_lib.summary(data) if data else None),
            render_tables(cards),
            render_sources(data),
            "_本区块由 `scripts/build_index.py` 自动生成，请勿手工编辑；改内容请改卡片或模板。_",
            "",
            END,
        ]
    )
    if BEGIN in template and END in template:
        head, rest = template.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        return head + block + tail
    return template + "\n\n" + block + "\n"

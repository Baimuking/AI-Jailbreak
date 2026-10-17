#!/usr/bin/env python3
"""pojia —— 破甲条目的命令行入口。

零第三方依赖（只用 stdlib），与 installers/install.ps1、install.sh 共用同一套
托管区块格式，任何一边写入的区块另一边都能识别与卸载。

    pojia list --model glm-5.3 --client codex
    pojia show gpt-5.6-identity-frame
    pojia apply gpt-5.6-identity-frame --client codex
    pojia rollback gpt-5.6-identity-frame --client cursor
    pojia search 翻译
    pojia doctor
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib import cards as cards_lib, sources as src_lib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

CLIENT_TARGETS = {
    "codex": "AGENTS.md",
    "dsh": "AGENTS.md",
    "zcode": "AGENTS.md",
    "antigravity": "AGENTS.md",
    "opencode": "AGENTS.md",
    "all": "AGENTS.md",
    "claude-code": "CLAUDE.md",
    "cursor": ".cursorrules",
    "api": ".pojia/system-prompt.md",
}

BEGIN = "<!-- pojia:begin {id} -->"
END = "<!-- pojia:end {id} -->"
BACKUP_ROOT = ".pojia/backups"


class CliError(RuntimeError):
    pass


def load() -> list:
    return cards_lib.load_cards(ROOT)


def find(cards: list, cid: str):
    for c in cards:
        if c.id == cid:
            return c
    raise CliError(f"没有 id 为 {cid!r} 的条目。用 `pojia list` 查看可用条目。")


def target_path(client: str | None, target: str | None) -> Path:
    if target:
        return Path(target).expanduser().resolve()
    if not client:
        raise CliError("需要 --client 或 --target 之一")
    leaf = CLIENT_TARGETS.get(client)
    if not leaf:
        raise CliError(f"未知客户端 {client!r}，可选：{', '.join(sorted(CLIENT_TARGETS))}")
    return (Path.cwd() / leaf).resolve()


def strip_block(text: str, cid: str) -> str:
    pattern = re.compile(
        r"\n?<!-- pojia:begin " + re.escape(cid) + r" -->.*?<!-- pojia:end " + re.escape(cid) + r" -->\n?",
        re.S,
    )
    return pattern.sub("\n", text)


def has_block(text: str, cid: str) -> bool:
    return BEGIN.format(id=cid) in text


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = Path.cwd() / BACKUP_ROOT / stamp
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / path.name
    shutil.copy2(path, out)
    return out


def cmd_list(args) -> int:
    cards = load()
    rows = []
    for c in cards:
        if args.kind and c.kind != args.kind:
            continue
        if args.status and c.status != args.status:
            continue
        if args.archetype and c.data.get("archetype") != args.archetype:
            continue
        if args.model:
            t = [x.lower() for x in c.targets]
            if "all" not in t and not any(args.model.lower() in x for x in t):
                continue
        if args.client:
            cl = [x.lower() for x in c.clients]
            if "all" not in cl and args.client.lower() not in cl:
                continue
        rows.append(c)

    rows.sort(key=lambda c: (-(c.strength or 0), c.id))
    if args.json:
        print(json.dumps([c.to_json() for c in rows], ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("没有匹配的条目。放宽 --model / --client 再试。")
        return 0
    for c in rows:
        arm = "  —  " if c.strength is None else f"{c.strength:5.1f}"
        print(f"{c.id:<34} {arm}  {c.status:<10} {c.kind:<9} {c.data['name']}")
    print(f"\n共 {len(rows)} 条")
    return 0


def cmd_show(args) -> int:
    card = find(load(), args.id)
    if args.json:
        print(json.dumps(card.to_json(), ensure_ascii=False, indent=2))
        return 0
    text = card.prompt_text
    if args.prompt_only:
        print(text)
        return 0
    d = card.data
    print(f"# {d['name']}  ({d['id']})")
    print(f"kind={d['kind']}  archetype={d.get('archetype')}  status={d['status']}  armor={d.get('strength')}")
    print(f"targets={', '.join(card.targets) or '-'}  clients={', '.join(card.clients) or '-'}")
    src = d.get("source") or {}
    if src.get("repo"):
        print(f"source={src['repo']}  license={src.get('license')}")
    if d.get("summary"):
        print(f"\n{d['summary']}")
    if d.get("notes"):
        print(f"\n[维护者备注]\n{d['notes']}")
    print("\n" + "-" * 60 + "\n")
    print(text or "（该条目没有可注入正文）")
    return 0


def cmd_search(args) -> int:
    needle = args.term.lower()
    hits = []
    for c in load():
        blob = " ".join(
            [
                c.id,
                str(c.data.get("name", "")),
                str(c.data.get("summary", "")),
                " ".join(c.targets),
                " ".join(str(t) for t in c.data.get("tags") or []),
                c.body,
            ]
        ).lower()
        if needle in blob:
            hits.append(c)
    if not hits:
        print(f"没有命中 {args.term!r}")
        return 0
    for c in sorted(hits, key=lambda x: x.id):
        print(f"{c.id:<34} {c.status:<10} {c.data['name']}")
    print(f"\n命中 {len(hits)} 条")
    return 0


def cmd_apply(args) -> int:
    card = find(load(), args.id)
    if card.kind != "prompt":
        raise CliError(f"{card.id} 是 {card.kind} 卡（文档/工具说明），没有可注入正文；只有 kind=prompt 能 apply")
    prompt = card.prompt_text
    if not prompt:
        raise CliError(f"{card.id} 没有可注入正文（kind={card.kind}）")
    path = target_path(args.client, args.target)
    block = f"{BEGIN.format(id=card.id)}\n{prompt.rstrip()}\n{END.format(id=card.id)}"

    if args.dry_run:
        print(f"目标 {path}")
        print("-" * 60)
        print(block)
        print("-" * 60)
        return 0

    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    updated_block = has_block(existing, card.id)
    base = strip_block(existing, card.id) if updated_block else existing
    base = base.rstrip()
    new_text = (base + "\n\n" if base else "") + block + "\n"

    path.parent.mkdir(parents=True, exist_ok=True)
    bk = backup(path)
    path.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"{'更新' if updated_block else '注入'} {card.id} -> {path}")
    if bk:
        print(f"备份 {bk}")
    return 0


def cmd_rollback(args) -> int:
    path = target_path(args.client, args.target)
    if not path.exists():
        print(f"{path} 不存在，无需回滚")
        return 0
    text = path.read_text(encoding="utf-8")
    if not has_block(text, args.id):
        print(f"{path} 中没有 {args.id} 的托管区块")
        return 0
    new_text = strip_block(text, args.id).rstrip() + "\n"
    bk = backup(path)
    path.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"已移除 {args.id} <- {path}")
    if bk:
        print(f"备份 {bk}")
    return 0


def cmd_recommend(args) -> int:
    """按目标模型 / 客户端挑出最合适的一条或多条。

    排序优先级：kind=prompt > targets 精确命中 > 含 all > 状态 > armor 分。
    这是 agent 调用本仓库的主入口（--json 便于程序解析）。
    """
    cards = [c for c in load() if c.kind == "prompt"]
    model = (args.model or "").lower()
    client = (args.client or "").lower()

    def score(c) -> tuple:
        targets = [t.lower() for t in c.targets]
        exact = 1 if model and any(model == t or model in t or t in model for t in targets) else 0
        generic = 1 if "all" in targets else 0
        cl = [x.lower() for x in c.clients]
        cl_hit = 1 if client and (client in cl or "all" in cl) else 0
        status_rank = {"verified": 4, "community": 3, "unverified": 2, "stale": 1, "archived": 0}.get(c.status, 0)
        return (exact, cl_hit, generic, status_rank, c.strength or 0)

    ranked = sorted(cards, key=score, reverse=True)
    if model:
        ranked = [c for c in ranked if score(c)[0] or score(c)[2]]
    if args.limit:
        ranked = ranked[: args.limit]

    def pick_client(c) -> str:
        """安装时优先用用户指定的客户端，其次卡片里排第一的。"""
        if client and client in [x.lower() for x in c.clients]:
            return client
        return c.clients[0] if c.clients else "all"

    if args.json:
        out = []
        for c in ranked:
            item = c.to_json()
            cl = pick_client(c)
            item["install"] = {
                "client": cl,
                "pwsh": f"pwsh -File installers/install.ps1 -Id {c.id} -Client {cl}",
                "bash": f"bash installers/install.sh --id {c.id} --client {cl}",
                "cli": f"python cli/pojia.py apply {c.id} --client {cl}",
            }
            out.append(item)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if not ranked:
        print("没有匹配的条目。用 `pojia list` 看全部，或去掉 --model 再试。")
        return 0
    for c in ranked:
        arm = "  —  " if c.strength is None else f"{c.strength:5.1f}"
        print(f"{c.id:<32} {arm}  {c.status:<10} model={','.join(c.targets)}")
        print(f"{'':<32}  → python cli/pojia.py apply {c.id} --client {pick_client(c)}")
    print(f"\n推荐 {len(ranked)} 条（按匹配度与状态排序）")
    return 0


def cmd_stats(args) -> int:
    cards = load()
    st = cards_lib.stats(cards)
    data = src_lib.load(ROOT)
    ss = src_lib.summary(data)
    print(f"条目总数      {st['total']}")
    print(f"按类型        {st['by_kind']}")
    print(f"按状态        {st['by_status']}")
    print(f"按形态        {st['by_archetype']}")
    print(f"上游仓库      {ss['count']}（累计 ★{ss['stars_total']:,}）")
    print(f"采集时间      {ss.get('generated_at') or '—'}")
    return 0


def cmd_doctor(args) -> int:
    ok = True
    print(f"仓库根        {ROOT}")
    print(f"Python        {sys.version.split()[0]}")

    schema = ROOT / "schema" / "card.schema.json"
    print(f"schema        {'OK' if schema.exists() else '缺失'}")
    ok &= schema.exists()

    cards = load()
    print(f"卡片          {len(cards)} 张")
    ok &= len(cards) > 0

    data = src_lib.load(ROOT)
    print(f"上游仓库      {len(data.get('repos', []))} 个")

    for rel in ("README.md", "docs/index.json", "site/data.json"):
        p = ROOT / rel
        print(f"{rel:<22}{'OK' if p.exists() else '缺失（运行 build_index.py）'}")

    sample = cards[0].id if cards else None
    if sample and (ROOT / "docs" / "prompts" / f"{sample}.txt").exists():
        print("正文导出      OK")
    else:
        print("正文导出      缺失（运行 build_index.py）")

    print("\n环境" + ("正常" if ok else "有问题"))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pojia", description="破甲条目索引与安装器")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="按条件列出条目")
    p.add_argument("--kind", choices=["prompt", "tool", "technique"])
    p.add_argument("--status")
    p.add_argument("--archetype")
    p.add_argument("--model")
    p.add_argument("--client")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="查看条目与正文")
    p.add_argument("id")
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt-only", action="store_true")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("search", help="全文检索")
    p.add_argument("term")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("recommend", help="按模型/客户端推荐条目（agent 主入口）")
    p.add_argument("--model")
    p.add_argument("--client")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_recommend)

    p = sub.add_parser("apply", help="注入到客户端配置")
    p.add_argument("id")
    p.add_argument("--client")
    p.add_argument("--target")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("rollback", help="移除已注入的条目")
    p.add_argument("id")
    p.add_argument("--client")
    p.add_argument("--target")
    p.set_defaults(func=cmd_rollback)

    p = sub.add_parser("stats", help="统计")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("doctor", help="自检")
    p.set_defaults(func=cmd_doctor)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except CliError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

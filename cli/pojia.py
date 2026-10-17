#!/usr/bin/env python3
"""pojia —— 破甲条目的命令行入口。

零第三方依赖（只用 stdlib），与 installers/install.ps1、install.sh 共用同一套
托管区块格式，任何一边写入的区块另一边都能识别与卸载。

最省事的用法（不需要 id，也不需要记客户端）：

    pojia install                      # 交互式向导，问两个问题就装好
    pojia apply --model glm-5.3        # 自动挑一条并装到探测到的配置文件
    pojia apply glm-5.3-identity-frame # 知道 id 就直接装
    pojia status                       # 看当前项目装了哪些
    pojia rollback glm-5.3-identity-frame
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

# 客户端 -> 默认写入的文件
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

# 文件 -> 它一次覆盖的客户端（避免用户重复装同一个文件）
TARGET_COVERS = {
    "AGENTS.md": ["codex", "dsh", "zcode", "antigravity", "opencode", "all"],
    "CLAUDE.md": ["claude-code"],
    ".cursorrules": ["cursor"],
    ".pojia/system-prompt.md": ["api"],
}

DEFAULT_CLIENT = "codex"

BEGIN = "<!-- pojia:begin {id} -->"
END = "<!-- pojia:end {id} -->"
BACKUP_ROOT = ".pojia/backups"
RAW_BASE = "https://raw.githubusercontent.com/Baimuking/AI-Jailbreak/main"


class CliError(RuntimeError):
    pass


# ---------------------------------------------------------------- 基础

def load() -> list:
    return cards_lib.load_cards(ROOT)


def find(cards: list, cid: str):
    for c in cards:
        if c.id == cid:
            return c
    raise CliError(f"没有 id 为 {cid!r} 的条目。用 `pojia list` 查看可用条目。")


def detect_targets(base: Path) -> list[str]:
    """探测当前项目里已存在的配置文件，按优先顺序返回相对路径。"""
    found = []
    for rel in ("AGENTS.md", "CLAUDE.md", ".cursorrules", ".pojia/system-prompt.md"):
        if (base / rel).exists():
            found.append(rel)
    if (base / ".cursor").is_dir() and ".cursorrules" not in found:
        found.append(".cursorrules")
    return found


def resolve_target(rel: str) -> Path:
    return (Path.cwd() / rel).resolve()


def rank_prompts(cards: list, model: str | None, client: str | None) -> list:
    """按「模型精确命中 > 客户端命中 > all 兜底 > 状态 > 分数」排序。"""
    model = (model or "").lower()
    client = (client or "").lower()
    pool = [c for c in cards if c.kind == "prompt"]

    def key(c) -> tuple:
        targets = [t.lower() for t in c.targets]
        exact = 1 if model and any(model == t or model in t or t in model for t in targets) else 0
        generic = 1 if "all" in targets else 0
        cl = [x.lower() for x in c.clients]
        cl_hit = 1 if client and (client in cl or "all" in cl) else 0
        status_rank = {"verified": 4, "community": 3, "unverified": 2, "stale": 1, "archived": 0}.get(c.status, 0)
        return (exact, cl_hit, generic, status_rank, c.strength or 0)

    ranked = sorted(pool, key=key, reverse=True)
    if model:
        ranked = [c for c in ranked if key(c)[0] or key(c)[2]]
    return ranked


def best_client_for(card, requested: str | None) -> str:
    """安装时优先用用户指定的客户端，其次卡片里的第一个。"""
    req = (requested or "").lower()
    if req and req in [x.lower() for x in card.clients]:
        return req
    if requested and requested in CLIENT_TARGETS:
        return requested
    return card.clients[0] if card.clients else "all"


# ---------------------------------------------------------------- 托管区块

def strip_block(text: str, cid: str) -> str:
    """移除托管区块，并归一化尾随换行。

    归一化规则（三个实现必须一致）：区块外内容末尾的连续换行压成一个；
    结果为空则返回空串。这样「原文件以单个换行结尾」这个主流情况下是逐字节还原。
    """
    pattern = re.compile(
        r"\r?\n?<!-- pojia:begin " + re.escape(cid) + r" -->.*?<!-- pojia:end " + re.escape(cid) + r" -->\r?\n?",
        re.S,
    )
    out = pattern.sub("", text)
    stripped = out.rstrip("\r\n")
    return stripped + "\n" if stripped.strip() else ""


def has_block(text: str, cid: str) -> bool:
    return BEGIN.format(id=cid) in text


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    # 毫秒精度：同一秒内连续操作（apply 后立刻 rollback）不能撞同一个目录
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    dest = Path.cwd() / BACKUP_ROOT / stamp
    n = 1
    while dest.exists():
        n += 1
        dest = Path.cwd() / BACKUP_ROOT / f"{stamp}-{n}"
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / path.name
    shutil.copy2(path, out)
    return out


def install_into(path: Path, card, prompt: str, dry_run: bool) -> tuple[bool, Path | None]:
    """把卡片写进 path；返回 (是否是更新, 备份路径)。"""
    block = f"{BEGIN.format(id=card.id)}\n{prompt.rstrip()}\n{END.format(id=card.id)}"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    updated_block = has_block(existing, card.id)
    base = strip_block(existing, card.id) if updated_block else existing
    base = base.rstrip()
    new_text = (base + "\n\n" if base else "") + block + "\n"
    if dry_run:
        return updated_block, None
    path.parent.mkdir(parents=True, exist_ok=True)
    bk = backup(path)
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return updated_block, bk


# ---------------------------------------------------------------- 命令

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


def cmd_recommend(args) -> int:
    ranked = rank_prompts(load(), args.model, args.client)
    if args.limit:
        ranked = ranked[: args.limit]
    if args.json:
        out = []
        for c in ranked:
            item = c.to_json()
            cl = best_client_for(c, args.client)
            item["install"] = {
                "client": cl,
                "cli": f"python cli/pojia.py apply {c.id} --client {cl}",
                "pwsh": f"pwsh -File installers/install.ps1 -Id {c.id} -Client {cl}",
                "bash": f"bash installers/install.sh --id {c.id} --client {cl}",
                "one_line_windows": (
                    f'$s="$env:TEMP\\pojia.ps1"; irm {RAW_BASE}/installers/install.ps1 -OutFile $s; '
                    f"pwsh -File $s -Id {c.id} -Client {cl}"
                ),
                "one_line_unix": (
                    f"curl -fsSL {RAW_BASE}/installers/install.sh | bash -s -- --id {c.id} --client {cl}"
                ),
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
        print(f"{'':<32}  → pojia apply {c.id} --client {best_client_for(c, args.client)}")
    print(f"\n推荐 {len(ranked)} 条（按匹配度与状态排序）")
    return 0


def _do_apply(cards: list, *, cid: str | None, model: str | None, client: str | None,
              target: str | None, all_detected: bool, dry_run: bool, yes: bool,
              quiet: bool = False) -> int:
    # 1. 选卡片
    if cid:
        card = find(cards, cid)
        if card.kind != "prompt":
            raise CliError(f"{card.id} 是 {card.kind} 卡（文档/工具说明），没有可注入正文；只有 kind=prompt 能装")
    else:
        ranked = rank_prompts(cards, model, client)
        if not ranked:
            raise CliError("没有可用的破甲卡")
        card = ranked[0]
        if not quiet:
            print(f"自动选择: {card.id}  ({card.data['name']})")

    prompt = card.prompt_text
    if not prompt:
        raise CliError(f"{card.id} 没有可注入正文")

    # 2. 选目标文件
    if target:
        targets = [target]
    elif all_detected:
        targets = detect_targets(Path.cwd()) or ["AGENTS.md"]
    else:
        detected = detect_targets(Path.cwd())
        if client:
            targets = [CLIENT_TARGETS.get(client, "AGENTS.md")]
        elif detected:
            # 探测到多个时，优先 AGENTS.md（覆盖面最广）
            targets = ["AGENTS.md"] if "AGENTS.md" in detected else [detected[0]]
            if not quiet:
                print(f"探测到: {', '.join(detected)} → 写入 {targets[0]}（用 --all 可全部写入）")
        else:
            targets = ["AGENTS.md"]
            if not quiet:
                print("未探测到已有配置，新建 AGENTS.md")

    # 3. 确认
    if not yes and not dry_run and sys.stdin.isatty():
        names = ", ".join(str(resolve_target(t)) for t in targets)
        ans = input(f"把 {card.id} 写入 {names}？[Y/n] ").strip().lower()
        if ans and ans not in ("y", "yes"):
            print("已取消")
            return 1

    # 4. 写入
    rc = 0
    for rel in targets:
        path = resolve_target(rel)
        was_update, bk = install_into(path, card, prompt, dry_run)
        if dry_run:
            print(f"[dry-run] 将{'更新' if was_update else '写入'} {card.id} -> {path}")
            print("-" * 60)
            print(prompt.rstrip())
            print("-" * 60)
        else:
            print(f"{'更新' if was_update else '注入'} {card.id} -> {path}")
            if bk:
                print(f"备份 {bk}")
    if not dry_run:
        print(f"\n完成。回滚: pojia rollback {card.id}" + (f" --target {targets[0]}" if len(targets) == 1 else " --all"))
    return rc


def cmd_apply(args) -> int:
    return _do_apply(
        load(),
        cid=args.id,
        model=args.model,
        client=args.client,
        target=args.target,
        all_detected=args.all,
        dry_run=args.dry_run,
        yes=args.yes,
    )


def cmd_install(args) -> int:
    """无参数向导：问两个问题就把破甲装好。"""
    cards = load()
    if not sys.stdin.isatty():
        print("非交互环境，请直接用：pojia apply --model <模型> --client <客户端>", file=sys.stderr)
        return 2

    prompts = [c for c in cards if c.kind == "prompt"]
    models = sorted({t for c in prompts for t in c.targets if t != "all"})

    print("== pojia 向导 ==")
    print("\n可用模型：")
    for i, m in enumerate(models, 1):
        print(f"  {i:2d}. {m}")
    print(f"   {len(models) + 1:2d}. 其它 / 不知道（用模型无关的通用帧）")
    raw = input("\n选择模型编号（回车=最后一项）: ").strip()
    if not raw:
        model = None
    else:
        try:
            idx = int(raw)
            model = models[idx - 1] if 1 <= idx <= len(models) else None
        except ValueError:
            model = raw  # 直接输了模型名

    clients = ["codex", "claude-code", "cursor", "dsh", "zcode", "antigravity", "api"]
    detected = detect_targets(Path.cwd())
    print("\n客户端：")
    for i, cl in enumerate(clients, 1):
        mark = " *已存在" if any(cl in TARGET_COVERS.get(t, []) for t in detected) else ""
        print(f"  {i}. {cl:<12}{mark}")
    raw = input("\n选择客户端编号（回车=codex）: ").strip()
    client = clients[int(raw) - 1] if raw.isdigit() and 1 <= int(raw) <= len(clients) else "codex"

    ranked = rank_prompts(cards, model, client)
    if not ranked:
        print("没有合适的条目")
        return 1
    card = ranked[0]
    print(f"\n推荐: {card.id}  ({card.data['name']})")
    print(f"形态: {card.data.get('archetype')}  状态: {card.status}  armor: {card.strength or '未实测'}")
    print(f"目标模型: {', '.join(card.targets)}")
    if card.data.get("summary"):
        print(f"说明: {card.data['summary']}")
    if ranked[1:]:
        print(f"备选: {', '.join(c.id for c in ranked[1:3])}")

    ans = input("\n写入当前项目？[Y/n] ").strip().lower()
    if ans and ans not in ("y", "yes"):
        print("已取消。可先用 `pojia show <id>` 看正文。")
        return 1

    return _do_apply(cards, cid=card.id, model=model, client=client, target=None,
                     all_detected=False, dry_run=False, yes=True, quiet=True)


def cmd_rollback(args) -> int:
    cards = load()
    if args.id:
        ids = [find(cards, args.id).id]
    else:
        ids = None  # 全部

    if args.target:
        paths = [resolve_target(args.target)]
    elif args.all:
        paths = [resolve_target(t) for t in detect_targets(Path.cwd())]
    else:
        paths = [resolve_target("AGENTS.md")]

    total = 0
    for path in paths:
        if not path.exists():
            print(f"{path} 不存在，跳过")
            continue
        text = path.read_text(encoding="utf-8")
        found = ids if ids else re.findall(r"<!-- pojia:begin ([^\s]+) -->", text)
        for cid in found:
            if not has_block(text, cid):
                continue
            text = strip_block(text, cid).rstrip() + "\n"
            total += 1
            print(f"已移除 {cid} <- {path}")
        if found:
            bk = backup(path)
            path.write_text(text, encoding="utf-8", newline="\n")
            if bk:
                print(f"备份 {bk}")
    if total == 0:
        print("没有找到可移除的托管区块")
    return 0


def cmd_status(args) -> int:
    print(f"目录 {Path.cwd()}")
    files = detect_targets(Path.cwd())
    if not files:
        print("未发现任何配置文件（AGENTS.md / CLAUDE.md / .cursorrules）")
        print("下一步: pojia install")
        return 0
    total = 0
    for rel in files:
        path = resolve_target(rel)
        text = path.read_text(encoding="utf-8")
        ids = re.findall(r"<!-- pojia:begin ([^\s]+) -->", text)
        covers = ", ".join(TARGET_COVERS.get(rel, []))
        print(f"\n{rel}  （覆盖客户端: {covers}）")
        if not ids:
            print("  未安装任何条目")
            continue
        for cid in ids:
            total += 1
            try:
                card = find(load(), cid)
                print(f"  ✓ {cid:<34} {card.data['name']}")
            except CliError:
                print(f"  ? {cid:<34} （仓库中已无此条目，可能是旧版或拼写错误）")
    backups = sorted((Path.cwd() / BACKUP_ROOT).glob("*")) if (Path.cwd() / BACKUP_ROOT).exists() else []
    print(f"\n共 {total} 条已安装；备份 {len(backups)} 份在 {BACKUP_ROOT}/")
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

    for rel in ("README.md", "docs/index.json", "site/data.json", "manifest.json", "llms.txt"):
        p = ROOT / rel
        print(f"{rel:<22}{'OK' if p.exists() else '缺失（运行 build_index.py）'}")

    sample = cards[0].id if cards else None
    if sample and (ROOT / "docs" / "prompts" / f"{sample}.txt").exists():
        print("正文导出      OK")
    else:
        print("正文导出      缺失（运行 build_index.py）")

    print(f"当前目录      {Path.cwd()}  （已装 {len(detect_targets(Path.cwd()))} 个配置文件）")
    print("\n环境" + ("正常" if ok else "有问题"))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="pojia",
        description="破甲条目索引与安装器",
        epilog="最省事：pojia install（向导） 或 pojia apply --model <模型>",
    )
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

    p = sub.add_parser("recommend", help="按模型/客户端推荐（agent 主入口）")
    p.add_argument("--model")
    p.add_argument("--client")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_recommend)

    p = sub.add_parser("apply", help="安装条目（可省略 id，自动挑选）")
    p.add_argument("id", nargs="?", help="条目 id；省略则按 --model 自动挑")
    p.add_argument("--model", help="目标模型，用于自动挑选")
    p.add_argument("--client", help="codex / claude-code / cursor / dsh / zcode / antigravity / api")
    p.add_argument("--target", help="直接指定目标文件")
    p.add_argument("--all", action="store_true", help="写入所有探测到的配置文件")
    p.add_argument("--dry-run", action="store_true", help="只预览不写入")
    p.add_argument("--yes", "-y", action="store_true", help="跳过确认")
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("install", help="交互式向导（零参数）")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("rollback", help="移除已安装的条目")
    p.add_argument("id", nargs="?", help="省略则移除当前文件里的全部托管区块")
    p.add_argument("--client")
    p.add_argument("--target")
    p.add_argument("--all", action="store_true", help="对全部探测到的文件生效")
    p.set_defaults(func=cmd_rollback)

    p = sub.add_parser("status", help="查看当前项目装了哪些破甲")
    p.set_defaults(func=cmd_status)

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
    except KeyboardInterrupt:
        print("\n已中断")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

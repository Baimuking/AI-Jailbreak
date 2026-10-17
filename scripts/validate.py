#!/usr/bin/env python3
"""校验仓库全部卡片与 sources 数据。

用法：
    python scripts/validate.py            # 校验
    python scripts/validate.py --strict   # 额外要求：prompt 卡必须有正文、id 与文件名一致
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import cards as cards_lib, schema, sources as src_lib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REQUIRED_SRC_KEYS = ("full_name", "url", "stars", "category", "pushed_at")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    schema_path = ROOT / "schema" / "card.schema.json"
    card_schema = json.loads(schema_path.read_text(encoding="utf-8"))

    loaded = cards_lib.load_cards(ROOT)
    errors: list[str] = []
    warnings: list[str] = []

    if not loaded:
        warnings.append("prompts/ tools/ techniques/ 下没有任何卡片")

    for card in loaded:
        for err in schema.validate(card.data, card_schema, path=card.path):
            errors.append(err)
        stem = Path(card.path).stem
        if stem != card.id:
            errors.append(f"{card.path}: 文件名 {stem!r} 与 id {card.id!r} 不一致")
        if card.kind == "prompt":
            if not card.prompt_text:
                msg = f"{card.path}: prompt_file 指向的文件缺失或为空"
                (errors if args.strict else warnings).append(msg)
        src = card.data.get("source") or {}
        if src.get("repo") and not src.get("license"):
            warnings.append(f"{card.path}: 上游未声明 license，只允许保留链接不落正文")

    for dup_id, paths in cards_lib.duplicates(loaded).items():
        errors.append(f"重复 id {dup_id!r}: {', '.join(paths)}")

    data = src_lib.load(ROOT)
    for repo in data.get("repos", []):
        for key in REQUIRED_SRC_KEYS:
            if key not in repo:
                errors.append(f"sources: {repo.get('full_name', '?')} 缺少字段 {key}")
        if repo.get("category") not in src_lib.CATEGORIES:
            errors.append(f"sources: {repo.get('full_name')} 分类非法 {repo.get('category')!r}")
    if not data.get("repos"):
        warnings.append("sources/sources.json 为空，运行 python scripts/scan.py 采集")

    st = cards_lib.stats(loaded)
    print(f"卡片 {st['total']} 张 {st['by_kind']}")
    print(f"上游仓库 {len(data.get('repos', []))} 个")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\n校验失败：{len(errors)} 个错误")
        return 1
    print("\n校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

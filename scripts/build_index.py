#!/usr/bin/env python3
"""重建全部派生视图：README 索引、docs/index.json、site/data.json。

用法：
    python scripts/build_index.py          # 生成
    python scripts/build_index.py --check  # CI 用：若产物与磁盘不一致则失败
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import cards as cards_lib, render, sources as src_lib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def build() -> dict[str, str]:
    """返回 {相对路径: 新内容}。"""
    loaded = cards_lib.load_cards(ROOT)
    st = cards_lib.stats(loaded)
    data = src_lib.load(ROOT)

    template_path = ROOT / "README.template.md"
    if not template_path.exists():
        raise SystemExit("缺少 README.template.md")
    template = template_path.read_text(encoding="utf-8")

    payload = render.build_index_payload(loaded, data)
    outputs = {
        "README.md": render.render_readme(template, loaded, st, data),
        "docs/index.json": json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        "site/data.json": json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    }

    # 安装器只需纯正文，不必解析 front matter：单独导出 docs/prompts/<id>.txt
    # 只导出 kind=prompt；tool/technique 卡是文档，不该被当成提示词注入
    for card in loaded:
        if card.kind != "prompt":
            continue
        text = card.prompt_text
        if text:
            outputs[f"docs/prompts/{card.id}.txt"] = text.rstrip() + "\n"
    return outputs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只比对，不写盘")
    args = ap.parse_args()

    outputs = build()
    stale: list[str] = []
    for rel, content in outputs.items():
        path = ROOT / rel
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old == content:
            continue
        stale.append(rel)
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"写入 {rel}")

    if args.check:
        if stale:
            print("以下产物需要重新生成（运行 python scripts/build_index.py）:")
            for rel in stale:
                print(f"  - {rel}")
            return 1
        print("产物已是最新")
        return 0

    if not stale:
        print("无变化")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

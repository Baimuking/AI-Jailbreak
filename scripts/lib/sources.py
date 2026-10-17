"""上游仓库目录（sources）的读写。

sources/sources.json 是采集器的产物，也是 README/docs/site 的上游数据源。
字段口径与 GitHub Search API 对齐，便于每日 diff。
"""

from __future__ import annotations

import json
from pathlib import Path

CATEGORIES = {
    "A": "中文破甲/破限生态",
    "B": "中文越狱提示词/项目",
    "C": "英文越狱工具与提示词库",
    "D": "提示词注入/泄露",
    "E": "去审查/abliteration 模型与数据",
    "F": "红队评测/安全基准/防御",
    "G": "弱相关 AI 安全",
    "Z": "其他",
}

DEFAULT_PATH = "sources/sources.json"


def load(root: str | Path) -> dict:
    path = Path(root) / DEFAULT_PATH
    if not path.exists():
        return {"generated_at": None, "count": 0, "repos": [], "queries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(root: str | Path, data: dict) -> Path:
    path = Path(root) / DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def by_category(data: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {k: [] for k in CATEGORIES}
    for repo in data.get("repos", []):
        cat = repo.get("category", "Z")
        out.setdefault(cat, []).append(repo)
    for cat in out:
        out[cat].sort(key=lambda r: (-int(r.get("stars") or 0), r.get("full_name", "")))
    return out


def summary(data: dict) -> dict:
    repos = data.get("repos", [])
    cats = by_category(data)
    return {
        "count": len(repos),
        "by_category": {k: len(v) for k, v in cats.items()},
        "stars_total": sum(int(r.get("stars") or 0) for r in repos),
        "generated_at": data.get("generated_at"),
        "window": data.get("window", {}),
    }

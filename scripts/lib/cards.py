"""卡片加载与归一化。

约定：
  - 每张卡是一个 .md 文件，带 --- YAML front matter ---
  - 卡片 id 必须等于文件名 stem，且全局唯一
  - kind=prompt 的卡带 prompt_file，指向可复制的提示词正文
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import quality as quality_lib, yamlmini

CARD_DIRS = ("prompts", "tools", "techniques")
REQUIRED_KEYS = ("id", "name", "kind", "status", "language", "targets", "archetype", "added", "updated")


@dataclass
class Card:
    data: dict
    body: str
    path: str          # 相对仓库根的 POSIX 路径
    abs_path: Path
    _qcache: dict = field(default_factory=dict, repr=False, compare=False)

    def __getattr__(self, item: str) -> Any:
        try:
            return self.data[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    @property
    def id(self) -> str:
        return self.data["id"]

    @property
    def kind(self) -> str:
        return self.data["kind"]

    @property
    def status(self) -> str:
        return self.data["status"]

    @property
    def strength(self) -> float | None:
        return self.data.get("strength")

    @property
    def targets(self) -> list[str]:
        return list(self.data.get("targets") or [])

    @property
    def clients(self) -> list[str]:
        return list(self.data.get("clients") or [])

    @property
    def prompt_text(self) -> str:
        """返回可注入的提示词正文；无正文时返回空串。"""
        rel = self.data.get("prompt_file")
        if not rel:
            return self.body.strip()
        target = (self.abs_path.parent / rel).resolve()
        if not target.exists():
            return ""
        return target.read_text(encoding="utf-8").strip()

    def quality(self) -> tuple[float | None, dict[str, float]]:
        """结构完备度（0-10）。只对 kind=prompt 有意义。

        缓存在 _qcache，不写进 data，避免污染 schema 校验与 manifest 输出。
        """
        if "q" in self._qcache:
            return self._qcache["q"]
        if self.kind != "prompt":
            result: tuple[float | None, dict[str, float]] = (None, {})
        else:
            text = self.prompt_text
            result = quality_lib.score_text(text) if text else (None, {})
        self._qcache["q"] = result
        return result

    def quality_score(self) -> float | None:
        return self.quality()[0]

    def to_json(self) -> dict:
        d = dict(self.data)
        q, detail = self.quality()
        d["path"] = self.path
        d["body"] = self.body.strip()
        d["prompt_text"] = self.prompt_text
        d["quality"] = q
        d["quality_detail"] = detail
        return d


def load_cards(root: str | os.PathLike) -> list[Card]:
    root_p = Path(root)
    cards: list[Card] = []
    for sub in CARD_DIRS:
        base = root_p / sub
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name.startswith("_"):
                continue
            raw = path.read_text(encoding="utf-8")
            data, body = yamlmini.parse_front_matter(raw)
            cards.append(
                Card(
                    data=data,
                    body=body,
                    path=path.relative_to(root_p).as_posix(),
                    abs_path=path,
                )
            )
    return cards


def duplicates(cards: Iterable[Card]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for c in cards:
        seen.setdefault(c.id, []).append(c.path)
    return {k: v for k, v in seen.items() if len(v) > 1}


def stats(cards: list[Card]) -> dict:
    by_kind: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_archetype: dict[str, int] = {}
    for c in cards:
        by_kind[c.kind] = by_kind.get(c.kind, 0) + 1
        by_status[c.status] = by_status.get(c.status, 0) + 1
        by_archetype[c.data.get("archetype", "?")] = by_archetype.get(c.data.get("archetype", "?"), 0) + 1
    return {
        "total": len(cards),
        "by_kind": dict(sorted(by_kind.items())),
        "by_status": dict(sorted(by_status.items())),
        "by_archetype": dict(sorted(by_archetype.items(), key=lambda kv: -kv[1])),
        "verified": by_status.get("verified", 0),
    }

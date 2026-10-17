"""依赖零外部包的 YAML 子集解析/序列化器。

只支持本仓库卡片头与 sources 文件实际使用的语法：
  - 块状映射（缩进嵌套，最多两级使用）
  - 块状列表（`- item`）
  - 行内列表（`[a, b, c]`）
  - 标量：字符串（可带引号）、整数、浮点、true/false/null、ISO 日期（保留为字符串）
  - `#` 注释（仅整行或行尾前有空格时）

不追求 YAML 规范完整性；这样做的理由是仓库必须能在只有 stdlib 的
环境（含 GitHub Actions 裸 ubuntu runner）里跑通，不需要 pip install。
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["parse", "dump", "parse_front_matter", "YamlError"]

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class YamlError(ValueError):
    """解析失败。"""


def _strip_comment(line: str) -> str:
    """去掉行尾注释：只认空白后跟 # 的情况，避免误伤 URL 中的 #。"""
    out = []
    in_s = in_d = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "#" and not in_s and not in_d and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(text: str) -> Any:
    text = text.strip()
    if text == "":
        return None
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        inner = text[1:-1]
        if text[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        else:
            inner = inner.replace("''", "'")
        return inner
    if text.startswith("[") and text.endswith("]"):
        body = text[1:-1].strip()
        if not body:
            return []
        items, buf, in_s = [], [], False
        quote = ""
        for ch in body:
            if in_s:
                buf.append(ch)
                if ch == quote:
                    in_s = False
            elif ch in "\"'":
                in_s = True
                quote = ch
                buf.append(ch)
            elif ch == ",":
                items.append(_scalar("".join(buf)))
                buf = []
            else:
                buf.append(ch)
        if "".join(buf).strip():
            items.append(_scalar("".join(buf)))
        return items
    low = text.lower()
    if low in ("null", "~", "none"):
        return None
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if _DATE_RE.match(text):
        return text  # 保持字符串，避免时区/类型歧义
    if _INT_RE.match(text):
        return int(text)
    if _FLOAT_RE.match(text):
        return float(text)
    return text


def parse(text: str) -> Any:
    """解析一段 YAML 子集文本。"""
    lines: list[tuple[int, str]] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if not raw.strip():
            continue
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        if stripped.lstrip().startswith("#"):
            continue
        if "\t" in stripped[: len(stripped) - len(stripped.lstrip())]:
            raise YamlError("缩进不能用 Tab: %r" % raw)
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped[indent:].rstrip()))
    if not lines:
        return {}
    value, idx = _parse_block(lines, 0, lines[0][0])
    if idx != len(lines):
        raise YamlError("存在无法归属的行: %r" % (lines[idx],))
    return value


def _parse_block(lines: list[tuple[int, str]], i: int, indent: int) -> tuple[Any, int]:
    if lines[i][0] != indent:
        raise YamlError("缩进不一致: %r" % (lines[i],))
    if lines[i][1].startswith("-"):
        out_list: list[Any] = []
        while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("-"):
            body = lines[i][1][1:].strip()
            if not body:
                i += 1
                if i < len(lines) and lines[i][0] > indent:
                    val, i = _parse_block(lines, i, lines[i][0])
                    out_list.append(val)
                else:
                    out_list.append(None)
                continue
            if ": " in body and not body.startswith(("[", "{", '"', "'")):
                # 列表内的行内映射：- key: value
                m: dict[str, Any] = {}
                k, _, v = body.partition(":")
                m[k.strip()] = _scalar(v) if v.strip() else None
                out_list.append(m)
                i += 1
                continue
            out_list.append(_scalar(body))
            i += 1
        return out_list, i

    out_map: dict[str, Any] = {}
    while i < len(lines) and lines[i][0] == indent:
        content = lines[i][1]
        if content.startswith("-"):
            break
        key, sep, rest = content.partition(":")
        if not sep:
            raise YamlError("缺少冒号的行: %r" % content)
        key = key.strip()
        rest = rest.strip()
        i += 1
        if rest in ("|", "|-", "|+", ">", ">-", ">+"):
            # 块标量：收集所有更深缩进的行，按最小缩进还原相对缩进
            run: list[tuple[int, str]] = []
            while i < len(lines) and lines[i][0] > indent:
                run.append(lines[i])
                i += 1
            if not run:
                out_map[key] = ""
                continue
            base = min(l[0] for l in run)
            parts = [" " * (l[0] - base) + l[1] for l in run]
            joined = "\n".join(parts) if rest.startswith("|") else " ".join(p.strip() for p in parts)
            out_map[key] = joined.rstrip("\n") if rest.endswith("-") else joined + "\n"
        elif rest:
            out_map[key] = _scalar(rest)
        else:
            if i < len(lines) and lines[i][0] > indent:
                val, i = _parse_block(lines, i, lines[i][0])
                out_map[key] = val
            else:
                out_map[key] = None
    return out_map, i


def dump(obj: Any, indent: int = 0) -> str:
    """把 dict/list/scalar 序列化成上述子集风格的 YAML。"""
    pad = " " * indent
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append(f"{pad}{k}:")
                out.append(dump(v, indent + 2))
            elif isinstance(v, list) and not v:
                out.append(f"{pad}{k}: []")
            elif isinstance(v, dict) and not v:
                out.append(f"{pad}{k}: {{}}")
            else:
                out.append(f"{pad}{k}: {_fmt_scalar(v)}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, dict):
                first = True
                for k, vv in v.items():
                    prefix = f"{pad}- " if first else f"{pad}  "
                    first = False
                    if isinstance(vv, (dict, list)) and vv:
                        out.append(f"{prefix}{k}:")
                        out.append(dump(vv, indent + 4))
                    else:
                        out.append(f"{prefix}{k}: {_fmt_scalar(vv)}")
            else:
                out.append(f"{pad}- {_fmt_scalar(v)}")
    else:
        out.append(f"{pad}{_fmt_scalar(obj)}")
    return "\n".join(out)


def _fmt_scalar(v: Any) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    if s == "" or s != s.strip() or any(c in s for c in ":#[]{}'\"") or s.lower() in (
        "null",
        "true",
        "false",
        "yes",
        "no",
    ):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def parse_front_matter(text: str) -> tuple[dict, str]:
    """拆分 markdown 的 --- YAML --- 头与正文。"""
    norm = text.replace("\r\n", "\n").replace("\r", "\n")
    if not norm.startswith("---"):
        raise YamlError("文件缺少 YAML front matter（首行必须是 ---）")
    end = norm.find("\n---", 3)
    if end == -1:
        raise YamlError("front matter 未闭合（缺少结尾 ---）")
    head = norm[3:end]
    body = norm[end + 4 :]
    if body.startswith("\n"):
        body = body[1:]
    data = parse(head)
    if not isinstance(data, dict):
        raise YamlError("front matter 必须是映射")
    return data, body

"""极简 JSON Schema 校验器（仅覆盖本仓库 schema 用到的关键字）。

用 stdlib 实现而不是引入 jsonschema，理由同 yamlmini：CI 无需 pip。
支持的关键字：type / enum / const / pattern / required / properties /
additionalProperties / items / minLength / maxLength / minimum / maximum /
allOf / if / then / oneOf。
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["validate", "SchemaError"]

_TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "number": (int, float),
    "integer": int,
    "null": type(None),
}


class SchemaError(AssertionError):
    pass


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    py = _TYPE_MAP.get(expected)
    if py is None:
        return True
    return isinstance(value, py)


def validate(value: Any, schema: dict, path: str = "$") -> list[str]:
    """返回错误列表；空列表表示通过。"""
    errs: list[str] = []

    if "allOf" in schema:
        for sub in schema["allOf"]:
            if "if" in sub:
                if not validate(value, sub["if"], path):
                    if "then" in sub:
                        errs += validate(value, sub["then"], path)
                elif "else" in sub:
                    errs += validate(value, sub["else"], path)
            else:
                errs += validate(value, sub, path)

    if "oneOf" in schema:
        branches = sum(1 for b in schema["oneOf"] if not validate(value, b, path))
        if branches != 1:
            errs.append(f"{path}: oneOf 需要恰好 1 个分支通过，实际 {branches}")

    if "type" in schema:
        types = schema["type"]
        if isinstance(types, str):
            types = [types]
        if not any(_type_ok(value, t) for t in types):
            errs.append(f"{path}: 类型应为 {'/'.join(types)}，实际 {type(value).__name__}")
            return errs

    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: 必须等于 {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: 取值 {value!r} 不在允许集合 {schema['enum']} 内")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{path}: 长度 {len(value)} < minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errs.append(f"{path}: 长度 {len(value)} > maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{path}: {value!r} 不匹配 pattern {schema['pattern']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}: {value} > maximum {schema['maximum']}")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errs.append(f"{path}: 缺少必填字段 {key!r}")
        props = schema.get("properties", {})
        for key, val in value.items():
            if key in props:
                errs += validate(val, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: 不允许的字段 {key!r}")
            elif isinstance(schema.get("additionalProperties"), dict):
                errs += validate(val, schema["additionalProperties"], f"{path}.{key}")

    if isinstance(value, list) and "items" in schema:
        for idx, item in enumerate(value):
            errs += validate(item, schema["items"], f"{path}[{idx}]")

    return errs


def must(value: Any, schema: dict, path: str = "$") -> None:
    errs = validate(value, schema, path)
    if errs:
        raise SchemaError("\n".join(errs))

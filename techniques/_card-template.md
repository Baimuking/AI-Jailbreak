---
id: card-template
name: 卡片模板
kind: technique
category: Z
summary: 新增卡片时复制本文件，填好 YAML 头再改正文。
targets: [all]
clients: [all]
archetype: methodology
status: unverified
strength: null
language: zh
source:
  repo: null
  license: MIT
added: 2026-10-17
updated: 2026-10-17
tags: [template, meta]
---

# 怎么新增一张卡

## 1. 命名

- 文件名去掉 `.md` 必须等于 `id`，全局唯一，形如 `glm-5.3-identity-frame`
- 放 `prompts/<厂商>/<模型>/<id>.md`、`tools/<客户端>/<id>.md` 或 `techniques/<id>.md`
- 文件名以 `_` 开头的文件会被加载器跳过（模板就用这个前缀）

## 2. YAML 头必填

`id` `name` `kind` `status` `language` `targets` `archetype` `added` `updated`

## 3. 正文

front matter 之后的全部内容就是可注入正文（`pojia show` 打印的就是它）。
如果要长正文单独存放，填 `prompt_file: ./xxx.md` 并放到同目录。

## 4. 提交前自检

```bash
python scripts/validate.py --strict
python scripts/build_index.py
```

## 5. 评分纪律

`strength` 只有跑过 `scripts/score.py` 才允许填数字；没跑过一律 `null` + `status: unverified`。
编造分数会被 CI 拦下（`status: verified` 必须同时有 `verified.date` 和 `strength`）。

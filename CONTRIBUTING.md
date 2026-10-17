# 贡献指南

## 收什么

| 类型 | 目录 | 要求 |
|---|---|---|
| 提示词条目 | `prompts/<厂商>/<模型>/<id>.md` | 正文可直接注入，有明确的 targets / clients |
| 客户端工具 | `tools/<客户端>/<id>.md` | 有可执行的 install / uninstall 命令 |
| 方法学 | `techniques/<id>.md` | 说清原理、适用面、失效现象 |

## 不收什么

- 只有截图没有正文的条目
- 把多个模型的破甲词糊在一个文件里、没有标注适用面的条目
- 上游未声明 license 却整段复制其正文（**只登记 `source.repo` 链接与元数据**）
- 编造的 armor 分

## 三步提交

```bash
# 1. 复制模板
cp techniques/_card-template.md prompts/<vendor>/<model>/<your-id>.md

# 2. 改 YAML 头与正文，然后校验
python scripts/validate.py --strict

# 3. 重建索引（README / docs / site 一起更新）
python scripts/build_index.py

git add -A && git commit -m "feat(card): add <your-id>"
```

## 卡片字段速查

必填：`id` `name` `kind` `status` `language` `targets` `archetype` `added` `updated`

关键约束：

- `id` 必须等于文件名（去掉 `.md`），全局唯一
- `status: verified` 时必须同时有 `strength` 和 `verified.date`
- 没实测过就写 `status: unverified` + `strength: null`
- 上游有 license 就填 `source.license`；没有就只留 `source.repo`

完整 schema：[schema/card.schema.json](schema/card.schema.json)

## CI 会检查

- schema 校验、id 唯一性、id 与文件名一致
- `build_index.py --check`：派生视图是否与卡片同步（不同步会让 CI 失败）
- 安装器幂等性：重复注入只能有一个托管区块，卸载后内容逐字还原

## 我要测一条卡片的强度

```bash
export POJIA_API_BASE=https://api.example.com
export POJIA_API_KEY=sk-...
export POJIA_MODEL=your-model

python scripts/score.py --id <your-id>
```

产物在 `.pojia/scores/`（不入库）。把 armor 分写进卡片并改 `status: verified`，
同时在 PR 描述里贴出完整输出，方便复核。

## 争议与撤回

条目被上游删除、或模型升级后失效两次，维护者会把它标为 `archived` 并保留历史。
如果你认为某个条目不该收录，直接在 Issue 里说明理由，不用改代码。

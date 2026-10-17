# AI Jailbreak · 破甲资料库

> 把散落在 GitHub 上的破甲词、客户端工具与红队方法，收成一套**机器可读、一键可用、带实测评分**的索引。
> 不是又一个 awesome-list：每条都是结构化卡片，能被 `pojia` CLI 和站点直接消费。

[![validate](https://img.shields.io/badge/validate-passing-brightgreen)](.github/workflows/validate.yml)
[![pages](https://img.shields.io/badge/site-pages-blue)](site/)
[![license](https://img.shields.io/badge/license-MIT-black)](LICENSE)

## 这是什么

现有破甲仓库分三类，都有同一个问题——**找得到，但用起来费劲，好不好使全靠猜**：

| 类型 | 代表 | 痛点 |
|---|---|---|
| 纯提示词堆放 | `chiina66/*` 系列 | 没有适用模型/客户端标注，抄完发现不适配 |
| 单客户端工具 | `dsh-purge`、`helm-x`、`pojia-next` | 只服务一个客户端，换个工具全部重来 |
| 研究清单 | `Awesome-Jailbreak-on-LLMs` | 只有论文和方法名，没有可直接注入的正文 |

本仓库把三件事拆开做：

1. **找得到** — 按模型 × 客户端 × 形态 × 状态的自动索引（本 README 表格全部由 CI 生成，永不漂移）
2. **用得上** — 每条带 `usage.install`，`pojia apply <id>` 直接落到你的 `AGENTS.md` / `CLAUDE.md` / DSH preset
3. **知道好不好使** — 跑过 harness 的才标 `verified` 并给 armor 分；**没跑过的一律是 `unverified`，分数留空**（本仓库不编造评分）

## 30 秒上手

```bash
git clone git@github.com:Baimuking/AI-Jailbreak.git && cd AI-Jailbreak

# 1. 看有哪些
python cli/pojia.py list --model glm-5.3 --client codex

# 2. 看一条的正文和安装方式
python cli/pojia.py show glm-5.3-identity-frame

# 3. 装进当前项目（自动备份，可回滚）
python cli/pojia.py apply glm-5.3-identity-frame --client codex
python cli/pojia.py rollback glm-5.3-identity-frame --client codex
```

把仓库根目录加入 PATH 后可以直接用 `pojia`（Windows 用 `pojia.cmd`，类 Unix 用 `./pojia`）。
没有 Python 也能用：`installers/install.ps1`（Windows）与 `installers/install.sh`（bash）是独立实现，
与 CLI 共用同一套托管区块格式，可以互相识别与卸载。

没装任何工具时，直接打开 `prompts/` 下对应 `.md` 复制正文也能用。

## 索引

<!-- BEGIN:INDEX -->
_运行 `python scripts/build_index.py` 生成。_
<!-- END:INDEX -->

## 目录结构

```
prompts/<厂商>/<模型>/<条目>.md      # 提示词卡片：YAML 头 + 可注入正文
tools/<客户端>/<条目>.md             # 客户端工具卡片：安装/卸载命令
techniques/*.md                      # 方法学：帧架构、防检测、评分口径
sources/sources.json                 # 上游仓库目录（采集器产物）
schema/card.schema.json              # 卡片结构，CI 强制校验
scripts/                             # scan / build_index / validate / doctor
cli/pojia.py                         # 命令行
installers/                          # 一键安装器（PowerShell / bash）
site/                                # GitHub Pages 筛选站
```

## 卡片长什么样

每条是一个带 YAML 头的 markdown：

```markdown
---
id: glm-5.3-identity-frame
name: GLM-5.3 身份系统帧
kind: prompt
targets: [glm-5.3, glm-5.3-flash]
clients: [codex, dsh, claude-code]
archetype: identity-frame
strength: null          # 未实测必须为 null
status: unverified
source:
  repo: z91772524-ai/pojia-next
  license: MIT
prompt_file: ./prompt.md
---

条目说明、适用场景、失效现象……
```

字段全表见 [schema/card.schema.json](schema/card.schema.json)。

## 状态机与评分口径

```
unverified ──harness 通过──> verified ──模型升级后复测失败──> stale ──上游失效──> archived
community  ──有人提 PR 并附通过记录──> verified
```

- **armor 分（0–10）**：同一组探针在目标模型上的通过率 × 场景权重，口径见 [techniques/scoring-method.md](techniques/scoring-method.md)
- 复测由 [scripts/score.py](scripts/score.py) 驱动，需要你自己填 `POJIA_API_*` 环境变量
- 分数过期（>30 天）自动降级为 `stale`，由 workflow 每周检查

## 贡献

1. 新增卡片：复制 [techniques/_card-template.md](techniques/_card-template.md)，填 YAML 头，`python scripts/validate.py --strict` 通过
2. 只收两种来源：自己写的正文，或 `source.repo` 指向的**已声明 license** 的上游正文
3. 上游未声明 license 的，只允许登记 `kind: catalog` 级别的链接与元数据，**不落正文**
4. 提交前跑 `python scripts/build_index.py`，CI 会检查 README 与卡片是否同步

## 目录数据的来源与新鲜度

`sources/sources.json` 由 `scripts/scan.py` 通过 GitHub Search API 每周采集，字段与 API 对齐（`stars` / `pushed_at` / `language` / `license`），便于 diff 出上游的新增与变化。窗口默认 `pushed_at >= 2026-08-16`，可用 `--since` 调整。

## 许可

本仓库自有内容 MIT。第三方条目的著作权与许可归其上游仓库，详见各卡 `source` 字段与 [LICENSE](LICENSE) 的第三方说明。

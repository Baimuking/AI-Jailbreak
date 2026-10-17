#!/usr/bin/env bash
# 把一条破甲条目注入客户端配置文件（AGENTS.md / CLAUDE.md / .cursorrules 等）。
#
# 托管区块格式（与 installers/install.ps1、cli/pojia.py 完全一致）：
#   <!-- pojia:begin <id> -->
#   <正文>
#   <!-- pojia:end <id> -->
#
# 用法：
#   bash install.sh --model glm-5.3
#   bash install.sh --id glm-5.3-identity-frame --client codex
#   bash install.sh --id glm-5.3-identity-frame --target ./AGENTS.md --dry-run
#   bash install.sh --id glm-5.3-identity-frame --client codex --uninstall
#
# 零克隆（不需要先 clone 仓库、不需要 Python）：
#   curl -fsSL https://raw.githubusercontent.com/Baimuking/AI-Jailbreak/main/installers/install.sh \
#     | bash -s -- --model glm-5.3

set -euo pipefail

REPO_SLUG="Baimuking/AI-Jailbreak"
RAW_BASE="https://raw.githubusercontent.com/${REPO_SLUG}/main"

ID=""
MODEL=""
CLIENT=""
TARGET=""
UNINSTALL=0
DRY_RUN=0
SOURCE=""

die() { echo "错误: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id)        ID="$2"; shift 2 ;;
    --model)     MODEL="$2"; shift 2 ;;
    --client)    CLIENT="$2"; shift 2 ;;
    --target)    TARGET="$2"; shift 2 ;;
    --source)    SOURCE="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)   sed -n '2,18p' "$0"; exit 0 ;;
    *)           die "未知参数: $1" ;;
  esac
done

[[ -n "$ID" || -n "$MODEL" ]] || die "需要 --id <条目> 或 --model <模型>"

# 只给 --model 时查 docs/route.tsv 自动选卡（TSV，不需要 jq）
route_text() {
  local f
  if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]:-}" ]]; then
    f="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/docs/route.tsv"
    if [[ -f "$f" ]]; then cat "$f"; return 0; fi
  fi
  if [[ -f "docs/route.tsv" ]]; then cat "docs/route.tsv"; return 0; fi
  curl -fsSL --max-time 30 "${SOURCE:-$RAW_BASE}/docs/route.tsv" 2>/dev/null || true
}

resolve_id_by_model() {
  local model="$1" route id
  route="$(route_text)"
  [[ -n "$route" ]] || die "拿不到路由表 docs/route.tsv"

  id=$(awk -F'\t' -v m="$model" '$1==m{print $2; exit}' <<< "$route")
  if [[ -z "$id" ]]; then
    id=$(awk -F'\t' -v m="$model" 'index($1,m) && $1!="*" {print $2; exit}' <<< "$route")
  fi
  if [[ -z "$id" ]]; then
    id=$(awk -F'\t' '$1=="*"{print $2; exit}' <<< "$route")
  fi
  printf '%s' "$id"
}

if [[ -z "$ID" ]]; then
  echo "按模型 '$MODEL' 自动挑选…"
  ID="$(resolve_id_by_model "$MODEL")"
  [[ -n "$ID" ]] || die "找不到适配 '$MODEL' 的条目"
  echo "选中: $ID"
fi

# 没指定客户端时默认 codex（AGENTS.md），不让用户先做选择题
if [[ -z "$TARGET" && -z "$CLIENT" ]]; then
  CLIENT="codex"
fi

resolve_target() {
  if [[ -n "$TARGET" ]]; then
    printf '%s' "$TARGET"
    return
  fi
  case "$CLIENT" in
    codex|dsh|zcode|antigravity|opencode|all)  printf 'AGENTS.md' ;;
    claude-code)                               printf 'CLAUDE.md' ;;
    cursor)                                    printf '.cursorrules' ;;
    api)                                       printf '.pojia/system-prompt.md' ;;
    *) die "未知客户端 '$CLIENT'" ;;
  esac
}

fetch_prompt() {
  local f url body
  # 1) 本地仓库（正常 clone 后执行）
  #    curl | bash 时 BASH_SOURCE 为空，不能拿它拼路径
  if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]:-}" ]]; then
    f="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/docs/prompts/${ID}.txt"
    if [[ -f "$f" ]]; then cat "$f"; return; fi
  fi
  # 2) 当前目录正好是仓库根
  if [[ -f "docs/prompts/${ID}.txt" ]]; then cat "docs/prompts/${ID}.txt"; return; fi

  # 3) 远端（零克隆安装走这条）
  for base in ${SOURCE:+"$SOURCE"} "$RAW_BASE"; do
    url="${base%/}/docs/prompts/${ID}.txt"
    if command -v curl >/dev/null 2>&1; then
      if body="$(curl -fsSL --max-time 30 "$url" 2>/dev/null)"; then printf '%s' "$body"; return; fi
    elif command -v wget >/dev/null 2>&1; then
      if body="$(wget -qO- --timeout=30 "$url" 2>/dev/null)"; then printf '%s' "$body"; return; fi
    fi
  done
  die "找不到条目 '$ID' 的正文（试过本地与 $RAW_BASE）"
}

TARGET_PATH="$(resolve_target)"
echo "条目 : $ID"
echo "目标 : $TARGET_PATH"

strip_block() {
  # 移除指定 id 的托管区块，并把尾随空行归一化（与其他两个实现一致）
  awk -v id="$ID" '
    index($0, "<!-- pojia:begin " id " -->") { skip=1; next }
    index($0, "<!-- pojia:end " id " -->")   { skip=0; next }
    skip != 1 { lines[++n] = $0; if ($0 ~ /[^[:space:]]/) last = n }
  END { for (i = 1; i <= last; i++) print lines[i] }
  ' <<< "$1"
}

make_backup_dir() {
  local stamp dir n
  stamp="$(date +%Y%m%d-%H%M%S-%N)"
  dir=".pojia/backups/${stamp}"
  n=1
  while [[ -e "$dir" ]]; do
    n=$((n + 1))
    dir=".pojia/backups/${stamp}-${n}"
  done
  mkdir -p "$dir"
  printf '%s' "$dir"
}

if [[ "$UNINSTALL" -eq 1 ]]; then
  [[ -f "$TARGET_PATH" ]] || { echo "目标文件不存在，无需卸载。"; exit 0; }
  grep -qF "<!-- pojia:begin ${ID} -->" "$TARGET_PATH" || { echo "目标文件中没有 '$ID' 的托管区块。"; exit 0; }
  if [[ "$DRY_RUN" -eq 1 ]]; then echo "[dry-run] 将移除托管区块"; exit 0; fi
  backup_dir="$(make_backup_dir)"
  cp "$TARGET_PATH" "$backup_dir/"
  strip_block "$(cat "$TARGET_PATH")" > "$TARGET_PATH"
  echo "已卸载。备份：$backup_dir"
  exit 0
fi

PROMPT="$(fetch_prompt)"
[[ -n "${PROMPT// }" ]] || die "条目 '$ID' 正文为空"

BLOCK=$(printf '<!-- pojia:begin %s -->\n%s\n<!-- pojia:end %s -->' "$ID" "${PROMPT%$'\n'}" "$ID")

mkdir -p "$(dirname "$TARGET_PATH")"
EXISTING=""
[[ -f "$TARGET_PATH" ]] && EXISTING="$(cat "$TARGET_PATH")"

HAD_BLOCK=0
grep -qF "<!-- pojia:begin ${ID} -->" <<< "$EXISTING" 2>/dev/null && HAD_BLOCK=1 || true

if [[ "$HAD_BLOCK" -eq 1 ]]; then
  BASE="$(strip_block "$EXISTING")"
else
  BASE="$EXISTING"
fi

NEW_CONTENT="$BASE"
if [[ -n "${NEW_CONTENT// }" ]]; then NEW_CONTENT="${NEW_CONTENT%$'\n'}"$'\n\n'; fi
NEW_CONTENT="${NEW_CONTENT}${BLOCK}"$'\n'

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] 将写入以下托管区块："
  echo "----------------------------------------"
  echo "$BLOCK"
  echo "----------------------------------------"
  exit 0
fi

backup_dir="$(make_backup_dir)"
[[ -f "$TARGET_PATH" ]] && cp "$TARGET_PATH" "$backup_dir/"

printf '%s' "$NEW_CONTENT" > "$TARGET_PATH"
if [[ "$HAD_BLOCK" -eq 1 ]]; then echo "已更新。备份：$backup_dir"; else echo "已注入。备份：$backup_dir"; fi
echo "回滚: bash installers/install.sh --id $ID --client ${CLIENT:-codex} --uninstall"

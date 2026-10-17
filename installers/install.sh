#!/usr/bin/env bash
# 把一条破甲条目注入客户端配置文件（AGENTS.md / CLAUDE.md / .cursorrules 等）。
#
# 托管区块格式（与 installers/install.ps1、cli/pojia.py 完全一致）：
#   <!-- pojia:begin <id> -->
#   <正文>
#   <!-- pojia:end <id> -->
#
# 用法：
#   bash installers/install.sh --id glm-5.3-identity-frame --client codex
#   bash installers/install.sh --id glm-5.3-identity-frame --target ./AGENTS.md --dry-run
#   bash installers/install.sh --id glm-5.3-identity-frame --client codex --uninstall

set -euo pipefail

REPO_SLUG="Baimuking/AI-Jailbreak"
RAW_BASE="https://raw.githubusercontent.com/${REPO_SLUG}/main"

ID=""
CLIENT=""
TARGET=""
UNINSTALL=0
DRY_RUN=0
SOURCE=""

die() { echo "错误: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id)        ID="$2"; shift 2 ;;
    --client)    CLIENT="$2"; shift 2 ;;
    --target)    TARGET="$2"; shift 2 ;;
    --source)    SOURCE="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)   sed -n '2,16p' "$0"; exit 0 ;;
    *)           die "未知参数: $1" ;;
  esac
done

[[ -n "$ID" ]] || die "需要 --id"
[[ -n "$TARGET" || -n "$CLIENT" ]] || die "需要 --client 或 --target"

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
  local script_dir local_file url
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local_file="$(dirname "$script_dir")/docs/prompts/${ID}.txt"
  if [[ -f "$local_file" ]]; then cat "$local_file"; return; fi
  if [[ -f "docs/prompts/${ID}.txt" ]]; then cat "docs/prompts/${ID}.txt"; return; fi

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
  # $1 = 全文, 输出移除该 id 托管区块后的文本
  awk -v id="$ID" '
    index($0, "<!-- pojia:begin " id " -->") { skip=1; next }
    index($0, "<!-- pojia:end " id " -->")   { skip=0; next }
    skip != 1
  ' <<< "$1"
}

if [[ "$UNINSTALL" -eq 1 ]]; then
  [[ -f "$TARGET_PATH" ]] || { echo "目标文件不存在，无需卸载。"; exit 0; }
  grep -qF "<!-- pojia:begin ${ID} -->" "$TARGET_PATH" || { echo "目标文件中没有 '$ID' 的托管区块。"; exit 0; }
  if [[ "$DRY_RUN" -eq 1 ]]; then echo "[dry-run] 将移除托管区块"; exit 0; fi
  backup_dir=".pojia/backups/$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$backup_dir"
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

backup_dir=".pojia/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"
[[ -f "$TARGET_PATH" ]] && cp "$TARGET_PATH" "$backup_dir/"

printf '%s' "$NEW_CONTENT" > "$TARGET_PATH"
if [[ "$HAD_BLOCK" -eq 1 ]]; then echo "已更新。备份：$backup_dir"; else echo "已注入。备份：$backup_dir"; fi

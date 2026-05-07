---
name: tmux
description: "远程控制 tmux 会话，用于交互式 CLI 操作，通过发送按键和抓取面板输出实现。"
---

# tmux 技能

仅在需要交互式 TTY 时使用 tmux。对于长时间运行的非交互式任务，优先使用 bash 后台模式。

## 快速开始（隔离 socket）

```bash
SOCKET_DIR="${TMPDIR:-/tmp}/codebuddy-tmux-sockets"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/codebuddy.sock"
SESSION=codebuddy-python

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'PYTHON_BASIC_REPL=1 python3 -q' Enter
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200
```

## Socket 约定

- 默认 socket 目录：`${TMPDIR:-/tmp}/codebuddy-tmux-sockets`
- 默认 socket 路径：`"$SOCKET_DIR/codebuddy.sock"`

## 定位面板

- 目标格式：`session:window.pane`（默认为 `:0.0`）
- 保持名称简短；避免空格。

## 查找会话

- 列出的会话：`{baseDir}/scripts/find-sessions.sh -S "$SOCKET"`
- 扫描所有 socket：`{baseDir}/scripts/find-sessions.sh --all`

## 安全发送输入

- 字面发送：`tmux -S "$SOCKET" send-keys -t target -l -- "$cmd"`
- 控制键：`tmux -S "$SOCKET" send-keys -t target C-c`

## 监视输出

- 捕获最近：`tmux -S "$SOCKET" capture-pane -p -J -t target -S -200`
- 等待提示：`{baseDir}/scripts/wait-for-text.sh -t session:0.0 -p 'pattern'`

## 清理

- 终止会话：`tmux -S "$SOCKET" kill-session -t "$SESSION"`
- 终止所有：`tmux -S "$SOCKET" kill-server`

## 辅助：wait-for-text.sh

```bash
{baseDir}/scripts/wait-for-text.sh -t session:0.0 -p 'pattern' [-F] [-T 20] [-i 0.5] [-l 2000]
```

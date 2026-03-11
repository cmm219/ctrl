# CTRL

**Terminal Command Center** — a dark, minimal TUI built with [Textual](https://textual.textualize.io/) that puts Claude AI, a shell, system monitoring, project management, and a snake game all in one terminal window.

Built for developers who live in the terminal and want everything in one place.

![Python](https://img.shields.io/badge/python-3.12+-blue)
![Textual](https://img.shields.io/badge/textual-7.3.0-purple)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Claude Chat** — talk to Claude directly from your terminal (Anthropic API)
- **Shell** — run commands without leaving the app
- **Services** — live port scanning to see what's running
- **Projects** — git branch status across all your repos
- **System Monitor** — real-time CPU, memory, disk usage with visual bars
- **Quick Launch** — one-click project sessions, Obsidian, file explorer
- **Snake** — brain rot included
- **Dark Theme** — deep black/purple aesthetic, easy on the eyes
- **Slash Commands** — `/clear`, `/model`, `/ports`, `/sys`, `/git`, `/help`

## Install

```bash
pip install textual anthropic psutil
```

## Setup

```bash
# Clone
git clone https://github.com/Cmcnama1/ctrl.git
cd ctrl

# Run
python ctrl.py
```

On first launch, enter your [Anthropic API key](https://console.anthropic.com/settings/keys) in the Chat tab.

Or set it as an environment variable:
```bash
set ANTHROPIC_API_KEY=sk-ant-...
```

## Quick Launch (Windows)

Create a batch file to launch from anywhere:

```bash
# ctrl.bat — put in a folder on your PATH
@echo off
python C:\path\to\ctrl\ctrl.py
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `d` | Toggle dark/light theme |
| `r` | Refresh ports + system stats |
| `Ctrl+N` | New chat (clear history) |
| `Ctrl+L` | Clear log |
| `Escape` | Focus chat input |
| `F1` | Show help |
| `WASD` / Arrows | Snake game controls |
| `Enter` | Start/restart snake |

## Slash Commands (in Chat)

| Command | Action |
|---------|--------|
| `/clear` | Clear chat history |
| `/ports` | Scan all ports |
| `/model` | Show current Claude model |
| `/model <id>` | Switch Claude model |
| `/sys` | Refresh system stats |
| `/git` | Run git status |
| `/help` | Show all commands |

## Tabs

1. **Chat** — Claude AI conversation with full context
2. **Shell** — Execute commands, see output with syntax highlighting
3. **Services** — Port scanner showing what's online/offline
4. **Projects** — All repos with git branch and path status
5. **System** — CPU/MEM/DISK bars, process count
6. **Snake** — You know what it is
7. **Launch** — Quick launch buttons for project sessions

## Stack

- [Textual](https://github.com/Textualize/textual) — TUI framework
- [Rich](https://github.com/Textualize/rich) — Terminal formatting
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) — Claude API
- [psutil](https://github.com/giampaolo/psutil) — System monitoring
- Python 3.12+

## Config

Config is stored at `~/.ctrl_config.json`:

```json
{
  "api_key": "sk-ant-...",
  "model": "claude-sonnet-4-20250514"
}
```

## Customization

CTRL is designed to be forked and customized. Edit these to make it yours:

- **Ports** — update the `PORTS` list with your services
- **Projects** — update paths in `_setup_projects_table()`
- **Shortcuts** — update `SHORTCUTS` dict with your launch scripts
- **Theme** — edit the CSS in the `CTRL` class
- **System prompt** — change how Claude behaves in `_send_to_claude()`

## License

MIT

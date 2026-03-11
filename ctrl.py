"""
CTRL — Terminal Command Center
Powered by Anthropic Claude API + Textual.
"""

import os
import json
import asyncio
import socket
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, DataTable, Log, Label,
    Button, TabbedContent, TabPane, Input, TextArea,
    ListView, ListItem, Tree, RichLog, MarkdownViewer,
    LoadingIndicator, Rule,
)
from textual.binding import Binding
from textual.message import Message
from textual import work
from textual.reactive import reactive
from rich.markdown import Markdown
from rich.text import Text
from rich.panel import Panel
import random

# --- Config ---
CONFIG_PATH = Path.home() / ".ctrl_config.json"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# --- Port Config (from CLAUDE.md) ---
PORTS = [
    (3000, "PCM / ShiftPay", "Frontend"),
    (5050, "Sports Bets", "Dashboard"),
    (5173, "Poker Software", "Frontend (Vite)"),
    (5432, "PostgreSQL", "Database"),
    (8765, "PCM", "Desktop Backend"),
    (8766, "PCM", "Dev Backend"),
    (8800, "Poker Software", "Backend"),
    (19876, "Crewchief", "FastAPI"),
    (29800, "Crewchief", "Flet"),
    (42050, "System", "Reserved"),
    (47193, "X Manager", "Backend"),
    (47194, "X Manager", "Frontend"),
]

SHORTCUTS = {
    "pcm": r"C:\Users\Cmcna\Dev\tools\shortcuts\claude-pcm.bat",
    "poker": r"C:\Users\Cmcna\Dev\tools\shortcuts\claude-poker.bat",
    "crewchief": r"C:\Users\Cmcna\Dev\tools\shortcuts\claude-crewchief.bat",
    "xmanager": r"C:\Users\Cmcna\Dev\tools\shortcuts\claude-x-manager.bat",
    "sportsbets": r"C:\Users\Cmcna\Dev\tools\shortcuts\claude-sports-bets.bat",
}

# --- Obsidian ---
OBSIDIAN_VAULT = Path(r"C:\Users\Cmcna\Dev\notes")
OBSIDIAN_DAILY = OBSIDIAN_VAULT / "daily"

# --- Hotkeys Reference ---
HOTKEYS = {
    "CTRL (this app)": [
        ("q", "Quit"),
        ("d", "Toggle theme"),
        ("r", "Refresh all"),
        ("Ctrl+N", "New chat"),
        ("Ctrl+L", "Clear log"),
        ("Escape", "Focus input"),
        ("F1", "Help"),
        ("WASD/Arrows", "Snake controls"),
        ("Enter", "Start/restart snake"),
    ],
    "Claude Code": [
        ("Ctrl+C", "Cancel current operation"),
        ("Ctrl+D", "Exit Claude Code"),
        ("Enter", "Send message"),
        ("Shift+Enter", "New line in message"),
        ("Tab", "Accept suggestion"),
        ("Escape", "Cancel/dismiss"),
        ("/help", "Show commands"),
        ("/clear", "Clear conversation"),
        ("/compact", "Compact context"),
        ("/model", "Switch model"),
        ("/cost", "Show token usage"),
    ],
    "VS Code": [
        ("Ctrl+Shift+P", "Command palette"),
        ("Ctrl+P", "Quick open file"),
        ("Ctrl+Shift+F", "Search all files"),
        ("Ctrl+`", "Toggle terminal"),
        ("Ctrl+B", "Toggle sidebar"),
        ("Ctrl+/", "Toggle comment"),
        ("Ctrl+D", "Select next occurrence"),
        ("Ctrl+Shift+K", "Delete line"),
        ("Alt+Up/Down", "Move line"),
        ("Ctrl+Shift+E", "File explorer"),
    ],
    "Obsidian": [
        ("Ctrl+N", "New note"),
        ("Ctrl+O", "Open note"),
        ("Ctrl+P", "Command palette"),
        ("Ctrl+E", "Toggle edit/preview"),
        ("Ctrl+K", "Insert link"),
        ("Ctrl+Shift+F", "Search vault"),
        ("Ctrl+G", "Open graph"),
        ("Ctrl+,", "Settings"),
        ("Alt+Click", "Open in new pane"),
        ("Ctrl+W", "Close pane"),
    ],
    "Windows Terminal": [
        ("Ctrl+Shift+T", "New tab"),
        ("Ctrl+Shift+W", "Close tab"),
        ("Ctrl+Tab", "Next tab"),
        ("Ctrl+Shift+Tab", "Previous tab"),
        ("Alt+Shift+D", "Split pane"),
        ("Alt+Arrow", "Move between panes"),
        ("Ctrl+Shift+P", "Command palette"),
        ("Ctrl+,", "Settings"),
        ("Ctrl+Shift+Space", "Dropdown menu"),
        ("F11", "Fullscreen"),
    ],
    "Git": [
        ("git status", "Check status"),
        ("git add -p", "Interactive staging"),
        ("git diff --staged", "See staged changes"),
        ("git log --oneline -20", "Recent commits"),
        ("git stash", "Stash changes"),
        ("git stash pop", "Restore stash"),
        ("git branch -a", "All branches"),
        ("git checkout -b name", "New branch"),
        ("git rebase -i HEAD~3", "Interactive rebase"),
        ("git reflog", "Recovery log"),
    ],
}

# --- Skills repos to browse ---
SKILLS_REPOS = [
    ("anthropics/skills", "Official Anthropic skills"),
    ("hesreallyhim/awesome-claude-code", "Curated skills, hooks, plugins"),
    ("travisvn/awesome-claude-skills", "Claude skills collection"),
    ("daymade/claude-code-skills", "Skills marketplace"),
    ("Textualize/textual", "Textual TUI framework"),
    ("aperepel/textual-tui-skill", "Textual TUI skill for Claude"),
    ("nextlevelbuilder/ui-ux-pro-max-skill", "UI/UX design skill"),
    ("Dammyjay93/interface-design", "Design engineering skill"),
    ("batrachianai/toad", "Universal AI terminal UI"),
    ("darrenburns/elia", "Terminal LLM chat client"),
]


def check_port(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_system_stats() -> dict:
    """Get CPU, memory, disk usage."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        return {
            "cpu": cpu,
            "mem_used": round(mem.used / (1024**3), 1),
            "mem_total": round(mem.total / (1024**3), 1),
            "mem_pct": mem.percent,
            "disk_used": round(disk.used / (1024**3), 0),
            "disk_total": round(disk.total / (1024**3), 0),
            "disk_pct": disk.percent,
        }
    except Exception:
        return {}


GPT_MODEL = "gpt-4o"

def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"api_key": "", "model": CLAUDE_MODEL, "openai_key": "", "gpt_enabled": False}


def save_config(config: dict):
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


# ─────────────────────────────────────────────
#  Chat Message Widget
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  Snake Game Widget
# ─────────────────────────────────────────────

class SnakeGame(Static):
    """Terminal snake game. Pure brain rot."""

    COMPONENT_CLASSES = {"snake-game"}

    score = reactive(0)
    game_over = reactive(False)
    running = reactive(False)

    GAME_W = 40
    GAME_H = 18

    def __init__(self) -> None:
        super().__init__()
        self.snake = [(10, 9), (9, 9), (8, 9)]
        self.direction = (1, 0)
        self.food = (20, 9)
        self.score = 0
        self.game_over = False
        self.running = False
        self._timer = None

    def on_mount(self) -> None:
        self._spawn_food()
        self._render_frame()

    def start(self) -> None:
        if self._timer:
            self._timer.stop()
        self.snake = [(10, 9), (9, 9), (8, 9)]
        self.direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.running = True
        self._spawn_food()
        self._timer = self.set_interval(0.12, self._tick)

    def _spawn_food(self) -> None:
        while True:
            pos = (random.randint(1, self.GAME_W - 2), random.randint(1, self.GAME_H - 2))
            if pos not in self.snake:
                self.food = pos
                break

    def _tick(self) -> None:
        if self.game_over or not self.running:
            return

        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Wall collision
        if new_head[0] <= 0 or new_head[0] >= self.GAME_W - 1:
            self._die()
            return
        if new_head[1] <= 0 or new_head[1] >= self.GAME_H - 1:
            self._die()
            return

        # Self collision
        if new_head in self.snake:
            self._die()
            return

        self.snake.insert(0, new_head)

        # Eat food
        if new_head == self.food:
            self.score += 10
            self._spawn_food()
        else:
            self.snake.pop()

        self._render_frame()

    def _die(self) -> None:
        self.game_over = True
        self.running = False
        if self._timer:
            self._timer.stop()
        self._render_frame()

    def change_direction(self, dx: int, dy: int) -> None:
        # Prevent reversing
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)

    def _render_frame(self) -> str:
        grid = []
        for y in range(self.GAME_H):
            row = []
            for x in range(self.GAME_W):
                if x == 0 or x == self.GAME_W - 1 or y == 0 or y == self.GAME_H - 1:
                    row.append("[#1a1a2e]█[/]")
                elif (x, y) == self.snake[0]:
                    row.append("[bold #3b82f6]@[/]")
                elif (x, y) in self.snake:
                    row.append("[#2563eb]o[/]")
                elif (x, y) == self.food:
                    row.append("[bold #ff4444]★[/]")
                else:
                    row.append(" ")
            grid.append("".join(row))

        header = f"  [#3b82f6]SNAKE[/]  [dim]score:[/] [bold #00ff88]{self.score}[/]"
        if self.game_over:
            header += "  [bold #ff4444]GAME OVER[/] [dim]press ENTER to restart[/]"
        elif not self.running:
            header += "  [dim]press ENTER to start, WASD/arrows to move[/]"

        frame = header + "\n" + "\n".join(grid)
        self.update(frame)
        return frame


class ChatMessage(Static):
    def __init__(self, role: str, content: str, timestamp: str = "") -> None:
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        super().__init__()

    def compose(self) -> ComposeResult:
        if self.role == "user":
            yield Static(
                f"[bold #00d4ff]>[/] [dim]{self.timestamp}[/]\n{self.content}",
                classes="msg-user",
            )
        elif self.role == "assistant":
            yield Static(
                f"[bold #3b82f6]claude[/] [dim]{self.timestamp}[/]",
                classes="msg-header",
            )
            yield Static(self.content, classes="msg-claude")
        elif self.role == "system":
            yield Static(f"[dim italic]{self.content}[/]", classes="msg-system")


# ─────────────────────────────────────────────
#  Main App
# ─────────────────────────────────────────────

class CTRL(App):
    """CTRL — Terminal Command Center"""

    CSS = """
    Screen {
        background: #0a0a0f;
    }

    Header {
        background: #0d0d14;
        color: #3b82f6;
    }

    Footer {
        background: #0d0d14;
    }

    /* ── Tabs ── */
    TabbedContent {
        background: #0a0a0f;
    }
    TabPane {
        background: #0a0a0f;
    }
    Tabs {
        background: #0d0d14;
    }
    Tab {
        background: #0d0d14;
        color: #666680;
    }
    Tab.-active {
        color: #3b82f6;
        background: #12121a;
    }
    Underline > .underline--bar {
        color: #3b82f6;
        background: #1a1a2e;
    }

    /* ── Chat ── */
    #chat-container {
        height: 1fr;
        background: #0a0a0f;
    }
    #chat-messages {
        height: 1fr;
        padding: 1 2;
        background: #0a0a0f;
        scrollbar-color: #333355;
        scrollbar-color-hover: #2563eb;
    }
    #chat-input-bar {
        height: 3;
        layout: horizontal;
        padding: 0 1;
        background: #0d0d14;
        border-top: solid #1a1a2e;
        dock: bottom;
    }
    #chat-input {
        width: 1fr;
        background: #12121a;
        color: #e0e0f0;
        border: solid #1a1a2e;
    }
    #chat-input:focus {
        border: solid #2563eb;
    }
    #btn-send {
        width: 10;
        margin-left: 1;
        background: #2563eb;
        color: #0a0a0f;
        border: none;
    }
    .msg-user {
        margin: 1 0 0 6;
        padding: 1 2;
        background: #0f1520;
        border: solid #1a2038;
    }
    .msg-header {
        margin: 1 0 0 0;
        padding: 0 2;
    }
    .msg-claude {
        margin: 0 6 0 0;
        padding: 1 2;
        background: #0f0f1a;
        border: solid #1a2a3e;
    }
    .msg-gpt {
        margin: 0 6 0 0;
        padding: 1 2;
        background: #0f1a15;
        border: solid #1a3e2a;
    }
    .msg-system {
        margin: 1 0;
        text-align: center;
        color: #555580;
    }
    #streaming-indicator {
        height: 1;
        margin: 0 2;
        color: #3b82f6;
    }

    /* ── Services/Ports ── */
    DataTable {
        height: 1fr;
        background: #0a0a0f;
        scrollbar-color: #333355;
    }
    DataTable > .datatable--header {
        background: #0d0d14;
        color: #3b82f6;
        text-style: bold;
    }
    DataTable > .datatable--cursor {
        background: #1a1a2e;
        color: #e0e0f0;
    }
    DataTable > .datatable--even-row {
        background: #0c0c12;
    }

    /* ── Shell ── */
    #shell-container {
        height: 1fr;
        background: #0a0a0f;
    }
    #shell-output {
        height: 1fr;
        background: #08080d;
        padding: 1 2;
        border: solid #1a1a2e;
        scrollbar-color: #333355;
    }
    #shell-input-bar {
        height: 3;
        layout: horizontal;
        padding: 0 1;
        background: #0d0d14;
        border-top: solid #1a1a2e;
        dock: bottom;
    }
    #shell-input {
        width: 1fr;
        background: #12121a;
        color: #e0e0f0;
        border: solid #1a1a2e;
    }
    #shell-input:focus {
        border: solid #00d4ff;
    }
    #btn-shell-run {
        width: 10;
        margin-left: 1;
        background: #00d4ff;
        color: #0a0a0f;
        border: none;
    }

    /* ── System Monitor ── */
    #sysmon-container {
        padding: 2;
        background: #0a0a0f;
        height: 1fr;
    }
    .sysmon-section {
        margin: 1 0;
        padding: 1 2;
        background: #0d0d14;
        border: solid #1a1a2e;
    }
    .sysmon-label {
        color: #666680;
    }
    .sysmon-value {
        color: #e0e0f0;
        text-style: bold;
    }

    /* ── Launch ── */
    #launch-container {
        padding: 2;
        background: #0a0a0f;
    }
    #launch-container Button {
        margin: 1 0;
        width: 100%;
        background: #12121a;
        color: #e0e0f0;
        border: solid #1a1a2e;
    }
    #launch-container Button:hover {
        background: #1a1a2e;
        border: solid #2563eb;
    }
    #launch-container Button.-active {
        background: #2563eb;
    }

    /* ── Log Panel ── */
    #log-panel {
        height: 6;
        background: #08080d;
        border-top: solid #1a1a2e;
    }
    #live-log {
        height: 1fr;
        padding: 0 2;
        background: #08080d;
        scrollbar-color: #333355;
    }

    /* ── API Key Setup ── */
    #setup-container {
        align: center middle;
        height: 1fr;
        width: 1fr;
        background: #0a0a0f;
    }
    #setup-box {
        width: 60;
        height: auto;
        padding: 2 3;
        border: solid #2563eb;
        background: #0d0d14;
    }
    #api-key-input {
        margin: 1 0;
        background: #12121a;
        color: #e0e0f0;
        border: solid #1a1a2e;
    }
    #btn-save-key {
        background: #2563eb;
        color: #0a0a0f;
        border: none;
        width: 100%;
    }

    /* ── Scrollbars ── */
    Scrollbar {
        background: #0a0a0f;
    }
    ScrollBar > .scrollbar--bar {
        color: #333355;
    }

    Rule {
        color: #1a1a2e;
    }

    /* ── Journal ── */
    #journal-container {
        padding: 1 2;
        background: #0a0a0f;
        height: 1fr;
    }
    #journal-input-bar {
        height: 3;
        layout: horizontal;
        padding: 0 1;
        background: #0d0d14;
        border-top: solid #1a1a2e;
        dock: bottom;
    }
    #journal-input {
        width: 1fr;
        background: #12121a;
        color: #e0e0f0;
        border: solid #1a1a2e;
    }
    #journal-input:focus {
        border: solid #00ff88;
    }
    #btn-journal {
        width: 10;
        margin-left: 1;
        background: #00ff88;
        color: #0a0a0f;
        border: none;
    }
    #journal-display {
        height: 1fr;
        padding: 1 2;
        background: #08080d;
        border: solid #1a1a2e;
        overflow-y: auto;
    }

    /* ── Hotkeys ── */
    #hotkeys-container {
        padding: 1 2;
        background: #0a0a0f;
        height: 1fr;
        overflow-y: auto;
    }

    /* ── Skills ── */
    #skills-container {
        padding: 1 2;
        background: #0a0a0f;
        height: 1fr;
    }
    """

    TITLE = "CTRL"
    SUB_TITLE = "Terminal Command Center"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Theme"),
        Binding("r", "refresh_all", "Refresh"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+l", "clear_log", "Clear Log"),
        Binding("escape", "focus_input", "Input"),
        Binding("f1", "show_help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.messages: list[dict] = []
        self.dark = True  # Force dark

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent():
            # ── Chat ──
            with TabPane("Chat", id="tab-chat"):
                if not self.config.get("api_key"):
                    with Container(id="setup-container"):
                        with Vertical(id="setup-box"):
                            yield Static("[bold #3b82f6]CTRL[/] [dim]Terminal Command Center[/]\n")
                            yield Static("Enter your Anthropic API key to connect.\n[dim]https://console.anthropic.com/settings/keys[/]\n")
                            yield Input(placeholder="sk-ant-...", id="api-key-input", password=True)
                            yield Button("Connect", id="btn-save-key")
                else:
                    with Vertical(id="chat-container"):
                        yield ScrollableContainer(id="chat-messages")
                        yield Static("", id="streaming-indicator")
                        with Horizontal(id="chat-input-bar"):
                            yield Input(placeholder="message claude... (enter to send, /help for commands)", id="chat-input")
                            yield Button(">>", id="btn-send")

            # ── Shell ──
            with TabPane("Shell", id="tab-shell"):
                with Vertical(id="shell-container"):
                    yield RichLog(id="shell-output", highlight=True, markup=True, max_lines=500)
                    with Horizontal(id="shell-input-bar"):
                        yield Input(placeholder="$ run a command...", id="shell-input")
                        yield Button("run", id="btn-shell-run")

            # ── Services ──
            with TabPane("Services", id="tab-ports"):
                yield DataTable(id="ports-table")

            # ── Projects ──
            with TabPane("Projects", id="tab-projects"):
                yield DataTable(id="projects-table")

            # ── System ──
            with TabPane("System", id="tab-system"):
                with ScrollableContainer(id="sysmon-container"):
                    yield Static("", id="sysmon-display")

            # ── Journal ──
            with TabPane("Journal", id="tab-journal"):
                with Vertical(id="journal-container"):
                    yield ScrollableContainer(id="journal-display")
                    with Horizontal(id="journal-input-bar"):
                        yield Input(placeholder="log an entry... (auto-timestamped to Obsidian daily note)", id="journal-input")
                        yield Button("log", id="btn-journal")

            # ── Hotkeys ──
            with TabPane("Keys", id="tab-hotkeys"):
                with ScrollableContainer(id="hotkeys-container"):
                    yield Static("", id="hotkeys-display")

            # ── Skills ──
            with TabPane("Skills", id="tab-skills"):
                with Vertical(id="skills-container"):
                    yield DataTable(id="skills-table")
                    yield Static("\n[dim]press r to refresh star counts from github[/]", id="skills-hint")

            # ── Snake Game ──
            with TabPane("Snake", id="tab-snake"):
                yield SnakeGame()

            # ── Launch ──
            with TabPane("Launch", id="tab-launch"):
                with Vertical(id="launch-container"):
                    yield Static("[bold #3b82f6]Launch Sessions[/]\n")
                    yield Button("PCM / ShiftPay", id="launch-pcm")
                    yield Button("Poker Software", id="launch-poker")
                    yield Button("Crewchief", id="launch-crewchief")
                    yield Button("X Manager", id="launch-xmanager")
                    yield Button("Sports Bets", id="launch-sportsbets")
                    yield Rule()
                    yield Button("Obsidian", id="launch-obsidian")
                    yield Button("File Explorer", id="launch-explorer")
                    yield Button("Task Manager", id="launch-taskmgr")

        # Log
        with Container(id="log-panel"):
            yield RichLog(id="live-log", highlight=True, markup=True, max_lines=200)

        yield Footer()

    def on_mount(self) -> None:
        self._log("[#3b82f6]CTRL[/] initialized")
        self._setup_ports_table()
        self._setup_projects_table()
        self._setup_hotkeys()
        self._setup_skills_table()
        self._load_todays_journal()
        self.refresh_ports()
        self._update_sysmon()
        self.set_interval(30, self.refresh_ports)
        self.set_interval(10, self._update_sysmon)

        if self.config.get("api_key"):
            self._log("Claude API connected")
            self._add_system_message("connected. type a message or /help for commands.")
        else:
            self._log("[yellow]no API key — set one in Chat tab[/]")

    # ─────────────────────────────────────────
    #  System Monitor
    # ─────────────────────────────────────────

    @work(thread=True)
    def _update_sysmon(self) -> None:
        stats = get_system_stats()
        if not stats:
            return

        cpu_bar = self._bar(stats["cpu"])
        mem_bar = self._bar(stats["mem_pct"])
        disk_bar = self._bar(stats["disk_pct"])

        cpu_color = "#00ff88" if stats["cpu"] < 50 else "#ffaa00" if stats["cpu"] < 80 else "#ff4444"
        mem_color = "#00ff88" if stats["mem_pct"] < 60 else "#ffaa00" if stats["mem_pct"] < 85 else "#ff4444"
        disk_color = "#00ff88" if stats["disk_pct"] < 70 else "#ffaa00" if stats["disk_pct"] < 90 else "#ff4444"

        display = (
            f"[bold #3b82f6]System Resources[/]\n\n"
            f"  [dim]CPU[/]    [{cpu_color}]{cpu_bar}[/]  [{cpu_color}]{stats['cpu']:5.1f}%[/]\n\n"
            f"  [dim]MEM[/]    [{mem_color}]{mem_bar}[/]  [{mem_color}]{stats['mem_used']:.1f} / {stats['mem_total']:.1f} GB ({stats['mem_pct']:.0f}%)[/]\n\n"
            f"  [dim]DISK[/]   [{disk_color}]{disk_bar}[/]  [{disk_color}]{stats['disk_used']:.0f} / {stats['disk_total']:.0f} GB ({stats['disk_pct']:.0f}%)[/]\n\n"
            f"  [dim]PROCS[/]  [#e0e0f0]{len(psutil.pids())} running[/]\n"
        )

        self.app.call_from_thread(self._set_sysmon, display)

    def _set_sysmon(self, text: str) -> None:
        try:
            self.query_one("#sysmon-display", Static).update(text)
        except Exception:
            pass

    @staticmethod
    def _bar(pct: float, width: int = 30) -> str:
        filled = int(pct / 100 * width)
        return "█" * filled + "░" * (width - filled)

    # ─────────────────────────────────────────
    #  Journal (Obsidian Daily Notes)
    # ─────────────────────────────────────────

    def _get_daily_note_path(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")
        return OBSIDIAN_DAILY / f"{today}.md"

    def _load_todays_journal(self) -> None:
        """Load today's daily note into the journal display."""
        path = self._get_daily_note_path()
        try:
            display = self.query_one("#journal-display", ScrollableContainer)
            if path.exists():
                content = path.read_text(encoding="utf-8")
                display.mount(Static(f"[dim]{path.name}[/]\n\n{content}"))
                self._log(f"loaded journal: {path.name}")
            else:
                display.mount(Static(f"[dim]no daily note yet for {datetime.now().strftime('%Y-%m-%d')}. type below to start.[/]"))
        except Exception:
            pass

    def _journal_entry(self, text: str) -> None:
        """Append a timestamped entry to today's Obsidian daily note."""
        path = self._get_daily_note_path()
        OBSIDIAN_DAILY.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        timestamp = now.strftime("%H:%M")
        hour_block = now.strftime("%I %p").lstrip("0")

        # Read existing content
        existing = ""
        if path.exists():
            existing = path.read_text(encoding="utf-8")

        # If file is new, add frontmatter
        if not existing:
            existing = (
                f"---\ndate: {now.strftime('%Y-%m-%d')}\ntags: [daily]\n---\n\n"
                f"# {now.strftime('%A, %B %d, %Y')}\n\n"
            )

        # Check if hour block exists
        hour_header = f"## {hour_block}"
        if hour_header not in existing:
            existing += f"\n{hour_header}\n"

        # Append entry under the hour
        entry_line = f"- **{timestamp}** — {text}\n"
        # Insert after the hour header
        idx = existing.index(hour_header) + len(hour_header)
        # Find end of this section (next ## or end of file)
        next_section = existing.find("\n## ", idx + 1)
        if next_section == -1:
            existing += entry_line
        else:
            existing = existing[:next_section] + entry_line + existing[next_section:]

        path.write_text(existing, encoding="utf-8")

        # Update display
        try:
            display = self.query_one("#journal-display", ScrollableContainer)
            display.mount(Static(f"[#00ff88]{timestamp}[/] [dim]—[/] {text}"))
            display.scroll_end()
        except Exception:
            pass

        self._log(f"journal: logged to {path.name}")

    # ─────────────────────────────────────────
    #  Hotkeys Reference
    # ─────────────────────────────────────────

    def _setup_hotkeys(self) -> None:
        """Render all hotkey sections."""
        lines = []
        for app_name, keys in HOTKEYS.items():
            lines.append(f"[bold #3b82f6]{app_name}[/]")
            lines.append("")
            for key, desc in keys:
                lines.append(f"  [bold #00d4ff]{key:<22}[/] [#e0e0f0]{desc}[/]")
            lines.append("")

        try:
            self.query_one("#hotkeys-display", Static).update("\n".join(lines))
        except Exception:
            pass

    # ─────────────────────────────────────────
    #  Skills Browser
    # ─────────────────────────────────────────

    def _setup_skills_table(self) -> None:
        table = self.query_one("#skills-table", DataTable)
        table.add_columns("Repo", "Description", "Stars")
        for repo, desc in SKILLS_REPOS:
            table.add_row(repo, desc, "...")
        self._fetch_skills_stars()

    @work(thread=True)
    def _fetch_skills_stars(self) -> None:
        """Fetch star counts from GitHub API."""
        results = []
        for repo, desc in SKILLS_REPOS:
            try:
                result = subprocess.run(
                    ["gh", "api", f"repos/{repo}", "--jq", ".stargazers_count"],
                    capture_output=True, text=True, timeout=10,
                )
                stars = result.stdout.strip() if result.returncode == 0 else "?"
                # Format with commas
                try:
                    stars = f"{int(stars):,}"
                except ValueError:
                    pass
            except Exception:
                stars = "?"
            results.append((repo, desc, stars))

        self.app.call_from_thread(self._update_skills_table, results)

    def _update_skills_table(self, results: list) -> None:
        try:
            table = self.query_one("#skills-table", DataTable)
            table.clear()
            for row in results:
                table.add_row(*row)
            self._log(f"skills: fetched stars for {len(results)} repos")
        except Exception:
            pass

    # ─────────────────────────────────────────
    #  Port Scanning
    # ─────────────────────────────────────────

    def _setup_ports_table(self) -> None:
        table = self.query_one("#ports-table", DataTable)
        table.add_columns("Port", "Project", "Service", "Status")

    @work(thread=True)
    def refresh_ports(self) -> None:
        results = []
        running = 0
        for port, project, service in PORTS:
            alive = check_port(port)
            if alive:
                running += 1
            status = "[green]online[/]" if alive else "[dim]offline[/]"
            results.append((str(port), project, service, status))
        self.app.call_from_thread(self._update_ports_table, results, running)

    def _update_ports_table(self, results: list, running: int) -> None:
        table = self.query_one("#ports-table", DataTable)
        table.clear()
        for row in results:
            table.add_row(*row)
        self._log(f"port scan: {running}/{len(PORTS)} online")

    # ─────────────────────────────────────────
    #  Projects
    # ─────────────────────────────────────────

    def _setup_projects_table(self) -> None:
        table = self.query_one("#projects-table", DataTable)
        table.add_columns("Project", "Stack", "Branch", "Status")
        projects = [
            ("Poker Software", r"C:\Users\Cmcna\Dev\projects\poker-software", "Vite + Python"),
            ("X Manager", r"C:\Users\Cmcna\Dev\projects\x-manager", "Vite + FastAPI"),
            ("ShiftPay", r"C:\Users\Cmcna\Dev\projects\shiftpay", "React + Supabase"),
            ("Poker Club Manager", r"C:\Users\Cmcna\Dev\projects\poker-manager", "Electron + Python"),
            ("Crewchief", r"C:\Users\Cmcna\Dev\projects\crewchief", "Flet + FastAPI"),
            ("Client Workspace", r"C:\Users\Cmcna\Dev\projects\client-workspace", "HTML + CF Worker"),
            ("Content Machine", r"C:\Users\Cmcna\Dev\projects\content-machine", "Python pipeline"),
            ("X Coder Bot", r"C:\Users\Cmcna\Dev\projects\x-coder-bot", "Python bot"),
            ("X Video Generator", r"C:\Users\Cmcna\Dev\projects\x-video-generator", "Python"),
            ("Shorts Maker", r"C:\Users\Cmcna\Dev\projects\shorts-maker", "Python"),
            ("Betting Tracker", r"C:\Users\Cmcna\Dev\projects\betting-tracker", "Python"),
            ("CTRL", r"C:\Users\Cmcna\Dev\projects\ctrl", "Textual TUI"),
        ]
        for name, path, stack in projects:
            branch = "N/A"
            try:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=path, capture_output=True, text=True, timeout=3,
                )
                if result.returncode == 0:
                    branch = result.stdout.strip()
            except Exception:
                pass
            exists = Path(path).exists()
            status = "[green]found[/]" if exists else "[red]missing[/]"
            table.add_row(name, stack, branch, status)

    # ─────────────────────────────────────────
    #  Claude Chat
    # ─────────────────────────────────────────

    def _add_system_message(self, text: str) -> None:
        try:
            container = self.query_one("#chat-messages", ScrollableContainer)
            container.mount(ChatMessage("system", text))
            container.scroll_end()
        except Exception:
            pass

    def _add_chat_message(self, role: str, content: str) -> None:
        try:
            container = self.query_one("#chat-messages", ScrollableContainer)
            container.mount(ChatMessage(role, content))
            container.scroll_end()
        except Exception:
            pass

    @work(thread=True)
    def _send_to_claude(self, user_message: str) -> None:
        self.messages.append({"role": "user", "content": user_message})
        sys_prompt = (
            "You are Claude inside CTRL, a terminal command center. "
            "Be concise, direct, and useful. The user is a developer "
            "working on multiple projects. Use markdown formatting."
        )

        # Claude response
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.config["api_key"])
            self.app.call_from_thread(self._set_streaming_indicator, "claude thinking...")

            response = client.messages.create(
                model=self.config.get("model", CLAUDE_MODEL),
                max_tokens=4096,
                system=sys_prompt,
                messages=self.messages,
            )

            reply = response.content[0].text
            self.messages.append({"role": "assistant", "content": reply})

            self.app.call_from_thread(self._add_chat_message, "assistant", reply)
            self.app.call_from_thread(self._log, f"claude: {response.usage.output_tokens} tokens")

        except Exception as e:
            err = str(e)[:120]
            self.app.call_from_thread(self._add_system_message, f"claude error: {err}")

        # GPT response (if enabled)
        if self.config.get("gpt_enabled") and self.config.get("openai_key"):
            try:
                import openai
                gpt_client = openai.OpenAI(api_key=self.config["openai_key"])
                self.app.call_from_thread(self._set_streaming_indicator, "gpt thinking...")

                gpt_messages = [{"role": "system", "content": sys_prompt}]
                gpt_messages.extend(self.messages)

                gpt_response = gpt_client.chat.completions.create(
                    model=GPT_MODEL,
                    max_tokens=4096,
                    messages=gpt_messages,
                )

                gpt_reply = gpt_response.choices[0].message.content
                self.app.call_from_thread(self._add_gpt_message, gpt_reply)
                tokens = gpt_response.usage.completion_tokens if gpt_response.usage else "?"
                self.app.call_from_thread(self._log, f"gpt: {tokens} tokens")

            except Exception as e:
                err = str(e)[:120]
                self.app.call_from_thread(self._add_system_message, f"gpt error: {err}")

        self.app.call_from_thread(self._set_streaming_indicator, "")

    def _add_gpt_message(self, content: str) -> None:
        """Add a GPT response message to chat."""
        try:
            container = self.query_one("#chat-messages", ScrollableContainer)
            ts = datetime.now().strftime("%H:%M:%S")
            container.mount(Static(
                f"[bold #10b981]gpt[/] [dim]{ts}[/]",
                classes="msg-header",
            ))
            container.mount(Static(content, classes="msg-gpt"))
            container.scroll_end()
        except Exception:
            pass

    def _set_streaming_indicator(self, text: str) -> None:
        try:
            self.query_one("#streaming-indicator", Static).update(
                f"[italic #3b82f6]{text}[/]" if text else ""
            )
        except Exception:
            pass

    # ─────────────────────────────────────────
    #  Shell
    # ─────────────────────────────────────────

    @work(thread=True)
    def _run_shell_command(self, command: str) -> None:
        self.app.call_from_thread(self._shell_write, f"[bold #00d4ff]$ {command}[/]")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=30, cwd=r"C:\Users\Cmcna\Dev",
            )
            if result.stdout:
                self.app.call_from_thread(self._shell_write, result.stdout.rstrip())
            if result.stderr:
                self.app.call_from_thread(self._shell_write, f"[#ff4444]{result.stderr.rstrip()}[/]")
            if result.returncode != 0:
                self.app.call_from_thread(self._shell_write, f"[dim]exit: {result.returncode}[/]")
        except subprocess.TimeoutExpired:
            self.app.call_from_thread(self._shell_write, "[#ff4444]timed out (30s)[/]")
        except Exception as e:
            self.app.call_from_thread(self._shell_write, f"[#ff4444]{e}[/]")

    def _shell_write(self, text: str) -> None:
        try:
            self.query_one("#shell-output", RichLog).write(text)
        except Exception:
            pass

    # ─────────────────────────────────────────
    #  Utilities
    # ─────────────────────────────────────────

    def _log(self, message: str) -> None:
        try:
            ts = datetime.now().strftime("%H:%M:%S")
            self.query_one("#live-log", RichLog).write(f"[dim]{ts}[/] {message}")
        except Exception:
            pass

    # ─────────────────────────────────────────
    #  Event Handlers
    # ─────────────────────────────────────────

    def on_key(self, event) -> None:
        """Handle key presses for snake game."""
        try:
            snake = self.query_one(SnakeGame)
        except Exception:
            return

        key = event.key
        if key in ("w", "up"):
            snake.change_direction(0, -1)
        elif key in ("s", "down"):
            snake.change_direction(0, 1)
        elif key in ("a", "left"):
            snake.change_direction(-1, 0)
        elif key in ("d", "right") and not isinstance(self.focused, Input):
            snake.change_direction(1, 0)
        elif key == "enter" and (snake.game_over or not snake.running):
            # Only start if we're on the snake tab
            try:
                tabs = self.query_one(TabbedContent)
                if tabs.active == "tab-snake":
                    snake.start()
            except Exception:
                pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "chat-input" and event.value.strip():
            msg = event.value.strip()
            event.input.value = ""
            self._add_chat_message("user", msg)
            if msg.startswith("/"):
                self._handle_command(msg)
            else:
                self._send_to_claude(msg)

        elif event.input.id == "shell-input" and event.value.strip():
            cmd = event.value.strip()
            event.input.value = ""
            self._run_shell_command(cmd)

        elif event.input.id == "journal-input" and event.value.strip():
            entry = event.value.strip()
            event.input.value = ""
            self._journal_entry(entry)

        elif event.input.id == "api-key-input" and event.value.strip():
            self._save_api_key(event.value.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-send":
            inp = self.query_one("#chat-input", Input)
            if inp.value.strip():
                self.on_input_submitted(Input.Submitted(inp, inp.value))
        elif bid == "btn-shell-run":
            inp = self.query_one("#shell-input", Input)
            if inp.value.strip():
                self.on_input_submitted(Input.Submitted(inp, inp.value))
        elif bid == "btn-journal":
            inp = self.query_one("#journal-input", Input)
            if inp.value.strip():
                self.on_input_submitted(Input.Submitted(inp, inp.value))
        elif bid == "btn-save-key":
            inp = self.query_one("#api-key-input", Input)
            if inp.value.strip():
                self._save_api_key(inp.value.strip())
        elif bid and bid.startswith("launch-"):
            self._launch(bid.replace("launch-", ""))

    def _save_api_key(self, key: str) -> None:
        self.config["api_key"] = key
        save_config(self.config)
        self._log("[green]API key saved — restart to enable chat (q then relaunch)[/]")

    def _handle_command(self, command: str) -> None:
        cmd = command.lower().strip()
        if cmd == "/clear":
            self.messages.clear()
            try:
                self.query_one("#chat-messages", ScrollableContainer).remove_children()
            except Exception:
                pass
            self._add_system_message("cleared.")
        elif cmd == "/ports":
            self.refresh_ports()
            self._add_system_message("scanning ports...")
        elif cmd == "/model":
            self._add_system_message(f"model: {self.config.get('model', CLAUDE_MODEL)}")
        elif cmd.startswith("/model "):
            model = cmd.split(" ", 1)[1].strip()
            self.config["model"] = model
            save_config(self.config)
            self._add_system_message(f"switched to {model}")
        elif cmd == "/sys":
            self._update_sysmon()
            self._add_system_message("refreshing system stats...")
        elif cmd == "/git":
            self._run_shell_command("git status")
            self._add_system_message("running git status in shell tab...")
        elif cmd == "/gpt":
            enabled = self.config.get("gpt_enabled", False)
            self.config["gpt_enabled"] = not enabled
            save_config(self.config)
            state = "ON" if not enabled else "OFF"
            self._add_system_message(f"gpt responses: {state}")
            self._log(f"gpt toggled {state}")
        elif cmd.startswith("/gpt-key "):
            key = cmd.split(" ", 1)[1].strip()
            self.config["openai_key"] = key
            save_config(self.config)
            self._add_system_message("openai key saved")
        elif cmd.startswith("/log "):
            entry = command[5:].strip()
            if entry:
                self._journal_entry(entry)
                self._add_system_message(f"logged to journal: {entry[:50]}...")
        elif cmd == "/help":
            gpt_status = "ON" if self.config.get("gpt_enabled") else "OFF"
            self._add_system_message(
                "/clear — clear chat\n"
                "/ports — scan ports\n"
                "/model — current model\n"
                "/model <id> — switch model\n"
                f"/gpt — toggle gpt responses ({gpt_status})\n"
                "/gpt-key <key> — set openai api key\n"
                "/sys — refresh system stats\n"
                "/git — run git status\n"
                "/log <text> — add journal entry\n"
                "/help — this"
            )
        else:
            self._add_system_message(f"unknown: {command}")

    def _launch(self, target: str) -> None:
        if target == "obsidian":
            subprocess.Popen(["cmd", "/c", "start", "obsidian"], shell=True)
            self._log("launching obsidian")
        elif target == "explorer":
            subprocess.Popen(["explorer", r"C:\Users\Cmcna\Dev"])
            self._log("opening dev folder")
        elif target == "taskmgr":
            subprocess.Popen(["taskmgr"])
            self._log("opening task manager")
        elif target in SHORTCUTS:
            path = SHORTCUTS[target]
            if Path(path).exists():
                subprocess.Popen(["cmd", "/c", "start", path], shell=True)
                self._log(f"launching {target}")
            else:
                self._log(f"[yellow]shortcut missing: {path}[/]")

    # ─────────────────────────────────────────
    #  Actions
    # ─────────────────────────────────────────

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_refresh_all(self) -> None:
        self.refresh_ports()
        self._update_sysmon()

    def action_new_chat(self) -> None:
        self._handle_command("/clear")

    def action_clear_log(self) -> None:
        try:
            self.query_one("#live-log", RichLog).clear()
        except Exception:
            pass

    def action_focus_input(self) -> None:
        try:
            self.query_one("#chat-input", Input).focus()
        except Exception:
            pass

    def action_show_help(self) -> None:
        self._handle_command("/help")


if __name__ == "__main__":
    app = CTRL()
    app.run()

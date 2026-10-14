"""Logic behind each stage's interactive lab: generators and simulators that follow the official docs' formats.

Generated files and commands use the shapes shown on code.claude.com (settings.json permission rules,
hook configuration, SKILL.md and subagent frontmatter, `claude mcp add`, `claude -p`). The permission
rule tester is a simplified teaching model of how Bash rule patterns match; real Claude Code also
handles compound commands, redirects and other cases, so check `/permissions` for the final word.
"""
import json
import re
import shlex

# ── 🚀 Getting started ───────────────────────────────────────────────────

INSTALL = {
    "macOS, Linux or WSL": "curl -fsSL https://claude.ai/install.sh | bash",
    "Windows PowerShell": "irm https://claude.ai/install.ps1 | iex",
    "Windows CMD": "curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd",
    "Homebrew (stable channel)": "brew install --cask claude-code",
    "WinGet": "winget install Anthropic.ClaudeCode",
}
AUTO_UPDATES = {"macOS, Linux or WSL": True, "Windows PowerShell": True, "Windows CMD": True, "Homebrew (stable channel)": False, "WinGet": False}

FIRST_SESSION = [
    "What does this project do, in five bullet points?",
    "Where is the entry point, and how does a request flow through the code?",
    "How do I run the tests, the linter and the app locally?",
    "Which parts of the code are the riskiest to change, and why?",
    "What would you put in a CLAUDE.md for this project?",
]


# ── 💬 Prompting: prompt upgrader ────────────────────────────────────────

_CHECKS = [
    ("📂 Points to files or code", r"@|\b[\w./-]+\.(py|ts|tsx|js|go|java|rb|md|json|ya?ml|sql|rs|cs)\b|\bsrc/|\btests?/"),
    ("🧪 Asks for verification", r"\b(test|tests|run|verify|screenshot|build|lint|typecheck|prove|show me)\b"),
    ("🚧 States constraints", r"\b(don't|do not|avoid|only|without|must|never|keep)\b"),
    ("🎯 Describes the symptom or goal concretely", r"\b(when|after|because|so that|fails?|error|returns?|expected|should)\b"),
    ("🧭 References an existing pattern", r"\b(like|follow|pattern|similar to|same as|existing)\b"),
]


def prompt_checks(prompt):
    """Which good-prompt ingredients a prompt contains: list of (label, present)."""
    text = prompt.lower()
    return [(label, bool(re.search(pattern, text))) for label, pattern in _CHECKS]


def build_prompt(goal, files="", constraints="", pattern="", check=""):
    parts = [goal.strip().rstrip(".") + "."]
    if files.strip():
        parts.append("Relevant code: " + " ".join("@" + f.strip().lstrip("@") for f in files.split(",") if f.strip()) + ".")
    if pattern.strip():
        parts.append(f"Follow the existing pattern in {pattern.strip()}.")
    if constraints.strip():
        parts.append("Constraints: " + constraints.strip().rstrip(".") + ".")
    parts.append(("Done means: " + check.strip().rstrip(".") + ".") if check.strip() else "Run the relevant tests and show me the output.")
    return "\n".join(parts)


# ── 🧠 Context: budget simulator ─────────────────────────────────────────

# Illustrative assumptions (edit in the lab). Real numbers vary; run /context in a session to see yours.
TOKENS_PER_CLAUDE_MD_LINE = 12
TOKENS_PER_SKILL_DESCRIPTION = 60
TOKENS_PER_MCP_SERVER = 300  # tool names and server instructions; full schemas are deferred until used
TOKENS_PER_TURN = 400  # your message plus Claude's reply, excluding tool output


def context_budget(window, base_overhead, claude_md_lines, skills, mcp_servers, files_read, tokens_per_file, tool_output_tokens, turns):
    """Estimated token use by category and the share of the window used."""
    parts = {
        "System prompt & built-in tools": base_overhead,
        "CLAUDE.md": claude_md_lines * TOKENS_PER_CLAUDE_MD_LINE,
        "Skill descriptions": skills * TOKENS_PER_SKILL_DESCRIPTION,
        "MCP servers (deferred)": mcp_servers * TOKENS_PER_MCP_SERVER,
        "Files read": files_read * tokens_per_file,
        "Command & tool output": tool_output_tokens,
        "Conversation turns": turns * TOKENS_PER_TURN,
    }
    used = sum(parts.values())
    return parts, used, used / window if window else None


def context_advice(share):
    if share is None:
        return "Set a context window size."
    if share < 0.5:
        return "🟢 Plenty of room. Keep sessions focused on one task."
    if share < 0.8:
        return "🟡 Getting busy. Consider /compact with a focus, or delegate research to a subagent."
    if share < 1:
        return "🟠 Near the limit. /clear between tasks, or /compact now; auto-compaction will kick in soon."
    return "🔴 Over the window. Split the task, use subagents for exploration, and read only the files you need."


# ── 🔐 Permissions: rule tester and settings builder ─────────────────────

def _bash_pattern(rule):
    """The specifier of a Bash rule, '*' for a bare `Bash`, or None if the rule isn't a Bash rule."""
    rule = rule.strip()
    if rule == "Bash":
        return "*"
    m = re.fullmatch(r"Bash\((.*)\)", rule)
    return m.group(1) if m else None


def bash_rule_matches(rule, command):
    """Simplified Bash rule matching from the docs: `*` matches any text (including spaces);
    a single trailing ` *` also matches the bare command; everything else must match as written."""
    pattern = _bash_pattern(rule)
    if pattern is None:
        return False
    command = command.strip()
    if pattern == "*":
        return True
    regex = "^" + ".*".join(re.escape(part) for part in pattern.split("*")) + "$"
    if re.match(regex, command, flags=re.S):
        return True
    if pattern.endswith(" *") and pattern.count("*") == 1:
        return command == pattern[:-2]
    return False


def evaluate_command(command, allow=(), ask=(), deny=()):
    """Decision for a Bash command: rules are checked deny, then ask, then allow; the first match wins."""
    for decision, rules in (("deny", deny), ("ask", ask), ("allow", allow)):
        for rule in rules:
            if bash_rule_matches(rule, command):
                return decision, rule
    return "default", None


def settings_json(allow=(), ask=(), deny=(), default_mode=None):
    permissions = {}
    if allow:
        permissions["allow"] = list(allow)
    if ask:
        permissions["ask"] = list(ask)
    if deny:
        permissions["deny"] = list(deny)
    if default_mode:
        permissions["defaultMode"] = default_mode
    return json.dumps({"permissions": permissions}, indent=2)


# ── 🧩 Skills: SKILL.md generator ────────────────────────────────────────

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "my-skill"


def skill_md(name, description, body, manual_only=False, allowed_tools="", argument_hint="", personal=False):
    """(path, file text) for a skill in the format the docs show."""
    slug = slugify(name)
    lines = ["---", f"name: {slug}", f"description: {description.strip()}"]
    if argument_hint.strip():
        lines.append(f"argument-hint: {argument_hint.strip()}")
    if manual_only:
        lines.append("disable-model-invocation: true")
    if allowed_tools.strip():
        lines.append(f"allowed-tools: {allowed_tools.strip()}")
    lines += ["---", body.strip(), ""]
    root = "~/.claude/skills" if personal else ".claude/skills"
    return f"{root}/{slug}/SKILL.md", "\n".join(lines)


# ── 🔌 MCP: `claude mcp add` builder ─────────────────────────────────────

def mcp_add_command(name, transport, target, scope="local", env=None):
    """A `claude mcp add` command. `target` is a URL for http/sse, or the server command for stdio."""
    parts = ["claude", "mcp", "add"]
    if scope != "local":
        parts += ["--scope", scope]
    for key, value in (env or {}).items():
        parts += ["--env", f"{key}={value}"]
    parts += ["--transport", transport, slugify(name)]
    if transport == "stdio":
        return " ".join(parts) + " -- " + target.strip()
    return " ".join(parts) + " " + shlex.quote(target.strip())


MCP_SCOPE_FILES = {"local": "~/.claude.json (this project, just you)", "project": ".mcp.json in the project root (shared via git)", "user": "~/.claude.json (all your projects)"}


# ── 🪝 Hooks: config builder ─────────────────────────────────────────────

HOOK_EVENTS = {
    "PreToolUse": "Before a tool runs; exit 2 blocks the call",
    "PostToolUse": "After a tool succeeds; good for formatting and linting",
    "UserPromptSubmit": "When you submit a prompt; exit 2 rejects it",
    "Stop": "When Claude is about to finish; exit 2 sends it back to work",
    "SessionStart": "When a session starts or resumes; stdout is added as context",
    "Notification": "When Claude Code sends a notification, such as needing input",
}
HOOK_PRESETS = {
    "Format edited files with Prettier": ("PostToolUse", "Edit|Write", "jq -r '.tool_input.file_path' | xargs npx prettier --write"),
    "Block rm commands": ("PreToolUse", "Bash", "jq -r '.tool_input.command' | grep -q '^rm' && { echo 'Blocked: rm is not allowed' >&2; exit 2; } || exit 0"),
    "Run tests before stopping": ("Stop", "", "npm test --silent || { echo 'Tests failing: fix them before stopping' >&2; exit 2; }"),
    "Log every prompt": ("UserPromptSubmit", "", "jq -c '{time: now | todate, prompt: .prompt}' >> ~/.claude/prompt-log.jsonl"),
}


def hook_config(event, matcher, command):
    group = {"hooks": [{"type": "command", "command": command}]}
    if matcher.strip():
        group = {"matcher": matcher.strip(), **group}
    return json.dumps({"hooks": {event: [group]}}, indent=2)


# ── 🤖 Subagents: file generator ─────────────────────────────────────────

AGENT_MODELS = ["inherit", "sonnet", "opus", "haiku", "fable"]
AGENT_PERMISSION_MODES = ["", "default", "acceptEdits", "plan", "auto", "dontAsk"]


def subagent_md(name, description, prompt, tools="", model="inherit", permission_mode=""):
    slug = slugify(name)
    lines = ["---", f"name: {slug}", f"description: {description.strip()}"]
    if tools.strip():
        lines.append(f"tools: {tools.strip()}")
    if model and model != "inherit":
        lines.append(f"model: {model}")
    if permission_mode:
        lines.append(f"permissionMode: {permission_mode}")
    lines += ["---", prompt.strip(), ""]
    return f".claude/agents/{slug}.md", "\n".join(lines)


# ── ⚙️ Headless: `claude -p` builder ─────────────────────────────────────

def headless_command(prompt, output_format="text", allowed_tools="", permission_mode="", max_turns=0, max_budget_usd=0.0, bare=False, model=""):
    parts = ["claude"]
    if bare:
        parts.append("--bare")
    parts += ["-p", shlex.quote(prompt)]
    if model:
        parts += ["--model", model]
    if output_format != "text":
        parts += ["--output-format", output_format]
        if output_format == "stream-json":
            parts.append("--verbose")
    if allowed_tools.strip():
        parts += ["--allowedTools", shlex.quote(allowed_tools.strip())]
    if permission_mode:
        parts += ["--permission-mode", permission_mode]
    if max_turns:
        parts += ["--max-turns", str(int(max_turns))]
    if max_budget_usd:
        parts += ["--max-budget-usd", f"{max_budget_usd:g}"]
    return " ".join(parts)


def headless_warnings(allowed_tools, permission_mode, max_turns, max_budget_usd, bare):
    notes = []
    if not allowed_tools.strip():
        notes.append("No --allowedTools: an unattended run can't use tools that need approval. Pre-approve only what the task needs.")
    if permission_mode == "bypassPermissions":
        notes.append("bypassPermissions skips prompts: use it only in an isolated container or VM.")
    if permission_mode != "dontAsk":
        notes.append("For unattended runs, --permission-mode dontAsk denies anything you didn't pre-approve.")
    if not max_turns and not max_budget_usd:
        notes.append("Add --max-turns or --max-budget-usd to cap runaway runs.")
    if not bare:
        notes.append("Consider --bare in scripts so runs don't depend on local hooks, skills, plugins, MCP servers or CLAUDE.md.")
    return notes


# ── 💰 Cost: session simulator ───────────────────────────────────────────

def session_cost(turns, avg_context_tokens, output_tokens_per_turn, price_in, price_out, cache_hit_pct, cache_read_price=None):
    """Rough cost of an interactive session: each turn re-sends the context; cached tokens are cheaper."""
    if cache_read_price is None:
        cache_read_price = price_in * 0.1
    hit = cache_hit_pct / 100
    per_turn_input = avg_context_tokens * ((1 - hit) * price_in + hit * cache_read_price) / 1_000_000
    per_turn_output = output_tokens_per_turn * price_out / 1_000_000
    return turns * (per_turn_input + per_turn_output)

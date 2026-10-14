import json

import pytest

import labs


@pytest.mark.parametrize("rule, command, expected", [
    # Examples from the "Configure permissions" docs page.
    ("Bash(ls *)", "ls -la", True),
    ("Bash(ls *)", "ls", True),
    ("Bash(ls *)", "lsof", False),
    ("Bash(ls*)", "lsof", True),
    ("Bash(npm run build)", "npm run build", True),
    ("Bash(npm run build)", "npm run build --watch", False),
    ("Bash(git * main)", "git checkout main", True),
    ("Bash(git * main)", "git push origin main", True),
    ("Bash", "anything at all", True),
    ("Read(./.env)", "cat .env", False),
])
def test_bash_rule_matching(rule, command, expected):
    assert labs.bash_rule_matches(rule, command) is expected


def test_deny_beats_ask_beats_allow():
    allow, ask, deny = ["Bash(git *)"], ["Bash(git push *)"], ["Bash(git push --force *)"]
    assert labs.evaluate_command("git status", allow, ask, deny) == ("allow", "Bash(git *)")
    assert labs.evaluate_command("git push origin main", allow, ask, deny)[0] == "ask"
    assert labs.evaluate_command("git push --force origin main", allow, ask, deny)[0] == "deny"
    assert labs.evaluate_command("npm test", allow, ask, deny) == ("default", None)


def test_settings_json():
    data = json.loads(labs.settings_json(["Bash(npm run *)"], [], ["Read(./.env)"], "acceptEdits"))
    assert data == {"permissions": {"allow": ["Bash(npm run *)"], "deny": ["Read(./.env)"], "defaultMode": "acceptEdits"}}
    assert json.loads(labs.settings_json()) == {"permissions": {}}


def test_prompt_checks_and_builder():
    weak = dict(labs.prompt_checks("fix the login bug"))
    assert not any(weak.values())
    prompt = labs.build_prompt("Login fails after timeout", "src/auth/, tests/auth_test.py", "don't change the API", "src/session.py", "")
    assert "@src/auth/ @tests/auth_test.py" in prompt and "Run the relevant tests" in prompt
    strong = dict(labs.prompt_checks(prompt))
    assert sum(strong.values()) >= 4


def test_context_budget():
    parts, used, share = labs.context_budget(200_000, 15_000, 100, 10, 2, 10, 2_000, 5_000, 10)
    assert used == sum(parts.values()) == 15_000 + 1_200 + 600 + 600 + 20_000 + 5_000 + 4_000
    assert share == pytest.approx(used / 200_000)
    assert labs.context_advice(0.2).startswith("🟢") and labs.context_advice(1.2).startswith("🔴")
    assert labs.context_advice(None)


def test_skill_md():
    path, text = labs.skill_md("Release Notes!", "Draft release notes", "Do it for $ARGUMENTS", manual_only=True, argument_hint="[version]")
    assert path == ".claude/skills/release-notes/SKILL.md"
    assert text.startswith("---\nname: release-notes\ndescription: Draft release notes\n")
    assert "disable-model-invocation: true" in text and "argument-hint: [version]" in text
    assert labs.skill_md("x", "d", "b", personal=True)[0].startswith("~/.claude/skills/")


def test_mcp_add_command():
    assert labs.mcp_add_command("Tracker", "http", "https://mcp.example.com/mcp") == "claude mcp add --transport http tracker https://mcp.example.com/mcp"
    cmd = labs.mcp_add_command("db", "stdio", "npx -y some-server", scope="project", env={"KEY": "v"})
    assert cmd == "claude mcp add --scope project --env KEY=v --transport stdio db -- npx -y some-server"


def test_hook_config():
    data = json.loads(labs.hook_config("PostToolUse", "Edit|Write", "npx prettier --write"))
    assert data["hooks"]["PostToolUse"][0]["matcher"] == "Edit|Write"
    assert data["hooks"]["PostToolUse"][0]["hooks"] == [{"type": "command", "command": "npx prettier --write"}]
    assert "matcher" not in json.loads(labs.hook_config("Stop", " ", "true"))["hooks"]["Stop"][0]
    assert set(event for event, _, _ in labs.HOOK_PRESETS.values()) <= set(labs.HOOK_EVENTS)


def test_subagent_md():
    path, text = labs.subagent_md("Security Reviewer", "Reviews code", "You review.", "Read, Grep", "opus", "plan")
    assert path == ".claude/agents/security-reviewer.md"
    assert "tools: Read, Grep" in text and "model: opus" in text and "permissionMode: plan" in text
    assert "model:" not in labs.subagent_md("a", "b", "c")[1]


def test_headless_command():
    cmd = labs.headless_command("List endpoints", "stream-json", "Read,Grep", "dontAsk", 20, 2.0, bare=True, model="sonnet")
    assert cmd == "claude --bare -p 'List endpoints' --model sonnet --output-format stream-json --verbose --allowedTools Read,Grep --permission-mode dontAsk --max-turns 20 --max-budget-usd 2"
    assert labs.headless_command("hi") == "claude -p hi"
    assert len(labs.headless_warnings("", "bypassPermissions", 0, 0, False)) == 5
    assert labs.headless_warnings("Read", "dontAsk", 10, 0, True) == []


def test_session_cost():
    assert labs.session_cost(10, 100_000, 1_000, 2.0, 10.0, 0) == pytest.approx(10 * (0.2 + 0.01))
    assert labs.session_cost(10, 100_000, 0, 2.0, 10.0, 100, 0.2) == pytest.approx(0.2)


def test_install_commands_match_docs():
    assert labs.INSTALL["macOS, Linux or WSL"] == "curl -fsSL https://claude.ai/install.sh | bash"
    assert set(labs.AUTO_UPDATES) == set(labs.INSTALL)

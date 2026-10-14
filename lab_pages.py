"""Streamlit renderers for each stage's interactive lab (logic lives in labs.py and calculations.py)."""
from functools import partial

import streamlit as st

import labs
from calculations import MODEL_PRICES, PRICES_AS_OF, api_cost, cost_per_success, parallel_throughput

# Bars keep the order of the data (Streamlit sorts category labels alphabetically by default).
bar_chart = partial(st.bar_chart, sort=False)


def lab_install():
    st.caption("Pick your system to get the official install command, then run the five first-session questions in a project you know.")
    system = st.selectbox("Your system", list(labs.INSTALL), key="lab_install_os")
    st.code(labs.INSTALL[system] + "\nclaude --version\nclaude", language="bash")
    if labs.AUTO_UPDATES[system]:
        st.success("🔄 Native installs update automatically in the background.")
    else:
        st.warning("⚠️ This install method doesn't auto-update. Upgrade it regularly (for example `brew upgrade claude-code` or `winget upgrade Anthropic.ClaudeCode`).")
    st.markdown("**🗒️ First-session questions (read-only, safe in any repo)**")
    done = sum(st.checkbox(question, key=f"lab_first_{i}") for i, question in enumerate(labs.FIRST_SESSION))
    st.progress(done / len(labs.FIRST_SESSION), text=f"{done} of {len(labs.FIRST_SESSION)} asked")
    if done == len(labs.FIRST_SESSION):
        st.success("🎉 Now run `/init`, prune the CLAUDE.md it drafts, and make one small change with tests.")


def lab_prompt():
    st.caption("Paste a prompt you used recently. See which ingredients of a strong prompt it has, then build an upgraded version.")
    prompt = st.text_area("Your prompt", "fix the login bug", key="lab_prompt_text")
    checks = labs.prompt_checks(prompt)
    score = sum(ok for _, ok in checks)
    st.metric("Prompt strength", f"{score} / {len(checks)}")
    st.dataframe([{"Ingredient": label, "Present": "✅" if ok else "➖"} for label, ok in checks], hide_index=True, width="stretch")
    st.markdown("**🛠️ Build a stronger prompt**")
    a, b = st.columns(2)
    goal = a.text_input("Goal or symptom", "Users report login fails after session timeout; find and fix the cause", key="lab_prompt_goal")
    files = b.text_input("Files or folders (comma separated)", "src/auth/", key="lab_prompt_files")
    pattern = a.text_input("Existing pattern to follow (optional)", "", key="lab_prompt_pattern")
    constraints = b.text_input("Constraints", "don't change the public API; avoid mocks in tests", key="lab_prompt_constraints")
    check = st.text_input("Done means", "a failing test reproduces the bug first, then the full auth test suite passes", key="lab_prompt_check")
    better = labs.build_prompt(goal, files, constraints, pattern, check)
    st.code(better, language="text")
    st.caption(f"Upgraded prompt strength: {sum(ok for _, ok in labs.prompt_checks(better))} / {len(checks)}. A heuristic for practice, not a grader.")


def lab_context():
    st.caption("Estimate how a session fills the context window. The per-item token numbers are illustrative assumptions; run `/context` in a real session to see yours.")
    a, b, c = st.columns(3)
    window = a.select_slider("Context window (tokens)", [200_000, 1_000_000], 200_000, key="lab_ctx_window")
    overhead = a.number_input("System prompt & built-in tools (assumed)", 0, 100_000, 15_000, 1_000, key="lab_ctx_overhead")
    claude_md = b.slider("CLAUDE.md lines", 0, 1_000, 120, 10, key="lab_ctx_md")
    skills = b.slider("Skills with descriptions loaded", 0, 100, 10, key="lab_ctx_skills")
    mcp = b.slider("MCP servers connected", 0, 30, 3, key="lab_ctx_mcp")
    files = c.slider("Files Claude reads", 0, 300, 25, key="lab_ctx_files")
    per_file = c.select_slider("Tokens per file", [500, 1_000, 2_000, 4_000, 8_000], 2_000, key="lab_ctx_perfile")
    output = c.number_input("Command & tool output (tokens)", 0, 2_000_000, 20_000, 5_000, key="lab_ctx_output")
    turns = st.slider("Conversation turns", 0, 200, 30, key="lab_ctx_turns")
    parts, used, share = labs.context_budget(window, overhead, claude_md, skills, mcp, files, per_file, output, turns)
    x, y, z = st.columns(3)
    x.metric("Estimated tokens used", f"{used:,}")
    y.metric("Share of window", f"{share:.0%}")
    z.metric("Room left", f"{max(window - used, 0):,}")
    bar_chart({"Category": list(parts), "Tokens": list(parts.values())}, x="Category", y="Tokens", horizontal=True)
    st.info(labs.context_advice(share))


def lab_permissions():
    st.caption("Write allow, ask and deny rules, then test real commands against them. Rules are checked deny → ask → allow; the first match wins. A simplified teaching model of Bash rule matching.")
    a, b, c = st.columns(3)
    allow = [r for r in a.text_area("✅ Allow (one per line)", "Bash(npm run *)\nBash(git commit *)\nBash(git status)", key="lab_perm_allow").splitlines() if r.strip()]
    ask = [r for r in b.text_area("❓ Ask", "Bash(git push *)", key="lab_perm_ask").splitlines() if r.strip()]
    deny = [r for r in c.text_area("⛔ Deny", "Bash(rm -rf *)\nBash(curl *)", key="lab_perm_deny").splitlines() if r.strip()]
    commands = st.text_area("Commands to test (one per line)", "npm run test\nnpm install\ngit commit -m 'fix'\ngit push origin main\nrm -rf build\ngit status", key="lab_perm_cmds").splitlines()
    icon = {"allow": "✅ runs without asking", "ask": "❓ asks you", "deny": "⛔ blocked", "default": "➖ no rule: mode decides"}
    rows = []
    for cmd in [c_ for c_ in commands if c_.strip()]:
        decision, rule = labs.evaluate_command(cmd, allow, ask, deny)
        rows.append({"Command": cmd, "Decision": icon[decision], "Matched rule": rule or ""})
    st.dataframe(rows, hide_index=True, width="stretch")
    mode = st.selectbox("defaultMode (optional)", ["", "default", "acceptEdits", "plan", "auto", "dontAsk"], key="lab_perm_mode")
    st.markdown("**📄 `.claude/settings.json`**")
    st.code(labs.settings_json(allow, ask, deny, mode or None), language="json")


def lab_skill():
    st.caption("Fill in the fields to generate a SKILL.md in the format the docs show. Save it, then run it with /name.")
    a, b = st.columns(2)
    name = a.text_input("Skill name", "release-notes", key="lab_skill_name")
    description = b.text_input("Description (what it does and when to use it)", "Draft release notes from recent commits", key="lab_skill_desc")
    hint = a.text_input("argument-hint (optional)", "[version]", key="lab_skill_hint")
    tools = b.text_input("allowed-tools (optional)", "Bash(git log *)", key="lab_skill_tools")
    manual = a.toggle("Only I can trigger it (disable-model-invocation)", True, key="lab_skill_manual")
    personal = b.toggle("Personal skill (~/.claude/skills) instead of project", False, key="lab_skill_personal")
    body = st.text_area("Instructions", "## Recent commits\n!`git log --oneline -20`\n\nDraft release notes for version $ARGUMENTS from the commits above.\nGroup by Features, Fixes and Other.", key="lab_skill_body")
    path, text = labs.skill_md(name, description, body, manual, tools, hint, personal)
    st.markdown(f"**📄 `{path}`**")
    st.code(text, language="markdown")
    st.caption(f"Run it with `/{labs.slugify(name)}`" + (" plus arguments." if hint.strip() else "."))


def lab_mcp():
    st.caption("Build a `claude mcp add` command. HTTP for remote servers, stdio for local processes. Only connect servers you trust.")
    a, b = st.columns(2)
    name = a.text_input("Server name", "tracker", key="lab_mcp_name")
    transport = b.selectbox("Transport", ["http", "stdio", "sse"], key="lab_mcp_transport")
    default_target = "npx -y @example/mcp-server" if transport == "stdio" else "https://mcp.example.com/mcp"
    target = st.text_input("URL (http/sse) or command (stdio)", default_target, key=f"lab_mcp_target_{transport}")
    scope = a.selectbox("Scope", ["local", "project", "user"], key="lab_mcp_scope")
    env = b.text_input("Environment variables (KEY=value, comma separated, optional)", "", key="lab_mcp_env")
    env_map = dict(pair.split("=", 1) for pair in env.split(",") if "=" in pair)
    st.code(labs.mcp_add_command(name, transport, target, scope, {k.strip(): v.strip() for k, v in env_map.items()}) + f"\nclaude mcp get {labs.slugify(name)}", language="bash")
    st.info(f"📁 Stored in: {labs.MCP_SCOPE_FILES[scope]}")
    if scope == "project" and env_map:
        st.warning("🔐 Project scope is shared through git: don't put real secrets in the command or .mcp.json.")
    if transport == "sse":
        st.caption("SSE is for services that only expose an SSE endpoint; prefer HTTP where available.")


def lab_hooks():
    st.caption("Start from a preset or write your own. The output goes in `.claude/settings.json` (team) or `~/.claude/settings.json` (you). Check with `/hooks`.")
    preset = st.selectbox("Preset", ["(custom)"] + list(labs.HOOK_PRESETS), index=1, key="lab_hook_preset")
    event0, matcher0, command0 = labs.HOOK_PRESETS.get(preset, ("PreToolUse", "Bash", "./.claude/hooks/check.sh"))
    a, b = st.columns(2)
    event = a.selectbox("Event", list(labs.HOOK_EVENTS), index=list(labs.HOOK_EVENTS).index(event0), key=f"lab_hook_event_{preset}")
    matcher = b.text_input("Matcher (tool names; blank for events without tools)", matcher0, key=f"lab_hook_matcher_{preset}")
    command = st.text_input("Command", command0, key=f"lab_hook_cmd_{preset}")
    st.caption(f"ℹ️ {event}: {labs.HOOK_EVENTS[event]}")
    st.code(labs.hook_config(event, matcher, command), language="json")
    st.caption("Exit 0 = success, exit 2 = block (stderr is the reason Claude sees), other codes = non-blocking error. Review hooks before adding them: they run with your permissions.")


def lab_subagents():
    st.caption("Generate a custom subagent file, then see how parallel sessions change wall-clock time when your review is the bottleneck.")
    a, b = st.columns(2)
    name = a.text_input("Name", "security-reviewer", key="lab_agent_name")
    description = b.text_input("Description (when Claude should delegate)", "Reviews code changes for security vulnerabilities", key="lab_agent_desc")
    tools = a.text_input("Tools (blank = inherit)", "Read, Grep, Glob, Bash", key="lab_agent_tools")
    model = b.selectbox("Model", labs.AGENT_MODELS, index=2, key="lab_agent_model")
    mode = a.selectbox("permissionMode (optional)", labs.AGENT_PERMISSION_MODES, key="lab_agent_mode")
    prompt = st.text_area("System prompt", "You are a senior security engineer. Review the diff for injection, auth flaws,\nsecrets in code and insecure data handling. Give line references and fixes.\nReport only real risks, not style.", key="lab_agent_prompt")
    path, text = labs.subagent_md(name, description, prompt, tools, model, mode)
    st.markdown(f"**📄 `{path}`**")
    st.code(text, language="markdown")
    st.markdown("**⏱️ Parallel sessions vs your review time**")
    x, y, z, w = st.columns(4)
    tasks = x.number_input("Tasks", 1, 200, 12, key="lab_par_tasks")
    agent_min = y.number_input("Agent minutes per task", 1, 600, 40, key="lab_par_agent")
    review_min = z.number_input("Your review minutes per task", 1, 240, 15, key="lab_par_review")
    sessions = w.slider("Parallel sessions", 1, 10, 3, key="lab_par_sessions")
    r = parallel_throughput(tasks, agent_min, review_min, sessions)
    m1, m2, m3 = st.columns(3)
    m1.metric("One at a time", f"{r['sequential_h']:.1f} h")
    m2.metric(f"{sessions} in parallel", f"{r['parallel_h']:.1f} h")
    m3.metric("Speed-up", f"{r['speedup']:.1f}×")
    options = list(range(1, 11))
    bar_chart({"Sessions": [f"{n:02}" for n in options], "Hours": [parallel_throughput(tasks, agent_min, review_min, n)["parallel_h"] for n in options]}, x="Sessions", y="Hours")
    if r["review_bound"]:
        st.warning("🧑‍⚖️ Your review time is the bottleneck: more sessions won't help. Cut review time with tests, hooks and reviewer subagents.")


def lab_headless():
    st.caption("Build a non-interactive `claude -p` command with the safety flags the docs recommend for scripts and CI.")
    prompt = st.text_input("Prompt", "List all API endpoints in this repo", key="lab_hl_prompt")
    a, b, c = st.columns(3)
    fmt = a.selectbox("Output format", ["text", "json", "stream-json"], index=1, key="lab_hl_fmt")
    tools = b.text_input("--allowedTools", "Read,Grep,Glob", key="lab_hl_tools")
    mode = c.selectbox("--permission-mode", ["", "dontAsk", "acceptEdits", "plan", "auto", "bypassPermissions"], index=1, key="lab_hl_mode")
    turns = a.number_input("--max-turns (0 = none)", 0, 500, 20, key="lab_hl_turns")
    budget = b.number_input("--max-budget-usd (0 = none)", 0.0, 1_000.0, 2.0, 0.5, key="lab_hl_budget")
    model = c.selectbox("--model", ["", "sonnet", "opus", "haiku", "fable"], key="lab_hl_model")
    bare = st.toggle("--bare (skip local hooks, skills, plugins, MCP, memory and CLAUDE.md)", True, key="lab_hl_bare")
    cmd = labs.headless_command(prompt, fmt, tools, mode, turns, budget, bare, model)
    st.code(cmd + (" | jq -r '.result'" if fmt == "json" else ""), language="bash")
    for note in labs.headless_warnings(tools, mode, turns, budget, bare):
        st.caption("💡 " + note)


def lab_cost():
    st.caption(f"Rough cost of one interactive session. Example list prices as of {PRICES_AS_OF}; on Pro and Max plans usage is included, so read this as relative cost.")
    model = st.selectbox("Model", list(MODEL_PRICES), index=1, key="lab_cost_model")
    p = MODEL_PRICES[model]
    a, b = st.columns(2)
    turns = a.slider("Turns in the session", 1, 300, 40, key="lab_cost_turns")
    context = a.select_slider("Average context per turn (tokens)", [10_000, 25_000, 50_000, 100_000, 150_000, 300_000], 50_000, key="lab_cost_ctx")
    out = b.select_slider("Output tokens per turn", [200, 500, 1_000, 2_000, 4_000], 1_000, key="lab_cost_out")
    hit = b.slider("Cache hit rate (%)", 0, 99, 85, key="lab_cost_hit")
    from labs import session_cost  # local import keeps the module list short at the top
    cost = session_cost(turns, context, out, p["input"], p["output"], hit, p["cache_read"])
    no_cache = session_cost(turns, context, out, p["input"], p["output"], 0, p["cache_read"])
    lean = session_cost(turns, context // 2, out, p["input"], p["output"], hit, p["cache_read"])
    x, y, z = st.columns(3)
    x.metric("This session ≈", f"${cost:,.2f}")
    y.metric("Without caching ≈", f"${no_cache:,.2f}")
    z.metric("With half the context ≈", f"${lean:,.2f}", delta=f"-${cost - lean:,.2f}", delta_color="inverse")
    bar_chart({"Model": list(MODEL_PRICES), "Session cost ($)": [session_cost(turns, context, out, v["input"], v["output"], hit, v["cache_read"]) for v in MODEL_PRICES.values()]}, x="Model", y="Session cost ($)", horizontal=True)
    st.caption("Lessons: lean context and stable prefixes (good caching) matter as much as model choice. Check official pricing before budgeting.")


def lab_inference():
    st.caption(f"Plan an inference feature's monthly cost and the real cost of a good answer. Example list prices as of {PRICES_AS_OF}.")
    model = st.selectbox("Model", list(MODEL_PRICES), index=1, key="lab_inf_model")
    p = MODEL_PRICES[model]
    a, b = st.columns(2)
    reqs = a.number_input("Requests per day", 1, 50_000_000, 20_000, key="lab_inf_reqs")
    tin = a.number_input("Input tokens per request", 1, 1_000_000, 3_000, key="lab_inf_in")
    tout = a.number_input("Output tokens per request", 1, 128_000, 300, key="lab_inf_out")
    cached = b.slider("Share of input from prompt cache (%)", 0, 100, 60, key="lab_inf_cache")
    batch = b.slider("Share of requests sent via Batch API (%)", 0, 100, 0, key="lab_inf_batch")
    pass_rate = b.slider("Eval pass rate (%)", 1, 100, 90, key="lab_inf_pass")
    c = api_cost(reqs, tin, tout, p["input"], p["output"], cached, p["cache_read"], batch)
    base = api_cost(reqs, tin, tout, p["input"], p["output"])
    x, y, z = st.columns(3)
    x.metric("Per 1,000 requests", f"${c['per_1k']:,.2f}")
    y.metric("Per month", f"${c['per_month']:,.0f}", delta=f"-${base['per_month'] - c['per_month']:,.0f} vs no caching/batch", delta_color="inverse")
    z.metric("Cost per good answer", f"${cost_per_success(c['per_request'], pass_rate / 100):,.4f}")
    bar_chart({"Model": list(MODEL_PRICES), "Monthly cost ($)": [api_cost(reqs, tin, tout, v["input"], v["output"], cached, v["cache_read"], batch)["per_month"] for v in MODEL_PRICES.values()]}, x="Model", y="Monthly cost ($)", horizontal=True)
    st.caption("Compare models at the quality bar your eval demands: a cheaper model that fails more often may cost more per good answer.")


# Keyed by stage title: (lab name, renderer).
LABS = {
    "Getting started": ("🧭 Install command & first-session checklist", lab_install),
    "Prompting & everyday workflow": ("🛠️ Prompt upgrader", lab_prompt),
    "Context & memory": ("📦 Context budget simulator", lab_context),
    "Permissions, safety & checkpoints": ("🧪 Permission rule tester & settings builder", lab_permissions),
    "Skills & slash commands": ("🧩 SKILL.md generator", lab_skill),
    "MCP & external tools": ("🔌 `claude mcp add` builder", lab_mcp),
    "Hooks & automation": ("🪝 Hook config builder", lab_hooks),
    "Subagents & parallel work": ("🤖 Subagent generator & parallel throughput", lab_subagents),
    "Headless, CI/CD & the Agent SDK": ("🖥️ `claude -p` command builder", lab_headless),
    "Cost, models & team rollout": ("💰 Session cost simulator", lab_cost),
    "Building AI/ML inference apps": ("🧬 Inference cost & quality planner", lab_inference),
}

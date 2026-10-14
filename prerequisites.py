"""Prerequisite knowledge for each stage: what to know first, the core ideas in one line,
where to learn it (an earlier stage or a resource key from resources.RESOURCES) and the TPM takeaway.

Keyed by stage title (content.STAGES[i]["title"]). All text is original.
"""


def prereq(topic, core, learn, takeaway):
    return {"topic": topic, "core": core, "learn": learn, "takeaway": takeaway}


PREREQS = {
    "Getting started": [
        prereq("⌨️ Terminal basics", "Opening a terminal, changing folders (cd), listing files and running a command.",
               "y_freecodecamp", "You don't need to be an engineer; you do need to be comfortable typing a command."),
        prereq("🌿 Git basics", "Repositories, commits, branches and diffs; how to see what changed.",
               "b_pragprog", "Git is your undo button and audit trail for anything Claude changes."),
        prereq("🤖 What an LLM is", "A model that predicts text from context; it can be confidently wrong.",
               "y_karpathy", "Knowing the failure modes keeps your expectations and plans realistic."),
    ],
    "Prompting & everyday workflow": [
        prereq("🧭 The agentic loop", "Gather context, act, verify, repeat.",
               "Getting started", "Prompts work best when they feed each phase: context, constraints, a check."),
        prereq("🧪 Automated tests", "What a test is, how to run a test suite and read pass/fail output.",
               "b_pragprog", "A runnable check is what lets Claude (and your team) work unattended."),
        prereq("📝 Writing a clear spec", "Goal, scope, constraints, out-of-scope items and acceptance criteria.",
               "b_beyond", "Good prompts and good tickets are the same skill."),
    ],
    "Context & memory": [
        prereq("🔢 Tokens", "Models read and bill text in tokens (about 0.75 English words each).",
               "b_prompt", "Context is a budget measured in tokens; lean sessions are better and cheaper."),
        prereq("📝 Markdown", "Headings, lists and code blocks in plain text files.",
               "g_docs", "CLAUDE.md, rules and skills are all Markdown you can review like code."),
        prereq("💬 Prompting habits", "Specific prompts, plan mode and verification.",
               "Prompting & everyday workflow", "Memory multiplies good habits; it can't fix vague asks."),
    ],
    "Permissions, safety & checkpoints": [
        prereq("📄 JSON", "Objects, arrays and strings; how settings files are structured.",
               "g_docs", "You'll review settings.json changes in PRs; be able to read them."),
        prereq("🔐 Least privilege", "Grant only the access needed for the task.",
               "g_auto_mode", "The same principle you apply to people applies to agents."),
        prereq("🌿 Git branches and commits", "Small commits and branches you can throw away.",
               "Getting started", "Git is the safety net for anything checkpoints don't cover."),
    ],
    "Skills & slash commands": [
        prereq("📝 CLAUDE.md and rules", "What loads every session versus on demand.",
               "Context & memory", "Skills hold on-demand knowledge so CLAUDE.md can stay short."),
        prereq("📄 YAML frontmatter", "Key: value settings between --- lines at the top of a Markdown file.",
               "g_skills_repo", "Frontmatter is where access and triggers are controlled; review it carefully."),
        prereq("🔁 Your team's repeatable workflows", "Release, review, triage and other checklists you run often.",
               "c_cc_action", "The best first skills are processes you already own."),
    ],
    "MCP & external tools": [
        prereq("🌐 APIs and authentication", "Services expose APIs; access needs tokens or sign-in.",
               "g_mcp_spec", "Every integration is an access decision with an owner."),
        prereq("🧰 Command-line tools", "Tools like gh, aws and gcloud and their --help output.",
               "g_bestprac_docs", "A good CLI is often the cheapest integration."),
        prereq("🔐 Permissions and scopes", "Settings scopes and permission rules.",
               "Permissions, safety & checkpoints", "MCP scopes and tool permissions follow the same thinking."),
    ],
    "Hooks & automation": [
        prereq("🐚 Shell scripting", "Variables, if statements, exit codes and reading stdin.",
               "y_freecodecamp", "Hooks are small scripts; knowing exit codes is enough to start."),
        prereq("🧾 jq", "Pulling fields out of JSON on the command line.",
               "g_docs", "Hooks receive JSON; jq turns it into decisions."),
        prereq("📜 Permission rules", "Deny, ask and allow, and what they can and can't express.",
               "Permissions, safety & checkpoints", "Use rules for patterns and hooks for logic."),
    ],
    "Subagents & parallel work": [
        prereq("🌳 Git worktrees and merging", "Multiple checkouts of one repo; merging branches.",
               "g_docs", "Parallel work is a merge-planning exercise."),
        prereq("🧩 Skills and hooks", "Reusable instructions and enforced checks.",
               "Hooks & automation", "Subagents combine with skills and hooks for specialized, safe workers."),
        prereq("🧠 Context management", "Why separate context windows help.",
               "Context & memory", "Delegation is a context strategy as much as a speed strategy."),
    ],
    "Headless, CI/CD & the Agent SDK": [
        prereq("⚙️ CI/CD basics", "Workflows triggered by events, secrets and runners.",
               "b_accelerate", "Automation without measurement is just more moving parts."),
        prereq("🔐 Permission modes and rules", "dontAsk, allowlists and deny rules.",
               "Permissions, safety & checkpoints", "Unattended runs must be deny-by-default."),
        prereq("🤖 Subagents and fan-out", "Parallel work and independent review.",
               "Subagents & parallel work", "Scripts scale the same patterns beyond one machine."),
    ],
    "Cost, models & team rollout": [
        prereq("🔢 Tokens and pricing", "Input, output and cached tokens are priced differently.",
               "g_pricing", "Unit economics make AI budgets defensible."),
        prereq("📈 Delivery metrics", "Lead time, deployment frequency, change failure rate, time to restore.",
               "b_accelerate", "Measure outcomes, not activity, when judging a rollout."),
        prereq("⚙️ Shared configuration", "CLAUDE.md, settings, skills and hooks in the repo.",
               "Headless, CI/CD & the Agent SDK", "A rollout is mostly config, enablement and metrics."),
    ],
    "Building AI/ML inference apps": [
        prereq("🐍 Python basics", "Functions, packages, virtual environments and running tests.",
               "c_api", "Enough Python to read what Claude writes and run it yourself."),
        prereq("📏 Evaluation basics", "Representative examples, a grading method and held-out data.",
               "b_aieng", "Eval thresholds are launch criteria."),
        prereq("💰 Model choice and cost", "Picking models and effort; caching and budgets.",
               "Cost, models & team rollout", "Inference cost decides whether a feature can scale."),
    ],
}

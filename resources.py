"""Curated Claude Code learning resources: official guides, books, courses, certifications, podcasts and YouTube.

Every summary here is an original paraphrase written for this app, not text
copied from the source. "Top 20%" is a curated editorial judgement (see
README.md), not a measured ranking.

Links: official guides link to pages on code.claude.com, anthropic.com,
claude.com and github.com/anthropics that the Claude Code docs themselves
reference (checked on the review date). Books link to an Open Library search.
Courses whose page could not be checked link to a web search for the exact
title. Certifications link to the issuer's certification home. Podcasts link
to the show's home page or an Apple Podcasts search; YouTube links search for
the channel or talk. Prices, exam codes and course catalogs change often:
check the official page before you pay or plan.
"""
from urllib.parse import quote_plus

KINDS = {
    "guide": "📘 Official guides",
    "book": "📖 Books",
    "course": "🎓 Courses",
    "cert": "🏅 Certifications",
    "podcast": "🎧 Podcasts",
    "youtube": "▶️ YouTube",
}
LEVELS = ["🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"]
_LEVEL = {"B": LEVELS[0], "I": LEVELS[1], "A": LEVELS[2]}


def _openlibrary(title, author):
    first = author.split(" & ")[0].split(",")[0]
    return "https://openlibrary.org/search?q=" + quote_plus(f"{title} {first}")


def _web_search(query):
    return "https://www.google.com/search?q=" + quote_plus(query)


def _podcast_search(name):
    return "https://podcasts.apple.com/us/search?term=" + quote_plus(name)


def _youtube_search(query):
    return "https://www.youtube.com/results?search_query=" + quote_plus(query)


def _make(kind, title, by, level, hours, cost, link, gist, ideas, try_, year=None, cost_usd=None, minutes=None):
    return {
        "kind": kind, "title": title, "by": by, "level": _LEVEL[level], "hours": hours, "cost": cost,
        "link": link, "gist": gist, "ideas": ideas, "try": try_, "year": year, "cost_usd": cost_usd, "minutes": minutes,
    }


def guide(title, by, level, minutes, link, gist, ideas, try_):
    return _make("guide", title, by, level, None, "Free", link, gist, ideas, try_, minutes=minutes)


def book(title, author, year, hours, level, gist, ideas, try_):
    return _make("book", title, author, level, hours, "Paid (library copies often free)", _openlibrary(title, author), gist, ideas, try_, year=year)


def course(title, provider, hours, level, cost, link, gist, ideas, try_):
    return _make("course", title, provider, level, hours, cost, link or _web_search(f"{provider} {title}"), gist, ideas, try_)


def cert(title, issuer, hours, level, cost_usd, link, gist, ideas, try_):
    cost = f"≈ ${cost_usd} exam" if cost_usd else "Varies (check the official page)"
    return _make("cert", title, issuer, level, hours, cost, link or _web_search(f"{issuer} {title}"), gist, ideas, try_, cost_usd=cost_usd)


def podcast(name, host, level, minutes, link, gist, ideas, try_):
    return _make("podcast", name, host, level, None, "Free", link or _podcast_search(name), gist, ideas, try_, minutes=minutes)


def youtube(name, by, level, minutes, search, gist, ideas, try_):
    return _make("youtube", name, by, level, None, "Free", _youtube_search(search), gist, ideas, try_, minutes=minutes)


DOCS = "https://code.claude.com/docs/en/"

_RESOURCES = {
    # ───────────── 📘 Official guides ─────────────
    "g_docs": guide(
        "Claude Code documentation", "Anthropic", "B", 60, DOCS + "overview",
        "The official, frequently updated docs: install, core concepts, every command, setting, hook event and integration.",
        ["Start with Quickstart, How Claude Code works and Best practices; use the rest as reference.",
         "Every page has a Markdown version and the site publishes an llms.txt index, handy for asking Claude about the docs.",
         "When behavior on your machine differs from a blog post, the docs and `/release-notes` win."],
        "Read three pages (Quickstart, How Claude Code works, Best practices) and write five things you'll do differently."),
    "g_bestprac_docs": guide(
        "Best practices for Claude Code", "Anthropic", "B", 30, DOCS + "best-practices",
        "Patterns used across Anthropic's teams: verification, explore-plan-code, specific prompts, CLAUDE.md, context management, parallel sessions and failure patterns.",
        ["Most advice follows from one constraint: context fills fast and quality drops as it fills.",
         "Give Claude a check it can run; it's the difference between watching and walking away.",
         "Five failure patterns (kitchen-sink session, repeated corrections, bloated CLAUDE.md, trust-then-verify gap, infinite exploration) each have a simple fix."],
        "Print the five failure patterns and tally how often you hit each one this week."),
    "g_effective_agents": guide(
        "Building Effective AI Agents", "Anthropic Engineering", "I", 25, "https://www.anthropic.com/engineering/building-effective-agents",
        "Anthropic's guide to agent design: start with simple, composable patterns and add autonomy only when it pays for itself.",
        ["Workflows (code-orchestrated) and agents (model-directed) suit different problems.",
         "Simple patterns such as prompt chaining, routing and evaluator-optimizer cover many needs.",
         "Invest in tool design and clear interfaces as much as in prompts."],
        "Classify three AI ideas at work as single call, workflow or agent, and justify each."),
    "g_context_eng": guide(
        "Effective context engineering for AI agents", "Anthropic Engineering", "I", 25, "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents",
        "Why context is a finite resource for agents, and techniques to curate it: compaction, note-taking and sub-agent architectures.",
        ["Aim for the smallest set of high-signal tokens that gets the job done.",
         "Just-in-time retrieval (load data when needed) beats stuffing everything up front.",
         "Long tasks benefit from structured notes and delegating to sub-agents with clean contexts."],
        "Audit one long session with /context and list what you could have loaded just in time instead."),
    "g_tools": guide(
        "Writing effective tools for AI agents—using AI agents", "Anthropic Engineering", "I", 25, "https://www.anthropic.com/engineering/writing-tools-for-agents",
        "How to design, evaluate and improve the tools (including MCP servers) agents call, often with the agent's help.",
        ["Fewer, well-chosen tools beat wrapping every API endpoint.",
         "Clear names, descriptions and token-efficient responses change agent behavior a lot.",
         "Evaluate tools with realistic tasks and let the agent suggest improvements."],
        "Review the descriptions of one MCP server you use and rewrite the weakest one."),
    "g_skills_eng": guide(
        "Equipping agents for the real world with Agent Skills", "Anthropic Engineering", "I", 20, "https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills",
        "The design behind Agent Skills: folders of instructions, scripts and resources that load progressively, only when relevant.",
        ["Progressive disclosure: a short description first, the full content only when needed.",
         "Skills can bundle scripts so deterministic steps run as code.",
         "Treat third-party skills like software: review before you install."],
        "Sketch the folder for one skill you'd build: SKILL.md, one script, one reference file."),
    "g_steering": guide(
        "Steering Claude Code: when to use CLAUDE.md, skills, hooks, and subagents", "Claude blog (Anthropic)", "I", 15,
        "https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more",
        "A practical guide to picking the right extension for each kind of instruction, referenced from the official docs.",
        ["Always-on facts go in CLAUDE.md; on-demand knowledge goes in skills.",
         "Anything that must happen every time belongs in a hook.",
         "Subagents are for isolation and parallelism, not for storing rules."],
        "Sort ten instructions you've given Claude into CLAUDE.md, rule, skill, hook or subagent."),
    "g_teams": guide(
        "How Anthropic teams use Claude Code", "Claude blog (Anthropic)", "B", 20, "https://claude.com/blog/how-anthropic-teams-use-claude-code",
        "Examples of how engineering and non-engineering teams inside Anthropic use Claude Code day to day.",
        ["Non-engineers use it too, for data work, docs and internal tools.",
         "Teams share what works through CLAUDE.md, skills and checked-in settings.",
         "Parallel sessions and review patterns change how work is split."],
        "Pick one workflow from the article and try it on your own team for a week."),
    "g_auto_mode": guide(
        "How we built Claude Code auto mode", "Anthropic Engineering", "A", 20, "https://www.anthropic.com/engineering/claude-code-auto-mode",
        "Why and how Claude Code's auto mode uses a separate classifier to approve routine actions and block risky ones.",
        ["Approval fatigue makes manual prompts less safe than they look.",
         "A classifier reviewing actions can block scope escalation and actions driven by hostile content.",
         "Deny rules and sandboxing still matter alongside auto mode."],
        "List the last ten permission prompts you approved and how many you actually read."),
    "g_action": guide(
        "claude-code-action (GitHub repository)", "Anthropic", "A", 30, "https://github.com/anthropics/claude-code-action",
        "The source, setup docs, examples and security notes for running Claude Code in GitHub Actions.",
        ["Start from the examples folder rather than writing a workflow from scratch.",
         "Read the security doc before enabling it on repositories with outside contributors.",
         "`claude_args` passes CLI flags such as model and allowed tools."],
        "Copy one example workflow to a test repository and trigger it with an @claude comment."),
    "g_skills_repo": guide(
        "anthropics/skills (GitHub repository)", "Anthropic", "I", 30, "https://github.com/anthropics/skills",
        "Example skills from Anthropic that show structure, frontmatter and bundled scripts you can adapt.",
        ["Reading good skills is the fastest way to write your own.",
         "Notice how descriptions state when to use the skill.",
         "Scripts inside skills keep deterministic steps reliable."],
        "Adapt one example skill to your project and invoke it with /name."),
    "g_mcp_spec": guide(
        "Model Context Protocol: introduction", "modelcontextprotocol.io", "I", 20, "https://modelcontextprotocol.io/introduction",
        "The official introduction to MCP: clients, servers, tools, resources and prompts.",
        ["MCP standardizes how AI applications connect to tools and data.",
         "Servers can expose tools (actions), resources (data) and prompts (templates).",
         "The same server works with any MCP-capable client."],
        "Draw how Claude Code, one MCP server and the external system it wraps talk to each other."),
    "g_agent_sdk": guide(
        "Agent SDK overview", "Anthropic", "A", 30, DOCS + "agent-sdk/overview",
        "How to run Claude Code's agent loop programmatically from the CLI, Python or TypeScript to build your own agents.",
        ["The SDK gives you built-in tools, context management, hooks, subagents and permissions.",
         "Use it when you need a custom agent product rather than an interactive tool.",
         "Scripted runs should set tool allowlists and budgets."],
        "Build the SDK quickstart agent, then add one custom tool."),
    "g_pricing": guide(
        "Claude API pricing", "Anthropic", "I", 10, "https://platform.claude.com/docs/en/about-claude/pricing",
        "Official per-model token prices, prompt caching and batch pricing for the Claude API.",
        ["Output tokens cost several times more than input tokens.",
         "Cache reads are billed at a small fraction of the input price.",
         "Batch processing is discounted for work that can wait."],
        "Plug your own token counts into this app's API cost calculator using today's official prices."),
    # ───────────── 📖 Books ─────────────
    "b_vibe": book(
        "Vibe Coding", "Gene Kim & Steve Yegge", 2025, 8, "I",
        "Two well-known engineering authors make the case for building software with AI coding agents and describe the practices that keep it safe and productive.",
        ["Treat agents like a fast but fallible team: delegate with clear goals and check results.",
         "Small batches, fast feedback and good tests matter even more with AI.",
         "Developers move from typing code to directing and reviewing work."],
        "Pick one practice from the book and apply it to every Claude Code session for a week."),
    "b_beyond": book(
        "Beyond Vibe Coding", "Addy Osmani", 2025, 6, "B",
        "A practical guide to AI-assisted engineering that goes past quick demos to maintainable, reviewed, production-quality work.",
        ["Use AI for the first 70%, and own the last 30% (edge cases, quality, integration).",
         "Specs, tests and review are what turn AI output into shippable software.",
         "Choose the right mode: exploration, pairing or delegated agent work."],
        "Write a one-page spec before your next feature and compare the result with an unspecified one."),
    "b_aieng": book(
        "AI Engineering", "Chip Huyen", 2025, 15, "I",
        "A comprehensive guide to building applications on foundation models: evaluation, prompting, RAG, agents, fine-tuning and inference optimization.",
        ["Evaluation is the hardest and most important part of AI engineering.",
         "Start with prompting and retrieval before fine-tuning.",
         "Inference cost and latency shape product design."],
        "Read the evaluation chapters and write an eval plan for one feature."),
    "b_prompt": book(
        "Prompt Engineering for LLMs", "John Berryman & Albert Ziegler", 2024, 8, "I",
        "How LLMs read prompts and how to design context, from two engineers who worked on GitHub Copilot.",
        ["Think of prompts as documents the model completes.",
         "Context selection and ordering matter as much as wording.",
         "Measure prompt changes instead of trusting intuition."],
        "Rewrite one weak Claude Code prompt using the book's context-assembly ideas."),
    "b_agents": book(
        "Building Applications with AI Agents", "Michael Albada", 2025, 10, "A",
        "Design patterns for agentic systems: tools, planning, memory, multi-agent coordination, evaluation and safety.",
        ["Start with one agent and well-designed tools before going multi-agent.",
         "Memory and orchestration are architecture decisions with trade-offs.",
         "Measure agents with task-level evals, not just single responses."],
        "Map your subagents and skills onto the book's patterns and note one gap."),
    "b_handsonllm": book(
        "Hands-On Large Language Models", "Jay Alammar & Maarten Grootendorst", 2024, 12, "I",
        "A highly visual, code-first tour of how LLMs work and how to use them for classification, search, RAG and generation.",
        ["Embeddings and retrieval power many practical LLM apps.",
         "Visual intuition for tokens and attention helps debug behavior.",
         "Small, well-chosen models can beat large ones on narrow tasks."],
        "Have Claude Code build one notebook example from the book for your own data."),
    "b_dmls": book(
        "Designing Machine Learning Systems", "Chip Huyen", 2022, 14, "A",
        "How to design ML systems for production: data, features, deployment, monitoring and iteration.",
        ["Production ML is mostly data and infrastructure, not models.",
         "Plan for distribution shift and monitoring from day one.",
         "Batch vs online inference is a core design choice."],
        "Write a deployment and monitoring checklist for one inference feature."),
    "b_pragprog": book(
        "The Pragmatic Programmer", "David Thomas & Andrew Hunt", 2019, 10, "B",
        "Timeless software craftsmanship advice that becomes more important when an AI writes much of the code.",
        ["Don't live with broken windows: fix small problems early.",
         "Make it easy to verify: tests, automation and small steps.",
         "Take responsibility for results, whoever (or whatever) typed the code."],
        "Choose one tip and encode it as a CLAUDE.md rule or a hook."),
    "b_accelerate": book(
        "Accelerate", "Nicole Forsgren, Jez Humble & Gene Kim", 2018, 6, "I",
        "Research-backed metrics and practices for high-performing software delivery, useful for measuring AI-assisted development.",
        ["Four key metrics: deployment frequency, lead time, change failure rate, time to restore.",
         "Speed and stability improve together with good practices.",
         "Measure outcomes at the team level, not individual activity."],
        "Baseline the four metrics before a Claude Code pilot so you can show real impact."),
    "b_cointel": book(
        "Co-Intelligence", "Ethan Mollick", 2024, 5, "B",
        "A practical guide to working alongside AI as a coworker, tutor and creative partner.",
        ["Invite AI into every task you're allowed to, to learn where it helps.",
         "Stay the human in the loop: you own the result.",
         "Assume today's model is the weakest you'll use."],
        "For a week, try Claude Code first on every eligible task and log where it saved time."),
    "b_aiassist": book(
        "AI-Assisted Programming", "Tom Taulli", 2024, 6, "B",
        "An accessible overview of using AI coding tools across the development lifecycle, from planning to testing.",
        ["AI helps across the lifecycle, not only while typing code.",
         "Good prompts look like good specifications.",
         "Review and testing stay human responsibilities."],
        "Use Claude Code for one non-coding SDLC task (test plan, release notes, runbook)."),
    # ───────────── 🎓 Courses ─────────────
    "c_cc_action": course(
        "Claude Code in Action", "Anthropic Academy", 2, "B", "Free", None,
        "Anthropic's own short course on using Claude Code: context, workflows, custom commands, MCP, hooks and GitHub integration.",
        ["Context management is the core skill.",
         "Extensions (commands, MCP, hooks) turn Claude Code into a team tool.",
         "GitHub integration brings Claude into PRs and issues."],
        "Do the course alongside a real repository and apply each lesson the same day."),
    "c_dlai_cc": course(
        "Claude Code: A Highly Agentic Coding Assistant", "DeepLearning.AI", 2, "B", "Free", None,
        "A hands-on short course built with Anthropic covering everyday Claude Code workflows on real projects.",
        ["Explore a codebase before changing it.",
         "Use planning, subagents and parallel sessions for larger work.",
         "Integrate MCP servers and GitHub for end-to-end tasks."],
        "Recreate one course project on your own codebase."),
    "c_mcp_intro": course(
        "Introduction to Model Context Protocol", "Anthropic Academy", 2, "I", "Free", None,
        "Build an MCP server and client and learn tools, resources and prompts.",
        ["Tools are actions, resources are data, prompts are templates.",
         "The MCP inspector helps debug servers.",
         "Good tool descriptions drive good tool use."],
        "Build a tiny MCP server for a personal data source and connect it to Claude Code."),
    "c_mcp_adv": course(
        "Model Context Protocol: Advanced Topics", "Anthropic Academy", 2, "A", "Free", None,
        "Deeper MCP topics such as sampling, notifications, transports and production concerns.",
        ["Transport choice affects deployment and scaling.",
         "Servers can request model completions through the client (sampling).",
         "Production servers need auth, logging and limits."],
        "Review one MCP server you use against the course's production checklist."),
    "c_dlai_mcp": course(
        "MCP: Build Rich-Context AI Apps with Anthropic", "DeepLearning.AI", 2, "I", "Free", None,
        "A short course on building MCP servers and clients and connecting them to AI applications.",
        ["MCP removes one-off integrations between apps and tools.",
         "Build a server once, reuse it across clients.",
         "Remote servers make tools shareable across a team."],
        "Connect the course's server to Claude Code with `claude mcp add`."),
    "c_api": course(
        "Building with the Claude API", "Anthropic Academy", 8, "I", "Free", None,
        "A comprehensive course on building apps with the Claude API: prompting, tool use, RAG, evals, MCP and agents.",
        ["Prompt evaluation should be systematic, not by eye.",
         "Tool use and structured output make model calls reliable in code.",
         "Agents and workflows are built from the same API primitives."],
        "Build the course's eval workflow for your own prototype."),
    "c_ai_fluency": course(
        "AI Fluency: Framework & Foundations", "Anthropic Academy", 3, "B", "Free", None,
        "A framework for working with AI effectively and responsibly: delegation, description, discernment and diligence.",
        ["Decide what to delegate to AI and what to keep.",
         "Describe tasks clearly; judge outputs critically.",
         "Stay accountable for how AI output is used."],
        "Apply the framework to one Claude Code task and write what you'd delegate next time."),
    "c_vandy": course(
        "Claude Code: Software Engineering with Generative AI Agents", "Vanderbilt University (Coursera)", 8, "I", "Free to audit; certificate paid", None,
        "A university course on engineering software with AI agents, using Claude Code for structured, verifiable work.",
        ["Structure work so an agent can verify it.",
         "Specs and tests are the steering wheel.",
         "Parallel agents need clear task boundaries."],
        "Take one module and apply its workflow to a side project."),
    "c_hf_agents": course(
        "AI Agents Course", "Hugging Face", 20, "I", "Free", None,
        "A free, hands-on course on how AI agents work, with frameworks, tools and a final project.",
        ["Agents combine a model, tools and a loop.",
         "Observability and evaluation are essential for agents.",
         "Framework choice matters less than clear tools and tasks."],
        "Compare the course's agent loop with Claude Code's gather-act-verify loop."),
    # ───────────── 🏅 Certifications ─────────────
    "x_academy": cert(
        "Anthropic Academy course certificates", "Anthropic", 6, "B", None, None,
        "Completion certificates from Anthropic Academy courses: a free way to show structured Claude learning.",
        ["Low cost, fast to earn.",
         "Pairs well with a public project that uses the skills.",
         "Shows recent, vendor-specific learning."],
        "Finish Claude Code in Action and attach the certificate to a project write-up."),
    "x_cca": cert(
        "Claude Certified Architect – Foundations", "Anthropic", 20, "I", None, None,
        "Anthropic's credential for designing solutions with Claude. Eligibility and availability may depend on Anthropic's partner programs; confirm on the official page.",
        ["Check the official exam guide for the current domains and format.",
         "Most valuable when paired with shipped work.",
         "Check current eligibility and exam details before planning."],
        "Read the official exam guide and map each domain to a stage of this app."),
    "x_awsaip": cert(
        "AWS Certified AI Practitioner (AIF-C01)", "Amazon Web Services", 15, "B", 100, "https://aws.amazon.com/certification/",
        "A foundational exam on AI, ML and generative AI concepts and AWS services, including Amazon Bedrock where Claude is available.",
        ["Good AI literacy proof for TPMs.",
         "Covers responsible AI and use-case selection.",
         "Bedrock knowledge helps when Claude runs through AWS."],
        "Pair the exam with a small Bedrock-hosted Claude prototype."),
    "x_awsgenai": cert(
        "AWS Certified Generative AI Developer – Professional", "Amazon Web Services", 60, "A", 300, "https://aws.amazon.com/certification/",
        "A professional-level exam on building generative AI solutions on AWS, including evaluation, safety and operations.",
        ["Production concerns: cost, latency, monitoring and security.",
         "RAG and agent architectures on AWS.",
         "Hands-on experience matters more than memorization."],
        "Use Claude Code to build the hands-on labs you study with."),
    "x_ai102": cert(
        "Microsoft Certified: Azure AI Engineer Associate (AI-102)", "Microsoft", 40, "I", 165, "https://learn.microsoft.com/credentials/",
        "An associate exam on designing and implementing AI solutions on Azure, including generative AI and agents.",
        ["Useful if your company runs on Azure (Claude is available through Microsoft Foundry).",
         "Covers responsible AI and solution monitoring.",
         "Free Microsoft Learn paths support preparation."],
        "Build one Foundry-hosted inference prototype with Claude Code while studying."),
    "x_gcpgenai": cert(
        "Google Cloud Generative AI Leader", "Google Cloud", 15, "B", 99, "https://cloud.google.com/learn/certification",
        "A non-technical exam on generative AI strategy, use cases and Google Cloud offerings.",
        ["Strong fit for TPMs and leaders.",
         "Focuses on business value and adoption.",
         "Short preparation time."],
        "Write a one-page AI adoption plan using the exam's framing."),
    "x_cpmai": cert(
        "PMI Cognitive Project Management in AI (PMI-CPMAI)", "Project Management Institute", 30, "I", None, "https://www.pmi.org",
        "A method-based certification for running AI and data projects, from business understanding to operationalization.",
        ["Iterative phases fit AI uncertainty.",
         "Data readiness is a first-class gate.",
         "Speaks the language of program governance."],
        "Map a Claude Code rollout pilot onto the CPMAI phases."),
    # ───────────── 🎧 Podcasts ─────────────
    "p_latent": podcast(
        "Latent Space", "swyx & Alessio Fanelli", "A", 60, "https://www.latent.space",
        "The AI engineer's podcast, with in-depth interviews with builders of coding agents and AI tools.",
        ["Coding agents are one of the fastest-moving areas in AI engineering.",
         "Builders explain design trade-offs you won't find in docs.",
         "Good for spotting trends early."],
        "Search the feed for Claude Code episodes and note one idea to try."),
    "p_pragmatic": podcast(
        "The Pragmatic Engineer", "Gergely Orosz", "I", 60, None,
        "Deep conversations on how software teams actually work, increasingly including AI coding tools.",
        ["How real teams adopt AI tools, not just hype.",
         "Engineering culture shapes AI success.",
         "Practical numbers on productivity and quality."],
        "Listen to one AI-tools episode and compare with your team's experience."),
    "p_aiandi": podcast(
        "AI & I", "Dan Shipper (Every)", "B", 60, None,
        "Interviews with people about how they use AI to think, write and build, including heavy Claude Code users.",
        ["Workflows from people who use AI all day.",
         "Many uses beyond coding.",
         "Concrete prompts and setups."],
        "Copy one workflow you hear and run it for a week."),
    "p_practical": podcast(
        "Practical AI", "Daniel Whitenack & Chris Benson", "B", 45, "https://practicalai.fm",
        "Accessible conversations about making AI practical and productive, including tools and MCP.",
        ["Focus on applied, real-world AI.",
         "Covers infrastructure and tooling.",
         "Good on-ramp for non-specialists."],
        "Listen to one episode on agents or MCP and summarize it for your team."),
    "p_lenny": podcast(
        "Lenny's Podcast", "Lenny Rachitsky", "B", 75, "https://www.lennysnewsletter.com/podcast",
        "Product and growth interviews, with frequent episodes on AI products and how AI changes product and engineering work.",
        ["How product leaders think about AI features.",
         "Adoption and change management stories.",
         "Career advice in the AI era."],
        "Pick one AI episode and write three takeaways for your role."),
    "p_sedaily": podcast(
        "Software Engineering Daily", "Software Engineering Daily", "I", 50, None,
        "Technical interviews on software engineering topics, including developer tools, agents and infrastructure.",
        ["Broad coverage of engineering topics.",
         "Hear from tool builders directly.",
         "Useful for context on the ecosystem."],
        "Listen to one episode on developer tooling or MCP."),
    "p_dwarkesh": podcast(
        "Dwarkesh Podcast", "Dwarkesh Patel", "A", 120, "https://www.dwarkesh.com",
        "Long-form interviews with AI researchers and leaders about where AI capabilities are heading.",
        ["Big-picture view of AI progress.",
         "Helps plan for rapidly improving models.",
         "Deep, technical guests."],
        "Note one prediction and how it would change your team's plans."),
    # ───────────── ▶️ YouTube ─────────────
    "y_anthropic": youtube(
        "Anthropic (official channel)", "Anthropic", "B", 20, "Anthropic Claude Code",
        "Official talks, demos and conference sessions on Claude Code and building with Claude.",
        ["Hear best practices from the people who build it.",
         "Demos show workflows faster than text.",
         "Conference talks cover advanced patterns."],
        "Watch one Claude Code talk and try its main tip the same day."),
    "y_karpathy": youtube(
        "Software Is Changing (Again)", "Andrej Karpathy", "B", 40, "Andrej Karpathy Software Is Changing Again",
        "A widely shared talk on 'Software 3.0', LLMs as a new kind of computer, and building partially autonomous apps.",
        ["Prompts are a new kind of program.",
         "Keep humans in a fast generate-verify loop.",
         "Build 'autonomy sliders' into AI products."],
        "Write down where your Claude Code use sits on the autonomy slider and why."),
    "y_indydevdan": youtube(
        "IndyDevDan", "IndyDevDan", "A", 25, "IndyDevDan Claude Code",
        "An independent creator focused on agentic coding with Claude Code: hooks, subagents and multi-agent workflows.",
        ["Advanced patterns for hooks and subagents.",
         "Emphasis on engineering discipline with agents.",
         "Many concrete configurations."],
        "Reproduce one hook or subagent setup from a video in a test repo."),
    "y_colemedin": youtube(
        "Cole Medin", "Cole Medin", "I", 25, "Cole Medin Claude Code",
        "Practical videos on AI coding workflows, context engineering and agent building.",
        ["Context engineering templates.",
         "End-to-end builds with AI coding tools.",
         "MCP and agent integrations."],
        "Adapt one context-engineering template to your project."),
    "y_aiengineer": youtube(
        "AI Engineer (conference talks)", "AI Engineer", "I", 30, "AI Engineer conference Claude Code",
        "Talks from the AI Engineer conferences, including sessions on coding agents, evals and production AI.",
        ["Practitioners share what worked in production.",
         "Evals and reliability are recurring themes.",
         "Good map of the AI engineering landscape."],
        "Watch one talk on evals and apply one idea to your prototype."),
    "y_fireship": youtube(
        "Fireship", "Fireship", "B", 10, "Fireship Claude Code",
        "Fast, funny explainers of developer tools and AI news, good for quick orientation.",
        ["Short overviews before deep dives.",
         "Keeps you current on tools.",
         "Entertaining refreshers."],
        "Watch one AI coding video, then check its claims against the docs."),
    "y_freecodecamp": youtube(
        "freeCodeCamp: Claude Code tutorials", "freeCodeCamp.org", "B", 90, "freeCodeCamp Claude Code tutorial",
        "Free long-form tutorials, including full courses on AI coding tools and building with Claude.",
        ["Step-by-step, beginner friendly.",
         "Full projects rather than snippets.",
         "Free and ad-light."],
        "Follow one tutorial end to end in a fresh repository."),
    "y_codewithclaude": youtube(
        "Code with Claude talks", "Anthropic", "I", 30, "Code with Claude Anthropic conference talk",
        "Recorded sessions from Anthropic's developer conference covering Claude Code workflows and building with Claude.",
        ["Best practices from Anthropic engineers.",
         "Real workflows shown live.",
         "Roadmap context for features."],
        "Watch the Claude Code best-practices session and update your CLAUDE.md afterwards."),
}

RESOURCES = {key: {"key": key, **value} for key, value in _RESOURCES.items()}

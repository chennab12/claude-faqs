# 🧑‍💻 Claude Code Learning Hub

One place to learn [Claude Code](https://code.claude.com/docs/en/overview) from scratch to advanced, for use at work and at home, including building AI/ML inference apps on the Claude API. Every section has a TPM takeaway. It follows the layout of [ai-ml-learnings](https://github.com/chennab12/ai-ml-learnings): a sidebar menu, one page per stage, previous/next buttons, a master cheatsheet, a learning plan and calculators.

## Pages

- 🏠 **Start here**: totals, a 30-minutes-a-day routine, the 11 stages grouped by level, and a ten-item fast track.
- 🗺️ **Roadmap & skill ladder**: stage dates for your weekly hours, and a beginner-to-expert self-assessment that names your two biggest gaps.
- 📌 **Master cheatsheet**: one row per concept (with its TPM takeaway and docs link), every copy-paste snippet, key numbers, a KPI library, practice projects, prerequisites, common mistakes, a 33-term glossary and every resource in one line, with CSV downloads.
- **11 stages, 33 core concepts**, ordered basics → intermediate → advanced:
  - 🟢 Getting started · Prompting & everyday workflow · Context & memory
  - 🟡 Permissions, safety & checkpoints · Skills & slash commands · MCP & external tools · Hooks & automation
  - 🔴 Subagents & parallel work · Headless, CI/CD & the Agent SDK · Cost, models & team rollout · Building AI/ML inference apps

  Every concept has a gist, why it matters, a plain-words explanation, an example, a copy-paste snippet, three insights, two intuition tips, two experiments to try, three timed next steps, a metric to track, a 🧭 **TPM takeaway**, links to the official docs pages it follows, the best resources and a three-question quick check.

  The bottom of every stage adds a 📊 KPI table, a 🔬 interactive lab (install picker and first-session checklist, prompt upgrader, context budget simulator, permission rule tester and settings.json builder, SKILL.md generator, `claude mcp add` builder, hook config builder, subagent generator with a parallel-throughput model, `claude -p` command builder, session cost simulator, inference cost and quality planner), a 🛠️ worked project with a "your turn" project, a ⚠️ table of common mistakes and fixes, and a 🧩 prerequisites table.
- 📚 **Resource library**: 56 resources (14 official guides, 11 books, 9 courses, 7 certifications, 7 podcasts, 8 YouTube channels) with filters by type, level, stage, cost and keyword. Each has a gist, three insights and one thing to try.
- 🏅 **Certification guide**: exam fees, prep hours and a suggested order.
- 📝 **Quiz center**: 99 multiple-choice questions with explanations, filtered by stage, a "my missed questions" review mode and accuracy by stage.
- 🗓️ **My learning plan**: pick books, courses and certifications and set weekly hours to get finish dates; download as CSV.
- 🧮 **Calculators**: team cost, productivity ROI, tokens & context, prompt caching savings, API inference cost, agent reliability, parallel throughput and study time.
- 📖 **Official docs map**: every docs page the app follows and which concepts use it.
- 🔎 **Search everything**: concepts, snippets, tips, mistakes, glossary and resources in one box.
- 💾 **Save or restore progress** (sidebar), ▶️ **Continue where you left off**, and **deep links** such as `?page=hooks-automation`.

## About the content

"Top 20%" is a curated editorial judgement, not a measured ranking: the concepts are the ones the official docs and Anthropic's guides return to most, because they give the most results per hour of learning.

Feature facts (commands, flags, settings, file paths, hook events, frontmatter fields) follow the official docs at [code.claude.com](https://code.claude.com/docs/en/overview), reviewed 14 October 2026, and each concept links the pages it follows. Claude Code ships often, so when the app and the docs disagree, the docs win. All summaries, takeaways and quiz questions are original text, not quotes.

Book links search [Open Library](https://openlibrary.org). Courses and certifications link to the official page where it was checked, otherwise to a web search for the exact title. Podcasts link to the show or a podcast search, and YouTube links search for the channel. **Model prices, exam fees and course catalogs change often**, so check the official page before paying. Calculators are back-of-envelope illustrations, not vendor quotes.

| File | What it holds |
|---|---|
| `content.py` | Stages, concepts, quizzes, glossary, skill ladder, docs page titles |
| `practice.py` | KPIs, worked projects, mistakes, intuition tips |
| `prerequisites.py` | Prerequisites per stage |
| `resources.py` | The resource catalog |
| `calculations.py` | Calculator math and example model prices |
| `labs.py` / `lab_pages.py` | Lab logic (generators, rule tester, simulators) and their pages |
| `app.py` | Navigation and every page |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pip install pytest && python -m pytest -q`. GitHub Actions runs them on every push. For Streamlit Community Cloud, deploy this repository with `app.py` as the entry point.
